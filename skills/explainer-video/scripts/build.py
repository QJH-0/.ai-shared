"""把 manim 场景渲染成带 TTS 配音的讲解视频。

流程：manim 渲染动画 → edge-tts 生成配音 → 按差值补齐视频末尾 → 合成 MP4。

用法：
    python build.py --scene demo.py --class Demo --narration narration.txt --out final.mp4
                    [--voice zh-CN-XiaoxiaoNeural] [--quality m] [--workdir .]

配音比动画长时，视频末尾冻结最后一帧补足（`tpad=stop_mode=clone`），
保证旁白一句不丢；动画比配音长时按配音长度截断。
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

FFMPEG_CONFIG_KEY = "ffmpeg_executable"


def _run(cmd, **kw):
    return subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                          errors="replace", **kw)


def ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def duration(path: Path) -> float:
    """用 ffmpeg 的 stderr 解析时长——imageio-ffmpeg 只带 ffmpeg，没有 ffprobe。"""
    out = _run([ffmpeg_exe(), "-i", path]).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        raise RuntimeError(f"无法解析时长：{path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def render(scene: Path, scene_class: str, quality: str, workdir: Path) -> Path:
    """渲染 manim 场景，返回产物 MP4 路径。

    manim 默认从 PATH 找 ffmpeg，本机 PATH 里没有；用 --config_file 显式指定。
    """
    media_dir = workdir / "media"
    cfg = workdir / "manim.cfg"
    cfg.write_text(f"[CLI]\n{FFMPEG_CONFIG_KEY} = {ffmpeg_exe()}\n", encoding="utf-8")

    proc = _run([sys.executable, "-m", "manim", f"-q{quality}", "--format=mp4",
                 "--config_file", cfg, "--media_dir", media_dir,
                 scene, scene_class], cwd=workdir)
    if proc.returncode != 0:
        raise RuntimeError(f"manim 渲染失败：\n{proc.stdout[-3000:]}\n{proc.stderr[-3000:]}")

    hits = sorted(media_dir.glob(f"videos/**/{scene_class}.mp4"))
    if not hits:
        raise RuntimeError(f"渲染成功但未找到产物：{media_dir}/videos/**/{scene_class}.mp4")
    return hits[0]


def narrate(text: str, voice: str, out_mp3: Path) -> Path:
    proc = _run([sys.executable, "-m", "edge_tts", "--text", text,
                 "--voice", voice, "--write-media", out_mp3])
    if proc.returncode != 0 or not out_mp3.exists():
        raise RuntimeError(f"edge-tts 失败（需联网）：\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    return out_mp3


def mux(video: Path, audio: Path, out: Path) -> Path:
    pad = duration(audio) - duration(video)
    if pad > 0:
        vf = f"[0:v]tpad=stop_mode=clone:stop_duration={pad:.2f}[v]"
        maps = ["-filter_complex", vf, "-map", "[v]", "-map", "1:a"]
    else:
        maps = ["-map", "0:v", "-map", "1:a"]

    proc = _run([ffmpeg_exe(), "-y", "-i", video, "-i", audio, *maps,
                 "-c:v", "libx264", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "128k", "-shortest", out])
    if proc.returncode != 0 or not out.exists():
        raise RuntimeError(f"合成失败：\n{proc.stderr[-3000:]}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="manim 场景 + TTS 配音 → 讲解视频")
    ap.add_argument("--scene", required=True, type=Path, help="manim 场景脚本（.py）")
    ap.add_argument("--class", dest="scene_class", required=True, help="场景类名")
    ap.add_argument("--narration", required=True, type=Path, help="配音文本文件（纯文本）")
    ap.add_argument("--out", required=True, type=Path, help="输出 MP4 路径")
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="edge-tts 音色")
    ap.add_argument("--quality", default="m", choices=list("l m h k"), help="manim 画质档")
    ap.add_argument("--workdir", type=Path, default=Path("."), help="中间产物目录")
    args = ap.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)
    text = args.narration.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("配音文本为空")

    video = render(args.scene.resolve(), args.scene_class, args.quality, args.workdir)
    print(f"渲染完成：{video}（{duration(video):.2f}s）")

    audio = narrate(text, args.voice, args.workdir / "voice.mp3")
    print(f"配音完成：{audio}（{duration(audio):.2f}s）")

    mux(video, audio, args.out.resolve())
    print(f"输出：{args.out}（{duration(args.out):.2f}s）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
