from __future__ import annotations

import json

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.simulation.loss_functions import compute_loss_components


def test_default_loss_components_include_formula_refs_and_not_raw_payload() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    node_losses = {"company:tsmc": 0.6, "equipment:euv_scanner": 0.4}
    result = compute_loss_components(snapshot, node_losses, duration_days=28)

    assert result["loss_mode"] == "resilience_integral_loss"
    assert result["primary_loss"] == result["resilience_integral_loss"]
    assert result["graph_weighted_loss"] > 0
    assert result["demand_fulfillment_loss"] >= 0
    assert result["capacity_functionality_loss"] > 0
    assert result["formula_refs"]
    assert result["calibration_status"] == "fixture_proxy_not_calibrated"
    assert "raw_payload" not in json.dumps(result, sort_keys=True)


def test_critical_node_loss_has_greater_graph_weighted_loss_than_noncritical() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    critical = compute_loss_components(snapshot, {"company:tsmc": 0.6}, duration_days=28)
    noncritical = compute_loss_components(snapshot, {"route:east_asia_air": 0.6}, duration_days=28)

    assert critical["graph_weighted_loss"] >= noncritical["graph_weighted_loss"]


def test_affected_mean_remains_legacy_baseline_not_default() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    result = compute_loss_components(snapshot, {"company:tsmc": 0.6}, duration_days=28, loss_mode="affected_mean")

    assert result["loss_mode"] == "affected_mean"
    assert result["primary_loss"] == result["affected_mean"]
    assert "affected_mean:legacy_baseline" in result["warnings"]
