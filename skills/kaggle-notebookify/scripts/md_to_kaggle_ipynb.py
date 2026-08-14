from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


EXECUTABLE_LANGS = {"python", "py", "bash", "sh", "shell", "zsh"}
SHELL_LANGS = {"bash", "sh", "shell", "zsh"}

# Headings whose entire section should be dropped from the notebook.
# These are document-framing / citation-inventory sections that add
# noise to a Kaggle notebook.  Keywords are matched case-insensitively
# against the heading text, in both Chinese and English.
DROP_HEADING_KEYWORDS = (
    # Chinese
    "文档说明",
    "文档目的",
    "已联网核对",
    "核对的依据",
    "参考来源",
    "参考文献",
    "配套文档",
    "引用",
    # English
    "references",
    "bibliography",
    "citation",
    "acknowledgments",
    "appendix",
    "changelog",
    "license",
)

# Keywords that indicate a heading is relevant to notebook content
# even before any "cell" heading is seen.  This is now only used as
# a *secondary* signal — the default changed to keep-all so that
# English documents are not silently stripped.
PRE_CELL_KEEP_KEYWORDS = (
    # Chinese
    "前提",
    "准备",
    "依赖",
    "环境",
    "数据集",
    "路径",
    "输入",
    "输出",
    "使用",
    # English
    "setup",
    "install",
    "import",
    "data",
    "load",
    "train",
    "model",
    "config",
    "preprocess",
    "result",
    "evaluation",
    "notes",
    "usage",
    "environment",
    "dependency",
    "dataset",
    "path",
    "input",
    "output",
)
LOCAL_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((?:<)?(?:[A-Za-z]:[\\/]|/|file://)[^)<>]+(?:>)?\)"
)
ATX_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
FENCE_START_RE = re.compile(r"^(```+|~~~+)\s*([A-Za-z0-9_+\-]*)\s*$")


@dataclass
class CodeBlock:
    lang: str
    text: str


@dataclass
class MarkdownChunk:
    kind: str
    text: str
    level: int | None = None


def strip_local_links(text: str) -> str:
    return LOCAL_LINK_RE.sub(lambda m: m.group(1), text)


def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = strip_local_links(text)
    return text


def is_cell_heading(text: str) -> bool:
    return "cell" in text.lower()


def should_drop_heading(text: str) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in DROP_HEADING_KEYWORDS)


def should_keep_pre_cell_heading(text: str, level: int) -> bool:
    lowered = text.lower()
    if level == 1:
        return True
    return any(keyword.lower() in lowered for keyword in PRE_CELL_KEEP_KEYWORDS)


def looks_like_executable(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    patterns = (
        r"^\s*import\s+\w+",
        r"^\s*from\s+\w+\s+import\s+",
        r"^\s*def\s+\w+\(",
        r"^\s*class\s+\w+",
        r"^\s*@\w+",
        r"^\s*!",
        r"^\s*%",
        r"^\s*pip\s+install\b",
        r"^\s*python\b",
    )
    return any(re.search(pattern, stripped, re.M) for pattern in patterns)


def split_markdown_chunks(text: str) -> list[MarkdownChunk]:
    lines = text.splitlines()
    chunks: list[MarkdownChunk] = []
    buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        joined = "\n".join(buffer).strip()
        if joined:
            chunks.append(MarkdownChunk(kind="text", text=joined))
        buffer = []

    for line in lines:
        heading_match = ATX_HEADING_RE.match(line)
        if heading_match:
            flush_buffer()
            level = len(heading_match.group(1))
            chunks.append(
                MarkdownChunk(kind="heading", text=heading_match.group(2).strip(), level=level)
            )
            continue

        if line.strip() == "":
            flush_buffer()
            continue

        buffer.append(line.rstrip())

    flush_buffer()
    return chunks


def parse_markdown_blocks(text: str) -> list[CodeBlock | str]:
    lines = text.splitlines()
    blocks: list[CodeBlock | str] = []
    markdown_buffer: list[str] = []
    code_buffer: list[str] = []
    in_code = False
    fence = ""
    lang = ""

    def flush_markdown() -> None:
        nonlocal markdown_buffer
        joined = "\n".join(markdown_buffer).strip()
        if joined:
            blocks.append(joined)
        markdown_buffer = []

    for line in lines:
        if not in_code:
            match = FENCE_START_RE.match(line)
            if match:
                flush_markdown()
                in_code = True
                fence = match.group(1)
                lang = match.group(2).lower()
                code_buffer = []
                continue
            markdown_buffer.append(line)
            continue

        if line.strip() == fence:
            blocks.append(CodeBlock(lang=lang, text="\n".join(code_buffer).rstrip()))
            in_code = False
            fence = ""
            lang = ""
            code_buffer = []
            continue

        code_buffer.append(line.rstrip("\n"))

    if in_code:
        blocks.append(CodeBlock(lang=lang, text="\n".join(code_buffer).rstrip()))
    else:
        flush_markdown()

    return blocks


def markdown_fence(lang: str, text: str) -> str:
    lang_suffix = lang if lang else ""
    body = text.rstrip()
    return f"```{lang_suffix}\n{body}\n```"


def shell_cell_source(text: str) -> str:
    stripped_lines = [line for line in text.splitlines() if line.strip()]
    if stripped_lines and all(line.lstrip().startswith(("!", "%", "#")) for line in stripped_lines):
        return text.rstrip() + "\n"
    return "%%bash\n" + text.rstrip() + "\n"


def make_markdown_cell(source: str, cell_index: int) -> dict:
    return {
        "cell_type": "markdown",
        "id": f"cell-{cell_index:04d}",
        "metadata": {},
        "source": source.rstrip() + "\n",
    }


def make_code_cell(source: str, cell_index: int) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": f"cell-{cell_index:04d}",
        "metadata": {},
        "outputs": [],
        "source": source.rstrip() + "\n",
    }


