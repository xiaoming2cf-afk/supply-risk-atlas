from __future__ import annotations

from datetime import datetime

from sra_core.contracts.domain import EdgeState


def temporal_neighbor_sample(
    edge_states: list[EdgeState],
    target_id: str,
    as_of_time: datetime,
    limit: int = 10,
) -> list[EdgeState]:
    candidates = [
        edge
        for edge in edge_states
        if edge.target_id == target_id
        and edge.valid_from <= as_of_time
        and (edge.valid_to is None or edge.valid_to <= as_of_time)
    ]
    return sorted(candidates, key=lambda edge: (edge.risk_score, edge.weight), reverse=True)[:limit]
