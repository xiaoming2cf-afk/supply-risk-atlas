from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import ConnectorFetchResult, ConnectorRecord, sanitize_external_text


class OfacSanctionsListLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("ofac_sanctions_list_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "sanctions_screening_event",
                    "screening_event_id": f"sanctions_screening:{record.source_record_id}",
                    "entity_name": sanitize_external_text(metadata.get("entity_name")),
                    "list_type": sanitize_external_text(metadata.get("list_type")),
                    "program": sanitize_external_text(metadata.get("program")),
                    "country": sanitize_external_text(metadata.get("country")),
                    "match_confidence": float(metadata.get("match_confidence", 0.0)),
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.55)),
                    "payload_hash": record.payload_hash,
                    "evidence_text_summary": record.payload_summary,
                    "compliance_note": "Compliance risk awareness only; no operational guidance.",
                    "warnings": ["sanctions_compliance_summary_only"],
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="ofac_sanctions_list_lite_live_fetch_not_implemented",
            warnings=("live_fetch_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    return OfacSanctionsListLiteConnector(config=ConnectorConfig(mode="fixture", **kwargs)).fetch()
