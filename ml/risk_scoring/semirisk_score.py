from __future__ import annotations

from collections import deque
from typing import Any, Iterable

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.contracts.semiconductor import SemiriskEdge, SemiriskGraphSnapshot, SemiriskNode


FEATURE_VERSION = "semirisk_risk_score_v0.1"
RISK_SCORE_WARNING_FIXTURE_GRAPH = "fixture_graph:not_production_ready"
DEFAULT_ENTITY_ID = "company:tsmc"

COMPONENT_WEIGHTS = {
    "exposure_score": 0.25,
    "criticality_score": 0.25,
    "substitution_gap": 0.15,
    "policy_risk": 0.15,
    "event_pressure": 0.10,
    "market_pressure": 0.10,
}

EXPOSURE_EDGE_TYPES = {
    "depends_on",
    "requires",
    "supplies",
    "produces",
    "routes_through",
    "participates_in",
}


class RiskScoreUnavailable(ValueError):
    """Raised when the fixture graph cannot support an evidence-backed score."""


def score_semirisk_entity(
    node_id: str = DEFAULT_ENTITY_ID,
    *,
    snapshot: SemiriskGraphSnapshot | None = None,
) -> dict[str, Any]:
    """Compute a deterministic fixture-only risk score for one SemiRisk graph node."""

    graph = snapshot or build_semiconductor_fixture_snapshot()
    node_by_id = {node.node_id: node for node in graph.nodes}
    node = node_by_id.get(node_id)
    if node is None:
        raise RiskScoreUnavailable(f"unknown node_id: {node_id}")

    distances = _node_distances(graph, node_id, depth=2)
    components = _score_components(graph, node, distances)
    available = [component for component in components if component["status"] == "available"]
    evidence_refs = _unique_evidence(
        ref
        for component in available
        for ref in component.get("evidence_refs", [])
    )
    if not available or not evidence_refs:
        raise RiskScoreUnavailable(f"insufficient evidence for risk score: {node_id}")

    available_weight = sum(float(component["weight"]) for component in available)
    score = round(
        sum(float(component["value"]) * float(component["weight"]) for component in available)
        / available_weight,
        2,
    )
    for component in components:
        if component["status"] == "available":
            normalized_weight = float(component["weight"]) / available_weight
            component["weighted_contribution"] = round(float(component["value"]) * normalized_weight, 4)
        else:
            component["weighted_contribution"] = None

    warnings = [RISK_SCORE_WARNING_FIXTURE_GRAPH]
    warnings.extend(
        f"risk_component_unavailable:{component['name']}"
        for component in components
        if component["status"] != "available"
    )
    return {
        "node_id": node.node_id,
        "entity": _node_identity(node),
        "score": _clamp_score(score),
        "level": level_for_score(score),
        "components": components,
        "evidence_refs": evidence_refs,
        "feature_version": FEATURE_VERSION,
        "graph_version": graph.graph_version,
        "source_manifest_id": graph.source_manifest_id,
        "as_of_time": graph.as_of_time.isoformat(),
        "fixture_graph": True,
        "warnings": sorted(set(warnings)),
    }


def rank_risk_portfolio(
    *,
    snapshot: SemiriskGraphSnapshot | None = None,
    node_type: str | None = "company",
    limit: int = 20,
) -> dict[str, Any]:
    graph = snapshot or build_semiconductor_fixture_snapshot()
    limit = max(1, min(int(limit), 100))
    candidates = [
        node
        for node in graph.nodes
        if node_type is None or node.node_type == node_type
    ]
    scores: list[dict[str, Any]] = []
    warnings = {RISK_SCORE_WARNING_FIXTURE_GRAPH}
    for node in candidates:
        try:
            result = score_semirisk_entity(node.node_id, snapshot=graph)
        except RiskScoreUnavailable as exc:
            warnings.add(f"risk_score_unavailable:{node.node_id}:{type(exc).__name__}")
            continue
        scores.append(
            {
                "node_id": result["node_id"],
                "canonical_name": result["entity"]["canonical_name"],
                "node_type": result["entity"]["node_type"],
                "score": result["score"],
                "level": result["level"],
                "evidence_ref_count": len(result["evidence_refs"]),
            }
        )
    scores.sort(key=lambda item: (-float(item["score"]), str(item["node_id"])))
    return {
        "graph_version": graph.graph_version,
        "source_manifest_id": graph.source_manifest_id,
        "feature_version": FEATURE_VERSION,
        "as_of_time": graph.as_of_time.isoformat(),
        "fixture_graph": True,
        "node_type": node_type,
        "scores": scores[:limit],
        "warnings": sorted(warnings),
    }


