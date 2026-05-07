from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal, Self

from pydantic import Field, field_validator, model_validator

from sra_core.contracts.domain import StrictModel, ensure_aware, utcnow


AllowedUse = Literal[
    "research",
    "commercial_risk_analysis",
    "internal_operations",
    "redistribution",
    "derived_products",
]

UpdateCadence = Literal[
    "real_time",
    "15_minutes",
    "hourly",
    "daily",
    "nightly",
    "three_times_daily",
    "weekly",
    "monthly",
    "irregular",
]

PayloadFormat = Literal["json", "csv", "xml", "zip", "txt"]


def canonical_payload_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def payload_checksum(payload: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_payload_bytes(payload)).hexdigest()


class SourceLicense(StrictModel):
    name: str
    url: str
    allowed_use: list[AllowedUse]
    requires_attribution: bool
    redistribution_allowed: bool
    commercial_use_allowed: bool
    restrictions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _commercial_policy_consistent(self) -> Self:
        has_commercial_use = "commercial_risk_analysis" in self.allowed_use
        if has_commercial_use and not self.commercial_use_allowed:
            raise ValueError("commercial_risk_analysis requires commercial_use_allowed=true")
        if "redistribution" in self.allowed_use and not self.redistribution_allowed:
            raise ValueError("redistribution allowed_use requires redistribution_allowed=true")
        return self


class SourceEndpoint(StrictModel):
    name: str
    url: str
    format: PayloadFormat
    auth: Literal["none"] = "none"
    notes: str | None = None


class SourceRegistryEntry(StrictModel):
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    source_name: str
    publisher: str
    homepage_url: str
    description: str
    public_no_key: Literal[True] = True
    license: SourceLicense
    endpoints: list[SourceEndpoint]
    update_cadence: UpdateCadence
    freshness_sla_hours: int = Field(gt=0)
    allowed_entities: list[str] = Field(default_factory=list)
    allowed_events: list[str] = Field(default_factory=list)
    owner: str = "data-ingestion"
    enabled: bool = True


