from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from pathlib import Path

from sra_core.api.envelope import ApiEnvelope
from sra_core.contracts.domain import EdgeState, PredictionResult
from sra_core.contracts.data import RawRecord, SourceManifest
from sra_core.ingestion.connectors import ConnectorBatch, SecEdgarConnector, connector_for_source
from sra_core.ingestion.registry import load_source_registry


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def test_public_connectors_only_emit_raw_records_and_manifest() -> None:
    payload = json.loads((FIXTURE_DIR / "sec_companyfacts_sample.json").read_text(encoding="utf-8"))
    batch = SecEdgarConnector().ingest_sample(
        source_record_id="0000320193-26-000010",
        event_time=datetime(2026, 1, 30, tzinfo=timezone.utc),
        ingest_time=datetime(2026, 1, 31, tzinfo=timezone.utc),
        raw_payload=payload,
    )

    assert isinstance(batch, ConnectorBatch)
    assert all(isinstance(record, RawRecord) for record in batch.records)
    assert isinstance(batch.manifest, SourceManifest)
    assert not isinstance(batch.manifest, EdgeState | ApiEnvelope | PredictionResult)

    signature = inspect.signature(SecEdgarConnector.ingest_sample)
    assert signature.return_annotation == "ConnectorBatch"


def test_all_registered_sources_have_public_connector_boundary() -> None:
    registry = load_source_registry()
    for source in registry.sources:
        connector = connector_for_source(source.source_id)
        assert connector.source_id == source.source_id


def test_ingest_and_freshness_manifest_are_idempotent_offline() -> None:
    payload = json.loads((FIXTURE_DIR / "sec_companyfacts_sample.json").read_text(encoding="utf-8"))
    kwargs = {
        "source_record_id": "0000320193-26-000010",
        "event_time": datetime(2026, 1, 30, tzinfo=timezone.utc),
        "ingest_time": datetime(2026, 1, 31, tzinfo=timezone.utc),
        "raw_payload": payload,
    }

    first = SecEdgarConnector().ingest_sample(**kwargs)
    second = SecEdgarConnector().ingest_sample(**kwargs)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.manifest.is_fresh is True
    assert first.manifest.status == "ok"


def test_stale_freshness_manifest_is_deterministic() -> None:
    record = RawRecord.from_payload(
        source_id="world_bank",
        source_record_id="NY.GDP.MKTP.CD:US:2024",
        event_time=datetime(2024, 12, 31, tzinfo=timezone.utc),
        published_time=datetime(2025, 1, 31, tzinfo=timezone.utc),
        observed_time=datetime(2025, 1, 31, tzinfo=timezone.utc),
        ingest_time=datetime(2026, 5, 2, tzinfo=timezone.utc),
        payload_format="json",
        raw_payload={"indicator": "NY.GDP.MKTP.CD", "country": "US", "date": "2024"},
        license_name="CC BY 4.0",
        allowed_use=["research", "commercial_risk_analysis", "redistribution"],
        attribution="World Bank",
    )
    checked_at = datetime(2026, 5, 2, tzinfo=timezone.utc)

    first = SourceManifest.from_records(
        source_id="world_bank",
        records=[record],
        checked_at=checked_at,
        freshness_sla_hours=24,
    )
    second = SourceManifest.from_records(
        source_id="world_bank",
        records=[record],
        checked_at=checked_at,
        freshness_sla_hours=24,
    )

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.is_fresh is False
    assert first.status == "stale"


def test_synthetic_data_is_fixture_only() -> None:
    synthetic = json.loads((FIXTURE_DIR / "synthetic_raw_record.json").read_text(encoding="utf-8"))
    registry_source_ids = {source.source_id for source in load_source_registry().sources}

    assert synthetic["fixture_type"] == "synthetic_only"
    assert synthetic["source_id"] not in registry_source_ids
