from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ["services", "packages", "ml", "graph_kernel", "tests", "scripts"]
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for name in SCAN_DIRS:
        directory = ROOT / name
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            if any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            files.append(path)
    return files


def main() -> int:
    failures: list[str] = []
    for path in _iter_python_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        nonempty_lines = [line for line in text.splitlines() if line.strip()]
        if len(nonempty_lines) <= 2 and len(text) > 500:
            failures.append(f"{path.relative_to(ROOT)} appears to be compressed into one or two lines")

    if failures:
        print("Python readability scan failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Python readability scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
