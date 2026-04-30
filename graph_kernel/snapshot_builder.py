from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha256

from graph_kernel.event_store import materialize_edge_states
from sra_core.contracts.domain import CanonicalEntity, EdgeEvent, EdgeState, GraphSnapshot


def graph_version_for(as_of_time: datetime, checksum: str) -> str:
    stamp = as_of_time.strftime("%Y%m%dT%H%M%SZ")
    return f"g_{stamp}_{checksum[:10]}"


def canonical_graph_payload(
    entities: list[CanonicalEntity],
    states: list[EdgeState],
    as_of_time: datetime,
) -> dict[str, object]:
    return {
        "as_of_time": as_of_time.isoformat(),
        "nodes": sorted(
            [
                {
                    "canonical_id": entity.canonical_id,
                    "entity_type": entity.entity_type,
                    "display_name": entity.display_name,
                    "country": entity.country,
                    "industry": entity.industry,
                }
                for entity in entities
            ],
            key=lambda item: item["canonical_id"],
        ),
        "edges": sorted(
            [
                {
                    "edge_id": state.edge_id,
                    "source_id": state.source_id,
                    "target_id": state.target_id,
                    "edge_type": state.edge_type,
                    "valid_from": state.valid_from.isoformat(),
                    "valid_to": state.valid_to.isoformat() if state.valid_to else None,
                    "weight": round(state.weight, 8),
                    "confidence": round(state.confidence, 8),
                    "risk_score": round(state.risk_score, 8),
                }
                for state in states
                if state.valid_from <= as_of_time and (state.valid_to is None or state.valid_to <= as_of_time)
            ],
            key=lambda item: item["edge_id"],
        ),
    }


def checksum_payload(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return sha256(encoded).hexdigest()


def build_graph_snapshot(
    entities: list[CanonicalEntity],
    edge_events: list[EdgeEvent],
    as_of_time: datetime,
    window_start: datetime,
) -> tuple[GraphSnapshot, list[EdgeState]]:
    provisional = "g_pending"
    states = materialize_edge_states(edge_events, as_of_time=as_of_time, graph_version=provisional)
    payload = canonical_graph_payload(entities, states, as_of_time)
    checksum = checksum_payload(payload)
    graph_version = graph_version_for(as_of_time, checksum)
    states = [state.model_copy(update={"graph_version": graph_version}) for state in states]
    payload = canonical_graph_payload(entities, states, as_of_time)
    checksum = checksum_payload(payload)
    snapshot = GraphSnapshot(
        snapshot_id=f"snapshot_{checksum[:16]}",
        graph_version=graph_version_for(as_of_time, checksum),
        as_of_time=as_of_time,
        window_start=window_start,
        window_end=as_of_time,
        node_count=len(entities),
        edge_count=len([state for state in states if state.valid_to is None]),
        checksum=checksum,
    )
    states = [state.model_copy(update={"graph_version": snapshot.graph_version}) for state in states]
    return snapshot, states
