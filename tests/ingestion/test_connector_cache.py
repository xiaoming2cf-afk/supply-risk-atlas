from __future__ import annotations

import json

from sra_core.ingestion.connectors.base import ConnectorRequest, PublicEvidenceConnector
from sra_core.ingestion.connectors.cache import ConnectorMetadataCache


def test_connector_cache_stores_metadata_without_raw_payload(tmp_path) -> None:
    connector = PublicEvidenceConnector("test_source")
    result = connector.fetch(
        ConnectorRequest(
            source_id="test_source",
            source_url="https://example.org/source",
            provenance_url="https://example.org/provenance",
            license_ref="https://example.org/terms",
            mode="fixture",
            fixture_payload={"raw": {"body": "must-not-store"}, "summary": "ok"},
        )
    )
    cache = ConnectorMetadataCache(tmp_path)

    path = cache.put(result)
    loaded = cache.get("test_source", result.payload_hash)
    rendered = json.dumps(loaded, sort_keys=True).lower()

    assert path.exists()
    assert loaded is not None
    assert loaded["payload_hash"] == result.payload_hash
    assert "must-not-store" not in rendered
    assert "body" not in rendered
    assert '"payload":' not in rendered
