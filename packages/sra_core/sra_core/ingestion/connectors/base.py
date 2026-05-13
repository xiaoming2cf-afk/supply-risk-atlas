from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from sra_core.ingestion.connectors.cache import ConnectorCachePolicy
from sra_core.ingestion.connectors.errors import ConnectorPayloadError
from sra_core.ingestion.connectors.rate_limit import InMemoryRateLimiter, RateLimitPolicy
from sra_core.ingestion.connectors.result import (
    ConnectorFetchResult,
    ConnectorRecord,
    sanitize_external_text,
    utc_now_iso,
)
from sra_core.sources import (
    license_policy_for_source,
    load_semiconductor_source_registry,
    source_status_for_source,
)


ConnectorMode = Literal["fixture", "dry_run", "live_disabled", "live"]


@dataclass(frozen=True)
class ConnectorConfig:
    mode: ConnectorMode = "live_disabled"
    max_records: int = 100
    timeout_seconds: float = 10.0
    fixture_path: str | Path | None = None
    rate_limit_policy: RateLimitPolicy = field(default_factory=RateLimitPolicy)
    cache_policy: ConnectorCachePolicy = field(default_factory=ConnectorCachePolicy)

    def validate(self) -> None:
        if self.max_records < 1 or self.max_records > 10_000:
            raise ConnectorPayloadError("max_records must be between 1 and 10000")
        if self.timeout_seconds <= 0 or self.timeout_seconds > 60:
            raise ConnectorPayloadError("timeout_seconds must be between 0 and 60")
        self.rate_limit_policy.validate()


class PublicEvidenceConnector:
    source_id: str

    def __init__(
        self,
        source_id: str,
        *,
        config: ConnectorConfig | None = None,
        rate_limiter: InMemoryRateLimiter | None = None,
    ) -> None:
        self.source_id = source_id
        self.config = config or ConnectorConfig()
        self.config.validate()
        self._rate_limiter = rate_limiter or InMemoryRateLimiter(self.config.rate_limit_policy)

    def fetch(self, params: dict[str, Any] | None = None) -> ConnectorFetchResult:
        params = params or {}
        if self.config.mode == "dry_run":
            return ConnectorFetchResult(
                source_id=self.source_id,
                mode=self.config.mode,
                status="dry_run",
                warnings=("dry_run_no_network_call",),
                metadata={"requested_params": self._sanitized_params(params)},
            )
        if self.config.mode == "fixture":
            return self.replay_fixture(self.config.fixture_path)
        if self.config.mode == "live_disabled":
            return ConnectorFetchResult.unavailable(
                source_id=self.source_id,
                mode=self.config.mode,
                reason="live_fetch_disabled_by_default",
            )
        self._rate_limiter.check(self.source_id)
        return self._fetch_live(params)

    def replay_fixture(self, fixture_path: str | Path | None) -> ConnectorFetchResult:
        if fixture_path is None:
            raise ConnectorPayloadError("fixture_path is required in fixture mode")
        payload = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
        records_payload = payload.get("records", payload if isinstance(payload, list) else [])
        if not isinstance(records_payload, list):
            raise ConnectorPayloadError("fixture payload must contain a records list")
        if len(records_payload) > self.config.max_records:
            raise ConnectorPayloadError("fixture record count exceeds connector max_records")
        source = load_semiconductor_source_registry().get(self.source_id)
        retrieved_at = str(payload.get("retrieved_at") or utc_now_iso())
        as_of_time = str(payload.get("as_of_time") or retrieved_at)
        records = tuple(
            ConnectorRecord.from_payload(
                source_id=self.source_id,
                source_record_id=str(row.get("source_record_id") or row.get("id") or index),
                payload=row,
                provenance_url=str(row.get("provenance_url") or row.get("source_url") or source.source_url),
                license_or_terms_ref=str(
                    row.get("license_or_terms_ref") or source.terms_url or source.source_url
                ),
                as_of_time=as_of_time,
                retrieved_at=retrieved_at,
                payload_summary=row.get("summary") or row.get("title") or row.get("name"),
                metadata=row,
            )
            for index, row in enumerate(records_payload)
            if isinstance(row, dict)
        )
        return ConnectorFetchResult(
            source_id=self.source_id,
            mode="fixture",
            status="ok",
            records=records,
            warnings=("fixture_mode_no_network_call",),
            metadata={
                "source_url": source.source_url,
                "license_or_terms_ref": source.terms_url,
                "record_limit": self.config.max_records,
            },
        )

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        return [
            {
                "source_id": record.source_id,
                "source_record_id": record.source_record_id,
                "payload_hash": record.payload_hash,
                "evidence_summary": record.payload_summary,
                "provenance_url": record.provenance_url,
                "confidence": 0.5,
            }
            for record in records
        ]

    def source_status(self) -> str:
        return source_status_for_source(load_semiconductor_source_registry().get(self.source_id))

    def license_policy(self) -> dict[str, Any]:
        return license_policy_for_source(load_semiconductor_source_registry().get(self.source_id))

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="live_connector_not_implemented",
            warnings=("explicit_admin_or_cli_trigger_required",),
        )

    @staticmethod
    def _sanitized_params(params: dict[str, Any]) -> dict[str, Any]:
        return {str(key): sanitize_external_text(value) for key, value in params.items()}
