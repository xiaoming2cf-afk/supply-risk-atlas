from __future__ import annotations

from sra_core.contracts.domain import CanonicalEntity, EdgeState


def graph_invariant_errors(entities: list[CanonicalEntity], states: list[EdgeState]) -> list[str]:
    entity_ids = {entity.canonical_id for entity in entities}
    errors: list[str] = []
    for state in states:
        if state.source_id not in entity_ids:
            errors.append(f"{state.edge_id}: source_id does not exist")
        if state.target_id not in entity_ids:
            errors.append(f"{state.edge_id}: target_id does not exist")
        if state.valid_to is not None and state.valid_from > state.valid_to:
            errors.append(f"{state.edge_id}: invalid temporal interval")
        if not 0 <= state.confidence <= 1:
            errors.append(f"{state.edge_id}: confidence out of range")
    return errors
