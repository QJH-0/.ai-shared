#!/usr/bin/env python3
"""Regression tests for merge_modules.py — especially resolve_imports().

Background: resolve_imports() originally stripped only the FIRST line of a
multi-line parenthesized relative import:

    from .quant import (LSQQuantizer, FBIWeightBinarizer,   <- stripped
                        TernaryWeightQuantizer)             <- orphaned!

The orphaned continuation lines kept their original indentation and caused
IndentationError when the merged notebook cell was executed on Kaggle.

Run:
    python test_merge_modules.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from merge_modules import resolve_imports  # noqa: E402

PASS = 0
FAIL = 0


def check(name: str, actual: str, expected: str) -> None:
    global PASS, FAIL
    if actual == expected:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")
        print(f"    expected: {expected!r}")
        print(f"    actual:   {actual!r}")


def check_syntax(name: str, code: str) -> None:
    """Merged output must be valid Python (the original Kaggle failure mode)."""
    global PASS, FAIL
    try:
        ast.parse(code)
        PASS += 1
        print(f"  [PASS] {name}")
    except SyntaxError as e:
        FAIL += 1
        print(f"  [FAIL] {name}: {e}")


def main() -> int:
    print("== resolve_imports: single-line ==")
    check(
        "single-line relative import stripped",
        resolve_imports("from .config import cfg, DEVICE\nprint(cfg)\n"),
        "print(cfg)\n",
    )
    check(
        "from . import xxx stripped",
        resolve_imports("from . import utils\nprint(utils)\n"),
        "print(utils)\n",
    )
    check(
        "absolute import kept",
        resolve_imports("from torch import nn\nprint(nn)\n"),
        "from torch import nn\nprint(nn)\n",
    )

    print("== resolve_imports: multi-line parenthesized (the bug) ==")
    check(
        "multi-line import fully stripped",
        resolve_imports(
            "from .quant import (LSQQuantizer, ScaledBinaryActivation,\n"
            "                    TernaryWeightQuantizer, MultiBasisBinarizer,\n"
            "                    print_quant_ratio)\n"
            "print('ok')\n"
        ),
        "print('ok')\n",
    )
    check(
        "multi-line with closing paren on its own line",
        resolve_imports(
            "from .config import (\n"
            "    cfg,\n"
            "    DEVICE,\n"
            ")\n"
            "x = 1\n"
        ),
        "x = 1\n",
    )
    check(
        "nested parens inside import names",
        resolve_imports(
            "from .model import (A, B\n"
            "                    )\n"
            "y = 2\n"
        ),
        "y = 2\n",
    )
    check(
        "consecutive multi-line imports",
        resolve_imports(
            "from .config import (cfg, DEVICE,\n"
            "                     EXP_DIR)\n"
            "from .quant import (LSQQuantizer,\n"
            "                    update_beta)\n"
            "z = 3\n"
        ),
        "z = 3\n",
    )

    print("== merged code is syntactically valid ==")
    realistic = (
        "import torch\n"
        "from .config import (cfg, DEVICE, STAGE_BIT, STAGE_TAG,\n"
        "                     unwrap_model, SCALE_KEY_SUBSTR)\n"
        "from .quant import (LSQQuantizer, ScaledBinaryActivation, FBIWeightBinarizer,\n"
        "                    TernaryWeightQuantizer, MultiBasisBinarizer,\n"
        "                    update_beta, update_soft_sign, update_bi_real_shortcut,\n"
        "                    print_quant_ratio, print_model_memory)\n"
        "\n"
        "\n"
        "class CheckpointManager:\n"
        "    def save(self, model):\n"
        "        state = {'epoch': 1, 'model_state_dict': {},\n"
        "                 'best_metric': 0.5, 'stage_name': 'stage0'}\n"
        "        return state\n"
    )
    check_syntax("realistic module merge (indentation-safe)", resolve_imports(realistic))

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
