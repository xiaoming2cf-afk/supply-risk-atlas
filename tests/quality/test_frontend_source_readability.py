from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FEATURE_ROOT = ROOT / "apps" / "web" / "src" / "features"
SMOKE_SCRIPT = ROOT / "scripts" / "browser-smoke.mjs"


CRITICAL_FRONTEND_FILES = [
    FEATURE_ROOT / "graph-explorer" / "SupplyRelationshipView.tsx",
    FEATURE_ROOT / "graph-explorer" / "DemandRelationshipView.tsx",
    FEATURE_ROOT / "graph-explorer" / "ProductionDependencyView.tsx",
    FEATURE_ROOT / "graph-explorer" / "SupplyDemandBalanceView.tsx",
    FEATURE_ROOT / "common" / "pageRelevance.ts",
]


def _physical_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_large_frontend_feature_files_are_not_single_line_minified() -> None:
    offenders: list[str] = []
    for path in FEATURE_ROOT.rglob("*"):
        if path.suffix not in {".ts", ".tsx"}:
            continue
        if path.stat().st_size <= 5_000:
            continue
        physical_lines = len(_physical_lines(path))
        if physical_lines < 20:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_critical_graph_and_page_relevance_files_are_readable() -> None:
    for path in CRITICAL_FRONTEND_FILES:
        assert path.exists(), str(path)
        lines = _physical_lines(path)
        assert len(lines) >= 20, str(path.relative_to(ROOT))
        assert any(line.startswith("export ") for line in lines), str(path.relative_to(ROOT))


def test_browser_smoke_script_is_readable_not_minified() -> None:
    assert SMOKE_SCRIPT.exists()
    assert len(_physical_lines(SMOKE_SCRIPT)) >= 100
