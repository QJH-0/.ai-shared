---
name: explainer-video
description: >
  用 manim 生成 3b1b 风格的讲解视频：脚本 → 程序化动画 → TTS 配音 → 合成 MP4。
  当需要把某个原理讲成一支视频、要「3b1b 风格的解释」「动画演示 + 旁白」「公式推导动画」时使用。
  Triggers: 讲解视频, 3b1b, manim, 动画讲解, explainer video, 视频解释, 公式推导动画, 动画演示.
---

# 3b1b 风格讲解视频

## 适用

原理、推导、演化过程这类「讲十遍不如看一遍」的内容。一句话能说清的内容不要做视频。

manim 就是 3b1b 本人使用的动画引擎，所以「3b1b 风格」在这里不是模仿，是同一个工具。

## 环境（本机实测，2026-10-04）

| 组件 | 版本 / 位置 |
|------|-------------|
| Python | `C:\Users\20448\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe` |
| manim | 0.21.0 |
| imageio-ffmpeg | 0.6.0（内置 ffmpeg v7.1，**不含 ffprobe**） |
| edge-tts | 已装（云端免费 TTS，实测可用） |
| LaTeX | **未安装** |

一次性安装（已在本机完成，重装或换机时用）：

```bash
"C:/Users/20448/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe" -m pip install \
  -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
  manim imageio-ffmpeg edge-tts
```

**本机网络实测（重要）**：

- 清华源不可用（返回 `from versions: none`）；阿里云与 `pypi.org` 可用，但**约 100 KB/s**。
- 整棵依赖树约 350 MB，安装要 **20–30 分钟**。pip 的进度条用 `\r` 回写，**不写进重定向的日志**——看起来像卡死，其实在下载。判断进度的可靠方式是看 venv 体积（`du -sh <venv>`）而不是看日志。
- 加 `--progress-bar off` 可避免日志里的 `\r` 污染。
- 单个大 wheel（如 31 MB 的 `imageio_ffmpeg`）若 pip 长时间无进展，用 `curl -sL -C -` 断点续传到本地，再 `pip install <本地 wheel>`。

## 管道

四步，已由 `scripts/build.py` 串起来：

```bash
"C:/Users/20448/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe" \
  "C:/Users/20448/.ai-shared/skills/explainer-video/scripts/build.py" \
  --scene scene.py --class MyScene --narration narration.txt --out final.mp4 \
  --quality m --workdir .
```

| 步骤 | 做什么 |
|------|--------|
| 1 | manim 渲染场景为 MP4 |
| 2 | edge-tts 把旁白文本转成 MP3 |
| 3 | 量出两者时长，按差值补齐视频末尾 |
| 4 | ffmpeg 合成，输出带配音的 MP4 |

`--quality`：`l` = 480p15、`m` = 720p30、`h` = 1080p60（默认 `m`）。画质越高渲染越慢。

## 写场景脚本

```python
from manim import *


class MyScene(Scene):
    def construct(self):
        title = Text("注意力机制", font_size=56)
        formula = Text("softmax(QKᵀ/√d) V", font_size=32).next_to(title, DOWN)
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(formula, shift=UP * 0.3), run_time=0.8)
        self.wait(1.0)
```

规则：

- **用 `Text` 不用 `MathTex`**。本机无 LaTeX，`MathTex` / `Tex` 会直接失败。公式写成 Unicode（`QKᵀ`、`√d`、`α β γ ∫ Σ`）或用 `Text` 分段拼。
- **动画总时长对齐旁白**。先写旁白、生成 TTS、量出秒数，再回头调 `run_time` 与 `self.wait()`。差值由第 3 步补齐兜底，但动画明显短于旁白时画面会长时间定格。
- **一个 `Scene` 讲一件事**。内容多就拆多个场景分别渲染，再按顺序拼接。

## 关键实现细节（踩过的坑）

- **manim 找不到 ffmpeg**：它默认从 PATH 找，本机 PATH 里没有。必须用 `--config_file` 指定一个含 `ffmpeg_executable` 的 `manim.cfg`；`build.py` 会自动生成。
- **画质参数要合并写**：`-qm` 合法，`-m` 会报 `No such option '-m'`。
- **产物路径**：`<media_dir>/videos/<脚本名>/<画质目录>/<类名>.mp4`，画质目录为 `480p15` / `720p30` / `1080p60`。
- **只加 `-shortest` 会截掉旁白**（实测：视频 2.40 s + 旁白 5.59 s → 输出 4.40 s，丢 1.19 s 配音）。必须先 `tpad=stop_mode=clone:stop_duration=<差值>` 把视频补到旁白长度。
- **没有 ffprobe**：`imageio-ffmpeg` 只提供 ffmpeg。取时长要从 `ffmpeg -i <文件>` 的 stderr 里抓 `Duration: HH:MM:SS.ss`。
- **给 Python 传路径必须用 `C:/...`**。Git Bash 风格的 `/c/Users/...` 会被解释成相对路径，报 `can't open file 'C:\\c\\Users\\...'`。

## 已知限制

- **无 LaTeX**：复杂公式（多行对齐、矩阵、积分号上下限）用 Unicode 拼不出来的，得先装 LaTeX（MiKTeX 约 1 GB），本机未装。
- **edge-tts 需联网**：离线环境改用 Windows 内置 SAPI5（`pyttsx3`），音色明显更机械。
- **配音是整段单轨**：`build.py` 把整篇旁白合成一条音轨，做不到「第 3 秒讲什么、第 8 秒讲什么」的逐句对齐。要精确对齐得按段落切分 TTS 并分别计算偏移。
- **渲染耗时**：720p30 的一分钟动画在本机是分钟级；1080p60 更慢。先出 480p15 看节奏，定稿再提画质。

## 反模式

| 反模式 | 问题 |
|--------|------|
| 一句话的结论做成视频 | 打开成本远大于收益，用文本或图表 |
| 动画时长远短于旁白 | 画面长时间定格，观众以为卡了 |
| 用 `MathTex` 硬上 | 本机无 LaTeX，直接报错；改 `Text` + Unicode |
| 一次渲染 1080p60 试错 | 迭代一轮等太久；先用 480p15 定节奏 |
| 把 skill 当视频生成模型用 | manim 是**程序化动画**，不能生成实拍/写实画面；那类需求走 VideoGen |
