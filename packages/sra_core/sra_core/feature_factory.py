from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any

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
    paths_by_target: dict[str, list[Any]] = {}
    for path in paths:
        paths_by_target.setdefault(path.target_id, []).append(path)

    entity_ids = [entity.canonical_id for entity in entities]
    max_inbound = max([len(edges) for edges in inbound.values()] + [1])
    max_outbound = max([len(edges) for edges in outbound.values()] + [1])
    max_total = max(
        [
            len(inbound.get(entity_id, [])) + len(outbound.get(entity_id, []))
            for entity_id in entity_ids
        ]
        + [1]
    )
    max_path_count = max([len(paths) for paths in paths_by_target.values()] + [1])
    max_source_diversity = max(
        [len({edge.source for edge in edges}) for edges in inbound.values()] + [1]
    )

    values: list[FeatureValue] = []
    for entity in entities:
        if entity.entity_type not in {"firm", "port", "product"}:
            continue
        inbound_edges = inbound.get(entity.canonical_id, [])
        outbound_edges = outbound.get(entity.canonical_id, [])
        entity_paths = paths_by_target.get(entity.canonical_id, [])
        path_scores = [_path_score(path) for path in entity_paths]
        path_risks = [float(path.path_risk) for path in entity_paths]
        path_confidences = [float(path.path_confidence) for path in entity_paths]
        source_count = len({edge.source for edge in inbound_edges})
        features = {
            "inbound_edge_count": float(len(inbound_edges)),
            "outbound_edge_count": float(len(outbound_edges)),
            "total_edge_count": float(len(inbound_edges) + len(outbound_edges)),
            "inbound_degree_norm": len(inbound_edges) / max_inbound,
            "outbound_degree_norm": len(outbound_edges) / max_outbound,
            "total_degree_norm": (len(inbound_edges) + len(outbound_edges)) / max_total,
            "incoming_risk_max": max([edge.risk_score for edge in inbound_edges] + [0.0]),
            "incoming_risk_mean": _mean([edge.risk_score for edge in inbound_edges]),
            "incoming_confidence_mean": _mean([edge.confidence for edge in inbound_edges]),
            "incoming_weight_mean": _mean([_clamp01(edge.weight) for edge in inbound_edges]),
            "evidence_quality_mean": _mean([_edge_evidence_quality(edge) for edge in inbound_edges]),
            "source_diversity_norm": source_count / max_source_diversity,
            "path_count": float(len(entity_paths)),
            "path_count_norm": len(entity_paths) / max_path_count,
            "path_risk_max": max(path_risks + [0.0]),
            "path_risk_mean": _mean(path_risks),
            "path_score_max": max(path_scores + [0.0]),
            "path_score_mean": _mean(path_scores),
            "path_confidence_mean": _mean(path_confidences),
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


def _path_score(path: Any) -> float:
    return _clamp01(
        float(path.path_risk) * float(path.path_confidence) * _clamp01(path.path_weight)
    )


def _edge_evidence_quality(edge: EdgeState) -> float:
    explicit_quality = _attribute_float(
        edge,
        ("evidence_quality", "source_reliability", "reliability", "quality"),
    )
    if explicit_quality is None:
        return _clamp01(edge.confidence)
    return _clamp01(edge.confidence * _clamp01(explicit_quality))


def _attribute_float(edge: EdgeState, names: tuple[str, ...]) -> float | None:
    for name in names:
        if name not in edge.attributes:
            continue
        value = edge.attributes[name]
        if isinstance(value, int | float):
            return float(value)
    return None


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))
