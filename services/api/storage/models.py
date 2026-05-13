from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceManifestRecord:
    source_manifest_id: str
    created_at: str
    graph_version: str | None
    source_count: int
    checksum: str
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SourceStatusRecord:
    source_id: str
    publisher: str
    enabled_by_default: bool
    connector_status: str
    license_or_terms_summary: str
    last_checked_at: str | None
    freshness_sla_hours: int | None
    status: str
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RawRecordIndex:
    raw_record_id: str
    source_id: str
    source_record_id: str
    retrieved_at: str
    as_of_time: str
    payload_hash: str
    raw_payload_summary: str
    provenance_url: str
    license_or_terms_ref: str
    raw_payload_stored: bool = False
    raw_payload_path: str | None = None


@dataclass(frozen=True)
class StoredRunRecord:
    run_id: str
    run_type: str
    created_at: str
    status: str
    graph_version: str | None
    source_manifest_id: str | None
    request_hash: str | None
    summary: dict[str, Any]
    warnings: list[str]
    evidence_refs: list[str]
    versions: dict[str, Any]


@dataclass(frozen=True)
class StoredReportRecord:
    report_id: str
    report_run_id: str | None
    created_at: str
    format: str
    graph_version: str | None
    source_manifest_id: str | None
    report_json: dict[str, Any] | None
    report_markdown: str | None
    content_hash: str
    warnings: list[str]
