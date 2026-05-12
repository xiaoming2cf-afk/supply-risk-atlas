from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RawRecordIndex:
    raw_id: str
    source_id: str
    source_record_id: str
    payload_hash: str
    raw_payload_summary: str
    provenance_url: str
    license_or_terms_ref: str
    retrieved_at: str
    as_of_time: str


@dataclass(frozen=True)
class SourceManifestRecord:
    source_manifest_id: str
    graph_version: str | None
    as_of_time: str | None
    source_status: str
    license_terms: list[dict[str, Any]] = field(default_factory=list)
    manifest: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StoredRunRecord:
    run_id: str
    run_type: str
    created_at: str
    graph_version: str | None
    source_manifest_id: str | None
    status: str
    summary: dict[str, Any]
    warnings: list[str]
    versions: dict[str, Any]


@dataclass(frozen=True)
class StoredReportRecord:
    report_id: str
    created_at: str
    graph_version: str | None
    source_manifest_id: str | None
    format: str
    report_json: dict[str, Any]
    report_markdown: str | None
    warnings: list[str]

