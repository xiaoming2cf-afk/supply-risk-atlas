from __future__ import annotations

from typing import Any

from sra_core.contracts.semiconductor import SemiriskGraphSnapshot

from .propagation import evidence_refs_for_edge


TYPE_TO_SHOCK = {
    "country": "country",
    "region": "country",
    "material": "material",
    "chemical": "material",
    "equipment": "equipment",
    "component": "equipment",
    "product_grade": "demand",
    "technology_node": "process_stage",
    "process_stage": "process_stage",
    "company": "company",
    "facility": "facility",
    "route": "route",
    "policy_event": "policy",
    "risk_event": "risk_event",
    "market_indicator": "demand",
}


def generate_shock_candidates(
    snapshot: SemiriskGraphSnapshot,
    *,
    candidate_scope: dict[str, Any] | None = None,
    allowed_shock_types: list[str] | None = None,
    forbidden_shock_types: list[str] | None = None,
    limit: int = 48,
) -> list[dict[str, Any]]:
    scope = candidate_scope or {}
    node_types = {str(item) for item in scope.get("node_types", []) if str(item)}
    allowed = {str(item) for item in (allowed_shock_types or []) if str(item)}
    forbidden = {str(item) for item in (forbidden_shock_types or []) if str(item)}
    risk_by_node: dict[str, float] = {}
    confidence_by_node: dict[str, float] = {}
    evidence_by_node: dict[str, list[dict[str, Any]]] = {}
    for edge in snapshot.edges:
        score = float(edge.weight) * max(0.1, float(edge.confidence))
        if edge.edge_type in {"restricted_by", "impacted_by"}:
            score *= 1.2
        for node_id in (edge.source_node_id, edge.target_node_id):
            risk_by_node[node_id] = max(risk_by_node.get(node_id, 0.0), score)
            confidence_by_node[node_id] = max(confidence_by_node.get(node_id, 0.0), float(edge.confidence))
            evidence_by_node.setdefault(node_id, []).extend(evidence_refs_for_edge(edge))

    candidates = []
    for node in snapshot.nodes:
        if node_types and node.node_type not in node_types:
            continue
        shock_type = TYPE_TO_SHOCK.get(node.node_type, "company")
        if allowed and shock_type not in allowed:
            continue
        if shock_type in forbidden:
            continue
        risk = risk_by_node.get(node.node_id, 0.0)
        if risk <= 0:
            continue
        candidates.append(
            {
                "shock_id": f"shock:{shock_type}:{node.node_id}",
                "shock_type": shock_type,
                "target_id": node.node_id,
                "target_type": node.node_type,
                "label": node.canonical_name,
                "severity": round(max(0.35, min(0.96, 0.45 + risk * 0.45)), 4),
                "duration_days": 60 if shock_type == "policy" else 28,
                "confidence": round(max(0.35, confidence_by_node.get(node.node_id, node.confidence)), 4),
                "evidence_refs": _unique_refs(evidence_by_node.get(node.node_id, []))[:6],
            }
        )
    return sorted(candidates, key=lambda item: (-item["severity"], -item["confidence"], item["target_id"]))[:limit]


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {}
    for ref in refs:
        by_key[(ref.get("source_id"), ref.get("source_record_id"), ref.get("payload_hash"), ref.get("edge_id"))] = ref
    return [by_key[key] for key in sorted(by_key)]

