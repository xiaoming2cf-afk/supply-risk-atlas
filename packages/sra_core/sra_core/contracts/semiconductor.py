from __future__ import annotations

import json
import re
from datetime import datetime
from hashlib import sha256
from typing import Any, Literal, Self

from pydantic import Field, PrivateAttr, field_validator, model_validator

from sra_core.contracts.domain import StrictModel, ensure_aware


DEFAULT_SEMIRISK_AS_OF_TIME = "2026-05-01T00:00:00Z"
SEMIRISK_ONTOLOGY_VERSION = "semiconductor_ontology_v0.1"
SEMIRISK_GRAPH_SCHEMA_VERSION = "semirisk_graph_snapshot_v0.1"

SemiconductorSourceId = Literal[
    "eto_cset_advanced_semiconductor_supply_chain",
    "wsts_historical_billings",
    "global_trade_alert_semiconductor_export_controls",
    "gdelt_semiconductor_events",
]

SemiconductorNodeType = Literal[
    "company",
    "country",
    "region",
    "facility",
    "process_stage",
    "equipment",
    "material",
    "chemical",
    "component",
    "product_grade",
    "technology_node",
    "policy_event",
    "risk_event",
    "market_indicator",
    "trade_flow",
    "route",
]

SemiconductorEdgeType = Literal[
    "participates_in",
    "located_in",
    "requires",
    "produces",
    "supplies",
    "depends_on",
    "substitutable_with",
    "restricted_by",
    "impacted_by",
    "exports_to",
    "imports_from",
    "routes_through",
    "correlated_with",
    "evidence_for",
]


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def payload_hash(payload: Any) -> str:
    return sha256(canonical_json_bytes(payload)).hexdigest()


def slug(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return re.sub(r"_+", "_", text) or "unknown"


def parse_semirisk_time(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return ensure_aware(value)
    return ensure_aware(datetime.fromisoformat(value.replace("Z", "+00:00")))


class SemiconductorSourceRef(StrictModel):
    source_id: SemiconductorSourceId
    source_record_id: str
    raw_id: str
    payload_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance_url: str
    retrieved_at: datetime
    as_of_time: datetime

    @field_validator("retrieved_at", "as_of_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class SemiconductorRawRecord(StrictModel):
    source_id: SemiconductorSourceId
    source_record_id: str
    retrieved_at: datetime
    source_published_at: datetime | None = None
    as_of_time: datetime
    payload_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    provenance_url: str
    raw_payload_summary: str
    license_or_terms_ref: str
    _payload: dict[str, Any] = PrivateAttr(default_factory=dict)

    @field_validator("retrieved_at", "source_published_at", "as_of_time")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else None

    @model_validator(mode="after")
    def _valid_times(self) -> Self:
        if self.source_published_at and self.source_published_at > self.retrieved_at:
            raise ValueError("source_published_at must be <= retrieved_at")
        return self

    @property
    def raw_id(self) -> str:
        return f"raw:{self.source_id}:{self.source_record_id}:{self.payload_hash[:16]}"

    @property
    def payload(self) -> dict[str, Any]:
        return dict(self._payload)

    def source_ref(self) -> SemiconductorSourceRef:
        return SemiconductorSourceRef(
            source_id=self.source_id,
            source_record_id=self.source_record_id,
            raw_id=self.raw_id,
            payload_hash=self.payload_hash,
            provenance_url=self.provenance_url,
            retrieved_at=self.retrieved_at,
            as_of_time=self.as_of_time,
        )

    @classmethod
    def from_fixture(
        cls,
        *,
        source_id: SemiconductorSourceId,
        row: dict[str, Any],
        license_or_terms_ref: str,
    ) -> SemiconductorRawRecord:
        row_hash = payload_hash({"source_id": source_id, "record": row})
        record = cls(
            source_id=source_id,
            source_record_id=str(row["source_record_id"]),
            retrieved_at=parse_semirisk_time(row["retrieved_at"]),
            source_published_at=parse_semirisk_time(row["source_published_at"])
            if row.get("source_published_at")
            else None,
            as_of_time=parse_semirisk_time(row["as_of_time"]),
            payload_hash=row_hash,
            provenance_url=str(row["provenance_url"]),
            raw_payload_summary=str(row["raw_payload_summary"]),
            license_or_terms_ref=license_or_terms_ref,
        )
        record._payload = dict(row)
        return record


class SemiconductorEntity(StrictModel):
    entity_id: str
    entity_type: SemiconductorNodeType
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    sector_tags: list[str] = Field(default_factory=list)
    source_refs: list[SemiconductorSourceRef] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime
    valid_to: datetime | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("country_code")
    @classmethod
    def _country_upper(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @field_validator("valid_from", "valid_to")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else None


class SemiconductorEvent(StrictModel):
    event_id: str
    event_type: Literal["policy_event", "risk_event"]
    canonical_name: str
    event_time: datetime
    summary: str
    affected_entity_ids: list[str] = Field(default_factory=list)
    source_refs: list[SemiconductorSourceRef] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime
    valid_to: datetime | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_time", "valid_from", "valid_to")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else None


class SemiconductorMarketIndicator(StrictModel):
    indicator_id: str
    indicator_type: Literal["market_indicator"]
    canonical_name: str
    region: str
    period: str
    value: float
    unit: str
    source_refs: list[SemiconductorSourceRef] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime
    valid_to: datetime | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("valid_from", "valid_to")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else None


class SemiriskNode(StrictModel):
    node_id: str
    node_type: SemiconductorNodeType
    canonical_name: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    source_refs: list[SemiconductorSourceRef] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime
    valid_to: datetime | None = None

    @field_validator("valid_from", "valid_to")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else None


class SemiriskEdge(StrictModel):
    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: SemiconductorEdgeType
    weight: float = Field(default=1.0, ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime
    valid_to: datetime | None = None
    provenance_refs: list[SemiconductorSourceRef] = Field(min_length=1)
    evidence_text_summary: str
    attributes: dict[str, Any] = Field(default_factory=dict)

    @field_validator("valid_from", "valid_to")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else None


class SemiconductorPromotionResult(StrictModel):
    schema_version: str = "semiconductor_promotion_v0.1"
    as_of_time: datetime
    source_manifest_id: str
    raw_records: list[SemiconductorRawRecord]
    silver_entities: list[SemiconductorEntity]
    silver_events: list[SemiconductorEvent]
    market_indicators: list[SemiconductorMarketIndicator]
    graph_nodes: list[SemiriskNode]
    graph_edges: list[SemiriskEdge]
    source_manifest: dict[str, Any]

    @field_validator("as_of_time")
    @classmethod
    def _aware_time(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class SemiriskGraphSnapshot(StrictModel):
    graph_version: str
    ontology_version: str
    source_manifest_id: str
    as_of_time: datetime
    node_count: int = Field(ge=0)
    edge_count: int = Field(ge=0)
    node_count_by_type: dict[str, int]
    edge_count_by_type: dict[str, int]
    missing_provenance_count: int = Field(ge=0)
    unresolved_entity_count: int = Field(ge=0)
    stale_source_count: int = Field(ge=0)
    nodes: list[SemiriskNode]
    edges: list[SemiriskEdge]
    quality_report: dict[str, Any]

    @field_validator("as_of_time")
    @classmethod
    def _aware_time(cls, value: datetime) -> datetime:
        return ensure_aware(value)
