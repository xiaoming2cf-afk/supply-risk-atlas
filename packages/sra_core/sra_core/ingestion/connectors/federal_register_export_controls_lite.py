from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import ConnectorFetchResult, ConnectorRecord, sanitize_external_text


class FederalRegisterExportControlsLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("federal_register_export_controls_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "export_control_policy_event",
                    "policy_event_id": f"federal_register_policy:{record.source_record_id}",
                    "jurisdiction": sanitize_external_text(metadata.get("jurisdiction", "US")),
                    "policy_type": sanitize_external_text(metadata.get("policy_type")),
                    "policy_title": sanitize_external_text(metadata.get("policy_title")),
                    "publication_date": sanitize_external_text(metadata.get("publication_date")),
                    "affected_items": [
                        sanitize_external_text(item) for item in metadata.get("affected_items", [])
                    ],
                    "compliance_summary": record.payload_summary,
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.55)),
                    "payload_hash": record.payload_hash,
                    "evidence_text_summary": record.payload_summary,
                    "warnings": ["federal_register_summary_only_terms_review_required"],
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="federal_register_export_controls_lite_live_fetch_not_implemented",
            warnings=("terms_review_required_before_live_ingestion", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    return FederalRegisterExportControlsLiteConnector(
        config=ConnectorConfig(mode="fixture", **kwargs)
    ).fetch()
