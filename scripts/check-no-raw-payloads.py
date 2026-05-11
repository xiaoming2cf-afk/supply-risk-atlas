from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRS = [
    ROOT / "artifacts",
    ROOT / "experiments" / "semirisk_validation" / "outputs",
]
BLOCKED_KEY_RE = re.compile(r'"(?:raw_payload|source_payload|private_diagnostics)"\s*:', re.IGNORECASE)
BLOCKED_VALUE_RE = re.compile(r"(?i)(RAW-[A-Z0-9_-]*PAYLOAD|BEGIN PRIVATE KEY|api[_-]?key\s*[:=]|(?<![A-Za-z0-9])sk-[A-Za-z0-9._-]{8,})")


def _iter_output_files() -> list[Path]:
    files: list[Path] = []
    for directory in OUTPUT_DIRS:
        if not directory.exists():
            continue
        files.extend(path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt", ".csv"})
    return files


def _looks_like_json(path: Path, text: str) -> bool:
    if path.suffix.lower() != ".json":
        return False
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return False
    return True


def main() -> int:
    failures: list[str] = []
    for path in _iter_output_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        if BLOCKED_KEY_RE.search(text):
            failures.append(f"{path.relative_to(ROOT)} contains a blocked raw/private payload key")
        if BLOCKED_VALUE_RE.search(text):
            failures.append(f"{path.relative_to(ROOT)} contains a secret-like or raw-payload marker")
        if path.suffix.lower() == ".json" and not _looks_like_json(path, text):
            failures.append(f"{path.relative_to(ROOT)} is not valid JSON")

    if failures:
        print("Raw/private payload scan failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Raw/private payload scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
