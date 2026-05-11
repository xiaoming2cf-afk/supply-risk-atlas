from __future__ import annotations

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.risk_scoring.concentration import (
    concentration_level,
    country_concentration_by_input,
    hhi,
    significant_dependency,
    source_concentration_by_node,
)
from ml.risk_scoring.risk_framework import score_likelihood_impact_vulnerability


def test_hhi_equal_suppliers_and_monopoly() -> None:
    assert hhi([0.25, 0.25, 0.25, 0.25]) == 0.25
    assert hhi([1.0]) == 1.0
    assert concentration_level(0.19) == "low"
    assert concentration_level(0.20) == "moderate"
    assert concentration_level(0.40) == "high"


def test_concentration_outputs_fixture_warnings_and_oecd_thresholds() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    source = source_concentration_by_node(snapshot, "company:tsmc")
    country = country_concentration_by_input(snapshot, "company:tsmc")

    assert source["hhi_scale"] == "0_to_1"
    assert source["threshold_policy"] == "oecd_derived_supply_chain"
    assert source["threshold_basis"]["high"] == ">=0.40"
    assert "fixture_proxy_supplier_shares" in source["warnings"]
    assert country["global_reference_hhi"] == 0.20
    assert "fixture_global_reference_hhi_proxy" in country["warnings"]


def test_significant_dependency_uses_oecd_derived_operational_rule() -> None:
    assert significant_dependency(0.50, 0.20) is True
    assert significant_dependency(0.40, 0.20) is False
    assert significant_dependency(0.50, 0.19) is False


def test_high_concentration_increases_vulnerability_proxy() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    node = next(item for item in snapshot.nodes if item.node_id == "company:tsmc")
    context_edges = [
        edge
        for edge in snapshot.edges
        if edge.source_node_id == "company:tsmc" or edge.target_node_id == "company:tsmc"
    ]
    payload = score_likelihood_impact_vulnerability(snapshot, node, context_edges=context_edges)

    assert payload["concentration"]["source_concentration"]["hhi"] >= 0.20
    assert payload["vulnerability_modifier"] >= 0.75
