from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from sra_core.contracts.semiconductor import SemiriskEdge, SemiriskGraphSnapshot


PROPAGATION_EDGE_TYPES = {
    "depends_on",
    "requires",
    "supplies",
    "produces",
    "participates_in",
    "routes_through",
    "restricted_by",
    "impacted_by",
}


def resolve_targets(snapshot: SemiriskGraphSnapshot, selectors: list[str]) -> list[str]:
    node_by_id = {node.node_id: node for node in snapshot.nodes}
    aliases = {
        "country:taiwan": "country:tw",
        "chemical:specialty_gas": "chemical:specialty_gas",
    }
    resolved: list[str] = []
    for selector in selectors:
        normalized = aliases.get(selector, selector)
        if normalized in node_by_id:
            resolved.append(normalized)
            continue
        if selector.startswith("node_type:"):
            node_type = selector.split(":", 1)[1]
            resolved.extend(node.node_id for node in snapshot.nodes if node.node_type == node_type)
            continue
        text = selector.lower().replace("_", " ")
        matches = [
            node.node_id
            for node in snapshot.nodes
            if text in node.canonical_name.lower() or text in node.node_id.lower().replace("_", " ")
        ]
        resolved.extend(matches)
    return sorted(dict.fromkeys(resolved))


def propagate_loss(
    snapshot: SemiriskGraphSnapshot,
    *,
    initial_losses: dict[str, float],
    duration_days: float,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    steps = max(1, min(12, int(round(max(1.0, duration_days) / 7.0))))
    losses = {node_id: _clamp01(value) for node_id, value in initial_losses.items()}
    traces: list[dict[str, Any]] = []
    edges = [edge for edge in snapshot.edges if edge.edge_type in PROPAGATION_EDGE_TYPES]
    for step in range(1, steps + 1):
        next_losses = dict(losses)
        for edge in edges:
            for source_id, target_id, direction_multiplier, direction in _edge_directions(edge):
                source_loss = losses.get(source_id, 0.0)
                if source_loss <= 0:
                    continue
                contribution = source_loss * _edge_transmission(edge) * direction_multiplier
                contribution = _apply_mitigation(contribution, snapshot, target_id, edge)
                if contribution <= next_losses.get(target_id, 0.0):
                    continue
                next_losses[target_id] = _clamp01(contribution)
                traces.append(
                    {
                        "step": step,
                        "edge_id": edge.edge_id,
                        "edge_type": edge.edge_type,
                        "source_node_id": source_id,
                        "target_node_id": target_id,
                        "direction": direction,
                        "loss_contribution": round(contribution * 100.0, 4),
                        "evidence_refs": evidence_refs_for_edge(edge),
                    }
                )
        losses = {node_id: _clamp01(value * 0.97) for node_id, value in next_losses.items()}
    return losses, traces


def summarize_affected_nodes(
    snapshot: SemiriskGraphSnapshot,
    losses_by_iteration: list[dict[str, float]],
    *,
    limit: int = 12,
) -> list[dict[str, Any]]:
    node_by_id = {node.node_id: node for node in snapshot.nodes}
    collected: dict[str, list[float]] = defaultdict(list)
    for losses in losses_by_iteration:
        for node_id, loss in losses.items():
            if loss >= 0.01:
                collected[node_id].append(loss * 100.0)
    rows = []
    for node_id, values in collected.items():
        node = node_by_id.get(node_id)
        rows.append(
            {
                "node_id": node_id,
                "label": node.canonical_name if node else node_id,
                "node_type": node.node_type if node else "unknown",
                "loss_score": round(mean(values), 4),
                "evidence_refs": _node_evidence(snapshot, node_id),
            }
        )
    return sorted(rows, key=lambda row: (-float(row["loss_score"]), str(row["node_id"])))[:limit]


def top_transmission_paths(
    snapshot: SemiriskGraphSnapshot,
    traces: list[dict[str, Any]],
    *,
    limit: int = 8,
) -> list[dict[str, Any]]:
    node_by_id = {node.node_id: node for node in snapshot.nodes}
    by_edge: dict[str, dict[str, Any]] = {}
    for trace in traces:
        key = f"{trace['edge_id']}:{trace['source_node_id']}:{trace['target_node_id']}"
        source_node = node_by_id.get(trace["source_node_id"])
        target_node = node_by_id.get(trace["target_node_id"])
        source_label = source_node.canonical_name if source_node else str(trace["source_node_id"])
        target_label = target_node.canonical_name if target_node else str(trace["target_node_id"])
        row = by_edge.setdefault(
            key,
            {
                "path_id": f"path:{key}",
                "node_sequence": [trace["source_node_id"], trace["target_node_id"]],
                "edge_sequence": [trace["edge_id"]],
                "loss_contribution": 0.0,
                "evidence_refs": [],
                "explanation": f"{source_label} transmitted normalized stress to {target_label} via {trace['edge_type']}.",
            },
        )
        row["loss_contribution"] = max(float(row["loss_contribution"]), float(trace["loss_contribution"]))
        row["evidence_refs"] = _unique_refs([*row["evidence_refs"], *trace["evidence_refs"]])
    return sorted(
        by_edge.values(),
        key=lambda row: (-float(row["loss_contribution"]), str(row["path_id"])),
    )[:limit]


def evidence_refs_for_edge(edge: SemiriskEdge) -> list[dict[str, Any]]:
    return [
        {
            "edge_id": edge.edge_id,
            "source_id": ref.source_id,
            "source_record_id": ref.source_record_id,
            "raw_id": ref.raw_id,
            "payload_hash": ref.payload_hash,
            "provenance_url": ref.provenance_url,
            "as_of_time": ref.as_of_time.isoformat(),
        }
        for ref in edge.provenance_refs
    ]


def _edge_directions(edge: SemiriskEdge) -> list[tuple[str, str, float, str]]:
    directions = [(edge.source_node_id, edge.target_node_id, 1.0, "source_to_target")]
    if edge.edge_type in {"depends_on", "requires", "routes_through", "participates_in"}:
        directions.append((edge.target_node_id, edge.source_node_id, 0.78, "dependency_feedback"))
    elif edge.edge_type in {"supplies", "produces"}:
        directions.append((edge.target_node_id, edge.source_node_id, 0.52, "supply_feedback"))
    elif edge.edge_type in {"restricted_by", "impacted_by"}:
        directions.append((edge.target_node_id, edge.source_node_id, 1.08, "policy_or_event_to_subject"))
    return directions


def _edge_transmission(edge: SemiriskEdge) -> float:
    factor = max(0.02, min(1.0, float(edge.weight) * max(0.1, float(edge.confidence))))
    if edge.edge_type == "restricted_by":
        factor *= 1.15
    if edge.edge_type == "impacted_by":
        factor *= 1.08
    return _clamp01(factor)


def _apply_mitigation(value: float, snapshot: SemiriskGraphSnapshot, node_id: str, edge: SemiriskEdge) -> float:
    node_by_id = {node.node_id: node for node in snapshot.nodes}
    node_attrs = node_by_id.get(node_id).attributes if node_id in node_by_id else {}
    edge_attrs = edge.attributes or {}
    substitutability = max(
        _attr_float(node_attrs, "substitutability_score", 0.0),
        _attr_float(edge_attrs, "substitutability_score", 0.0),
    )
    inventory_days = max(
        _attr_float(node_attrs, "inventory_buffer_days", 0.0),
        _attr_float(edge_attrs, "inventory_buffer_days", 0.0),
    )
    recovery_rate = max(
        _attr_float(node_attrs, "recovery_rate", 0.0),
        _attr_float(edge_attrs, "recovery_rate", 0.0),
    )
    inventory_offset = min(0.3, inventory_days / 120.0)
    mitigation = min(0.65, substitutability * 0.35 + inventory_offset + recovery_rate * 0.25)
    return _clamp01(value * (1.0 - mitigation))


def _node_evidence(snapshot: SemiriskGraphSnapshot, node_id: str) -> list[dict[str, Any]]:
    refs = []
    for edge in snapshot.edges:
        if edge.source_node_id == node_id or edge.target_node_id == node_id:
            refs.extend(evidence_refs_for_edge(edge))
    return _unique_refs(refs)


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {}
    for ref in refs:
        by_key[(ref.get("source_id"), ref.get("source_record_id"), ref.get("payload_hash"), ref.get("edge_id"))] = ref
    return [by_key[key] for key in sorted(by_key)]


def _attr_float(attrs: dict[str, Any], key: str, default: float) -> float:
    try:
        return float(attrs.get(key, default))
    except (TypeError, ValueError):
        return default


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))

