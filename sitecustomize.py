"""Local development import path helper.

When Python starts from the repository root, this file is imported by the
standard `site` module and makes `packages/sra_core` importable without a global
editable install. CI and production can still use `pip install -e .`.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRA_CORE = ROOT / "packages" / "sra_core"

for path in (SRA_CORE, ROOT):
    value = str(path)
    if value not in sys.path:
        sys.path.insert(0, value)
