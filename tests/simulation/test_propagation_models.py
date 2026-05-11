from __future__ import annotations

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.simulation.propagation import propagate_loss
from ml.simulation.propagation_models import aggregate_loss


def test_noisy_or_and_additive_cap_accumulate_multiple_sources() -> None:
    one = aggregate_loss(0.0, [0.3], mode="noisy_or")
    two = aggregate_loss(0.0, [0.3, 0.3], mode="noisy_or")
    additive = aggregate_loss(0.0, [0.3, 0.3], mode="additive_cap")

    assert two > one
    assert additive == 0.6


def test_leontief_mode_is_bottleneck_sensitive_and_max_is_legacy() -> None:
    assert aggregate_loss(0.0, [0.2, 0.8], mode="leontief_bottleneck") == 0.8
    assert aggregate_loss(0.1, [0.2, 0.8], mode="max") == 0.8


def test_multihop_auto_semiconductor_changes_downstream_nodes() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    losses, traces = propagate_loss(
        snapshot,
        initial_losses={"equipment:euv_scanner": 0.6},
        duration_days=28,
        propagation_mode="auto_semiconductor",
    )

    assert any(node_id != "equipment:euv_scanner" and value > 0 for node_id, value in losses.items())
    assert traces
    assert all("propagation_mode" in trace for trace in traces)
    assert all("formula_refs" in trace for trace in traces)


def test_substitutability_reduces_but_does_not_eliminate_loss() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    losses, _ = propagate_loss(
        snapshot,
        initial_losses={"chemical:photoresist": 0.7},
        duration_days=14,
        propagation_mode="auto_semiconductor",
    )

    downstream = [value for node_id, value in losses.items() if node_id != "chemical:photoresist"]
    assert downstream
    assert max(downstream) > 0
    assert max(downstream) < 0.7
