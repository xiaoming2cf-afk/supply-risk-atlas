from __future__ import annotations

from pathlib import Path


SOURCE_ROOTS = [
    Path("ml/risk_scoring"),
    Path("ml/simulation"),
    Path("ml/optimization"),
    Path("packages/sra_core/sra_core/reports"),
]


def test_large_python_modules_are_not_minified_one_line() -> None:
    """Guard against unreadable generated one-line Python modules."""

    offenders: list[str] = []
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            physical_lines = text.count("\n") + (1 if text else 0)
            estimated_line_equivalent = max(1, len(text) // 80)
            if estimated_line_equivalent > 300 and physical_lines < 20:
                offenders.append(str(path))

    assert offenders == []
