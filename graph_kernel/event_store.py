from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from hashlib import sha256

from sra_core.contracts.domain import EdgeEvent, EdgeState


def edge_identity(source_id: str, target_id: str, edge_type: str) -> str:
    digest = sha256(f"{source_id}|{target_id}|{edge_type}".encode("utf-8")).hexdigest()[:16]
    return f"edge_{digest}"


class EdgeEventStore:
    def __init__(self, events: Iterable[EdgeEvent] | None = None) -> None:
        self._events: list[EdgeEvent] = []
        for event in events or []:
            self.append(event)

    @property
    def events(self) -> tuple[EdgeEvent, ...]:
        return tuple(self._events)

    def append(self, event: EdgeEvent) -> None:
        if any(existing.edge_event_id == event.edge_event_id for existing in self._events):
            raise ValueError(f"duplicate edge_event_id {event.edge_event_id}")
        self._events.append(event)

    def visible_events(self, as_of_time: datetime) -> list[EdgeEvent]:
        return sorted(
            [
                event
                for event in self._events
                if event.ingest_time <= as_of_time and event.event_time <= as_of_time
            ],
            key=lambda event: (event.event_time, event.ingest_time, event.edge_event_id),
        )


def materialize_edge_states(
    edge_events: Iterable[EdgeEvent],
    as_of_time: datetime,
    graph_version: str,
) -> list[EdgeState]:
    store = EdgeEventStore(edge_events)
    states: dict[str, EdgeState] = {}
    removed: set[str] = set()
    for event in store.visible_events(as_of_time):
        edge_id = edge_identity(event.source_id, event.target_id, event.edge_type)
        if event.event_type == "remove":
            previous = states.get(edge_id)
            if previous is not None:
                states[edge_id] = previous.model_copy(update={"valid_to": event.event_time})
            removed.add(edge_id)
            continue

        if edge_id in removed and event.event_type != "create":
            continue

        attributes = dict(event.attributes)
        valid_from = attributes.pop("valid_from", event.event_time)
        weight = float(attributes.get("weight", 1.0))
        risk_score = float(attributes.get("risk_score", attributes.get("severity", 0.0)))
        existing = states.get(edge_id)
        if existing is not None and event.event_type in {"update", "decay"}:
            merged = dict(existing.attributes)
            merged.update(attributes)
            states[edge_id] = existing.model_copy(
                update={
                    "weight": weight,
                    "risk_score": max(0.0, min(1.0, risk_score)),
                    "confidence": event.confidence,
                    "attributes": merged,
                    "source": event.source,
                    "graph_version": graph_version,
                }
            )
        else:
            states[edge_id] = EdgeState(
                edge_id=edge_id,
                source_id=event.source_id,
                target_id=event.target_id,
                edge_type=event.edge_type,
                valid_from=valid_from,
                valid_to=None,
                weight=weight,
                confidence=event.confidence,
                risk_score=max(0.0, min(1.0, risk_score)),
                attributes=attributes,
                graph_version=graph_version,
                source=event.source,
            )

    return sorted(
        [state for state in states.values() if state.valid_to is None or state.valid_to <= as_of_time],
        key=lambda state: state.edge_id,
    )
