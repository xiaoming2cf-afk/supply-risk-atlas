from __future__ import annotations

import os
from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import (
    ConnectorFetchResult,
    ConnectorRecord,
    sanitize_external_text,
)


class SecEdgarLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("sec_edgar_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "company_disclosure_event",
                    "event_id": f"company_disclosure:{record.source_record_id}",
                    "company_identifier": sanitize_external_text(
                        metadata.get("company_identifier") or "unknown"
                    ),
                    "filing_date": sanitize_external_text(metadata.get("filing_date")),
                    "filing_type": sanitize_external_text(metadata.get("filing_type")),
                    "disclosure_type": sanitize_external_text(metadata.get("disclosure_type")),
                    "risk_factor_summary": record.payload_summary,
                    "supply_chain_keywords": [
                        sanitize_external_text(keyword)
                        for keyword in metadata.get("supply_chain_keywords", [])
                    ],
                    "semiconductor_keyword_match": bool(
                        metadata.get("semiconductor_keyword_match", False)
                    ),
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.6)),
                    "payload_hash": record.payload_hash,
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "license_or_terms_ref": record.license_or_terms_ref,
                    "evidence_text_summary": record.payload_summary,
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        if not os.environ.get("SEC_USER_AGENT"):
            return ConnectorFetchResult.unavailable(
                source_id=self.source_id,
                mode="live",
                reason="sec_user_agent_required_for_live_edgar_fetch",
                warnings=("live_fetch_disabled_by_default",),
            )
        if not (params.get("cik") or params.get("ticker")):
            return ConnectorFetchResult.unavailable(
                source_id=self.source_id,
                mode="live",
                reason="explicit_cik_or_ticker_required",
                warnings=("no_bulk_edgar_downloads",),
            )
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="sec_edgar_lite_live_fetch_not_implemented",
            warnings=("fixture_mode_required_in_ci",),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    config = ConnectorConfig(mode="fixture", **kwargs)
    return SecEdgarLiteConnector(config=config).fetch()

