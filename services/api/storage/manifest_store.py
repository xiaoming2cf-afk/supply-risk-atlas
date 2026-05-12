from __future__ import annotations

import json
from typing import Any

from services.api.runtime.run_store import sanitized_run_copy
from services.api.storage.models import RawRecordIndex, SourceManifestRecord
from services.api.storage.sqlite_store import SQLiteStore


class ManifestStore:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store
        self.store.initialize()

    def put_manifest(self, record: SourceManifestRecord) -> None:
        clean_manifest = sanitized_run_copy(record.manifest)
        self.store.execute(
            """
            INSERT OR REPLACE INTO source_manifest
            (source_manifest_id, graph_version, as_of_time, source_status, license_terms_json, manifest_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.source_manifest_id,
                record.graph_version,
                record.as_of_time,
                record.source_status,
                json.dumps(sanitized_run_copy(record.license_terms), sort_keys=True),
                json.dumps(clean_manifest, sort_keys=True),
            ),
        )

    def get_manifest(self, source_manifest_id: str) -> dict[str, Any] | None:
        row = self.store.fetch_one(
            "SELECT * FROM source_manifest WHERE source_manifest_id = ?",
            (source_manifest_id,),
        )
        if row is None:
            return None
        return {
            **row,
            "license_terms": json.loads(row["license_terms_json"]),
            "manifest": json.loads(row["manifest_json"]),
        }

    def put_raw_record_index(self, record: RawRecordIndex) -> None:
        self.store.execute(
            """
            INSERT OR REPLACE INTO raw_record_index
            (raw_id, source_id, source_record_id, payload_hash, raw_payload_summary, provenance_url,
             license_or_terms_ref, retrieved_at, as_of_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.raw_id,
                record.source_id,
                record.source_record_id,
                record.payload_hash,
                record.raw_payload_summary,
                record.provenance_url,
                record.license_or_terms_ref,
                record.retrieved_at,
                record.as_of_time,
            ),
        )

    def list_raw_record_index(self, source_id: str | None = None) -> list[dict[str, Any]]:
        if source_id:
            return self.store.fetch_all(
                "SELECT * FROM raw_record_index WHERE source_id = ? ORDER BY raw_id",
                (source_id,),
            )
        return self.store.fetch_all("SELECT * FROM raw_record_index ORDER BY source_id, raw_id")

