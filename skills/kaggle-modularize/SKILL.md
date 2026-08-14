---
name: kaggle-modularize
description: >
  Split a monolithic Jupyter notebook (.ipynb) into maintainable Python modules,
  then merge them back into a single Kaggle-uploadable notebook.
  Use when the user has a large/long .ipynb (typically 500+ lines) and wants to
  modularize it for development, or when they want to merge Python modules back
  into one .ipynb for Kaggle. Triggers: "notebook too long", "split notebook into
  modules", "modularize notebook", "merge modules into notebook", "拆分 notebook",
  "notebook 太长", "合并模块为 notebook", "kaggle notebook 拆分".
---

# Kaggle Modularize

Split monolithic notebooks into Python modules for development; merge back into a single `.ipynb` for Kaggle upload.

## When to Use

- A Kaggle notebook exceeds 500+ lines and becomes hard to maintain
- User wants IDE auto-completion, Git diff clarity, and module-level testing
- Final deliverable must be a single `.ipynb` uploaded to Kaggle

## Relationship to `kaggle-notebookify`

| Skill | Direction | Input | Output |
|-------|-----------|-------|--------|
| `kaggle-notebookify` | Markdown → Notebook | `.md` file | `.ipynb` |
| `kaggle-modularize` | Notebook ↔ Modules | large `.ipynb` or `.py` modules | `.py` package + merged `.ipynb` |

They are complementary: `notebookify` creates notebooks from Markdown drafts; `modularize` manages the engineering lifecycle of existing large notebooks.

## Workflow

### Phase 1: Split (notebook → modules)

1. **Read the source notebook** and identify logical boundaries:
   - Markdown description cells → preserve as notebook intro
   - `%%bash` / `pip install` cells → separate as "install" cell
   - Configuration / dataclasses → `config.py`
   - Dataset / DataLoader classes → `data.py`
   - Model definitions → `model.py`
   - Loss functions / metrics → `losses.py`
   - Training loop / `main()` → `train.py`
   - Any other utility code → appropriate module by concern

2. **Create a Python package directory** (e.g., `tse_train/`):
   ```
   project_dir/
   ├── my_package/
   │   ├── __init__.py
   │   ├── config.py
   │   ├── data.py
   │   ├── model.py
   │   └── train.py
   ├── entry_notebook.ipynb   # thin entry: import + call main()
   └── build_nb.py            # merge script
   ```

3. **Convert each cell's code** into the appropriate module:
   - Add proper `from __future__ import annotations` at top
   - Convert relative imports: `from .config import cfg`
   - Keep docstrings and type hints
   - Preserve execution order semantics (global state goes in `config.py`)

4. **Create a thin entry notebook** that only:
   - Installs dependencies (`%%bash` + `pip install`)
   - Imports from the package
   - Calls `main()` or equivalent

### Phase 2: Merge (modules → single notebook)

Use the bundled `scripts/merge_modules.py`:

```bash
python skills/kaggle-modularize/scripts/merge_modules.py \
    --pkg-dir my_package/ \
    --order config.py,data.py,model.py,losses.py,train.py \
    -o merged_notebook.ipynb \
    [--pip-packages "torch numpy ..."] \
    [--no-install-cell] \
    [--entry-call "main(train_loader, val_loader)"] \
    [--entry-prep "train_loader, val_loader = build_dataloaders()"]
```

What the merge script does:
1. Reads each `.py` module in the specified order
2. Strips `from __future__` imports (redundant in notebook context)
3. Strips relative imports (`from .xxx import ...`) — all names are in the same namespace
4. Inserts module separator comments
5. Wraps everything into a single code cell
6. Adds optional `%%bash` install cell and entry-point cells

### Phase 3: Verify

After merge, verify:
- All key class/function definitions present (grep check)
- No residual `from .` relative imports
- Notebook JSON is valid (`nbformat == 4`)
- Cell count is reasonable (3-6 cells typically)

## Module Splitting Guidelines

### How to identify module boundaries

| Signal in notebook cell | Target module |
|------------------------|---------------|
| `@dataclass`, config constants, hyperparameters | `config.py` |
| `class xxxDataset(Dataset)`, `DataLoader(...)` | `data.py` |
| `class xxxNet(nn.Module)`, `def create_model(...)` | `model.py` |
| `def xxx_loss(...)`, metric calculations | `losses.py` |
| `def train_one_epoch(...)`, `def validate(...)`, `def main(...)` | `train.py` |
| Quantization utilities, custom autograd functions | `quant.py` |
| Teacher model wrappers | `teacher.py` |

### What stays in the notebook (not extracted)

- `%%bash` pip install cells
- Markdown documentation cells
- Final entry-point calls (e.g., `main(train_loader, val_loader)`)

### Import resolution rules

When splitting:
- Module-level globals (e.g., `DEVICE`, `cfg`, `EXP_DIR`) → define in `config.py`, import elsewhere
- Cross-module references use relative imports: `from .config import cfg, DEVICE`
- Third-party imports (`torch`, `numpy`) stay in each module as-is

When merging (handled by `merge_modules.py`):
- `from __future__ import annotations` → stripped (redundant)
- `from .xxx import yyy` → stripped (same namespace)
- `import torch` etc. → kept (deduplicated by Python runtime)
- Inline imports inside functions → kept as-is

## Example

Source notebook structure (1200 lines, 12 cells):
```
cell 0:  markdown (intro)
cell 1:  %%bash pip install
cell 2:  imports + CFG dataclass + global setup
cell 3:  stage management functions
cell 4:  data index loading
cell 5:  Dataset class + DataLoader
cell 6:  quantization components
cell 7:  model classes + checkpoint manager
cell 8:  create_model()
cell 9:  loss functions
cell 10: teacher model wrapper
cell 11: training loop + main()
```

After split:
```
my_package/
├── __init__.py
├── config.py     ← cells 2, 3
├── data.py       ← cells 4, 5
├── quant.py      ← cell 6
├── model.py      ← cells 7, 8
├── losses.py     ← cell 9
├── teacher.py    ← cell 10
└── train.py      ← cell 11
```

After merge (`python merge_modules.py ...`):
```
merged_notebook.ipynb (5 cells):
  cell 0: markdown intro
  cell 1: %%bash pip install
  cell 2: all module code (merged, ~1000 lines)
  cell 3: data loader call
  cell 4: main() call
```
