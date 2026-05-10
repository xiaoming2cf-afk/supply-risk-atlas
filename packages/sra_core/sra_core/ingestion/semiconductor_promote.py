from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from sra_core.contracts.semiconductor import (
    DEFAULT_SEMIRISK_AS_OF_TIME,
    SemiconductorEntity,
    SemiconductorEvent,
    SemiconductorMarketIndicator,
    SemiconductorPromotionResult,
    SemiconductorRawRecord,
    SemiconductorSourceId,
    SemiriskEdge,
    SemiriskNode,
    parse_semirisk_time,
    payload_hash,
)
from sra_core.ingestion.connectors.base_semiconductor import load_semiconductor_registry
from sra_core.ingestion.connectors.eto_supply_chain import EtoSupplyChainConnector
from sra_core.ingestion.connectors.gdelt_semiconductor_events import (
    GdeltSemiconductorEventsConnector,
)
from sra_core.ingestion.connectors.gta_export_controls import GtaExportControlsConnector
from sra_core.ingestion.connectors.wsts_billings import WstsBillingsConnector


SEMICONDUCTOR_SOURCE_IDS: tuple[SemiconductorSourceId, ...] = (
    "eto_cset_advanced_semiconductor_supply_chain",
    "wsts_historical_billings",
    "global_trade_alert_semiconductor_export_controls",
    "gdelt_semiconductor_events",
)


def default_as_of_time() -> datetime:
    return parse_semirisk_time(DEFAULT_SEMIRISK_AS_OF_TIME)


def replay_semiconductor_fixtures(
    *,
    fixture_dir: str | Path | None = None,
    registry_path: str | Path | None = None,
) -> list[SemiconductorRawRecord]:
    connectors = [
        EtoSupplyChainConnector(),
        WstsBillingsConnector(),
        GtaExportControlsConnector(),
        GdeltSemiconductorEventsConnector(),
    ]
    records = [
        record
        for connector in connectors
        for record in connector.replay(fixture_dir=fixture_dir, registry_path=registry_path)
    ]
    return sorted(records, key=lambda item: (item.source_id, item.source_record_id))


def promote_semiconductor_fixtures(
    *,
    fixture_dir: str | Path | None = None,
    registry_path: str | Path | None = None,
    as_of_time: datetime | str = DEFAULT_SEMIRISK_AS_OF_TIME,
) -> SemiconductorPromotionResult:
    as_of = parse_semirisk_time(as_of_time)
    records = replay_semiconductor_fixtures(fixture_dir=fixture_dir, registry_path=registry_path)
    registry = load_semiconductor_registry(registry_path)
    registry_by_source = {source["source_id"]: source for source in registry.get("sources", [])}
    source_manifest = _source_manifest(records, registry_by_source, as_of)

    entity_by_id: dict[str, SemiconductorEntity] = {}
    events: dict[str, SemiconductorEvent] = {}
    indicators: dict[str, SemiconductorMarketIndicator] = {}
    edge_by_id: dict[str, SemiriskEdge] = {}

    for record in records:
        _promote_record(
            record=record,
            as_of_time=as_of,
            entity_by_id=entity_by_id,
            events=events,
            indicators=indicators,
            edge_by_id=edge_by_id,
        )

    nodes = [_node_from_entity(entity) for entity in sorted(entity_by_id.values(), key=lambda item: item.entity_id)]
    edges = sorted(edge_by_id.values(), key=lambda item: item.edge_id)
    return SemiconductorPromotionResult(
        as_of_time=as_of,
        source_manifest_id=source_manifest["source_manifest_id"],
        raw_records=records,
        silver_entities=sorted(entity_by_id.values(), key=lambda item: item.entity_id),
        silver_events=sorted(events.values(), key=lambda item: item.event_id),
        market_indicators=sorted(indicators.values(), key=lambda item: item.indicator_id),
        graph_nodes=nodes,
        graph_edges=edges,
        source_manifest=source_manifest,
    )


