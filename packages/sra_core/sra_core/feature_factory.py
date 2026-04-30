from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from graph_kernel.path_index import build_path_index
from sra_core.contracts.domain import CanonicalEntity, EdgeState, FeatureValue, GraphSnapshot


def _feature_id(entity_id: str, feature_name: str, as_of_time: datetime) -> str:
    digest = sha256(f"{entity_id}|{feature_name}|{as_of_time.isoformat()}".encode()).hexdigest()[:12]
    return f"feature_{digest}"


def compute_features(
    entities: list[CanonicalEntity],
    edge_states: list[EdgeState],
    snapshot: GraphSnapshot,
) -> list[FeatureValue]:
    version = f"f_{snapshot.graph_version.removeprefix('g_')}"
    active_edges = [edge for edge in edge_states if edge.valid_to is None]
    inbound: dict[str, list[EdgeState]] = {}
    outbound: dict[str, list[EdgeState]] = {}
    for edge in active_edges:
        inbound.setdefault(edge.target_id, []).append(edge)
        outbound.setdefault(edge.source_id, []).append(edge)
    paths = build_path_index(edge_states)
    paths_by_target: dict[str, list[float]] = {}
    for path in paths:
        paths_by_target.setdefault(path.target_id, []).append(path.path_risk)

    values: list[FeatureValue] = []
    for entity in entities:
        if entity.entity_type not in {"firm", "port", "product"}:
            continue
        features = {
            "inbound_edge_count": float(len(inbound.get(entity.canonical_id, []))),
            "outbound_edge_count": float(len(outbound.get(entity.canonical_id, []))),
            "incoming_risk_mean": _mean([edge.risk_score for edge in inbound.get(entity.canonical_id, [])]),
            "path_risk_max": max(paths_by_target.get(entity.canonical_id, [0.0])),
        }
        for name, value in features.items():
            values.append(
                FeatureValue(
                    feature_id=_feature_id(entity.canonical_id, name, snapshot.as_of_time),
                    entity_id=entity.canonical_id,
                    entity_type=entity.entity_type,
                    feature_name=name,
                    feature_value=value,
                    feature_time=snapshot.as_of_time,
                    as_of_time=snapshot.as_of_time,
                    feature_version=version,
                    source_snapshot=snapshot.snapshot_id,
                )
            )
    return sorted(values, key=lambda value: (value.entity_id, value.feature_name))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0