def level_for_score(score: float) -> str:
    if score < 25:
        return "low"
    if score < 50:
        return "guarded"
    if score < 70:
        return "elevated"
    if score < 85:
        return "severe"
    return "critical"


def _score_components(
    graph: SemiriskGraphSnapshot,
    node: SemiriskNode,
    distances: dict[str, int],
) -> list[dict[str, Any]]:
    edge_groups = {
        "exposure_score": _context_edges(graph, distances, EXPOSURE_EDGE_TYPES, max_edge_distance=1),
        "policy_risk": _context_edges(graph, distances, {"restricted_by"}, max_edge_distance=2),
        "event_pressure": _context_edges(graph, distances, {"impacted_by"}, max_edge_distance=2),
        "market_pressure": [
            edge
            for edge in _context_edges(graph, distances, {"correlated_with"}, max_edge_distance=2)
            if _touches_node_type(graph, edge, "market_indicator")
        ],
    }
    dependency_edges = _context_edges(
        graph,
        distances,
        {"depends_on", "requires", "supplies", "produces", "routes_through"},
        max_edge_distance=1,
    )
    substitutable_edges = _context_edges(graph, distances, {"substitutable_with"}, max_edge_distance=2)

    weighted_degree = _weighted_degree(graph, node.node_id)
    max_weighted_degree = max((_weighted_degree(graph, item.node_id) for item in graph.nodes), default=0.0)
    criticality_edges = _incident_edges(graph, node.node_id)

    components = [
        _edge_pressure_component(
            "exposure_score",
            edge_groups["exposure_score"],
            distances,
            "Dependency, supply, process, production, and route pressure near the entity.",
        ),
        _criticality_component(weighted_degree, max_weighted_degree, criticality_edges),
        _substitution_gap_component(dependency_edges, substitutable_edges, distances),
        _edge_pressure_component(
            "policy_risk",
            edge_groups["policy_risk"],
            distances,
            "Policy and export-control monitoring evidence connected to the entity context.",
        ),
        _edge_pressure_component(
            "event_pressure",
            edge_groups["event_pressure"],
            distances,
            "Risk event evidence connected to the entity context.",
        ),
        _edge_pressure_component(
            "market_pressure",
            edge_groups["market_pressure"],
            distances,
            "Market indicator evidence connected to the entity context.",
        ),
    ]
    return components


def _edge_pressure_component(
    name: str,
    edges: list[SemiriskEdge],
    distances: dict[str, int],
    explanation: str,
) -> dict[str, Any]:
    if not edges:
        return _unavailable_component(name, explanation)
    pressures = sorted(
        ((_discounted_pressure(edge, distances), edge.edge_id, edge) for edge in edges),
        key=lambda item: (item[0], item[1]),
    )
    values = [value for value, _, _ in pressures]
    top_values = sorted(values, reverse=True)[:5]
    value = round((0.6 * max(values)) + (0.4 * (sum(top_values) / len(top_values))), 2)
    evidence_edges = [edge for _, _, edge in sorted(pressures, key=lambda item: (-item[0], item[1]))[:5]]
    return _available_component(name, value, evidence_edges, explanation)


def _criticality_component(
    weighted_degree: float,
    max_weighted_degree: float,
    incident_edges: list[SemiriskEdge],
) -> dict[str, Any]:
    explanation = "Weighted direct graph degree normalized by the most connected fixture graph node."
    if max_weighted_degree <= 0 or not incident_edges:
        return _unavailable_component("criticality_score", explanation)
    value = round(100.0 * weighted_degree / max_weighted_degree, 2)
    return _available_component("criticality_score", value, incident_edges[:5], explanation)


def _substitution_gap_component(
    dependency_edges: list[SemiriskEdge],
    substitutable_edges: list[SemiriskEdge],
    distances: dict[str, int],
) -> dict[str, Any]:
    explanation = "Dependency pressure not covered by explicit substitutable-with evidence."
    if not dependency_edges:
        return _unavailable_component("substitution_gap", explanation)
    dependency_pressure = max(_discounted_pressure(edge, distances) for edge in dependency_edges)
    substitution_support = min(
        100.0,
        sum(_discounted_pressure(edge, distances) for edge in substitutable_edges),
    )
    value = round(max(0.0, dependency_pressure * (1.0 - substitution_support / 100.0)), 2)
    evidence_edges = sorted(
        [*dependency_edges, *substitutable_edges],
        key=lambda edge: _discounted_pressure(edge, distances),
        reverse=True,
    )[:5]
    return _available_component("substitution_gap", value, evidence_edges, explanation)


def _available_component(
    name: str,
    value: float,
    edges: list[SemiriskEdge],
    explanation: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "value": _clamp_score(value),
        "status": "available",
        "weight": COMPONENT_WEIGHTS[name],
        "weighted_contribution": None,
        "evidence_refs": _unique_evidence(_edge_evidence(edge) for edge in edges),
        "explanation": explanation,
    }