class SourceRegistry(StrictModel):
    registry_version: str
    generated_at: datetime = Field(default_factory=utcnow)
    sources: list[SourceRegistryEntry]

    @field_validator("generated_at")
    @classmethod
    def _aware_generated_at(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _unique_source_ids(self) -> Self:
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source_id values must be unique")
        return self


class RawRecord(StrictModel):
    raw_id: str
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    source_record_id: str
    event_time: datetime
    published_time: datetime
    observed_time: datetime
    ingest_time: datetime
    payload_format: PayloadFormat
    raw_payload: dict[str, Any]
    checksum: str = Field(pattern=r"^[a-f0-9]{64}$")
    license_name: str
    allowed_use: list[AllowedUse]
    attribution: str | None = None
    schema_version: str = "raw-record-v1"

    @field_validator("event_time", "published_time", "observed_time", "ingest_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _time_order_consistent(self) -> Self:
        if self.published_time > self.observed_time:
            raise ValueError("published_time must be <= observed_time")
        if self.observed_time > self.ingest_time:
            raise ValueError("observed_time must be <= ingest_time")
        return self

    @model_validator(mode="after")
    def _checksum_matches_payload(self) -> Self:
        expected = payload_checksum(self.raw_payload)
        if self.checksum != expected:
            raise ValueError("checksum must equal sha256 of canonical raw_payload")
        return self

    @classmethod
    def from_payload(
        cls,
        *,
        source_id: str,
        source_record_id: str,
        event_time: datetime,
        ingest_time: datetime,
        payload_format: PayloadFormat,
        raw_payload: dict[str, Any],
        license_name: str,
        allowed_use: list[AllowedUse],
        published_time: datetime | None = None,
        observed_time: datetime | None = None,
        attribution: str | None = None,
    ) -> RawRecord:
        checksum = payload_checksum(raw_payload)
        raw_id = f"raw:{source_id}:{source_record_id}:{checksum[:16]}"
        return cls(
            raw_id=raw_id,
            source_id=source_id,
            source_record_id=source_record_id,
            event_time=event_time,
            published_time=published_time or event_time,
            observed_time=observed_time or ingest_time,
            ingest_time=ingest_time,
            payload_format=payload_format,
            raw_payload=raw_payload,
            checksum=checksum,
            license_name=license_name,
            allowed_use=allowed_use,
            attribution=attribution,
        )


class SourceReference(StrictModel):
    source_id: str
    raw_id: str
    source_record_id: str


class GeoPoint(StrictModel):
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class SilverEntity(StrictModel):
    entity_id: str
    entity_type: Literal[
        "company",
        "legal_entity",
        "facility",
        "port",
        "airport",
        "country",
        "sanctioned_party",
        "vessel",
        "commodity",
        "location",
        "data_source",
        "data_category",
        "dataset",
        "indicator",
        "industry",
        "schema_field",
        "license_policy",
        "coverage_area",
        "source_release",
        "observation_series",
    ]
    display_name: str = Field(alias="displayName")
    source_refs: list[SourceReference]
    country_code: str | None = Field(default=None, alias="countryCode", min_length=2, max_length=2)
    geo_id: str | None = Field(default=None, alias="geoId")
    geo_level: str | None = Field(default=None, alias="geoLevel")
    province_code: str | None = Field(default=None, alias="provinceCode", min_length=2, max_length=2)
    parent_geo_id: str | None = Field(default=None, alias="parentGeoId")
    source_country_code: str | None = Field(default=None, alias="sourceCountryCode", min_length=2, max_length=2)
    external_ids: dict[str, str] = Field(default_factory=dict)
    geo: GeoPoint | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    updated_at: datetime = Field(default_factory=utcnow)
    schema_version: str = "silver-entity-v1"

    @field_validator("updated_at")
    @classmethod
    def _aware_updated_at(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class SilverEventEntityRef(StrictModel):
    entity_id: str
    role: str


class SilverEvent(StrictModel):
    event_id: str
    event_type: str
    source_refs: list[SourceReference]
    event_time: datetime
    published_time: datetime
    observed_time: datetime
    ingest_time: datetime
    entities: list[SilverEventEntityRef] = Field(default_factory=list)
    location: GeoPoint | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    schema_version: str = "silver-event-v1"

    @field_validator("event_time", "published_time", "observed_time", "ingest_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _time_order_consistent(self) -> Self:
        if self.published_time > self.observed_time:
            raise ValueError("published_time must be <= observed_time")
        if self.observed_time > self.ingest_time:
            raise ValueError("observed_time must be <= ingest_time")
        return self


class GoldEdgeEvent(StrictModel):
    edge_event_id: str
    source_entity_id: str
    target_entity_id: str
    edge_type: str
    event_type: Literal["create", "update", "decay", "remove"]
    event_time: datetime
    published_time: datetime
    observed_time: datetime
    ingest_time: datetime
    source_refs: list[SourceReference]
    evidence_event_ids: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    schema_version: str = "gold-edge-event-v1"

    @field_validator("event_time", "published_time", "observed_time", "ingest_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _time_order_consistent(self) -> Self:
        if self.published_time > self.observed_time:
            raise ValueError("published_time must be <= observed_time")
        if self.observed_time > self.ingest_time:
            raise ValueError("observed_time must be <= ingest_time")
        return self


class SourceManifest(StrictModel):
    manifest_id: str
    source_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    checked_at: datetime
    latest_record_time: datetime | None = None
    status: Literal["ok", "stale", "empty", "error"]
    raw_record_count: int = Field(ge=0)
    raw_ids: list[str] = Field(default_factory=list)
    raw_checksums: list[str] = Field(default_factory=list)
    manifest_checksum: str = Field(pattern=r"^[a-f0-9]{64}$")
    freshness_sla_hours: int = Field(gt=0)
    is_fresh: bool
    message: str | None = None
    schema_version: str = "source-manifest-v1"

    @field_validator("checked_at", "latest_record_time")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else value

    @model_validator(mode="after")
    def _freshness_consistent(self) -> Self:
        if self.raw_record_count != len(self.raw_ids):
            raise ValueError("raw_record_count must equal len(raw_ids)")
        if len(self.raw_ids) != len(self.raw_checksums):
            raise ValueError("raw_ids and raw_checksums must have same length")
        if self.latest_record_time is not None and self.latest_record_time > self.checked_at:
            raise ValueError("latest_record_time must be <= checked_at")
        expected = self.compute_manifest_checksum(
            source_id=self.source_id,
            checked_at=self.checked_at,
            latest_record_time=self.latest_record_time,
            raw_ids=self.raw_ids,
            raw_checksums=self.raw_checksums,
            freshness_sla_hours=self.freshness_sla_hours,
        )
        if self.manifest_checksum != expected:
            raise ValueError("manifest_checksum must match manifest content")
        expected_fresh = self.latest_record_time is not None and (
            self.checked_at - self.latest_record_time
        ).total_seconds() <= self.freshness_sla_hours * 3600
        if self.is_fresh != expected_fresh:
            raise ValueError("is_fresh must match latest_record_time and freshness_sla_hours")
        return self

    @staticmethod
    def compute_manifest_checksum(
        *,
        source_id: str,
        checked_at: datetime,
        latest_record_time: datetime | None,
        raw_ids: list[str],
        raw_checksums: list[str],
        freshness_sla_hours: int,
    ) -> str:
        payload = {
            "source_id": source_id,
            "checked_at": ensure_aware(checked_at).isoformat(),
            "latest_record_time": ensure_aware(latest_record_time).isoformat()
            if latest_record_time is not None
            else None,
            "raw_ids": sorted(raw_ids),
            "raw_checksums": sorted(raw_checksums),
            "freshness_sla_hours": freshness_sla_hours,
        }
        return payload_checksum(payload)

    @classmethod
    def from_records(
        cls,
        *,
        source_id: str,
        records: list[RawRecord],
        checked_at: datetime,
        freshness_sla_hours: int,
        status: Literal["ok", "stale", "empty", "error"] | None = None,
        message: str | None = None,
    ) -> SourceManifest:
        checked_at = ensure_aware(checked_at)
        latest_record_time = max((record.observed_time for record in records), default=None)
        raw_ids = [record.raw_id for record in records]
        raw_checksums = [record.checksum for record in records]
        is_fresh = latest_record_time is not None and (
            checked_at - latest_record_time
        ).total_seconds() <= freshness_sla_hours * 3600
        resolved_status = status or ("empty" if not records else "ok" if is_fresh else "stale")
        manifest_checksum = cls.compute_manifest_checksum(
            source_id=source_id,
            checked_at=checked_at,
            latest_record_time=latest_record_time,
            raw_ids=raw_ids,
            raw_checksums=raw_checksums,
            freshness_sla_hours=freshness_sla_hours,
        )
        return cls(
            manifest_id=f"manifest:{source_id}:{manifest_checksum[:16]}",
            source_id=source_id,
            checked_at=checked_at,
            latest_record_time=latest_record_time,
            status=resolved_status,
            raw_record_count=len(records),
            raw_ids=raw_ids,
            raw_checksums=raw_checksums,
            manifest_checksum=manifest_checksum,
            freshness_sla_hours=freshness_sla_hours,
            is_fresh=is_fresh,
            message=message,
        )
