from __future__ import annotations

import json

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.simulation.propagation import propagate_loss, resolve_targets, summarize_affected_nodes


def test_resolve_targets_supports_fixture_aliases() -> None:
    snapshot = build_semiconductor_fixture_snapshot()

    assert resolve_targets(snapshot, ["company:tsmc"]) == ["company:tsmc"]
    assert resolve_targets(snapshot, ["country:taiwan"]) == ["country:tw"]
    assert "company:asml" in resolve_targets(snapshot, ["node_type:company"])


def test_propagation_preserves_evidence_without_raw_payload() -> None:
    snapshot = build_semiconductor_fixture_snapshot()
    losses, traces = propagate_loss(
        snapshot,
        initial_losses={"company:tsmc": 0.72},
        duration_days=28,
    )
    affected = summarize_affected_nodes(snapshot, [losses])

    assert losses["company:tsmc"] > 0
    assert traces
    assert affected
    assert all(row["evidence_refs"] for row in affected)
    text = json.dumps({"losses": losses, "traces": traces, "affected": affected}, sort_keys=True)
    assert "raw_payload" not in text
    assert "private_diagnostics" not in text

