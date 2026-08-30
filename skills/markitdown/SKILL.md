---
name: markitdown
description: Use when converting PDFs, Office documents, images, audio, HTML, CSV, JSON, XML, EPUB, ZIP files, or URLs into Markdown for LLM ingestion, summarization, indexing, or text analysis.
---

# MarkItDown

Use this skill when a file or URL needs to be converted into Markdown for downstream LLM work.

## Local Source

The local MarkItDown source repo is at:

`C:\Users\20448\.ai-shared\skills\markitdown`

The Python package lives at:

`C:\Users\20448\.ai-shared\skills\markitdown\packages\markitdown`

## Quick Use

Install from local source:

```powershell
pip install -e "C:\Users\20448\.ai-shared\skills\markitdown\packages\markitdown[all]"
```

Convert a file:

```powershell
markitdown "D:\path\to\file.pdf" -o "D:\path\to\file.md"
```

Or pipe output:

```powershell
markitdown "D:\path\to\file.pdf" > "D:\path\to\file.md"
```

## Supported Inputs

- PDF
- PowerPoint
- Word
- Excel
- Images
- Audio
- HTML
- CSV, JSON, XML
- EPUB
- ZIP
- YouTube URLs

## Notes

- Requires Python 3.10 or higher.
- Optional dependencies control format support. `[all]` installs the broadest support set.
- CLI entrypoint is `markitdown`.
- Python API entrypoint is `from markitdown import MarkItDown`.
