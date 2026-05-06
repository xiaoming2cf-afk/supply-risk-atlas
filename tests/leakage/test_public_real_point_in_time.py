from __future__ import annotations

from sra_core.real_pipeline import PUBLIC_REAL_AS_OF_TIME, build_public_real_dataset, run_public_real_pipeline


def test_public_real_edge_events_are_visible_only_after_observed_ingest_time() -> None:
    dataset = build_public_real_dataset()

    assert dataset.edge_events
    assert all(event.ingest_time <= PUBLIC_REAL_AS_OF_TIME for event in dataset.edge_events)
    assert all(event.event_time <= PUBLIC_REAL_AS_OF_TIME for event in dataset.edge_events)


def test_public_real_features_do_not_exceed_snapshot_as_of_time() -> None:
    result = run_public_real_pipeline()

    assert result.features
    assert all(feature.feature_time <= result.snapshot.as_of_time for feature in result.features)
    assert all(feature.as_of_time <= result.snapshot.as_of_time for feature in result.features)