def _unavailable_component(name: str, explanation: str) -> dict[str, Any]:
    return {
        "name": name,
        "value": None,
        "status": "unavailable",
        "weight": COMPONENT_WEIGHTS[name],
        "weighted_contribution": None,
        "evidence_refs": [],
        "explanation": explanation,
    }


def _weighted_degree(graph: SemiriskGraphSnapshot, node_id: str) -> float:
    return round(
        sum(edge.weight * edge.confidence for edge in _incident_edges(graph, node_id)),
        6,
    )


def _incident_edges(graph: SemiriskGraphSnapshot, node_id: str) -> list[SemiriskEdge]:
    return [
        edge
        for edge in graph.edges
        if edge.source_node_id == node_id or edge.target_node_id == node_id
    ]


def _node_distances(
    graph: SemiriskGraphSnapshot,
    node_id: str,
    *,
    depth: int,
) -> dict[str, int]:
    adjacency: dict[str, list[str]] = {}
    for edge in graph.edges:
        adjacency.setdefault(edge.source_node_id, []).append(edge.target_node_id)
        adjacency.setdefault(edge.target_node_id, []).append(edge.source_node_id)
    distances = {node_id: 0}
    queue: deque[tuple[str, int]] = deque([(node_id, 0)])
    while queue:
        current, distance = queue.popleft()
        if distance >= depth:
            continue
        for neighbor in adjacency.get(current, []):
            if neighbor in distances:
                continue
            distances[neighbor] = distance + 1
            queue.append((neighbor, distance + 1))
    return distances


def _context_edges(
    graph: SemiriskGraphSnapshot,
    distances: dict[str, int],
    edge_types: set[str],
    *,
    max_edge_distance: int,
) -> list[SemiriskEdge]:
    selected = [
        edge
        for edge in graph.edges
        if edge.edge_type in edge_types and _edge_distance(edge, distances) <= max_edge_distance
    ]
    return sorted(selected, key=lambda edge: edge.edge_id)


def _edge_distance(edge: SemiriskEdge, distances: dict[str, int]) -> int:
    return min(
        distances.get(edge.source_node_id, 99),
        distances.get(edge.target_node_id, 99),
    )


def _discounted_pressure(edge: SemiriskEdge, distances: dict[str, int]) -> float:
    discount = {0: 1.0, 1: 0.65, 2: 0.45}.get(_edge_distance(edge, distances), 0.0)
    return min(100.0, edge.weight * edge.confidence * 100.0 * discount)


def _touches_node_type(graph: SemiriskGraphSnapshot, edge: SemiriskEdge, node_type: str) -> bool:
    node_by_id = {node.node_id: node for node in graph.nodes}
    return any(
        node_by_id.get(node_id) is not None and node_by_id[node_id].node_type == node_type
        for node_id in (edge.source_node_id, edge.target_node_id)
    )


def _edge_evidence(edge: SemiriskEdge) -> dict[str, Any]:
    refs = [
        {
            "source_id": ref.source_id,
            "source_record_id": ref.source_record_id,
            "raw_id": ref.raw_id,
            "payload_hash": ref.payload_hash,
            "provenance_url": ref.provenance_url,
            "retrieved_at": ref.retrieved_at.isoformat(),
            "as_of_time": ref.as_of_time.isoformat(),
        }
        for ref in edge.provenance_refs
    ]
    return {
        "edge_id": edge.edge_id,
        "source_node_id": edge.source_node_id,
        "target_node_id": edge.target_node_id,
        "edge_type": edge.edge_type,
        "evidence_text_summary": edge.evidence_text_summary,
        "source_refs": refs,
    }


def _unique_evidence(refs: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {}
    for ref in refs:
        key = (
            ref.get("edge_id"),
            tuple(
                sorted(
                    (
                        item.get("source_id"),
                        item.get("source_record_id"),
                        item.get("payload_hash"),
                    )
                    for item in ref.get("source_refs", [])
                )
            ),
        )
        by_key[key] = ref
    return [by_key[key] for key in sorted(by_key)]


def _node_identity(node: SemiriskNode) -> dict[str, Any]:
    return {
        "node_id": node.node_id,
        "node_type": node.node_type,
        "canonical_name": node.canonical_name,
        "attributes": {
            key: value
            for key, value in node.attributes.items()
            if key not in {"raw_payload", "payload", "private_diagnostics"}
        },
        "confidence": node.confidence,
        "valid_from": node.valid_from.isoformat(),
        "valid_to": node.valid_to.isoformat() if node.valid_to else None,
    }


def _clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 2)
