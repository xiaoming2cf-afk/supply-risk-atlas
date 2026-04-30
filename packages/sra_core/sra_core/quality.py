from __future__ import annotations

from datetime import datetime

from sra_core.contracts.domain import ApiEnvelope, CanonicalEntity, EdgeEvent, EdgeState
from sra_core.ontology import Ontology


def validate_edge_events(
    events: list[EdgeEvent],
    entities: list[CanonicalEntity],
    ontology: Ontology,
) -> list[str]:
    errors: list[str] = []
    entity_ids = {entity.canonical_id for entity in entities}
    edge_types = set(ontology.edge_types)
    for event in events:
        if event.source_id not in entity_ids:
            errors.append(f"{event.edge_event_id}: missing source entity {event.source_id}")
        if event.target_id not in entity_ids:
            errors.append(f"{event.edge_event_id}: missing target entity {event.target_id}")
        if event.edge_type not in edge_types:
            errors.append(f"{event.edge_event_id}: unknown edge_type {event.edge_type}")
        if not event.source:
            errors.append(f"{event.edge_event_id}: source is required")
    return errors


def validate_edge_states(states: list[EdgeState], entities: list[CanonicalEntity]) -> list[str]:
    errors: list[str] = []
    entity_ids = {entity.canonical_id for entity in entities}
    for state in states:
        if state.source_id not in entity_ids:
            errors.append(f"{state.edge_id}: missing source entity {state.source_id}")
        if state.target_id not in entity_ids:
            errors.append(f"{state.edge_id}: missing target entity {state.target_id}")
        if state.valid_to is not None and state.valid_from > state.valid_to:
            errors.append(f"{state.edge_id}: valid_from after valid_to")
        if not 0.0 <= state.confidence <= 1.0:
            errors.append(f"{state.edge_id}: confidence out of range")
    return errors


def assert_visible_at(ingest_time: datetime, prediction_time: datetime) -> None:
    if ingest_time > prediction_time:
        raise ValueError("record ingest_time is later than prediction_time/as_of_time")


def validate_api_envelope(envelope: ApiEnvelope) -> list[str]:
    errors: list[str] = []
    if not envelope.request_id:
        errors.append("request_id is required")
    if envelope.status not in {"success", "error"}:
        errors.append("status must be success or error")
    metadata = envelope.metadata
    required = [
        metadata.graph_version,
        metadata.feature_version,
        metadata.label_version,
        metadata.model_version,
        metadata.as_of_time,
    ]
    if any(value is None or value == "" for value in required):
        errors.append("metadata must include graph, feature, label, model versions and as_of_time")
    return errors
