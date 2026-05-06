from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, populate_by_name=True)


class VersionMetadata(StrictModel):
    graph_version: str
    feature_version: str
    label_version: str
    model_version: str
    as_of_time: datetime
    audit_ref: str | None = None
    lineage_ref: str | None = None
    data_mode: Literal["real", "synthetic", "mock"] = "real"
    freshness_status: Literal["fresh", "stale", "partial", "unavailable"] = "fresh"
    source_count: int = Field(default=0, ge=0)
    source_manifest_ref: str | None = None

    @field_validator("as_of_time")
    @classmethod
    def _aware_as_of_time(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class ApiError(StrictModel):
    code: str
    message: str
    field: str | None = None


class ApiSourceMetadata(StrictModel):
    name: str
    url: str | None = None
    lineage_ref: str | None = None
    license: str | None = None


class ApiEnvelope(StrictModel):
    request_id: str
    status: Literal["success", "error"]
    data: Any
    metadata: VersionMetadata
    warnings: list[str] = Field(default_factory=list)
    errors: list[ApiError] = Field(default_factory=list)
    mode: Literal["real", "synthetic", "mock"] = "real"
    source_status: Literal["fresh", "stale", "partial", "unavailable"] = "fresh"
    source: ApiSourceMetadata | None = None


class SourceRegistry(StrictModel):
    source_id: str
    source_name: str
    source_type: str
    license_type: str
    update_frequency: str
    reliability_score: float = Field(ge=0.0, le=1.0)
    owner: str
    created_at: datetime = Field(default_factory=utcnow)


class RawRecord(StrictModel):
    raw_id: str
    source_id: str
    source_record_id: str
    event_time: datetime
    ingest_time: datetime
    raw_payload: dict[str, Any]
    checksum: str
    license_tag: str

    @field_validator("event_time", "ingest_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class CanonicalEntity(StrictModel):
    canonical_id: str
    entity_type: str
    display_name: str
    country: str | None = None
    industry: str | None = None
    external_ids: dict[str, str] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @field_validator("created_at", "updated_at")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class EntityAlias(StrictModel):
    alias_id: str
    canonical_id: str
    alias_name: str
    source_id: str
    match_method: Literal["exact", "fuzzy", "embedding", "manual"]
    confidence: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utcnow)

    @field_validator("created_at")
    @classmethod
    def _aware_created(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class EventFact(StrictModel):
    event_id: str
    event_type: str
    event_time: datetime
    ingest_time: datetime
    location: str | None = None
    severity: float = Field(default=0.0, ge=0.0, le=1.0)
    source_id: str
    raw_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("event_time", "ingest_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)


class EdgeEvent(StrictModel):
    edge_event_id: str
    source_id: str
    target_id: str
    edge_type: str
    event_type: Literal["create", "update", "decay", "remove"]
    event_time: datetime
    published_time: datetime | None = None
    observed_time: datetime | None = None
    ingest_time: datetime
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    source: str

    @field_validator("event_time", "published_time", "observed_time", "ingest_time")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else value

    @model_validator(mode="after")
    def _time_order_consistent(self) -> EdgeEvent:
        if (
            self.published_time is not None
            and self.observed_time is not None
            and self.published_time > self.observed_time
        ):
            raise ValueError("published_time must be <= observed_time")
        if self.observed_time is not None and self.observed_time > self.ingest_time:
            raise ValueError("observed_time must be <= ingest_time")
        return self


class EdgeState(StrictModel):
    edge_id: str
    source_id: str
    target_id: str
    edge_type: str
    valid_from: datetime
    valid_to: datetime | None = None
    weight: float = Field(default=1.0, ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    attributes: dict[str, Any] = Field(default_factory=dict)
    graph_version: str
    source: str

    @field_validator("valid_from", "valid_to")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else value

    @model_validator(mode="after")
    def _valid_interval(self) -> EdgeState:
        if self.valid_to is not None and self.valid_from > self.valid_to:
            raise ValueError("valid_from must be <= valid_to")
        return self


class GraphSnapshot(StrictModel):
    snapshot_id: str
    graph_version: str
    as_of_time: datetime
    window_start: datetime
    window_end: datetime
    node_count: int = Field(ge=0)
    edge_count: int = Field(ge=0)
    checksum: str
    created_at: datetime = Field(default_factory=utcnow)

    @field_validator("as_of_time", "window_start", "window_end", "created_at")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _valid_window(self) -> GraphSnapshot:
        if self.window_start > self.window_end:
            raise ValueError("window_start must be <= window_end")
        if self.window_end > self.as_of_time:
            raise ValueError("window_end must be <= as_of_time")
        return self


class PathIndex(StrictModel):
    path_id: str
    source_id: str
    target_id: str
    meta_path: str
    node_sequence: list[str]
    edge_sequence: list[str]
    path_length: int = Field(ge=1)
    path_weight: float = Field(ge=0.0)
    path_risk: float = Field(ge=0.0, le=1.0)
    path_confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime
    valid_to: datetime | None = None

    @field_validator("valid_from", "valid_to")
    @classmethod
    def _aware_times(cls, value: datetime | None) -> datetime | None:
        return ensure_aware(value) if value is not None else value


class FeatureValue(StrictModel):
    feature_id: str
    entity_id: str
    entity_type: str
    feature_name: str
    feature_value: float
    feature_time: datetime
    as_of_time: datetime
    feature_version: str
    source_snapshot: str

    @field_validator("feature_time", "as_of_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _point_in_time_safe(self) -> FeatureValue:
        if self.feature_time > self.as_of_time:
            raise ValueError("feature_time must be <= as_of_time")
        return self


class LabelValue(StrictModel):
    label_id: str
    target_id: str
    target_type: str
    label_name: str
    prediction_time: datetime
    horizon: int = Field(gt=0)
    label_time: datetime
    label_value: float
    confidence: float = Field(ge=0.0, le=1.0)
    label_version: str
    label_source: str

    @field_validator("prediction_time", "label_time")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _future_label(self) -> LabelValue:
        if self.label_time < self.prediction_time:
            raise ValueError("label_time must be >= prediction_time")
        return self


class PredictionResult(StrictModel):
    prediction_id: str
    target_id: str
    target_type: str
    prediction_time: datetime
    horizon: int = Field(gt=0)
    risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: Literal["low", "medium", "high", "critical"]
    confidence_low: float = Field(ge=0.0, le=1.0)
    confidence_high: float = Field(ge=0.0, le=1.0)
    model_version: str
    graph_version: str
    feature_version: str
    label_version: str
    created_at: datetime = Field(default_factory=utcnow)
    top_drivers: list[str] = Field(default_factory=list)
    top_paths: list[str] = Field(default_factory=list)

    @field_validator("prediction_time", "created_at")
    @classmethod
    def _aware_times(cls, value: datetime) -> datetime:
        return ensure_aware(value)

    @model_validator(mode="after")
    def _valid_interval(self) -> PredictionResult:
        if self.confidence_low > self.confidence_high:
            raise ValueError("confidence_low must be <= confidence_high")
        return self


class PredictionRequest(StrictModel):
    target_id: str | None = None
    horizon: int = Field(default=30, gt=0, le=365)
    include_explanations: bool = True
    parameters: dict[str, Any] = Field(default_factory=dict)


class ExplanationRequest(StrictModel):
    prediction_id: str | None = None
    target_id: str | None = None
    include_paths: bool = True


class SimulationRequest(StrictModel):
    intervention_type: Literal[
        "remove_node",
        "remove_edge",
        "close_port",
        "increase_tariff",
        "replace_supplier",
        "increase_inventory_buffer",
    ] = "close_port"
    target_id: str = "port_kaohsiung"
    parameters: dict[str, Any] = Field(default_factory=dict)


class ReportRequest(StrictModel):
    report_type: Literal["brief", "entity", "portfolio", "simulation"] = "brief"
    target_id: str | None = None
    include_sections: list[str] = Field(default_factory=list)


class ExplanationPath(StrictModel):
    explanation_id: str
    prediction_id: str
    path_id: str
    node_sequence: list[str]
    edge_sequence: list[str]
    contribution_score: float
    causal_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class InterventionRun(StrictModel):
    run_id: str
    intervention_type: Literal[
        "remove_node",
        "remove_edge",
        "close_port",
        "increase_tariff",
        "replace_supplier",
        "increase_inventory_buffer",
    ]
    target_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    base_graph_version: str
    counterfactual_graph_version: str
    risk_delta: float
    created_by: str
    created_at: datetime = Field(default_factory=utcnow)

    @field_validator("created_at")
    @classmethod
    def _aware_created(cls, value: datetime) -> datetime:
        return ensure_aware(value)
