"""
广东醒狮 60s 短片 - 自动化剪辑脚本
作者脚本来源: 1e32b3f6-____2.txt (G1-G6 分镜)
素材: 一条按脚本拍好的 60s 视频 (16:9)
需要补齐: 爷爷旁白 (TTS) + 温暖钢琴 BGM + 烟花/掌声 SFX + 字幕

用法:
    python build_lion_dance.py                  # 用项目目录下 assets/lion_dance.mp4
    python build_lion_dance.py /path/video.mp4  # 自定义视频路径
"""

import os
import sys

# ========= Skill 环境自举 (必填, 来自 rules/setup.md) =========
current_dir = os.path.dirname(os.path.abspath(__file__))
env_root = os.getenv("JY_SKILL_ROOT", "").strip()
skill_candidates = [
    env_root,
    os.path.dirname(current_dir),                           # repo root
    os.path.join(current_dir, ".claude", "skills", "jianying-editor"),
    os.path.join(current_dir, ".agent", "skills", "jianying-editor"),
    os.path.join(current_dir, "skills", "jianying-editor"),
    os.path.abspath(".claude/skills/jianying-editor"),
]
skill_root = None
for p in skill_candidates:
    if p and os.path.exists(os.path.join(p, "scripts", "jy_wrapper.py")):
        skill_root = os.path.abspath(p)
        break
if not skill_root:
    raise ImportError("Could not locate jianying-editor skill root")
sys.path.insert(0, os.path.join(skill_root, "scripts"))

if sys.platform == "darwin":
    hb = "/opt/homebrew/bin"
    if hb not in os.environ.get("PATH", ""):
        os.environ["PATH"] = hb + ":" + os.environ.get("PATH", "")

from jy_wrapper import JyProject  # noqa: E402

# ========= 配置 =========
VIDEO_PATH = (
    sys.argv[1] if len(sys.argv) > 1
    else os.path.join(current_dir, "assets", "lion_dance.mp4")
)
PROJECT_NAME = "广东醒狮_点睛"

# 爷爷旁白——每条 (起始秒, 文案)
NARRATIONS = [
    (4,  "老辈人讲啊，狮头一点睛，狮子就醒了。"),         # G1 02-15s
    (15, "我们广东人走到哪，就把狮子扛到哪。扛着它跑码头闯南洋。"),  # G2 15-25s
    (25, "有去香港讨生活的——"),                             # G3 25-35s
    (35, "有在深圳工地开工放鞭炮的。"),                     # G4 35-45s
    (45, "扛的不只是狮子，还有家乡。"),                     # G5 45-50s
]

# 云端资源 ID (来自 data/cloud_music_library.csv & cloud_sound_effects.csv)
BGM_ID         = "7273803822581041210"   # Documentary Piano (140s)
SFX_FIREWORK   = "7605852687803993380"   # 烟花爆炸音效19 (1.73s)
SFX_APPLAUSE   = "7605852073720155398"   # 室内拍手音效3 (0.97s)

SPEAKER_GRANDPA = "zh_male_iclvop_miaojijsqinggan"  # 深情男低音


def main() -> None:
    if not os.path.exists(VIDEO_PATH):
        raise FileNotFoundError(
            f"视频素材不存在: {VIDEO_PATH}\n"
            "把素材放到 _user_project/assets/lion_dance.mp4 "
            "或命令行传绝对路径: python build_lion_dance.py /abs/path/video.mp4"
        )

    # 1) 建工程 (16:9 竖横屏自适应——会在导入主视频时按素材比例覆盖)
    project = JyProject(PROJECT_NAME, overwrite=True)
    print(f"[OK] 工程已创建: {PROJECT_NAME}")

    # 2) 主视频入主轨, 从 0s 开始, 完整 60s
    main_seg = project.add_media_safe(
        VIDEO_PATH, start_time="0s", track_name="VideoTrack"
    )
    if not main_seg:
        raise RuntimeError("主视频导入失败")
    print(f"[OK] 主视频入轨: {VIDEO_PATH}")

    # 3) 铺 BGM —— 一整条温暖钢琴, 60s, 音量压到 0.4 让位旁白
    bgm_seg = project.add_cloud_music(
        BGM_ID, start_time="0s", duration="60s", track_name="BGM",
    )
    if bgm_seg is not None:
        try:
            bgm_seg.volume = 0.4
        except Exception:
            pass
        print("[OK] BGM 铺好 (Documentary Piano, vol=0.4)")
    else:
        print("[WARN] BGM 下载失败, 跳过 (剪映里可手动替换)")

    # 4) 五段 TTS 旁白 + 对齐字幕 (爷爷音色 - 深情男低音)
    for start_s, text in NARRATIONS:
        try:
            project.add_narrated_subtitles(
                text=text,
                speaker=SPEAKER_GRANDPA,
                start_time=f"{start_s}s",
                track_name="Subtitles",
            )
            print(f"[OK] 旁白+字幕 @ {start_s}s: {text}")
        except Exception as e:
            print(f"[WARN] 旁白 @ {start_s}s 失败: {e}")

    # 5) G4 片段 (35-45s) 的烟花 + 掌声
    #    鞭炮打在 36s (旁白"放鞭炮的"字正落下),
    #    掌声打在 37s 让情绪延续
    def _add_sfx(sid: str, start_s: int, track: str, label: str) -> None:
        try:
            seg = project.add_cloud_media(sid, start_time=f"{start_s}s", track_name=track)
            if seg is None:
                print(f"[WARN] {label} 下载失败 (在剪映里手动补)")
            else:
                print(f"[OK] SFX {label} @ {start_s}s")
        except Exception as e:
            print(f"[WARN] {label} 失败: {e}")

    _add_sfx(SFX_FIREWORK, 36, "SFX_Firework", "鞭炮")
    _add_sfx(SFX_APPLAUSE, 37, "SFX_Applause", "掌声")

    # 6) 保存
    result = project.save()
    print("\n==============================")
    print(f"[DONE] 草稿已生成: {result}")
    print("==============================")
    print("""
手工补齐提示 (剪映 UI 内音效搜索):
  G1 00:02  一声沉锣       → 搜 "锣" / "开场锣"
  G2 15-25  汽笛 + 海风     → 搜 "汽笛"、"海浪"
  G3 25-35  茶摊人声/木屐   → 搜 "人声氛围"、"街市"
  G6 50-60  收尾锣余音      → 搜 "锣 余音"
""")


if __name__ == "__main__":
    main()
