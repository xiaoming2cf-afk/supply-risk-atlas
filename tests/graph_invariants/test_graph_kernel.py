from datetime import datetime, timezone

from graph_kernel.graph_quality import graph_invariant_errors
from graph_kernel.path_index import build_path_index
from graph_kernel.snapshot_builder import build_graph_snapshot
from sra_core.synthetic import generate_synthetic_dataset


def test_graph_snapshot_is_deterministic() -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    window_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    first = generate_synthetic_dataset(seed=42)
    second = generate_synthetic_dataset(seed=42)
    snapshot_a, states_a = build_graph_snapshot(first.entities, first.edge_events, as_of, window_start)
    snapshot_b, states_b = build_graph_snapshot(second.entities, second.edge_events, as_of, window_start)
    assert snapshot_a.checksum == snapshot_b.checksum
    assert snapshot_a.graph_version == snapshot_b.graph_version
    assert [state.edge_id for state in states_a] == [state.edge_id for state in states_b]


def test_graph_invariants_hold_for_synthetic_snapshot() -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    window_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    synthetic = generate_synthetic_dataset(seed=42)
    _, states = build_graph_snapshot(synthetic.entities, synthetic.edge_events, as_of, window_start)
    assert graph_invariant_errors(synthetic.entities, states) == []


def test_path_index_references_existing_edges() -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    window_start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    synthetic = generate_synthetic_dataset(seed=42)
    _, states = build_graph_snapshot(synthetic.entities, synthetic.edge_events, as_of, window_start)
    edge_ids = {state.edge_id for state in states}
    paths = build_path_index(states)
    assert paths
    for path in paths:
        assert set(path.edge_sequence).issubset(edge_ids)
        assert path.path_length == len(path.edge_sequence)
