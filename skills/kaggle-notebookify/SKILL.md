---
name: kaggle-notebookify
description: Convert a single Markdown document into a Kaggle-uploadable Jupyter notebook. Use this whenever the user asks to turn one `.md` file into a `.ipynb`, a Kaggle notebook, or a notebook upload artifact, especially when fenced code blocks should become code cells and technical explanation should remain as markdown cells.
---

# Kaggle Notebookify

Use this skill when the input is one Markdown document and the desired output is one Kaggle-ready notebook.

## What this skill does

- Converts executable fenced code blocks into notebook code cells.
- Converts technical explanation into markdown cells.
- Drops notebook-hostile clutter such as reference inventories, cross-document navigation, and local absolute-path links.
- Produces a `.ipynb` file that can be uploaded to Kaggle directly.

## Input assumptions

- The source is a single `.md` file.
- The document uses fenced code blocks such as `python`, `bash`, `sh`, or `text`.
- The user wants code as code cells and explanation as markdown cells.

## Workflow

1. Confirm the source Markdown path.
2. Use the bundled script instead of hand-building notebook JSON.
3. By default, write the output notebook next to the source Markdown file with the same basename.
4. Validate the generated notebook by loading the JSON and checking the cell counts.
5. Report the output path and a short summary of generated markdown/code cells.

## Default conversion rules

- `python`, `py` -> code cell
- `bash`, `sh`, `shell`, `zsh` -> code cell
- `text` and non-executable fences -> markdown cell
- Unlabeled fenced blocks that clearly look executable -> code cell

For shell fences:

- If the content already uses IPython shell syntax like `!pip install`, keep it as-is.
- Otherwise prefix the cell with `%%bash` so it runs cleanly in Kaggle.

For markdown:

- Keep technical explanation, headings, and code-adjacent notes by default.
- Drop sections whose headings match citation/framing keywords (references, bibliography, changelog, license, etc.).
- Strip local absolute-path links down to plain labels.
- Use `--keep-all-markdown` to disable dropping entirely (e.g. for documents with no citation sections).

## Command

Run:

```bash
python skills/kaggle-notebookify/scripts/md_to_kaggle_ipynb.py <source.md>
```

Optional explicit output path:

```bash
python skills/kaggle-notebookify/scripts/md_to_kaggle_ipynb.py <source.md> -o <output.ipynb>
```

If the user wants to preserve *all* markdown sections (including references
and citation inventory), use `--keep-all-markdown`:

```bash
python skills/kaggle-notebookify/scripts/md_to_kaggle_ipynb.py <source.md> --keep-all-markdown
```

## Validation

After conversion, verify:

- the notebook file exists
- JSON loads successfully
- `nbformat` is `4`
- `cells` is non-empty
- code cell count matches the executable fenced blocks you intended to preserve

## Output expectations

Tell the user:

- source path
- output notebook path
- markdown cell count
- code cell count
- whether any sections were dropped by the cleaner

## Example prompts this skill should handle

- "Convert this Markdown notebook draft into a Kaggle `.ipynb`."
- "Turn `docs/foo.md` into a notebook I can upload to Kaggle."
- "Make a real notebook from this single markdown doc. Keep explanations as markdown cells."
