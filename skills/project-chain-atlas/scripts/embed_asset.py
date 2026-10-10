#!/usr/bin/env python3
"""把本地第三方库（JS / CSS）内联进单文件 HTML（project-chain-atlas）。

用途：需要成熟库能力（代码高亮、离线检索、图形缩放…）时，把库**内联**进交付物，
从而既不自己造轮子，又保住「单文件、离线可开」。选型见 references/ui-tech-choices.md。

本脚本**不联网、不下载、不安装**：库要你自己先取到本地（npm i 或下载 release），
再把路径交给它——`node_modules` 里的文件可以直接指路径。

用法：
    python embed_asset.py docs/链路手册.html \
        --css node_modules/prismjs/themes/prism.css \
        --js  node_modules/prismjs/components/prism-core.min.js \
        --license MIT

    # 只列已内联资产及其 hash（据此判断是否需要重新内联）
    python embed_asset.py docs/链路手册.html --list

    # 移除某个已内联资产
    python embed_asset.py docs/链路手册.html --remove prism-core.min.js

行为与保证：
    - CSS 插到 </head> 前，JS 插到 </body> 前，各用一对标记包裹：
          <!-- atlas:asset <name> sha256:<hash> --> … <!-- /atlas:asset <name> -->
    - 同名资产重复内联时**替换旧块**，不会越插越多（幂等）。
    - JS / CSS 内容里的 `</script` / `</style` 会被转义（`<\\/`），避免提前结束外层标签——
      这是内联脚本/样式的经典坑。
    - 未提供 --license 时打印告警，但继续（许可信息仍写进注释，值记为 unknown）。
    - 内联 CSS 落在自有样式**之后**，第三方样式优先级更高。若它盖掉了你调好的样式，
      在自有样式里用更具体的选择器覆盖，而不是去改库文件。

退出码：0 成功；2 参数或文件错误；3 HTML 结构不满足要求（缺 </head> / </body>）。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

OPEN_FMT = "<!-- atlas:asset {name} sha256:{digest} -->"
CLOSE_FMT = "<!-- /atlas:asset {name} -->"
ASSET_RE = re.compile(r"<!-- atlas:asset (?P<name>\S+) sha256:(?P<digest>[0-9a-f]+) -->")


def read_asset(path: Path) -> tuple[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"资产文件不存在：{path}")
    text = path.read_text(encoding="utf-8")
    return path.name, text


def escape_for_inline(text: str, tag: str) -> str:
    """转义内联内容里会提前闭合外层标签的序列。"""
    return re.sub(r"</" + tag, r"<\\/" + tag, text, flags=re.I)


def build_block(name: str, body: str, kind: str, license_text: str) -> str:
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    source = f"<!-- source: {name} | license: {license_text} | inlined by project-chain-atlas -->"
    open_mark = OPEN_FMT.format(name=name, digest=digest)
    close_mark = CLOSE_FMT.format(name=name)
    if kind == "js":
        payload = f"<script>\n{escape_for_inline(body, 'script')}\n</script>"
    else:
        payload = f"<style>\n{escape_for_inline(body, 'style')}\n</style>"
    return "\n".join([open_mark, source, payload, close_mark])


def insert_block(html: str, block: str, anchor: str) -> str:
    idx = html.rfind(anchor)
    if idx == -1:
        raise ValueError(f"HTML 里找不到 {anchor}")
    return html[:idx] + block + "\n" + html[idx:]


def upsert(html: str, name: str, block: str, anchor: str) -> tuple[str, bool]:
    """同名资产存在则替换，否则插入。返回 (新 HTML, 是否替换)。"""
    pattern = re.compile(
        r"<!-- atlas:asset " + re.escape(name) + r" sha256:[0-9a-f]+ -->.*?<!-- /atlas:asset "
        + re.escape(name) + r" -->",
        re.S,
    )
    if pattern.search(html):
        return pattern.sub(lambda _m: block, html, count=1), True
    return insert_block(html, block, anchor), False


def do_list(html: str) -> int:
    found = ASSET_RE.findall(html)
    if not found:
        print("未内联任何第三方资产。")
        return 0
    print(f"已内联 {len(found)} 项：")
    for name, digest in found:
        print(f"  {name}  sha256:{digest}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="把本地 JS/CSS 内联进单文件 HTML")
    parser.add_argument("html", help="目标单文件 HTML")
    parser.add_argument("--js", action="append", default=[], help="要内联的 JS 文件（可重复）")
    parser.add_argument("--css", action="append", default=[], help="要内联的 CSS 文件（可重复）")
    parser.add_argument("--license", default="unknown", help="许可标识，写进注释（如 MIT）")
    parser.add_argument("--list", action="store_true", help="只列出已内联资产及其 hash")
    parser.add_argument("--remove", action="append", default=[], help="按名称移除已内联资产")
    args = parser.parse_args()

    html_path = Path(args.html)
    if not html_path.exists():
        print(f"[error] HTML 不存在：{html_path}", file=sys.stderr)
        return 2
    html = html_path.read_text(encoding="utf-8")

    try:
        if args.list:
            return do_list(html)

        if args.remove:
            for name in args.remove:
                pattern = re.compile(
                    r"\n?<!-- atlas:asset " + re.escape(name)
                    + r" sha256:[0-9a-f]+ -->.*?<!-- /atlas:asset " + re.escape(name) + r" -->",
                    re.S,
                )
                if pattern.search(html):
                    html = pattern.sub("", html, count=1)
                    print(f"[ok] 已移除 {name}")
                else:
                    print(f"[warn] 未找到已内联的 {name}", file=sys.stderr)
            html_path.write_text(html, encoding="utf-8")
            return 0

        if not args.js and not args.css:
            print("[error] 没有要内联的资产，请用 --js / --css，或 --list / --remove", file=sys.stderr)
            return 2

        if args.license == "unknown":
            print("[warn] 未提供 --license，注释里的许可记为 unknown；交付前请补上", file=sys.stderr)

        for path_str, kind, anchor in (
            *((p, "css", "</head>") for p in args.css),
            *((p, "js", "</body>") for p in args.js),
        ):
            name, body = read_asset(Path(path_str))
            block = build_block(name, body, kind, args.license)
            html, replaced = upsert(html, name, block, anchor)
            print(f"[{'update' if replaced else 'inline'}] {name} ({kind}, {len(body)} 字节)")
    except FileNotFoundError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 3

    html_path.write_text(html, encoding="utf-8")
    print(f"[done] 已写入 {html_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
