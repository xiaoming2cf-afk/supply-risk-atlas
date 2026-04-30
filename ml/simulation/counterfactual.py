from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from sra_core.contracts.domain import EdgeState


@dataclass(frozen=True)
class CounterfactualResult:
    counterfactual_graph_version: str
    edge_states: list[EdgeState]
    removed_edges: list[str]


def build_counterfactual_edges(
    base_graph_version: str,
    edge_states: list[EdgeState],
    intervention_type: str,
    target_id: str,
) -> CounterfactualResult:
    removed: list[str] = []
    copied = [edge.model_copy(deep=True) for edge in edge_states]
    if intervention_type in {"remove_node", "close_port"}:
        kept: list[EdgeState] = []
        for edge in copied:
            if edge.source_id == target_id or edge.target_id == target_id:
                removed.append(edge.edge_id)
            else:
                kept.append(edge)
        copied = kept
    elif intervention_type == "remove_edge":
        copied = [edge for edge in copied if not (edge.edge_id == target_id and not removed.append(edge.edge_id))]
    elif intervention_type == "increase_tariff":
        copied = [
            edge.model_copy(update={"risk_score": min(1.0, edge.risk_score + 0.15)})
            if edge.target_id == target_id
            else edge
            for edge in copied
        ]
    digest = sha256(f"{base_graph_version}|{intervention_type}|{target_id}".encode()).hexdigest()[:12]
    version = f"cf_{digest}"
    copied = [edge.model_copy(update={"graph_version": version}) for edge in copied]
    return CounterfactualResult(version, copied, sorted(removed))
