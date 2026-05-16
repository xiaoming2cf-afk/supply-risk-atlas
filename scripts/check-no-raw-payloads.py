from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from collections.abc import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIRS = [
    ROOT / "artifacts",
    ROOT / "experiments" / "semirisk_validation" / "outputs",
]
BLOCKED_KEY_RE = re.compile(r'"(?:raw_payload|source_payload|private_diagnostics)"\s*:', re.IGNORECASE)
BLOCKED_VALUE_RE = re.compile(r"(?i)(RAW-[A-Z0-9_-]*PAYLOAD|BEGIN PRIVATE KEY|api[_-]?key\s*[:=]|(?<![A-Za-z0-9])sk-[A-Za-z0-9._-]{8,})")
BLOCKED_TRACKED_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".raw", ".pkl", ".pickle", ".parquet", ".feather"}
BLOCKED_TRACKED_PATH_PARTS = {("data", "runtime"), ("data", "raw")}


def _iter_output_files() -> list[Path]:
    files: list[Path] = []
    for directory in OUTPUT_DIRS:
        if not directory.exists():
            continue
        files.extend(path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt", ".csv"})
    return files


def _tracked_files() -> list[Path]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return []
    return [Path(line) for line in completed.stdout.splitlines() if line.strip()]


def _tracked_raw_artifact_failures(paths: Iterable[Path]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        parts = tuple(path.parts)
        has_blocked_path_part = any(blocked == parts[: len(blocked)] for blocked in BLOCKED_TRACKED_PATH_PARTS)
        has_blocked_suffix = path.suffix.lower() in BLOCKED_TRACKED_SUFFIXES
        if has_blocked_path_part or has_blocked_suffix:
            failures.append(f"{path.as_posix()} is a tracked raw/runtime artifact")
    return failures


def _looks_like_json(path: Path, text: str) -> bool:
    if path.suffix.lower() != ".json":
        return False
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return False
    return True


def main() -> int:
    failures: list[str] = _tracked_raw_artifact_failures(_tracked_files())
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
