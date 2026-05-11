from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECRET_RE = re.compile(
    r"(?i)(BEGIN PRIVATE KEY|AWS_SECRET_ACCESS_KEY\s*=|api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9._-]{16,}|(?<![A-Za-z0-9])sk-[A-Za-z0-9._-]{20,})"
)
SOURCE_DIRS = [
    ROOT / "services",
    ROOT / "packages",
    ROOT / "ml",
    ROOT / "graph_kernel",
    ROOT / "apps" / "web" / "src",
    ROOT / ".github" / "workflows",
]
REQUIRED_SECURITY_MARKERS = {
    ROOT / "services" / "api" / "security" / "validation.py": [
        "UNSAFE_PHRASES",
        "SECRET_VALUE_PATTERNS",
        "validate_request_size",
        "validate_report_payload",
    ],
    ROOT / "services" / "api" / "security" / "headers.py": [
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
    ],
    ROOT / "packages" / "sra_core" / "sra_core" / "reports" / "investigation.py": [
        "raw_payload_excluded",
        "private_diagnostics_excluded",
    ],
}


def _iter_source_files() -> list[Path]:
    files: list[Path] = []
    for directory in SOURCE_DIRS:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".mjs", ".yml", ".yaml"}:
                files.append(path)
    return files


def _run_script(name: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    return [result.stdout.strip(), result.stderr.strip()]


def main() -> int:
    failures: list[str] = []
    for path in _iter_source_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        if SECRET_RE.search(text):
            failures.append(f"{path.relative_to(ROOT)} contains a secret-like literal")

    for path, markers in REQUIRED_SECURITY_MARKERS.items():
        if not path.exists():
            failures.append(f"Missing required security boundary file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in markers:
            if marker not in text:
                failures.append(f"{path.relative_to(ROOT)} is missing marker {marker!r}")

    for helper in ("check-no-raw-payloads.py", "check-no-one-line-python.py"):
        helper_failures = [item for item in _run_script(helper) if item]
        failures.extend(helper_failures)

    if failures:
        print("Security scan failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Security scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
