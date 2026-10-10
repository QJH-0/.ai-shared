#!/usr/bin/env python3
"""图表渲染与内联工具（project-chain-atlas）。

把用成熟图表 DSL（Mermaid / D2 / Graphviz）编写的图源，在**构建期**渲染成静态 SVG，
再回填进单文件 HTML 的槽位。产出物因此同时满足两点：创作层用行业标准工具（不手算坐标），
交付物仍是「单文件、离线可开、无运行时依赖」。

为什么是这个方案（设计取舍）：
    - 在页面里引 CDN 或内联图表运行时（mermaid.js 等）会破坏「离线单文件」这条非协商约束，
      还会让页面多背数 MB 运行时。
    - 手写内联 SVG 则把坐标、布局、箭头 marker 全压在人工上：改一处要重排全图，
      且同一文档多张图极易发生 id / marker 冲突（表现为箭头消失），旧规范只能靠人工纪律规避。
    - 构建期渲染 + 全量 id 命名空间化，既用上成熟工具，又把「多图冲突」这条从人工纪律
      变成脚本的确定性行为。这正是本工具存在的理由。

用法：
    # 0) 查看本机可用的渲染器（不联网、不安装）
    python scripts/render_diagrams.py --check

    # 1) 渲染图源为独立 SVG
    python scripts/render_diagrams.py diagrams/order-flow.mmd -o build/order-flow.svg

    # 2) 渲染并回填到 HTML 槽位。HTML 中先放好成对标记：
    #      <!-- atlas:diagram order-flow -->
    #      <!-- /atlas:diagram order-flow -->
    python scripts/render_diagrams.py diagrams/order-flow.mmd \
        --into docs/链路手册.html --slot order-flow

    # 3) 批量：把 diagrams/*.{mmd,mermaid,d2,dot,gv} 按文件名词干回填同名槽位
    python scripts/render_diagrams.py --batch diagrams --into docs/链路手册.html

    # 4) 纯离线：只用已经渲染好的 SVG（本机没有任何渲染器时走这条路，功能完整）
    python scripts/render_diagrams.py build/order-flow.svg \
        --into docs/链路手册.html --slot order-flow

    # 5) 允许在有网络时用 npx 拉取 mermaid-cli 兜底（默认关闭，见下）
    python scripts/render_diagrams.py diagrams/order-flow.mmd \
        --into docs/手册.html --slot order-flow --allow-npx

网络与安全边界：
    默认**不联网、不安装**。仅当显式传 --allow-npx 且本机无 mmdc 时，才回退到
    `npx -y @mermaid-js/mermaid-cli`（会下载依赖，且体积较大）。纯 .svg 输入路径
    完全离线，不调用任何外部命令。

退出码：0 成功；2 工具/参数错误（含找不到渲染器、槽位不存在）；3 渲染器调用失败。
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Callable
from pathlib import Path

# ------------------------------ 渲染器登记 ------------------------------
# 每项：(可执行名, 支持的扩展名集合, 构建命令函数(src, out) -> list[str])
TOOLS: tuple[tuple[str, frozenset[str], Callable[[str, str], list[str]]], ...] = (
    ("mmdc", frozenset({"mmd", "mermaid"}),
     lambda src, out: ["mmdc", "-i", src, "-o", out]),
    ("d2", frozenset({"d2"}),
     lambda src, out: ["d2", src, out]),
    ("dot", frozenset({"dot", "gv"}),
     lambda src, out: ["dot", "-Tsvg", src, "-o", out]),
)

NPX_TOOL = ("npx", frozenset({"mmd", "mermaid"}),
            lambda src, out: ["npx", "-y", "@mermaid-js/mermaid-cli", "-i", src, "-o", out])

SUPPORTED_EXT = frozenset().union(*(t[1] for t in TOOLS))

SLOT_OPEN = "<!-- atlas:diagram {name} -->"
SLOT_CLOSE = "<!-- /atlas:diagram {name} -->"


class ToolError(RuntimeError):
    """参数或环境导致的、可直接向用户报错的问题。"""


class RenderFailed(RuntimeError):
    """外部渲染器返回非零退出码。"""


# ------------------------------ 渲染 ------------------------------

def _candidates(ext: str, allow_npx: bool):
    for name, exts, build in TOOLS:
        if ext in exts:
            yield name, build
    if allow_npx and ext in NPX_TOOL[1]:
        yield NPX_TOOL[0], NPX_TOOL[2]


def find_tool(ext: str, allow_npx: bool):
    """返回 (可执行名, 构建函数)；找不到返回 None。只探测，不安装。"""
    for name, build in _candidates(ext, allow_npx):
        if shutil.which(name):
            return name, build
    return None


def render(src: Path, allow_npx: bool) -> str:
    ext = src.suffix.lower().lstrip(".")
    if ext == "svg":
        return src.read_text(encoding="utf-8")

    if ext not in SUPPORTED_EXT:
        raise ToolError(
            f"不支持的图源扩展名 .{ext}（可用：{', '.join(sorted(SUPPORTED_EXT))} 或 .svg）"
        )

    found = find_tool(ext, allow_npx)
    if found is None:
        hint = "" if allow_npx else "；仅 Mermaid 可在有网络时用 --allow-npx 兜底"
        raise ToolError(
            f"未找到可渲染 .{ext} 的工具（尝试过：" +
            "、".join(name for name, _ in _candidates(ext, allow_npx)) +
            "）。请安装后用 --check 确认" + hint + "；或改传已渲染好的 .svg。"
        )

    name, build = found
    out = Path(tempfile.gettempdir()) / f"atlas_render_{uuid.uuid4().hex[:8]}.svg"
    cmd = build(str(src), str(out))
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=300)
    except (subprocess.TimeoutExpired, OSError) as exc:
        out.unlink(missing_ok=True)
        raise RenderFailed(f"{name} 调用失败：{exc}") from exc

    if proc.returncode != 0 or not out.exists():
        out.unlink(missing_ok=True)
        detail = proc.stderr.decode("utf-8", errors="replace").strip()[:800]
        raise RenderFailed(
            f"{name} 渲染失败（退出码 {proc.returncode}）：\n{' '.join(cmd)}\n{detail}"
        )
    try:
        return out.read_text(encoding="utf-8")
    finally:
        out.unlink(missing_ok=True)


# ------------------------------ SVG 净化 ------------------------------

def sanitize_svg(svg: str, prefix: str | None) -> str:
    """把渲染器产出的 SVG 整理成可安全内联进单文件 HTML 的形式。

    做四件事：
      1. 去掉 XML 声明 / DOCTYPE / 注释 —— 内联后不需要，且注释里可能含未转义字符。
      2. 全量 id 命名空间化 —— 同一文档多张图若各自带 `id="my-svg"`、`id="flowchart-pointEnd"`
         等同名 id 与 `url(#...)` 引用，会互相覆盖，表现之一就是「第二张图箭头消失」。
         统一加前缀后，图与图之间不再冲突。
      3. 去掉根元素的 width/height/style —— 让 CSS（`svg.flow{width:100%;height:auto}`）
         统一控制尺寸，图随内容列自适应；渲染器写死的 max-width 会阻挡这一点。
      4. 给根元素加 class="flow" 与 role="img" —— 供 CSS 与可访问性使用。
    """
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg, flags=re.I)
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)

    if prefix:
        ids = set(re.findall(r'\sid="([^"]+)"', svg))
        # 长的先替换，避免 "a" 提前命中并破坏 "a-b"
        for old in sorted(ids, key=len, reverse=True):
            new = prefix + old
            svg = svg.replace(f'id="{old}"', f'id="{new}"')
            svg = svg.replace(f"url(#{old})", f"url(#{new})")
            svg = re.sub(r"#" + re.escape(old) + r"(?![A-Za-z0-9_-])", "#" + new, svg)

    root = re.search(r"<svg\b[^>]*>", svg)
    if not root:
        raise ToolError("渲染结果不是 SVG（未找到根 <svg> 标签）")

    tag = root.group(0)
    tag = re.sub(r'\s(?:width|height)="[^"]*"', "", tag)
    tag = re.sub(r'\sstyle="[^"]*"', "", tag)
    if re.search(r'\sclass="', tag):
        tag = re.sub(r'\sclass="([^"]*)"', lambda m: f' class="{m.group(1).strip()} flow"', tag, count=1)
    else:
        tag = tag[:-1].rstrip() + ' class="flow">'
    if "role=" not in tag:
        tag = tag[:-1].rstrip() + ' role="img">'
    if "viewBox=" not in tag:
        print("[warn] SVG 根元素没有 viewBox，无法自适应缩放；请检查渲染器输出", file=sys.stderr)

    return svg[:root.start()] + tag + svg[root.end():]


# ------------------------------ 回填 HTML ------------------------------

def inline_into(html: str, name: str, svg: str) -> str:
    """把 svg 替换进成对槽位标记之间；槽位不存在则报错（不静默新建）。"""
    pattern = re.compile(
        re.escape(SLOT_OPEN.format(name=name)) + r"(.*?)" + re.escape(SLOT_CLOSE.format(name=name)),
        re.S,
    )
    if not pattern.search(html):
        raise ToolError(
            f"HTML 中找不到槽位 {name}。请先加入成对标记：\n"
            f"  {SLOT_OPEN.format(name=name)}\n  {SLOT_CLOSE.format(name=name)}"
        )
    return pattern.sub(lambda _m: SLOT_OPEN.format(name=name) + "\n" + svg.strip() + "\n" + SLOT_CLOSE.format(name=name), html)


# ------------------------------ CLI ------------------------------

def do_check() -> int:
    print("可用渲染器：")
    for name, exts, _build in TOOLS:
        ext_str = "/".join(sorted(exts))
        path = shutil.which(name)
        print(f"  [{'OK' if path else '--'}] {name:6s} (.<{ext_str}>)  {path or '未安装'}")
    npx = shutil.which("npx")
    print(f"  [{'OK' if npx else '--'}] npx    (mermaid 兜底，需 --allow-npx，会联网)  {npx or '未安装'}")
    print("\n纯 .svg 输入路径不需要任何渲染器（完全离线）。")
    return 0


def build_one(src: Path, slot: str | None, allow_npx: bool) -> str:
    prefix = f"diag-{slot}-" if slot else None
    return sanitize_svg(render(src, allow_npx), prefix)


def main() -> int:
    parser = argparse.ArgumentParser(description="图表渲染与内联（project-chain-atlas）")
    parser.add_argument("source", nargs="?", help="图源文件（.mmd/.mermaid/.d2/.dot/.gv/.svg）")
    parser.add_argument("-o", "--out", help="输出独立 SVG 路径")
    parser.add_argument("--into", help="把渲染结果回填进这个 HTML 文件")
    parser.add_argument("--slot", help="HTML 中的槽位名（配合 --into）")
    parser.add_argument("--batch", help="批量渲染目录下所有受支持的图源，按文件名词干回填同名槽位")
    parser.add_argument("--allow-npx", action="store_true", help="本机无 mmdc 时允许用 npx 拉取 mermaid-cli（联网）")
    parser.add_argument("--namespace", help="渲染为独立 SVG 时使用的 id 前缀（默认不加前缀）")
    parser.add_argument("--check", action="store_true", help="只检查本机可用渲染器")
    args = parser.parse_args()

    if args.check:
        return do_check()

    try:
        if args.batch:
            if not args.into:
                raise ToolError("--batch 必须配合 --into 使用（批量回填到同一份 HTML）")
            files = sorted(
                p for p in Path(args.batch).iterdir()
                if p.is_file() and p.suffix.lower().lstrip(".") in SUPPORTED_EXT
            )
            if not files:
                raise ToolError(f"{args.batch} 下没有受支持的图源（{', '.join(sorted(SUPPORTED_EXT))}）")
            html = Path(args.into).read_text(encoding="utf-8")
            for f in files:
                name = f.stem
                svg = build_one(f, name, args.allow_npx)
                html = inline_into(html, name, svg)
                print(f"[ok] {f.name} -> 槽位 {name}")
            Path(args.into).write_text(html, encoding="utf-8")
            print(f"[done] 已回填 {len(files)} 张图到 {args.into}")
            return 0

        if not args.source:
            raise ToolError("需要提供图源文件，或用 --batch / --check")
        src = Path(args.source)
        if not src.exists():
            raise ToolError(f"图源不存在：{src}")

        if args.into:
            if not args.slot:
                raise ToolError("--into 必须配合 --slot 使用（指定槽位名）")
            html = Path(args.into).read_text(encoding="utf-8")
            html = inline_into(html, args.slot, build_one(src, args.slot, args.allow_npx))
            Path(args.into).write_text(html, encoding="utf-8")
            print(f"[done] {src.name} -> 槽位 {args.slot}（{args.into}）")
            return 0

        if not args.out:
            raise ToolError("请用 -o 指定输出 SVG，或用 --into 回填到 HTML")
        svg = sanitize_svg(render(src, args.allow_npx), args.namespace)
        Path(args.out).write_text(svg, encoding="utf-8")
        print(f"[done] {src.name} -> {args.out}（{len(svg)} 字节）")
        return 0

    except ToolError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2
    except RenderFailed as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
