from __future__ import annotations

from sra_core.contracts.domain import EdgeState


def diff_edge_states(before: list[EdgeState], after: list[EdgeState]) -> dict[str, list[str]]:
    before_map = {edge.edge_id: edge for edge in before if edge.valid_to is None}
    after_map = {edge.edge_id: edge for edge in after if edge.valid_to is None}
    before_ids = set(before_map)
    after_ids = set(after_map)
    changed = [
        edge_id
        for edge_id in sorted(before_ids & after_ids)
        if before_map[edge_id].model_dump(mode="json") != after_map[edge_id].model_dump(mode="json")
    ]
    return {
        "added": sorted(after_ids - before_ids),
        "removed": sorted(before_ids - after_ids),
        "changed": changed,
    }
