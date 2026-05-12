from __future__ import annotations

import ast
from pathlib import Path
from typing import NamedTuple


SOURCE_ROOTS = [
    Path("services/api"),
    Path("graph_kernel"),
    Path("ml"),
    Path("packages/sra_core/sra_core"),
    Path("scripts"),
]

MINIFIED_EQUIVALENT_LINE_THRESHOLD = 120
MINIFIED_PHYSICAL_LINE_THRESHOLD = 20
SERVICE_API_MIN_PHYSICAL_LINES = 10
SERVICE_API_FUNCTION_CLASS_THRESHOLD = 2


class SourceStats(NamedTuple):
    path: Path
    physical_lines: int
    estimated_line_equivalent: int
    function_or_class_count: int


def _iter_python_sources() -> list[Path]:
    paths: list[Path] = []
    for root in SOURCE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            paths.append(path)
    return sorted(set(paths))


def _stats(path: Path) -> SourceStats:
    text = path.read_text(encoding="utf-8")
    physical_lines = len(text.splitlines()) if text else 0
    estimated_line_equivalent = max(
        1,
        len(text) // 80,
        text.count(";"),
        text.count(" def "),
        text.count(" class "),
    )
    try:
        tree = ast.parse(text)
    except SyntaxError:
        function_or_class_count = text.count("def ") + text.count("class ")
    else:
        function_or_class_count = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            for node in ast.walk(tree)
        )
    return SourceStats(
        path=path,
        physical_lines=physical_lines,
        estimated_line_equivalent=estimated_line_equivalent,
        function_or_class_count=function_or_class_count,
    )


def test_large_python_modules_are_not_minified_one_line() -> None:
    """Guard against unreadable generated one-line Python modules."""

    offenders: list[str] = []
    for path in _iter_python_sources():
        stats = _stats(path)
        if (
            stats.estimated_line_equivalent > MINIFIED_EQUIVALENT_LINE_THRESHOLD
            and stats.physical_lines < MINIFIED_PHYSICAL_LINE_THRESHOLD
        ):
            offenders.append(
                f"{stats.path} physical_lines={stats.physical_lines} "
                f"estimated_line_equivalent={stats.estimated_line_equivalent}"
            )

    assert offenders == []


def test_service_api_modules_with_multiple_symbols_are_readable() -> None:
    offenders: list[str] = []
    for path in _iter_python_sources():
        if not path.as_posix().startswith("services/api/"):
            continue
        stats = _stats(path)
        if (
            stats.function_or_class_count > SERVICE_API_FUNCTION_CLASS_THRESHOLD
            and stats.physical_lines < SERVICE_API_MIN_PHYSICAL_LINES
        ):
            offenders.append(
                f"{stats.path} physical_lines={stats.physical_lines} "
                f"functions_or_classes={stats.function_or_class_count}"
            )

    assert offenders == []
