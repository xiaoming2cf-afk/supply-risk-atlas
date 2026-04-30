from graph_kernel.events import EdgeEvent, EdgeKey, materialize_edge_state
from graph_kernel.snapshots import snapshot_from_edge_states
from ml.features import FeatureFactory
from ml.labels import LabelFactory, LabelSpec


def test_late_observed_past_event_does_not_change_cutoff_features() -> None:
    visible = (
        EdgeEvent("supplier:a", "component:x", "supplies", "upsert", 0, 0, {"lead_time_days": 4}),
    )
    late_observed_delete = EdgeEvent("supplier:a", "component:x", "supplies", "delete", 1, 5)

    without_future = snapshot_from_edge_states(materialize_edge_state(visible, 4), 4)
    with_future = snapshot_from_edge_states(materialize_edge_state(visible + (late_observed_delete,), 4), 4)

    factory = FeatureFactory()
    assert factory.build(without_future) == factory.build(with_future)


def test_future_effective_event_is_not_materialized_even_when_observed() -> None:
    events = (
        EdgeEvent("supplier:a", "component:x", "supplies", "upsert", 0, 0),
        EdgeEvent("component:x", "facility:z", "used_by", "upsert", 10, 2),
    )

    states = materialize_edge_state(events, 5)

    assert EdgeKey("supplier:a", "component:x", "supplies") in states
    assert EdgeKey("component:x", "facility:z", "used_by") not in states


def test_labels_use_only_future_observed_window() -> None:
    events = (
        EdgeEvent("supplier:a", "component:x", "supplies", "upsert", 0, 0),
        EdgeEvent("supplier:a", "component:x", "supplies", "delete", 1, 5),
        EdgeEvent("supplier:b", "component:y", "supplies", "delete", 1, 9),
    )
    labels = LabelFactory(LabelSpec(horizon=1)).build(
        events,
        ["supplier:a", "component:x", "supplier:b", "component:y"],
        cutoff=4,
    )

    assert labels["supplier:a"] == 1
    assert labels["component:x"] == 1
    assert labels["supplier:b"] == 0
    assert labels["component:y"] == 0