def _promote_record(
    *,
    record: SemiconductorRawRecord,
    as_of_time: datetime,
    entity_by_id: dict[str, SemiconductorEntity],
    events: dict[str, SemiconductorEvent],
    indicators: dict[str, SemiconductorMarketIndicator],
    edge_by_id: dict[str, SemiriskEdge],
) -> None:
    ref = record.source_ref()
    valid_from = record.source_published_at or record.as_of_time
    payload = record.payload
    for row in payload.get("entities", []):
        entity = SemiconductorEntity(
            entity_id=row["node_id"],
            entity_type=row["node_type"],
            canonical_name=row["canonical_name"],
            aliases=list(row.get("aliases") or []),
            country_code=row.get("country_code"),
            sector_tags=list(row.get("sector_tags") or []),
            source_refs=[ref],
            confidence=float(row.get("confidence", 0.0)),
            valid_from=valid_from,
            valid_to=row.get("valid_to"),
            attributes=dict(row.get("attributes") or {}),
        )
        existing = entity_by_id.get(entity.entity_id)
        if existing is None:
            entity_by_id[entity.entity_id] = entity
        else:
            merged_refs = _unique_refs([*existing.source_refs, ref])
            entity_by_id[entity.entity_id] = existing.model_copy(update={"source_refs": merged_refs})

    for row in payload.get("events", []):
        event = SemiconductorEvent(
            event_id=row["event_id"],
            event_type=row["event_type"],
            canonical_name=row["canonical_name"],
            event_time=parse_semirisk_time(row["event_time"]),
            summary=row["summary"],
            affected_entity_ids=list(row.get("affected_entity_ids") or []),
            source_refs=[ref],
            confidence=float(row.get("confidence", 0.0)),
            valid_from=parse_semirisk_time(row["event_time"]),
            valid_to=row.get("valid_to"),
            attributes={"source_record_id": record.source_record_id},
        )
        events[event.event_id] = event

    for row in payload.get("market_indicators", []):
        indicator = SemiconductorMarketIndicator(
            indicator_id=row["indicator_id"],
            indicator_type=row["indicator_type"],
            canonical_name=row["canonical_name"],
            region=row["region"],
            period=row["period"],
            value=float(row["value"]),
            unit=row["unit"],
            source_refs=[ref],
            confidence=float(row.get("confidence", 0.0)),
            valid_from=valid_from,
            valid_to=row.get("valid_to"),
            attributes={"source_record_id": record.source_record_id},
        )
        indicators[indicator.indicator_id] = indicator

    for row in payload.get("edges", []):
        edge = SemiriskEdge(
            edge_id=row["edge_id"],
            source_node_id=row["source_node_id"],
            target_node_id=row["target_node_id"],
            edge_type=row["edge_type"],
            weight=float(row.get("weight", 1.0)),
            confidence=float(row.get("confidence", 0.0)),
            valid_from=valid_from,
            valid_to=row.get("valid_to"),
            provenance_refs=[ref],
            evidence_text_summary=row["evidence_text_summary"],
            attributes={
                **dict(row.get("attributes") or {}),
                "fixture_graph": True,
                "source_record_id": record.source_record_id,
                "as_of_time": as_of_time.isoformat(),
            },
        )
        existing = edge_by_id.get(edge.edge_id)
        if existing is None:
            edge_by_id[edge.edge_id] = edge
        else:
            merged_refs = _unique_refs([*existing.provenance_refs, ref])
            edge_by_id[edge.edge_id] = existing.model_copy(update={"provenance_refs": merged_refs})


def _node_from_entity(entity: SemiconductorEntity) -> SemiriskNode:
    return SemiriskNode(
        node_id=entity.entity_id,
        node_type=entity.entity_type,
        canonical_name=entity.canonical_name,
        attributes={
            **entity.attributes,
            "aliases": entity.aliases,
            "country_code": entity.country_code,
            "sector_tags": entity.sector_tags,
            "fixture_graph": True,
        },
        source_refs=entity.source_refs,
        confidence=entity.confidence,
        valid_from=entity.valid_from,
        valid_to=entity.valid_to,
    )


def _source_manifest(
    records: list[SemiconductorRawRecord],
    registry_by_source: dict[str, dict[str, Any]],
    as_of_time: datetime,
) -> dict[str, Any]:
    rows = []
    for source_id in SEMICONDUCTOR_SOURCE_IDS:
        source_records = [record for record in records if record.source_id == source_id]
        latest = max((record.source_published_at or record.as_of_time for record in source_records), default=None)
        freshness_sla_hours = int(registry_by_source.get(source_id, {}).get("freshness_sla_hours") or 1)
        stale = (
            latest is None
            or (as_of_time - latest).total_seconds() > freshness_sla_hours * 3600
        )
        rows.append(
            {
                "source_id": source_id,
                "record_count": len(source_records),
                "payload_hashes": sorted(record.payload_hash for record in source_records),
                "latest_source_published_at": latest.isoformat() if latest else None,
                "freshness_sla_hours": freshness_sla_hours,
                "status": "stale" if stale else "fresh",
            }
        )
    manifest_basis = {
        "as_of_time": as_of_time.isoformat(),
        "sources": rows,
    }
    manifest_id = f"semirisk_fixture_manifest_{payload_hash(manifest_basis)[:12]}"
    return {
        "source_manifest_id": manifest_id,
        "as_of_time": as_of_time.isoformat(),
        "fixture_graph": True,
        "record_count": len(records),
        "sources": rows,
        "stale_source_count": sum(1 for row in rows if row["status"] == "stale"),
        "manifest_hash": payload_hash(manifest_basis),
        "generated_at": as_of_time.isoformat(),
    }


def _unique_refs(refs):
    by_key = {
        (ref.source_id, ref.source_record_id, ref.payload_hash): ref
        for ref in refs
    }
    return [by_key[key] for key in sorted(by_key)]


def promotion_digest(promotion: SemiconductorPromotionResult) -> str:
    payload = {
        "source_manifest_id": promotion.source_manifest_id,
        "node_ids": [node.node_id for node in promotion.graph_nodes],
        "edge_ids": [edge.edge_id for edge in promotion.graph_edges],
        "raw_hashes": [record.payload_hash for record in promotion.raw_records],
    }
    return payload_hash(payload)
