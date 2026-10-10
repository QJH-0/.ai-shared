#!/usr/bin/env python3
"""真实无头浏览器交互回归工具（project-chain-atlas）。

用途：把一段「探针脚本」注入单文件 HTML 的副本，用无头 Chrome 跑一遍，
取回探针写入的 <div id="__result"> 内容，并据 RESULT=PASS / RESULT=FAIL 给出退出码。

为什么不用自建 DOM 桩：桩在 closest()、innerHTML='' 是否清空子节点、事件冒泡
这些行为上与真实浏览器有差异，而这些差异恰好会掩盖最常见的交互缺陷。

用法：
    python browser_regression.py <html-file> <probe.js> [--budget-ms 20000] [--chrome PATH] [--keep]

探针脚本契约（见 references/verification.md）：
    - 自行创建 <div id="__result"> 并写入文本行
    - 注册 window.onerror 把 JS 报错写进去
    - 末行写 RESULT=PASS 或 RESULT=FAIL

退出码：0 = 探针报告 PASS 且无 JSERROR；1 = FAIL 或有 JSERROR；2 = 工具自身出错。

安全边界（请遵守）：
    本工具会以 `--no-sandbox` 启动本机浏览器加载**你指定的 HTML**。--no-sandbox 是容器/CI
    环境的常规做法，但它意味着浏览器进程失去自身的沙箱保护。因此**只对你自己产出或已审阅过的
    本地 HTML 运行本工具**，不要指向来源不可信的页面。工具不联网、不下载、不安装任何依赖；
    唯一的写入是「注入探针后的临时 HTML 副本」与「临时浏览器 profile」，两者都在系统临时目录内，
    且使用后即删除。
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

CHROME_CANDIDATES = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)

RESULT_RE = re.compile(r'<div id="__result">(.*?)</div>', re.S)


def find_chrome(explicit: str | None) -> str:
    if explicit:
        if not Path(explicit).exists():
            raise FileNotFoundError(f"指定的浏览器不存在：{explicit}")
        return explicit
    env = os.environ.get("CHROME_PATH") or os.environ.get("CHROME_BIN")
    if env and Path(env).exists():
        return env
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    found = shutil.which("chrome") or shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return found
    raise FileNotFoundError(
        "未找到 Chrome/Chromium。请用 --chrome 指定，或设置环境变量 CHROME_PATH。"
    )


def inject(html: str, probe: str) -> str:
    """把探针包成 <script> 注入到 </body> 之前（只替换最后一次出现，避免误伤正文）。"""
    tag = f"\n<script>\n{probe}\n</script>\n"
    idx = html.rfind("</body>")
    if idx == -1:
        return html + tag
    return html[:idx] + tag + html[idx:]


def run_chrome(chrome: str, url: str, budget_ms: int) -> str:
    profile = Path(tempfile.gettempdir()) / f"dr_atlas_{uuid.uuid4().hex[:8]}"
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--user-data-dir={profile}",
        f"--virtual-time-budget={budget_ms}",
        "--dump-dom",
        url,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"浏览器超时（>{180}s），可调小 --budget-ms") from exc
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    # 有些版本的 dump-dom 会混入 stderr 噪音，只取 stdout
    return proc.stdout.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="无头浏览器交互回归")
    parser.add_argument("html", help="待测单文件 HTML")
    parser.add_argument("probe", help="探针脚本（.js）")
    parser.add_argument("--budget-ms", type=int, default=20000,
                        help="虚拟时间预算，默认 20000；动画/定时器多就调大")
    parser.add_argument("--chrome", default=None, help="浏览器可执行文件路径")
    parser.add_argument("--keep", action="store_true", help="保留注入后的临时 HTML 以便排查")
    args = parser.parse_args()

    html_path = Path(args.html)
    probe_path = Path(args.probe)
    if not html_path.exists():
        print(f"[error] HTML 不存在：{html_path}", file=sys.stderr)
        return 2
    if not probe_path.exists():
        print(f"[error] 探针不存在：{probe_path}", file=sys.stderr)
        return 2

    try:
        chrome = find_chrome(args.chrome)
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2

    merged = inject(html_path.read_text(encoding="utf-8"), probe_path.read_text(encoding="utf-8"))
    tmp_html = Path(tempfile.gettempdir()) / f"atlas_probe_{uuid.uuid4().hex[:8]}.html"
    tmp_html.write_text(merged, encoding="utf-8")
    if args.keep:
        print(f"[info] 注入后的 HTML：{tmp_html}")

    try:
        dom = run_chrome(chrome, tmp_html.resolve().as_uri(), args.budget_ms)
    except RuntimeError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2
    finally:
        if not args.keep:
            tmp_html.unlink(missing_ok=True)

    match = RESULT_RE.search(dom)
    if not match:
        print("[error] 未找到 #__result —— 探针可能没执行（检查脚本是否抛错、或预算太小）",
              file=sys.stderr)
        return 2

    report = match.group(1)
    report = (report.replace("&lt;", "<").replace("&gt;", ">")
                    .replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&"))
    print(report.strip())

    if "JSERROR=" in report:
        print("\n[FAIL] 页面存在 JS 报错", file=sys.stderr)
        return 1
    if "RESULT=PASS" not in report:
        print("\n[FAIL] 探针未报告 PASS", file=sys.stderr)
        return 1
    print("\n[OK] 交互回归通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
