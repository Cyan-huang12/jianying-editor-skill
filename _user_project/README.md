# 广东醒狮 60s 短片 · 自动化剪辑

按 G1-G6 分镜给已拍好的视频补齐：**TTS 爷爷旁白 + Documentary Piano BGM + 鞭炮/掌声 SFX + 字幕**。

## 需要你本地跑的原因

生成这份草稿需要连剪映云端服务器（下 BGM/SFX、调用 SAMI TTS），
Claude 的沙箱出口不给访问 `vlabvod.com` / `sami.bytedance.com`，
所以必须在你安装了剪映的那台电脑上执行脚本。

## 使用步骤

### 1. 装剪映 Skill（如果还没装）

```bash
git clone https://github.com/cyan-huang12/jianying-editor-skill.git \
    ~/.claude/skills/jianying-editor
```

（或者 `.agent/skills/jianying-editor` / `.trae/skills/jianying-editor`，看你用哪个 Agent 工具）

### 2. 装 Python 依赖

```bash
pip install -r ~/.claude/skills/jianying-editor/requirements.txt
pip install websockets  # SAMI TTS 需要
```

### 3. 把视频素材放到位

```bash
mkdir -p _user_project/assets
cp /你的视频.mp4 _user_project/assets/lion_dance.mp4
```

或直接传绝对路径（见下一步）。

### 4. 跑脚本

```bash
cd _user_project
python build_lion_dance.py                              # 用 assets/lion_dance.mp4
python build_lion_dance.py /abs/path/to/video.mp4       # 自定义路径
```

脚本会：
- 自动找剪映草稿根目录
- 建一个叫 `广东醒狮_点睛` 的新工程
- 导入你的主视频 (60s, 16:9)
- 从剪映云端下 Documentary Piano 做 BGM（整段 60s，音量 0.4）
- 用 SAMI 深情男低音 (`zh_male_iclvop_miaojijsqinggan`) 合成 5 段爷爷旁白 + 对齐字幕
- 从云端下烟花 + 掌声 SFX 打在 G4 36s / 37s

### 5. 打开剪映

直接双击打开 `广东醒狮_点睛` 工程。预览轴上应该能看到：

- **主轨**：你的视频 60s
- **BGM 轨**：Documentary Piano
- **VoiceOver 轨**：5 条 TTS 旁白
- **Subtitles 轨**：对齐的字幕
- **SFX 轨**：36s 鞭炮、37s 掌声

## 旁白时间分配

按脚本 BGM/人声要求对齐：

| 片段 | 起点 | 文案 |
|---|---|---|
| G1 | 04s | 老辈人讲啊，狮头一点睛，狮子就醒了。 |
| G2 | 15s | 我们广东人走到哪，就把狮子扛到哪。扛着它跑码头闯南洋。 |
| G3 | 25s | 有去香港讨生活的—— |
| G4 | 35s | 有在深圳工地开工放鞭炮的。 |
| G5 | 45s | 扛的不只是狮子，还有家乡。 |

G6 (50-60s) 无台词，钢琴推起 + 收尾静默。

## 需要你在剪映里手工补的 SFX

云端 SFX 库里只有鞭炮和掌声匹配脚本需求。
其他的在剪映 UI "音效素材" 面板里搜：

| 时间 | SFX | 搜索关键词 |
|---|---|---|
| 00:02 | 一声沉锣 | "锣"、"开场锣"、"中国风 锣" |
| 15-25s | 汽笛 + 海风 | "汽笛"、"海浪"、"海风" |
| 25-35s | 茶摊人声 + 木屐 | "街市"、"人声氛围"、"脚步 木屐" |
| 35s | 工地金属声 | "金属 撞击"、"工地" |
| 59s | 收尾锣余音 | "锣 余音"、"锣 回响" |

## 微调建议

在剪映 UI 里按需要再调：
- BGM 音量：旁白段落再压一点到 0.3，G6 无旁白段推到 0.6
- 旁白：如果 SAMI 调的速度/语气不对，右键换 `厚实男声` 或 `经典旁白`
- 字幕样式：默认底部黑色描边，可以换花字

## 卡住的话

脚本任何一步 `[WARN]` 的，就按剪映 UI 的手工操作补；
整段跑挂了，把终端输出发给我，我继续调。
