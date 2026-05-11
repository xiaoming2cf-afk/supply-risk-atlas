from __future__ import annotations

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.risk_scoring.critical_dependency import critical_dependency_importance


def test_critical_dependency_returns_oecd_style_proxy_fields() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    result = critical_dependency_importance(snapshot, "company:tsmc")

    assert 0 <= result["critical_dependency_score"] <= 1
    assert 0 <= result["supply_demand_risk"] <= 1
    assert 0 <= result["strategic_importance"] <= 1
    assert "oecd_supply_chain_resilience_critical_dependency" in result["formula_refs"]
    assert result["source_refs"]
    assert "fixture_proxy_critical_dependency" in result["warnings"]