def convert_blocks_to_cells(blocks: list[CodeBlock | str], keep_all_markdown: bool) -> tuple[list[dict], list[str]]:
    cells: list[dict] = []
    dropped_sections: list[str] = []
    markdown_buffer: list[str] = []
    seen_cell_heading = False
    current_keep = False
    current_heading = ""
    cell_index = 0

    def flush_markdown_buffer() -> None:
        nonlocal markdown_buffer, cell_index
        text = "\n\n".join(part.strip() for part in markdown_buffer if part.strip()).strip()
        if text:
            cells.append(make_markdown_cell(text, cell_index))
            cell_index += 1
        markdown_buffer = []

    for block in blocks:
        if isinstance(block, CodeBlock):
            flush_markdown_buffer()
            lang = block.lang.lower()
            text = block.text.rstrip()

            if lang in {"python", "py"} or (lang == "" and looks_like_executable(text)):
                cells.append(make_code_cell(text, cell_index))
                cell_index += 1
                continue

            if lang in SHELL_LANGS:
                cells.append(make_code_cell(shell_cell_source(text), cell_index))
                cell_index += 1
                continue

            markdown_buffer.append(markdown_fence(lang, text))
            continue

        markdown_text = normalize_markdown(block)
        chunks = split_markdown_chunks(markdown_text)
        for chunk in chunks:
            if chunk.kind == "heading":
                flush_markdown_buffer()
                heading_text = chunk.text.strip()
                current_heading = heading_text
                if is_cell_heading(heading_text):
                    seen_cell_heading = True

                if keep_all_markdown:
                    current_keep = True
                elif should_drop_heading(heading_text):
                    current_keep = False
                    dropped_sections.append(heading_text)
                else:
                    # Default: keep the section.  Previously this only kept
                    # sections matching PRE_CELL_KEEP_KEYWORDS, which silently
                    # dropped most English-language markdown content.
                    current_keep = True

                if current_keep:
                    markdown_buffer.append(f"{'#' * (chunk.level or 2)} {heading_text}")
                continue

            text = chunk.text.strip()
            if not text:
                continue

            if keep_all_markdown:
                markdown_buffer.append(text)
                continue

            if current_keep:
                markdown_buffer.append(text)
                continue

            if not seen_cell_heading and not current_heading:
                markdown_buffer.append(text)

    flush_markdown_buffer()
    return cells, dropped_sections


def build_notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": sys.version.split()[0],
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def default_output_path(source: Path) -> Path:
    return source.with_suffix(".ipynb")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert one Markdown document into a Kaggle-uploadable Jupyter notebook."
    )
    parser.add_argument("source", type=Path, help="Path to the source Markdown file.")
    parser.add_argument("-o", "--output", type=Path, help="Optional output .ipynb path.")
    parser.add_argument(
        "--keep-all-markdown",
        action="store_true",
        help="Keep all markdown sections instead of dropping notebook-noise sections.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source markdown file not found: {source}")
    if source.suffix.lower() != ".md":
        raise ValueError(f"Expected a .md file, got: {source.name}")

    output = args.output.resolve() if args.output else default_output_path(source)
    text = source.read_text(encoding="utf-8")
    blocks = parse_markdown_blocks(text)
    cells, dropped_sections = convert_blocks_to_cells(blocks, args.keep_all_markdown)
    notebook = build_notebook(cells)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")

    markdown_cells = sum(1 for cell in cells if cell["cell_type"] == "markdown")
    code_cells = sum(1 for cell in cells if cell["cell_type"] == "code")

    summary = {
        "source": str(source),
        "output": str(output),
        "total_cells": len(cells),
        "markdown_cells": markdown_cells,
        "code_cells": code_cells,
        "dropped_sections": dropped_sections,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
