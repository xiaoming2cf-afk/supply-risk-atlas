from __future__ import annotations

from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import (
    ConnectorFetchResult,
    ConnectorRecord,
    sanitize_external_text,
)


class WitsTradeTariffLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("world_bank_wits_trade_tariff_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        promoted: list[dict[str, Any]] = []
        for record in records:
            metadata = record.metadata
            promoted.append(
                {
                    "record_type": "trade_tariff_indicator",
                    "indicator_id": f"trade_tariff_indicator:{record.source_record_id}",
                    "indicator_type": sanitize_external_text(metadata.get("indicator_type")),
                    "country": sanitize_external_text(metadata.get("country")),
                    "partner": sanitize_external_text(metadata.get("partner") or "world"),
                    "commodity_group": sanitize_external_text(metadata.get("commodity_group")),
                    "period": sanitize_external_text(metadata.get("period")),
                    "value": float(metadata.get("value", 0.0) or 0.0),
                    "unit": sanitize_external_text(metadata.get("unit")),
                    "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                    "source_url": record.provenance_url,
                    "confidence": float(metadata.get("confidence", 0.55)),
                    "payload_hash": record.payload_hash,
                    "evidence_text_summary": record.payload_summary,
                    "warnings": ["tariff_and_trade_indicator_is_public_proxy_context"],
                }
            )
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="wits_trade_tariff_lite_live_fetch_not_implemented",
            warnings=("live_fetch_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    config = ConnectorConfig(mode="fixture", **kwargs)
    return WitsTradeTariffLiteConnector(config=config).fetch()
