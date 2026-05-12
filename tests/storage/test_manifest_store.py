from __future__ import annotations

import json

from services.api.storage.manifest_store import ManifestStore
from services.api.storage.models import RawRecordIndex, SourceManifestRecord
from services.api.storage.sqlite_store import SQLiteStore


def test_manifest_store_records_manifest_and_raw_index_without_payload(tmp_path) -> None:
    store = ManifestStore(SQLiteStore(tmp_path / "manifest.db"))

    store.put_manifest(
        SourceManifestRecord(
            source_manifest_id="manifest_test",
            graph_version="graph_test",
            as_of_time="2026-05-01T00:00:00Z",
            source_status="partial",
            license_terms=[{"source_id": "sec_edgar", "terms_url": "https://www.sec.gov/os/accessing-edgar-data"}],
            manifest={
                "source_manifest_id": "manifest_test",
                "raw_payload": {"secret": "must-not-store"},
                "sources": [{"source_id": "sec_edgar"}],
            },
        )
    )
    store.put_raw_record_index(
        RawRecordIndex(
            raw_id="raw:sec:1",
            source_id="sec_edgar",
            source_record_id="0001",
            payload_hash="a" * 64,
            raw_payload_summary="10-K risk factor summary only",
            provenance_url="https://www.sec.gov/Archives/example",
            license_or_terms_ref="https://www.sec.gov/os/accessing-edgar-data",
            retrieved_at="2026-05-01T00:00:00Z",
            as_of_time="2026-05-01T00:00:00Z",
        )
    )

    manifest = store.get_manifest("manifest_test")
    raw_rows = store.list_raw_record_index("sec_edgar")
    rendered = json.dumps({"manifest": manifest, "raw_rows": raw_rows}, sort_keys=True).lower()

    assert manifest is not None
    assert manifest["graph_version"] == "graph_test"
    assert raw_rows[0]["payload_hash"] == "a" * 64
    assert raw_rows[0]["raw_payload_summary"] == "10-K risk factor summary only"
    assert "must-not-store" not in rendered
    assert "secret" not in rendered
    assert "raw_payload" not in json.dumps(manifest["manifest"], sort_keys=True).lower()
