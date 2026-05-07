from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

import yaml

from graph_kernel.path_index import build_path_index
from graph_kernel.snapshot_builder import build_graph_snapshot, checksum_payload
from ml.datasets.builder import DatasetSample, build_dataset
from ml.models.baseline import BaselineRiskModel
from sra_core.contracts.data import GoldEdgeEvent, RawRecord, SilverEntity, SilverEvent, SourceManifest, SourceReference
from sra_core.contracts.domain import (
    CanonicalEntity,
    EdgeEvent,
    EdgeState,
    ExplanationPath,
    FeatureValue,
    GraphSnapshot,
    PredictionResult,
    SourceRegistry,
    VersionMetadata,
)
from sra_core.ingestion.connectors import connector_for_source
from sra_core.ingestion.bulk_public import load_promoted_catalog, load_promoted_manifest
from sra_core.ingestion.registry import load_source_registry
from sra_core.feature_factory import compute_features
from sra_core.label_factory import label_quality_report


PUBLIC_REAL_AS_OF_TIME = datetime(2026, 5, 2, tzinfo=timezone.utc)
PUBLIC_REAL_WINDOW_START = datetime(2026, 4, 1, tzinfo=timezone.utc)


@dataclass(frozen=True)
class SourceFreshness:
    source_id: str
    status: str
    last_successful_ingest: datetime
    max_stale_minutes: int
    record_count: int
    checksum: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "status": self.status,
            "last_successful_ingest": self.last_successful_ingest.isoformat(),
            "max_stale_minutes": self.max_stale_minutes,
            "record_count": self.record_count,
            "checksum": self.checksum,
        }


@dataclass(frozen=True)
class PublicRealDataset:
    sources: list[SourceRegistry]
    freshness: list[SourceFreshness]
    raw_records: list[RawRecord]
    source_manifests: list[SourceManifest]
    silver_entities: list[SilverEntity]
    silver_events: list[SilverEvent]
    gold_edge_events: list[GoldEdgeEvent]
    entities: list[CanonicalEntity]
    edge_events: list[EdgeEvent]
    source_manifest_ref: str
    source_manifest_checksum: str
    catalog_source: str
    promoted_manifest: dict[str, Any] | None = None


@dataclass(frozen=True)
class RealPipelineResult:
    real: PublicRealDataset
    snapshot: GraphSnapshot
    edge_states: list[EdgeState]
    features: list[FeatureValue]
    labels: list[object]
    samples: list[DatasetSample]
    predictions: list[PredictionResult]
    explanations: list[ExplanationPath]
    label_quality: dict[str, float | int]


