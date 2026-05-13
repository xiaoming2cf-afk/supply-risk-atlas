from __future__ import annotations

import json

from services.api.storage.manifest_store import ManifestStore
from services.api.storage.models import RawRecordIndex, SourceManifestRecord, SourceStatusRecord
from services.api.storage.sqlite_store import SQLiteStore


def test_manifest_store_records_manifest_source_status_and_raw_index_without_payload(tmp_path) -> None:
    store = ManifestStore(SQLiteStore(tmp_path / "manifest.db"))

    store.put_manifest(
        SourceManifestRecord(
            source_manifest_id="manifest_test",
            created_at="2026-05-01T00:00:00Z",
            graph_version="graph_test",
            source_count=1,
            checksum="checksum_test",
            status="partial",
            metadata={
                "source_manifest_id": "manifest_test",
                "raw_payload": {"secret": "must-not-store"},
                "sources": [{"source_id": "sec_edgar_lite"}],
            },
        )
    )
    store.put_source_status(
        SourceStatusRecord(
            source_id="sec_edgar_lite",
            publisher="SEC",
            enabled_by_default=False,
            connector_status="disabled_review_required",
            license_or_terms_summary="Public filing terms registered; raw filing bodies are excluded.",
            last_checked_at=None,
            freshness_sla_hours=72,
            status="disabled_review_required",
            warnings=["live_fetch_disabled"],
        )
    )
    store.put_raw_record_index(
        RawRecordIndex(
            raw_record_id="raw:sec:1",
            source_id="sec_edgar_lite",
            source_record_id="0001",
            retrieved_at="2026-05-01T00:00:00Z",
            as_of_time="2026-05-01T00:00:00Z",
            payload_hash="a" * 64,
            raw_payload_summary="10-K risk factor summary only",
            provenance_url="https://www.sec.gov/Archives/example",
            license_or_terms_ref="https://www.sec.gov/os/accessing-edgar-data",
        )
    )

    manifest = store.get_manifest("manifest_test")
    source_status = store.list_source_status()
    raw_rows = store.list_raw_record_index("sec_edgar_lite")
    rendered = json.dumps(
        {"manifest": manifest, "source_status": source_status, "raw_rows": raw_rows},
        sort_keys=True,
    ).lower()

    assert manifest is not None
    assert manifest["graph_version"] == "graph_test"
    assert source_status[0]["source_id"] == "sec_edgar_lite"
    assert raw_rows[0]["payload_hash"] == "a" * 64
    assert raw_rows[0]["raw_payload_stored"] == 0
    assert raw_rows[0]["raw_payload_path"] is None
    assert "must-not-store" not in rendered
    assert '"raw_payload":' not in rendered
    assert "secret" not in rendered
