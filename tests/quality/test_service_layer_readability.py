from __future__ import annotations

import ast
from pathlib import Path


SERVICE_DIR = Path("services/api/services")
ROUTE_DIR = Path("services/api/routes")
REQUIRED_READABLE_MODULES = {
    Path("services/api/services/graph_service.py"): 100,
    Path("services/api/services/risk_service.py"): 20,
    Path("services/api/services/scenario_service.py"): 20,
    Path("services/api/services/system_health_service.py"): 50,
    Path("services/api/routes/graph.py"): 20,
}


def _python_modules(root: Path) -> list[Path]:
    return sorted(path for path in root.glob("*.py") if "__pycache__" not in path.parts)


def _function_or_class_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    return sum(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for node in ast.walk(tree)
    )


def _physical_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def _estimated_line_equivalent(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    return max(1, len(text) // 80, text.count(";"), text.count(" def "), text.count(" class "))


def test_service_modules_are_not_single_line_minified_files() -> None:
    offenders: list[str] = []
    for path in _python_modules(SERVICE_DIR):
        if _function_or_class_count(path) > 2 and _physical_lines(path) < 10:
            offenders.append(
                f"{path} physical_lines={_physical_lines(path)} "
                f"estimated_line_equivalent={_estimated_line_equivalent(path)}"
            )

    assert offenders == []


def test_route_modules_are_not_single_line_minified_files() -> None:
    offenders: list[str] = []
    for path in _python_modules(ROUTE_DIR):
        if _function_or_class_count(path) > 2 and _physical_lines(path) < 10:
            offenders.append(
                f"{path} physical_lines={_physical_lines(path)} "
                f"estimated_line_equivalent={_estimated_line_equivalent(path)}"
            )

    assert offenders == []


def test_service_and_route_modules_have_readable_physical_lines() -> None:
    offenders: list[str] = []
    for path in [*_python_modules(SERVICE_DIR), *_python_modules(ROUTE_DIR)]:
        if _estimated_line_equivalent(path) > 120 and _physical_lines(path) < 20:
            offenders.append(
                f"{path} physical_lines={_physical_lines(path)} "
                f"estimated_line_equivalent={_estimated_line_equivalent(path)}"
            )

    assert offenders == []


def test_review_flagged_service_and_route_modules_have_acceptable_line_counts() -> None:
    offenders: list[str] = []
    for path, minimum_lines in REQUIRED_READABLE_MODULES.items():
        physical_lines = _physical_lines(path)
        if physical_lines < minimum_lines:
            offenders.append(f"{path} physical_lines={physical_lines} minimum={minimum_lines}")

    assert offenders == []
