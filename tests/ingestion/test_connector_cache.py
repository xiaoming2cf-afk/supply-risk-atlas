from __future__ import annotations

from sra_core.ingestion.connectors.cache import ConnectorCache, ConnectorCachePolicy
from sra_core.ingestion.connectors.result import ConnectorFetchResult, ConnectorRecord


def test_connector_cache_writes_metadata_without_records_by_default(tmp_path) -> None:
    record = ConnectorRecord.from_payload(
        source_id="sec_edgar_lite",
        source_record_id="sample-1",
        payload={"summary": "bounded public filing summary"},
        provenance_url="https://www.sec.gov/example",
        license_or_terms_ref="https://www.sec.gov/os/accessing-edgar-data",
    )
    result = ConnectorFetchResult(
        source_id="sec_edgar_lite",
        mode="fixture",
        status="ok",
        records=(record,),
    )
    cache = ConnectorCache(tmp_path)
    key = cache.key_for(source_id="sec_edgar_lite", params={"cik": "0001046179"})

    path = cache.write_metadata(key=key, result=result)
    cached = cache.read_metadata(key=key)

    assert path is not None
    assert cached is not None
    assert cached["records"] == []
    assert cached["record_count"] == 1
    assert "raw_payload" not in path.read_text(encoding="utf-8")


def test_connector_cache_can_keep_sanitized_record_metadata_when_enabled(tmp_path) -> None:
    record = ConnectorRecord.from_payload(
        source_id="gdelt_semiconductor_lite",
        source_record_id="gdelt-1",
        payload={"title": "Semiconductor supply-chain event"},
        provenance_url="https://www.gdeltproject.org/",
        license_or_terms_ref="https://www.gdeltproject.org/about.html",
    )
    result = ConnectorFetchResult(
        source_id="gdelt_semiconductor_lite",
        mode="fixture",
        status="ok",
        records=(record,),
    )
    cache = ConnectorCache(tmp_path, ConnectorCachePolicy(store_records=True))
    key = cache.key_for(source_id="gdelt_semiconductor_lite", params={"q": "chip"})

    cache.write_metadata(key=key, result=result)
    cached = cache.read_metadata(key=key)

    assert cached is not None
    assert cached["records"][0]["payload_stored"] is False
    assert cached["records"][0]["payload_hash"]
    assert "Semiconductor supply-chain event" in cached["records"][0]["payload_summary"]

