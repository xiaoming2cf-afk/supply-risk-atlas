from __future__ import annotations

import json
from typing import Any

from services.api.runtime.run_store import sanitized_run_copy
from services.api.storage.models import RawRecordIndex, SourceManifestRecord, SourceStatusRecord
from services.api.storage.sqlite_store import SQLiteStore


class ManifestStore:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store
        self.store.initialize()

    def put_manifest(self, record: SourceManifestRecord) -> None:
        self.store.execute(
            """
            INSERT OR REPLACE INTO source_manifest
            (source_manifest_id, created_at, graph_version, source_count, checksum, status, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.source_manifest_id,
                record.created_at,
                record.graph_version,
                record.source_count,
                record.checksum,
                record.status,
                _json(record.metadata),
            ),
        )

    def get_manifest(self, source_manifest_id: str) -> dict[str, Any] | None:
        row = self.store.fetch_one(
            "SELECT * FROM source_manifest WHERE source_manifest_id = ?",
            (source_manifest_id,),
        )
        if row is None:
            return None
        return {**row, "metadata": json.loads(row["metadata_json"])}

    def put_source_status(self, record: SourceStatusRecord) -> None:
        self.store.execute(
            """
            INSERT OR REPLACE INTO source_status
            (source_id, publisher, enabled_by_default, connector_status, license_or_terms_summary,
             last_checked_at, freshness_sla_hours, status, warnings_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.source_id,
                record.publisher,
                1 if record.enabled_by_default else 0,
                record.connector_status,
                record.license_or_terms_summary,
                record.last_checked_at,
                record.freshness_sla_hours,
                record.status,
                _json(record.warnings),
            ),
        )

    def list_source_status(self) -> list[dict[str, Any]]:
        rows = self.store.fetch_all("SELECT * FROM source_status ORDER BY source_id")
        return [{**row, "warnings": json.loads(row["warnings_json"])} for row in rows]

    def put_raw_record_index(self, record: RawRecordIndex) -> None:
        self.store.execute(
            """
            INSERT OR REPLACE INTO raw_record_index
            (raw_record_id, source_id, source_record_id, retrieved_at, as_of_time, payload_hash,
             raw_payload_summary, provenance_url, license_or_terms_ref, raw_payload_stored, raw_payload_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.raw_record_id,
                record.source_id,
                record.source_record_id,
                record.retrieved_at,
                record.as_of_time,
                record.payload_hash,
                record.raw_payload_summary,
                record.provenance_url,
                record.license_or_terms_ref,
                1 if record.raw_payload_stored else 0,
                record.raw_payload_path,
            ),
        )

    def list_raw_record_index(self, source_id: str | None = None) -> list[dict[str, Any]]:
        if source_id:
            return self.store.fetch_all(
                "SELECT * FROM raw_record_index WHERE source_id = ? ORDER BY raw_record_id",
                (source_id,),
            )
        return self.store.fetch_all("SELECT * FROM raw_record_index ORDER BY source_id, raw_record_id")


def _json(value: Any) -> str:
    return json.dumps(sanitized_run_copy(value), sort_keys=True)
