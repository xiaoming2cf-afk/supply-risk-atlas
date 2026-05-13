from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE_VIEW_ROOT = ROOT / "apps" / "web" / "src" / "features" / "graph-explorer" / "stage-views"

REQUIRED_STAGE_VIEWS = [
    "PolicyMacroGraphView.tsx",
    "MineralDependencyGraphView.tsx",
    "MaterialChemicalDependencyGraphView.tsx",
    "DesignIPDependencyGraphView.tsx",
    "EquipmentProcessDependencyGraphView.tsx",
    "FabProcessGraphView.tsx",
    "ProductDemandGraphView.tsx",
    "PackagingTestingGraphView.tsx",
    "LogisticsRouteGraphView.tsx",
    "DownstreamDemandGraphView.tsx",
    "EventTimelineGraphView.tsx",
    "ComplianceRiskGraphView.tsx",
]


def test_stage_graph_view_components_exist_and_use_generic_stage_contract() -> None:
    for filename in REQUIRED_STAGE_VIEWS:
        path = STAGE_VIEW_ROOT / filename
        assert path.exists(), filename
        text = path.read_text(encoding="utf-8")
        assert "StageGraphView" in text


def test_stage_graph_generic_view_shows_stage_metadata_and_declutter_limits() -> None:
    text = (STAGE_VIEW_ROOT / "StageGraphView.tsx").read_text(encoding="utf-8")

    assert "graph_version" in text
    assert "source_manifest_id" in text
    assert "data_mode" in text
    assert "graph_mode" in text
    assert "18 nodes / 30 edges" in text
    assert "evidence-context links are inspection links" in text
