from graph_kernel.events import EdgeEvent, EdgeKey, materialize_edge_state
from graph_kernel.snapshots import (
    EdgeRecord,
    GraphSnapshot,
    diff_snapshots,
    snapshot_checksum,
    snapshot_from_edge_states,
)
from graph_kernel.synthetic import SyntheticGraphSpec, generate_synthetic_edge_events


def test_synthetic_events_are_deterministic() -> None:
    spec = SyntheticGraphSpec(seed=42, supplier_count=4, component_count=3, facility_count=2, days=10)

    first = generate_synthetic_edge_events(spec)
    second = generate_synthetic_edge_events(spec)

    assert first == second
    assert any(event.action == "delete" for event in first)


def test_materialization_respects_observed_and_effective_cutoffs() -> None:
    events = (
        EdgeEvent("supplier:a", "component:x", "supplies", "upsert", 0, 0, {"lead_time_days": 4}),
        EdgeEvent("supplier:a", "component:x", "supplies", "delete", 1, 5),
        EdgeEvent("component:x", "facility:z", "used_by", "upsert", 10, 2),
    )

    state_at_4 = materialize_edge_state(events, 4, include_inactive=True)
    state_at_5 = materialize_edge_state(events, 5, include_inactive=True)

    assert state_at_4[EdgeKey("supplier:a", "component:x", "supplies")].active is True
    assert state_at_5[EdgeKey("supplier:a", "component:x", "supplies")].active is False
    assert EdgeKey("component:x", "facility:z", "used_by") not in state_at_5


def test_snapshot_checksum_is_canonical_for_equivalent_state() -> None:
    events = (
        EdgeEvent("b", "c", "used_by", "upsert", 0, 0, {"criticality": 0.7}, sequence=2),
        EdgeEvent("a", "b", "supplies", "upsert", 0, 0, {"lead_time_days": 3}, sequence=1),
    )
    reversed_events = tuple(reversed(events))

    left = snapshot_from_edge_states(materialize_edge_state(events, 0), 0)
    right = snapshot_from_edge_states(materialize_edge_state(reversed_events, 0), 0)

    assert snapshot_checksum(left) == snapshot_checksum(right)


def test_graph_diff_reports_added_removed_and_changed_edges() -> None:
    before = GraphSnapshot(
        as_of=0,
        nodes=("a", "b", "c"),
        edges=(
            EdgeRecord("a", "b", "supplies", {"lead_time_days": 3}),
            EdgeRecord("b", "c", "used_by", {"criticality": 0.5}),
        ),
    )
    after = GraphSnapshot(
        as_of=1,
        nodes=("a", "b", "d"),
        edges=(
            EdgeRecord("a", "b", "supplies", {"lead_time_days": 6}),
            EdgeRecord("b", "d", "used_by", {"criticality": 0.8}),
        ),
    )

    diff = diff_snapshots(before, after)

    assert diff.added_nodes == ("d",)
    assert diff.removed_nodes == ("c",)
    assert [edge.key for edge in diff.added_edges] == [EdgeKey("b", "d", "used_by")]
    assert [edge.key for edge in diff.removed_edges] == [EdgeKey("b", "c", "used_by")]
    assert len(diff.changed_edges) == 1
    assert diff.changed_edges[0].before.attrs["lead_time_days"] == 3
    assert diff.changed_edges[0].after.attrs["lead_time_days"] == 6
