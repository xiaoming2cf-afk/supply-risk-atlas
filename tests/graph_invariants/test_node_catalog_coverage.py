from __future__ import annotations

from graph_kernel.promoted_pipeline import build_promoted_artifacts


def test_promoted_graph_reports_node_catalog_coverage() -> None:
    artifacts = build_promoted_artifacts()
    coverage = artifacts["node_catalog_coverage"]

    assert coverage["catalog_node_count"] >= 150
    assert coverage["graph_node_count"] > 0
    assert coverage["covered_catalog_node_count"] > 0
    assert 0 < coverage["coverage_ratio"] <= 1
    assert "critical_mineral" in coverage["catalog_node_count_by_type"]
    assert "country" in coverage["graph_node_count_by_type"]
    assert coverage["warnings"] == ["node_catalog_is_broader_than_fixture_promoted_graph"]
