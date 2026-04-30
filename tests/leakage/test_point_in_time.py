from datetime import datetime, timedelta, timezone

import pytest

from graph_kernel.event_store import EdgeEventStore
from graph_kernel.snapshot_builder import build_graph_snapshot
from ml.datasets.builder import build_dataset
from sra_core.contracts.domain import FeatureValue
from sra_core.feature_factory import compute_features
from sra_core.label_factory import generate_labels
from sra_core.synthetic import generate_synthetic_dataset


def test_visible_events_exclude_late_ingest() -> None:
    synthetic = generate_synthetic_dataset(seed=42)
    store = EdgeEventStore(synthetic.edge_events)
    as_of = datetime(2026, 1, 10, tzinfo=timezone.utc)
    assert all(event.ingest_time <= as_of for event in store.visible_events(as_of))


def test_feature_times_do_not_exceed_as_of_time() -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    synthetic = generate_synthetic_dataset(seed=42)
    snapshot, states = build_graph_snapshot(
        synthetic.entities,
        synthetic.edge_events,
        as_of,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    features = compute_features(synthetic.entities, states, snapshot)
    assert all(feature.feature_time <= as_of and feature.as_of_time <= as_of for feature in features)


def test_dataset_builder_rejects_future_feature() -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    synthetic = generate_synthetic_dataset(seed=42)
    snapshot, states = build_graph_snapshot(
        synthetic.entities,
        synthetic.edge_events,
        as_of,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    labels = generate_labels(synthetic.edge_events, as_of)
    future_feature = FeatureValue(
        feature_id="feature_future",
        entity_id="firm_anchor",
        entity_type="firm",
        feature_name="future_signal",
        feature_value=1.0,
        feature_time=as_of + timedelta(days=1),
        as_of_time=as_of + timedelta(days=1),
        feature_version="f_bad",
        source_snapshot=snapshot.snapshot_id,
    )
    with pytest.raises(ValueError):
        build_dataset(as_of, snapshot.graph_version, [future_feature], labels, states, [])
