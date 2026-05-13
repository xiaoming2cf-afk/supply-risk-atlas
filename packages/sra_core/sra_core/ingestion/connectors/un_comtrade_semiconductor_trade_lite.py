from __future__ import annotations

from collections import defaultdict
from typing import Any

from sra_core.ingestion.connectors.base import ConnectorConfig, PublicEvidenceConnector
from sra_core.ingestion.connectors.result import (
    ConnectorFetchResult,
    ConnectorRecord,
    sanitize_external_text,
)


SIGNIFICANT_DEPENDENCY_SHARE = 0.20
HIGH_DEPENDENCY_SHARE = 0.40


class UnComtradeSemiconductorTradeLiteConnector(PublicEvidenceConnector):
    def __init__(self, *, config: ConnectorConfig | None = None) -> None:
        super().__init__("un_comtrade_semiconductor_trade_lite", config=config)

    def promote(self, records: tuple[ConnectorRecord, ...]) -> list[dict[str, Any]]:
        totals: dict[tuple[str, str, str], float] = defaultdict(float)
        for record in records:
            metadata = record.metadata
            key = (
                sanitize_external_text(metadata.get("reporter")),
                sanitize_external_text(metadata.get("commodity_code")),
                sanitize_external_text(metadata.get("flow_type")),
            )
            totals[key] += float(metadata.get("trade_value", 0.0) or 0.0)

        promoted: list[dict[str, Any]] = []
        shares_by_key: dict[tuple[str, str, str], list[float]] = defaultdict(list)
        staged: list[tuple[dict[str, Any], tuple[str, str, str], float]] = []
        for record in records:
            metadata = record.metadata
            key = (
                sanitize_external_text(metadata.get("reporter")),
                sanitize_external_text(metadata.get("commodity_code")),
                sanitize_external_text(metadata.get("flow_type")),
            )
            value = float(metadata.get("trade_value", 0.0) or 0.0)
            share = value / totals[key] if totals[key] else 0.0
            shares_by_key[key].append(share)
            staged.append(
                (
                    {
                        "record_type": "trade_flow",
                        "trade_flow_id": f"trade_flow:{record.source_record_id}",
                        "reporter": key[0],
                        "partner": sanitize_external_text(metadata.get("partner")),
                        "commodity_code": key[1],
                        "commodity_label": sanitize_external_text(metadata.get("commodity_label")),
                        "flow_type": key[2],
                        "period": sanitize_external_text(metadata.get("period")),
                        "value": value,
                        "quantity": metadata.get("quantity"),
                        "unit": sanitize_external_text(metadata.get("unit")),
                        "dependency_share": round(share, 6),
                        "significant_dependency": share >= SIGNIFICANT_DEPENDENCY_SHARE,
                        "high_dependency": share >= HIGH_DEPENDENCY_SHARE,
                        "source_refs": [f"{record.source_id}:{record.source_record_id}"],
                        "source_url": record.provenance_url,
                        "confidence": float(metadata.get("confidence", 0.55)),
                        "payload_hash": record.payload_hash,
                        "evidence_text_summary": record.payload_summary,
                        "warnings": ["hs_code_mapping_is_proxy_not_complete_supply_chain_truth"],
                    },
                    key,
                    share,
                )
            )

        hhi_by_key = {key: sum(share**2 for share in shares) for key, shares in shares_by_key.items()}
        for row, key, _share in staged:
            row["country_product_hhi"] = round(hhi_by_key[key], 6)
            promoted.append(row)
        return promoted

    def _fetch_live(self, params: dict[str, Any]) -> ConnectorFetchResult:
        return ConnectorFetchResult.unavailable(
            source_id=self.source_id,
            mode="live",
            reason="un_comtrade_lite_live_fetch_not_implemented",
            warnings=("live_fetch_disabled_by_default", "fixture_mode_required_in_ci"),
        )


def replay_fixture(**kwargs: Any) -> ConnectorFetchResult:
    config = ConnectorConfig(mode="fixture", **kwargs)
    return UnComtradeSemiconductorTradeLiteConnector(config=config).fetch()

