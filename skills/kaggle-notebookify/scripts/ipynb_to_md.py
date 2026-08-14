"""Convert a Kaggle .ipynb notebook back into a Markdown document.

Round-trip companion for md_to_kaggle_ipynb.py:
  ipynb -> md  (this script)
  md -> ipynb  (md_to_kaggle_ipynb.py)

Usage:
  python ipynb_to_md.py <source.ipynb>
  python ipynb_to_md.py <source.ipynb> -o <output.md>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BASH_MAGIC_RE = re.compile(r"^%%bash\s*\n?")
SHELL_CMD_RE = re.compile(r"^\s*!")


def detect_code_lang(source: str) -> str:
    """Detect the language tag for a fenced code block."""
    stripped = source.strip()
    if not stripped:
        return "python"

    # %%bash magic -> bash
    if stripped.startswith("%%bash"):
        return "bash"
    # %%sh magic -> sh
    if stripped.startswith("%%sh"):
        return "sh"
    # All lines start with ! -> bash (IPython shell commands)
    lines = [l for l in stripped.splitlines() if l.strip()]
    if lines and all(l.lstrip().startswith("!") for l in lines):
        return "bash"

    return "python"


def code_cell_to_fence(cell: dict) -> str:
    """Convert a code cell to a fenced code block string."""
    source = cell.get("source", "")
    if isinstance(source, list):
        source = "".join(source)

    lang = detect_code_lang(source)
    body = source

    # Strip %%bash / %%sh magic prefix
    if body.strip().startswith(("%%bash", "%%sh")):
        body = BASH_MAGIC_RE.sub("", body, count=1)

    # For bash cells with !-prefix, optionally strip the !
    # (only if ALL non-empty lines start with !)
    if lang == "bash":
        lines = body.splitlines()
        non_empty = [l for l in lines if l.strip()]
        if non_empty and all(l.lstrip().startswith("!") for l in non_empty):
            body = "\n".join(
                l.lstrip()[1:] if l.lstrip().startswith("!") else l
                for l in lines
            )

    body = body.rstrip()
    return f"```{lang}\n{body}\n```"


def markdown_cell_to_text(cell: dict) -> str:
    """Convert a markdown cell to plain markdown text."""
    source = cell.get("source", "")
    if isinstance(source, list):
        source = "".join(source)
    return source.strip()


def ipynb_to_markdown(notebook: dict) -> str:
    """Convert notebook dict to a markdown string."""
    cells = notebook.get("cells", [])
    parts: list[str] = []

    for cell in cells:
        cell_type = cell.get("cell_type", "")
        if cell_type == "markdown":
            text = markdown_cell_to_text(cell)
            if text:
                parts.append(text)
        elif cell_type == "code":
            source = cell.get("source", "")
            if isinstance(source, list):
                source = "".join(source)
            if source.strip():
                parts.append(code_cell_to_fence(cell))
        # Skip other cell types (raw, etc.)

    return "\n\n".join(parts) + "\n"


def default_output_path(source: Path) -> Path:
    return source.with_suffix(".md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a Kaggle .ipynb notebook back into a Markdown document."
    )
    parser.add_argument("source", type=Path, help="Path to the source .ipynb file.")
    parser.add_argument("-o", "--output", type=Path, help="Optional output .md path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source notebook not found: {source}")
    if source.suffix.lower() != ".ipynb":
        raise ValueError(f"Expected a .ipynb file, got: {source.name}")

    output = args.output.resolve() if args.output else default_output_path(source)

    notebook = json.loads(source.read_text(encoding="utf-8"))
    md_text = ipynb_to_markdown(notebook)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(md_text, encoding="utf-8")

    cells = notebook.get("cells", [])
    markdown_cells = sum(1 for c in cells if c.get("cell_type") == "markdown")
    code_cells = sum(1 for c in cells if c.get("cell_type") == "code")

    summary = {
        "source": str(source),
        "output": str(output),
        "total_cells": len(cells),
        "markdown_cells": markdown_cells,
        "code_cells": code_cells,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
