"""Temporal dataset builder for graph ML experiments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from graph_kernel.events import EdgeEvent, materialize_edge_state
from graph_kernel.snapshots import snapshot_from_edge_states

from .features import FeatureFactory
from .labels import LabelFactory


@dataclass(frozen=True)
class DatasetRecord:
    entity_id: str
    cutoff: int
    features: dict[str, float]
    label: int


class DatasetBuilder:
    def __init__(
        self,
        feature_factory: FeatureFactory | None = None,
        label_factory: LabelFactory | None = None,
    ) -> None:
        self.feature_factory = feature_factory or FeatureFactory()
        self.label_factory = label_factory or LabelFactory()

    def build(
        self,
        events: Iterable[EdgeEvent],
        *,
        cutoffs: Sequence[int],
    ) -> tuple[DatasetRecord, ...]:
        event_tuple = tuple(events)
        records: list[DatasetRecord] = []
        for cutoff in sorted(dict.fromkeys(cutoffs)):
            states = materialize_edge_state(event_tuple, cutoff)
            snapshot = snapshot_from_edge_states(states, cutoff)
            feature_rows = self.feature_factory.build(snapshot)
            labels = self.label_factory.build(event_tuple, feature_rows.keys(), cutoff=cutoff)
            for entity_id in sorted(feature_rows):
                records.append(
                    DatasetRecord(
                        entity_id=entity_id,
                        cutoff=cutoff,
                        features=dict(feature_rows[entity_id]),
                        label=labels.get(entity_id, 0),
                    )
                )
        return tuple(records)


def temporal_train_test_split(
    records: Iterable[DatasetRecord],
    *,
    test_cutoff_start: int,
) -> tuple[tuple[DatasetRecord, ...], tuple[DatasetRecord, ...]]:
    train: list[DatasetRecord] = []
    test: list[DatasetRecord] = []
    for record in sorted(records, key=lambda item: (item.cutoff, item.entity_id)):
        if record.cutoff >= test_cutoff_start:
            test.append(record)
        else:
            train.append(record)
    return tuple(train), tuple(test)
