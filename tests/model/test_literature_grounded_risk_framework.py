from __future__ import annotations

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.risk_scoring.risk_framework import (
    FEATURE_VERSION,
    FORMULA_VERSION,
    SCORING_METHOD,
    score_likelihood_impact_vulnerability,
)


def test_default_risk_framework_uses_likelihood_impact_vulnerability() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    node = next(item for item in snapshot.nodes if item.node_id == "company:tsmc")
    context_edges = [
        edge
        for edge in snapshot.edges
        if edge.source_node_id == node.node_id or edge.target_node_id == node.node_id
    ]
    result = score_likelihood_impact_vulnerability(snapshot, node, context_edges=context_edges)

    assert result["feature_version"] == FEATURE_VERSION
    assert result["scoring_method"] == SCORING_METHOD
    assert result["formula_version"] == FORMULA_VERSION
    assert result["score"] == round(100 * result["likelihood"] * result["impact"] * result["vulnerability_modifier"], 2)
    assert result["calibration_status"] == "fixture_proxy_not_calibrated"
    assert "nist_sp_800_30_r1_likelihood_impact" in result["formula_refs"]
    assert "fixture_proxy_not_calibrated" in result["warnings"]
