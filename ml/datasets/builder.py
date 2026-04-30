from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sra_core.contracts.domain import EdgeState, FeatureValue, LabelValue, PathIndex


@dataclass(frozen=True)
class DatasetSample:
    target_id: str
    target_type: str
    prediction_time: datetime
    horizon: int
    graph_version: str
    feature_version: str
    label_version: str
    node_features: dict[str, float]
    edge_features: dict[str, float]
    path_tokens: list[str]
    label: float | None


def build_dataset(
    prediction_time: datetime,
    graph_version: str,
    feature_values: list[FeatureValue],
    labels: list[LabelValue],
    edge_states: list[EdgeState],
    paths: list[PathIndex],
) -> list[DatasetSample]:
    labels_by_target = {(label.target_id, label.label_name): label for label in labels}
    feature_by_entity: dict[str, dict[str, float]] = {}
    for feature in feature_values:
        if feature.as_of_time > prediction_time or feature.feature_time > prediction_time:
            raise ValueError("feature leakage detected in dataset builder")
        feature_by_entity.setdefault(feature.entity_id, {})[feature.feature_name] = feature.feature_value

    incoming_risk: dict[str, float] = {}
    for edge in edge_states:
        incoming_risk[edge.target_id] = max(incoming_risk.get(edge.target_id, 0.0), edge.risk_score)

    path_by_target: dict[str, list[str]] = {}
    for path in paths:
        path_by_target.setdefault(path.target_id, []).append(path.path_id)

    samples: list[DatasetSample] = []
    for entity_id, features in sorted(feature_by_entity.items()):
        label = labels_by_target.get((entity_id, "firm_risk_30d"))
        if label and label.prediction_time != prediction_time:
            continue
        feature_version = next(
            feature.feature_version for feature in feature_values if feature.entity_id == entity_id
        )
        label_version = label.label_version if label else "l_unlabeled"
        samples.append(
            DatasetSample(
                target_id=entity_id,
                target_type="firm",
                prediction_time=prediction_time,
                horizon=30,
                graph_version=graph_version,
                feature_version=feature_version,
                label_version=label_version,
                node_features=features,
                edge_features={"incoming_risk_max": incoming_risk.get(entity_id, 0.0)},
                path_tokens=sorted(path_by_target.get(entity_id, []))[:8],
                label=label.label_value if label else None,
            )
        )
    return samples