def _utc(month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(2026, month, day, hour, minute, tzinfo=timezone.utc)


def _event_id(source: str, source_id: str, target_id: str, edge_type: str) -> str:
    digest = sha256(f"{source}|{source_id}|{target_id}|{edge_type}".encode("utf-8")).hexdigest()[:12]
    return f"real_edge_event_{digest}"


def _checksum(value: Any) -> str:
    return checksum_payload({"value": value})


def _public_real_node_catalog_path() -> Path:
    return Path(__file__).resolve().parents[3] / "configs" / "sources" / "public_real_node_catalog.yaml"


def _load_public_real_node_catalog(path: str | Path | None = None) -> dict[str, Any]:
    if path is not None:
        payload = _read_catalog_file(Path(path))
    else:
        env_catalog_path = os.environ.get("SUPPLY_RISK_REAL_CATALOG_PATH")
        if env_catalog_path:
            payload = _read_catalog_file(Path(env_catalog_path))
        else:
            payload = load_promoted_catalog()
            if payload is None:
                payload = _read_catalog_file(_public_real_node_catalog_path())
    if not isinstance(payload, dict):
        raise ValueError("public real node catalog must be a mapping")
    return _merge_missing_builtin_sources(payload)


def _read_catalog_file(catalog_path: Path) -> dict[str, Any]:
    with catalog_path.open("r", encoding="utf-8") as handle:
        if catalog_path.suffix.lower() == ".json":
            return json.load(handle)
        return yaml.safe_load(handle)


def _merge_missing_builtin_sources(catalog: dict[str, Any]) -> dict[str, Any]:
    configured_sources = {entry.source_id for entry in load_source_registry().sources}
    catalog_sources = {
        entity.get("source_id")
        for entity in catalog.get("entities", [])
        if isinstance(entity, dict)
    } | {
        edge.get("source")
        for edge in catalog.get("edges", [])
        if isinstance(edge, dict)
    }
    missing_sources = configured_sources - {source for source in catalog_sources if source}
    if not missing_sources:
        return catalog

    builtin = _read_catalog_file(_public_real_node_catalog_path())
    merged_entities = list(catalog.get("entities", []))
    merged_edges = list(catalog.get("edges", []))
    entity_ids = {
        entity["canonical_id"]
        for entity in merged_entities
        if isinstance(entity, dict) and "canonical_id" in entity
    }
    for entity in builtin.get("entities", []):
        if not isinstance(entity, dict) or entity.get("source_id") not in missing_sources:
            continue
        if entity["canonical_id"] in entity_ids:
            continue
        merged_entities.append(entity)
        entity_ids.add(entity["canonical_id"])
    edge_keys = {
        (edge.get("source"), edge.get("source_id"), edge.get("target_id"), edge.get("edge_type"))
        for edge in merged_edges
        if isinstance(edge, dict)
    }
    for edge in builtin.get("edges", []):
        if not isinstance(edge, dict) or edge.get("source") not in missing_sources:
            continue
        if edge.get("source_id") not in entity_ids or edge.get("target_id") not in entity_ids:
            continue
        key = (edge.get("source"), edge.get("source_id"), edge.get("target_id"), edge.get("edge_type"))
        if key in edge_keys:
            continue
        merged_edges.append(edge)
        edge_keys.add(key)
    return {
        **catalog,
        "catalog_version": f"{catalog.get('catalog_version', 'public-real')}-merged-{checksum_payload({'sources': sorted(missing_sources)})[:8]}",
        "entities": merged_entities,
        "edges": merged_edges,
    }


def _catalog_source() -> tuple[str, dict[str, Any] | None]:
    env_catalog_path = os.environ.get("SUPPLY_RISK_REAL_CATALOG_PATH")
    if env_catalog_path:
        return "override", None
    promoted_manifest = load_promoted_manifest()
    if promoted_manifest is not None and load_promoted_catalog() is not None:
        return "promoted", promoted_manifest
    return "builtin_partial", None


def _catalog_records_by_source(catalog: dict[str, Any]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    records: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for entity in catalog.get("entities", []):
        source_id = entity["source_id"]
        records.setdefault(source_id, {"entities": [], "edges": []})["entities"].append(
            {
                "canonical_id": entity["canonical_id"],
                "entity_type": entity["entity_type"],
                "display_name": entity["display_name"],
                "external_ids": entity.get("external_ids", {}),
            }
        )
    for edge in catalog.get("edges", []):
        source_id = edge["source"]
        records.setdefault(source_id, {"entities": [], "edges": []})["edges"].append(
            {
                "source_id": edge["source_id"],
                "target_id": edge["target_id"],
                "edge_type": edge["edge_type"],
            }
        )
    return records


def _catalog_entities(
    catalog: dict[str, Any],
    as_of_time: datetime,
) -> tuple[list[CanonicalEntity], dict[str, str]]:
    entities: list[CanonicalEntity] = []
    source_by_entity: dict[str, str] = {}
    seen: set[str] = set()
    for item in catalog.get("entities", []):
        canonical_id = item["canonical_id"]
        if canonical_id in seen:
            raise ValueError(f"duplicate catalog entity {canonical_id}")
        seen.add(canonical_id)
        source_by_entity[canonical_id] = item["source_id"]
        entities.append(
            CanonicalEntity(
                canonical_id=canonical_id,
                entity_type=item["entity_type"],
                display_name=item["display_name"],
                country=item.get("country"),
                industry=item.get("industry"),
                external_ids={
                    key: str(value)
                    for key, value in (item.get("external_ids") or {}).items()
                    if value is not None
                },
                confidence=float(item["confidence"]),
                created_at=as_of_time - timedelta(days=30),
                updated_at=as_of_time - timedelta(hours=2),
            )
        )
    return entities, source_by_entity


def _catalog_edge_events(
    catalog: dict[str, Any],
    source_manifest_ref: str,
) -> list[EdgeEvent]:
    edge_events: list[EdgeEvent] = []
    entity_ids = {item["canonical_id"] for item in catalog.get("entities", [])}
    for item in catalog.get("edges", []):
        source_id = item["source_id"]
        target_id = item["target_id"]
        if source_id not in entity_ids or target_id not in entity_ids:
            raise ValueError(f"catalog edge references unknown endpoint: {source_id}->{target_id}")
        event_time = _utc(4, int(item.get("day", 2)))
        attributes = dict(item.get("attributes") or {})
        edge_events.append(
            EdgeEvent(
                edge_event_id=_event_id(item["source"], source_id, target_id, item["edge_type"]),
                source_id=source_id,
                target_id=target_id,
                edge_type=item["edge_type"],
                event_type=item.get("event_type", "create"),
                event_time=event_time,
                published_time=event_time + timedelta(hours=2),
                observed_time=event_time + timedelta(hours=6),
                ingest_time=event_time + timedelta(hours=6),
                attributes={
                    "valid_from": event_time,
                    "source_manifest_ref": source_manifest_ref,
                    **attributes,
                },
                confidence=float(item["confidence"]),
                source=item["source"],
            )
        )
    return edge_events


def _ingest_public_real_raw_records(as_of_time: datetime) -> dict[str, Any]:
    catalog = _load_public_real_node_catalog()
    catalog_records_by_source = _catalog_records_by_source(catalog)
    source_payloads: dict[str, dict[str, Any]] = {
        "sec_edgar": {
            "source_record_id": "sec:submissions:0000320193",
            "event_time": _utc(4, 30, 12),
            "payload_format": "json",
            "raw_payload": {
                "cik": "0000320193",
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "source_url": "https://data.sec.gov/submissions/CIK0000320193.json",
            },
        },
        "gleif": {
            "source_record_id": "gleif:lei:semiconductor-public-sample",
            "event_time": _utc(4, 30, 10),
            "payload_format": "json",
            "raw_payload": {
                "entities": [
                    "Taiwan Semiconductor Manufacturing Company Limited",
                    "ASML Holding N.V.",
                    "Samsung Electronics Co., Ltd.",
                ],
                "source_url": "https://api.gleif.org/api/v1/lei-records",
            },
        },
        "gdelt": {
            "source_record_id": "gdelt:event:red-sea-semiconductor-logistics",
            "event_time": _utc(4, 25, 6),
            "payload_format": "json",
            "raw_payload": {
                "theme": "shipping_disruption",
                "query": "semiconductor logistics Red Sea disruption",
                "source_url": "https://www.gdeltproject.org/",
            },
        },
        "world_bank": {
            "source_record_id": "world_bank:indicator:logistics-context",
            "event_time": _utc(4, 30, 0),
            "payload_format": "json",
            "raw_payload": {
                "indicator": "trade_logistics_context",
                "countries": ["US", "TW", "NL", "KR"],
                "source_url": "https://api.worldbank.org/v2/",
            },
        },
        "ofac": {
            "source_record_id": "ofac:sanctions:semiconductor-policy-context",
            "event_time": _utc(5, 1, 9),
            "payload_format": "json",
            "raw_payload": {
                "list": "sanctions_list_service",
                "policy_context": "export_controls_and_sanctions_monitoring",
                "source_url": "https://ofac.treasury.gov/sanctions-list-service",
            },
        },
        "ourairports": {
            "source_record_id": "ourairports:airport-reference:tw-nl-us-kr",
            "event_time": _utc(5, 1, 8),
            "payload_format": "csv",
            "raw_payload": {
                "dataset": "airports.csv",
                "countries": ["TW", "NL", "US", "KR"],
                "source_url": "https://ourairports.com/data/",
            },
        },
        "nga_world_port_index": {
            "source_record_id": "nga_wpi:ports:kaohsiung-rotterdam",
            "event_time": _utc(5, 1, 7),
            "payload_format": "zip",
            "raw_payload": {
                "ports": ["Port of Kaohsiung", "Port of Rotterdam"],
                "source_url": "https://msi.nga.mil/Publications/WPI",
            },
        },
        "usgs_earthquakes": {
            "source_record_id": "usgs:earthquakes:m4-5-month",
            "event_time": _utc(5, 1, 6),
            "payload_format": "json",
            "raw_payload": {
                "feed": "M4.5+ earthquakes past month",
                "hazard_context": "recent seismic events that can transmit risk into ports, airports, and regional supply corridors",
                "source_url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson",
            },
        },
    }
    for source_id, records in catalog_records_by_source.items():
        if source_id not in source_payloads:
            continue
        source_payloads[source_id]["raw_payload"]["catalog_version"] = catalog["catalog_version"]
        source_payloads[source_id]["raw_payload"]["catalog_entities"] = records["entities"]
        source_payloads[source_id]["raw_payload"]["catalog_edges"] = records["edges"]
    batches = {}
    for source_id, payload in source_payloads.items():
        connector = connector_for_source(source_id)
        event_time = payload["event_time"]
        batches[source_id] = connector.ingest_sample(
            source_record_id=payload["source_record_id"],
            event_time=event_time,
            published_time=event_time + timedelta(hours=1),
            observed_time=as_of_time - timedelta(hours=2),
            ingest_time=as_of_time,
            raw_payload=payload["raw_payload"],
            payload_format=payload["payload_format"],
        )
    return batches


def public_real_sources(as_of_time: datetime = PUBLIC_REAL_AS_OF_TIME) -> list[SourceRegistry]:
    registry = load_source_registry()
    created_at = as_of_time - timedelta(days=14)
    reliability_by_source = {
        "sec_edgar": 0.95,
        "gleif": 0.96,
        "gdelt": 0.82,
        "world_bank": 0.94,
        "ofac": 0.98,
        "ourairports": 0.88,
        "nga_world_port_index": 0.9,
        "usgs_earthquakes": 0.93,
    }
    return [
        SourceRegistry(
            source_id=entry.source_id,
            source_name=entry.source_name,
            source_type=entry.endpoints[0].name if entry.endpoints else entry.update_cadence,
            license_type=entry.license.name,
            update_frequency=entry.update_cadence,
            reliability_score=reliability_by_source.get(entry.source_id, 0.8),
            owner=entry.owner,
            created_at=created_at,
        )
        for entry in registry.sources
    ]


def build_public_real_dataset(as_of_time: datetime = PUBLIC_REAL_AS_OF_TIME) -> PublicRealDataset:
    catalog = _load_public_real_node_catalog()
    catalog_source, promoted_manifest = _catalog_source()
    sources = public_real_sources(as_of_time)
    raw_batches = _ingest_public_real_raw_records(as_of_time)
    raw_records = [record for batch in raw_batches.values() for record in batch.records]
    source_manifests = [batch.manifest for batch in raw_batches.values()]
    source_ids = sorted(raw_batches)
    source_manifest_checksum = _checksum(
        {
            "sources": source_ids,
            "as_of_time": as_of_time.isoformat(),
            "raw_checksums": sorted(
                checksum for batch in raw_batches.values() for checksum in batch.manifest.raw_checksums
            ),
            "manifest_checksums": sorted(batch.manifest.manifest_checksum for batch in raw_batches.values()),
        }
    )
    source_manifest_ref = f"manifest_public_real_{source_manifest_checksum[:12]}"
    freshness = sorted(
        [
        SourceFreshness(
            source_id=batch.manifest.source_id,
            status="fresh" if batch.manifest.is_fresh else batch.manifest.status,
            last_successful_ingest=batch.manifest.checked_at,
            max_stale_minutes=batch.manifest.freshness_sla_hours * 60,
            record_count=batch.manifest.raw_record_count,
            checksum=batch.manifest.manifest_checksum,
        )
        for batch in raw_batches.values()
        ],
        key=lambda item: item.source_id,
    )
    source_ref_by_id = {
        source_id: SourceReference(
            source_id=batch.records[0].source_id,
            raw_id=batch.records[0].raw_id,
            source_record_id=batch.records[0].source_record_id,
        )
        for source_id, batch in raw_batches.items()
        if batch.records
    }
    entities = [
        CanonicalEntity(
            canonical_id="firm_apple",
            entity_type="firm",
            display_name="Apple Inc.",
            country="US",
            industry="Consumer electronics",
            external_ids={"sec_cik": "0000320193", "ticker": "AAPL"},
            confidence=0.99,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=2),
        ),
        CanonicalEntity(
            canonical_id="firm_tsmc",
            entity_type="firm",
            display_name="Taiwan Semiconductor Manufacturing Company Limited",
            country="TW",
            industry="Semiconductors",
            external_ids={"ticker": "2330.TW"},
            confidence=0.96,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=3),
        ),
        CanonicalEntity(
            canonical_id="firm_asml",
            entity_type="firm",
            display_name="ASML Holding N.V.",
            country="NL",
            industry="Semiconductor equipment",
            external_ids={"ticker": "ASML"},
            confidence=0.96,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=4),
        ),
        CanonicalEntity(
            canonical_id="firm_samsung_electronics",
            entity_type="firm",
            display_name="Samsung Electronics Co., Ltd.",
            country="KR",
            industry="Electronics and semiconductors",
            external_ids={"ticker": "005930.KS"},
            confidence=0.95,
            created_at=as_of_time - timedelta(days=30),
            updated_at=as_of_time - timedelta(hours=4),
        ),
        CanonicalEntity(
            canonical_id="country_us",
            entity_type="country",
            display_name="United States",
            country="US",
            industry=None,
            external_ids={"iso2": "US"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="country_tw",
            entity_type="country",
            display_name="Taiwan",
            country="TW",
            industry=None,
            external_ids={"iso2": "TW"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="country_nl",
            entity_type="country",
            display_name="Netherlands",
            country="NL",
            industry=None,
            external_ids={"iso2": "NL"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="country_kr",
            entity_type="country",
            display_name="South Korea",
            country="KR",
            industry=None,
            external_ids={"iso2": "KR"},
            confidence=1.0,
        ),
        CanonicalEntity(
            canonical_id="port_kaohsiung",
            entity_type="port",
            display_name="Port of Kaohsiung",
            country="TW",
            industry="Maritime logistics",
            external_ids={"source": "NGA World Port Index"},
            confidence=0.92,
        ),
        CanonicalEntity(
            canonical_id="port_rotterdam",
            entity_type="port",
            display_name="Port of Rotterdam",
            country="NL",
            industry="Maritime logistics",
            external_ids={"source": "NGA World Port Index"},
            confidence=0.93,
        ),
        CanonicalEntity(
            canonical_id="product_advanced_semiconductors",
            entity_type="product",
            display_name="Advanced semiconductors",
            country=None,
            industry="HS 8542",
            external_ids={"hs_code": "8542"},
            confidence=0.9,
        ),
        CanonicalEntity(
            canonical_id="policy_ofac_sanctions",
            entity_type="policy",
            display_name="OFAC sanctions exposure",
            country="US",
            industry="Sanctions",
            external_ids={"source": "OFAC Sanctions List Service"},
            confidence=0.98,
        ),
        CanonicalEntity(
            canonical_id="risk_event_red_sea_disruption",
            entity_type="risk_event",
            display_name="Red Sea shipping disruption",
            country=None,
            industry="Logistics risk",
            external_ids={"source": "GDELT"},
            confidence=0.82,
        ),
        CanonicalEntity(
            canonical_id="text_gdelt_semiconductor_logistics",
            entity_type="text_artifact",
            display_name="GDELT semiconductor logistics signal",
            country=None,
            industry="News evidence",
            external_ids={"source": "GDELT"},
            confidence=0.78,
        ),
    ]
    entities, source_by_entity = _catalog_entities(catalog, as_of_time)

    def edge(
        source_id: str,
        target_id: str,
        edge_type: str,
        source: str,
        event_time: datetime,
        confidence: float,
        **attributes: Any,
    ) -> EdgeEvent:
        return EdgeEvent(
            edge_event_id=_event_id(source, source_id, target_id, edge_type),
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            event_type="create",
            event_time=event_time,
            published_time=event_time + timedelta(hours=2),
            observed_time=event_time + timedelta(hours=6),
            ingest_time=event_time + timedelta(hours=6),
            attributes={
                "valid_from": event_time,
                "source_manifest_ref": source_manifest_ref,
                **attributes,
            },
            confidence=confidence,
            source=source,
        )

    edge_events = [
        edge("firm_apple", "country_us", "located_in", "sec_edgar", _utc(4, 2), 0.98, weight=1.0),
        edge("firm_tsmc", "country_tw", "located_in", "gleif", _utc(4, 2), 0.96, weight=1.0),
        edge("firm_asml", "country_nl", "located_in", "gleif", _utc(4, 2), 0.96, weight=1.0),
        edge("firm_samsung_electronics", "country_kr", "located_in", "gleif", _utc(4, 2), 0.95, weight=1.0),
        edge(
            "firm_tsmc",
            "product_advanced_semiconductors",
            "produces",
            "gleif",
            _utc(4, 3),
            0.88,
            weight=0.91,
            risk_score=0.31,
        ),
        edge(
            "firm_samsung_electronics",
            "product_advanced_semiconductors",
            "produces",
            "gleif",
            _utc(4, 3),
            0.84,
            weight=0.78,
            risk_score=0.24,
        ),
        edge(
            "firm_tsmc",
            "port_kaohsiung",
            "ships_through",
            "nga_world_port_index",
            _utc(4, 5),
            0.82,
            weight=0.74,
            risk_score=0.42,
            route_dependency=0.58,
        ),
        edge(
            "port_kaohsiung",
            "port_rotterdam",
            "route_connects",
            "nga_world_port_index",
            _utc(4, 5),
            0.78,
            weight=0.62,
            risk_score=0.46,
        ),
        edge(
            "policy_ofac_sanctions",
            "product_advanced_semiconductors",
            "policy_targets",
            "ofac",
            _utc(4, 9),
            0.91,
            severity=0.53,
            risk_score=0.53,
        ),
        edge(
            "risk_event_red_sea_disruption",
            "firm_apple",
            "event_affects",
            "gdelt",
            _utc(4, 18),
            0.72,
            severity=0.61,
            risk_score=0.61,
        ),
        edge(
            "risk_event_red_sea_disruption",
            "firm_asml",
            "event_affects",
            "gdelt",
            _utc(4, 18),
            0.69,
            severity=0.49,
            risk_score=0.49,
        ),
        edge(
            "text_gdelt_semiconductor_logistics",
            "firm_tsmc",
            "co_mentions",
            "gdelt",
            _utc(4, 25),
            0.76,
            sentiment=-0.34,
            mention_count=17,
            risk_score=0.57,
        ),
        edge(
            "firm_tsmc",
            "firm_apple",
            "risk_transmits_to",
            "gdelt",
            _utc(4, 26),
            0.68,
            path_risk=0.64,
            lag_days=14,
            risk_score=0.64,
        ),
    ]
    edge_events = _catalog_edge_events(catalog, source_manifest_ref)
    silver_entities = _build_silver_entities(entities, source_ref_by_id, source_by_entity)
    silver_events = _build_silver_events(source_ref_by_id, as_of_time)
    gold_edge_events = [
        GoldEdgeEvent(
            edge_event_id=edge.edge_event_id,
            source_entity_id=edge.source_id,
            target_entity_id=edge.target_id,
            edge_type=edge.edge_type,
            event_type=edge.event_type,
            event_time=edge.event_time,
            published_time=edge.published_time or edge.event_time,
            observed_time=edge.observed_time or edge.ingest_time,
            ingest_time=edge.ingest_time,
            source_refs=[source_ref_by_id[edge.source]],
            evidence_event_ids=[event.event_id for event in silver_events if event.source_refs[0].source_id == edge.source],
            attributes=edge.attributes,
            confidence=edge.confidence,
        )
        for edge in edge_events
    ]
    return PublicRealDataset(
        sources=sources,
        freshness=freshness,
        raw_records=raw_records,
        source_manifests=source_manifests,
        silver_entities=silver_entities,
        silver_events=silver_events,
        gold_edge_events=gold_edge_events,
        entities=entities,
        edge_events=edge_events,
        source_manifest_ref=source_manifest_ref,
        source_manifest_checksum=source_manifest_checksum,
        catalog_source=catalog_source,
        promoted_manifest=promoted_manifest,
    )


def _build_silver_entities(
    entities: list[CanonicalEntity],
    source_ref_by_id: dict[str, SourceReference],
    source_by_entity: dict[str, str],
) -> list[SilverEntity]:
    entity_type_map = {
        "firm": "company",
        "legal_entity": "legal_entity",
        "country": "country",
        "port": "port",
        "airport": "airport",
        "product": "commodity",
        "policy": "sanctioned_party",
        "risk_event": "location",
        "text_artifact": "location",
        "data_source": "data_source",
        "data_category": "data_category",
        "dataset": "dataset",
        "indicator": "indicator",
        "industry": "industry",
        "schema_field": "schema_field",
        "license_policy": "license_policy",
        "coverage_area": "coverage_area",
        "source_release": "source_release",
        "observation_series": "observation_series",
    }
    silver_entities: list[SilverEntity] = []
    for entity in entities:
        source_id = source_by_entity[entity.canonical_id]
        silver_entities.append(
            SilverEntity(
                entity_id=entity.canonical_id,
                entity_type=entity_type_map[entity.entity_type],
                display_name=entity.display_name,
                source_refs=[source_ref_by_id[source_id]],
                country_code=entity.country,
                external_ids=entity.external_ids,
                attributes={"domain_entity_type": entity.entity_type, "industry": entity.industry},
                confidence=entity.confidence,
                updated_at=entity.updated_at,
            )
        )
    return silver_entities


def _build_silver_events(
    source_ref_by_id: dict[str, SourceReference],
    as_of_time: datetime,
) -> list[SilverEvent]:
    return [
        SilverEvent(
            event_id="silver_event_gdelt_red_sea_disruption",
            event_type="disruption",
            source_refs=[source_ref_by_id["gdelt"]],
            event_time=_utc(4, 25, 6),
            published_time=_utc(4, 25, 8),
            observed_time=as_of_time - timedelta(hours=2),
            ingest_time=as_of_time,
            entities=[
                {"entity_id": "risk_event_red_sea_disruption", "role": "event"},
                {"entity_id": "firm_apple", "role": "affected"},
            ],
            attributes={"source_manifest_stage": "silver"},
            confidence=0.72,
        ),
        SilverEvent(
            event_id="silver_event_ofac_policy_context",
            event_type="sanctions_update",
            source_refs=[source_ref_by_id["ofac"]],
            event_time=_utc(5, 1, 9),
            published_time=_utc(5, 1, 10),
            observed_time=as_of_time - timedelta(hours=2),
            ingest_time=as_of_time,
            entities=[
                {"entity_id": "policy_ofac_sanctions", "role": "policy"},
                {"entity_id": "product_advanced_semiconductors", "role": "target"},
            ],
            attributes={"source_manifest_stage": "silver"},
            confidence=0.91,
        ),
    ]


def _catalog_cache_key() -> str:
    env_catalog_path = os.environ.get("SUPPLY_RISK_REAL_CATALOG_PATH")
    if env_catalog_path:
        path = Path(env_catalog_path)
        try:
            stat = path.stat()
            return f"env:{path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}"
        except OSError:
            return f"env:{env_catalog_path}:missing"
    promoted_manifest = load_promoted_manifest()
    if promoted_manifest:
        return f"promoted:{promoted_manifest.get('checksum') or promoted_manifest.get('catalog_version')}"
    return "builtin"


def run_public_real_pipeline(
    as_of_time: datetime = PUBLIC_REAL_AS_OF_TIME,
    window_start: datetime = PUBLIC_REAL_WINDOW_START,
) -> RealPipelineResult:
    return _run_public_real_pipeline_cached(as_of_time, window_start, _catalog_cache_key())


@lru_cache(maxsize=8)
def _run_public_real_pipeline_cached(
    as_of_time: datetime,
    window_start: datetime,
    catalog_cache_key: str,
) -> RealPipelineResult:
    real = build_public_real_dataset(as_of_time=as_of_time)
    snapshot, edge_states = build_graph_snapshot(
        real.entities,
        real.edge_events,
        as_of_time=as_of_time,
        window_start=window_start,
    )
    features = compute_features(real.entities, edge_states, snapshot)
    labels: list[object] = []
    paths = build_path_index(edge_states)
    samples = build_dataset(
        prediction_time=as_of_time,
        graph_version=snapshot.graph_version,
        feature_values=features,
        labels=[],
        edge_states=edge_states,
        paths=paths,
    )
    model = BaselineRiskModel()
    predictions = [model.predict(sample, created_at=as_of_time + timedelta(minutes=1)) for sample in samples]
    explanations = [
        ExplanationPath(
            explanation_id=f"explain_{prediction.prediction_id.removeprefix('pred_')}",
            prediction_id=prediction.prediction_id,
            path_id=prediction.top_paths[0] if prediction.top_paths else "path_public_real",
            node_sequence=[],
            edge_sequence=[],
            contribution_score=prediction.risk_score,
            causal_score=min(1.0, prediction.risk_score + 0.08),
            confidence=0.68,
            evidence=[
                "public_no_key_source_manifest",
                real.source_manifest_ref,
                "point_in_time_public_graph",
            ],
        )
        for prediction in predictions
    ]
    return RealPipelineResult(
        real=real,
        snapshot=snapshot,
        edge_states=edge_states,
        features=features,
        labels=labels,
        samples=samples,
        predictions=predictions,
        explanations=explanations,
        label_quality=label_quality_report([]),
    )


def real_metadata(result: RealPipelineResult) -> VersionMetadata:
    first_feature_version = result.features[0].feature_version if result.features else "f_none"
    first_model_version = result.predictions[0].model_version if result.predictions else "model_none"
    promoted_status = (result.real.promoted_manifest or {}).get("source_status")
    freshness_status = (
        "partial"
        if result.real.catalog_source != "promoted"
        or promoted_status not in {None, "fresh"}
        or any(item.status != "fresh" for item in result.real.freshness)
        else "fresh"
    )
    return VersionMetadata(
        graph_version=result.snapshot.graph_version,
        feature_version=first_feature_version,
        label_version="l_public_real_unlabeled",
        model_version=first_model_version,
        as_of_time=result.snapshot.as_of_time,
        audit_ref=f"audit_{result.real.source_manifest_ref}",
        lineage_ref=result.real.source_manifest_checksum,
        data_mode="real",
        freshness_status=freshness_status,
        source_count=len(result.real.sources),
        source_manifest_ref=result.real.source_manifest_ref,
    )
