from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SOURCE_TIERS = {"tier_0", "tier_1", "tier_2", "tier_3"}
DATA_CATEGORIES = {
    "supply_chain_structure",
    "market_indicator",
    "trade_flow",
    "policy_export_control",
    "sanctions_compliance",
    "event_news",
    "natural_hazard",
    "logistics",
    "literature_methodology",
    "manual_upload",
}

SOURCE_STATUS_VALUES = {
    "enabled_fixture",
    "enabled_promoted",
    "enabled_live_available",
    "live_unavailable",
    "disabled_review_required",
    "unavailable_terms_review",
    "deferred_paid_or_proprietary",
}

CONNECTOR_STATUS_VALUES = {
    "fixture_connector",
    "promoted_connector",
    "live_connector_available",
    "live_connector_unavailable",
    "disabled_review_required",
    "deferred_not_allowed",
}

REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "publisher",
    "source_url",
    "terms_url",
    "license_or_terms_summary",
    "allowed_use",
    "redistribution_limits",
    "attribution",
    "requires_api_key",
    "enabled_by_default",
    "live_fetch_default",
    "update_frequency",
    "freshness_sla_hours",
    "connector",
    "raw_contract",
    "silver_contract",
    "graph_contract",
    "owner",
    "review_status",
    "source_tier",
    "data_category",
    "pii_risk",
    "raw_payload_storage_policy",
    "api_visibility_policy",
    "geography_normalization_policy",
}


@dataclass(frozen=True)
class SourceEntry:
    source_id: str
    publisher: str
    source_url: str
    terms_url: str
    license_or_terms_summary: str
    allowed_use: tuple[str, ...]
    redistribution_limits: str
    attribution: str
    requires_api_key: bool
    enabled_by_default: bool
    live_fetch_default: bool
    update_frequency: str
    freshness_sla_hours: int
    connector: str
    raw_contract: str
    silver_contract: str
    graph_contract: str
    owner: str
    review_status: str
    source_tier: str
    data_category: str
    pii_risk: str
    raw_payload_storage_policy: str
    api_visibility_policy: str
    geography_normalization_policy: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "SourceEntry":
        allowed_use = raw.get("allowed_use")
        if not isinstance(allowed_use, list):
            allowed_use = []
        return cls(
            source_id=str(raw.get("source_id", "")),
            publisher=str(raw.get("publisher", "")),
            source_url=str(raw.get("source_url", "")),
            terms_url=str(raw.get("terms_url", "")),
            license_or_terms_summary=str(raw.get("license_or_terms_summary", "")),
            allowed_use=tuple(str(item) for item in allowed_use),
            redistribution_limits=str(raw.get("redistribution_limits", "")),
            attribution=str(raw.get("attribution", "")),
            requires_api_key=bool(raw.get("requires_api_key", False)),
            enabled_by_default=bool(raw.get("enabled_by_default", False)),
            live_fetch_default=bool(raw.get("live_fetch_default", False)),
            update_frequency=str(raw.get("update_frequency", "")),
            freshness_sla_hours=int(raw.get("freshness_sla_hours", 0)),
            connector=str(raw.get("connector", "")),
            raw_contract=str(raw.get("raw_contract", "")),
            silver_contract=str(raw.get("silver_contract", "")),
            graph_contract=str(raw.get("graph_contract", "")),
            owner=str(raw.get("owner", "")),
            review_status=str(raw.get("review_status", "")),
            source_tier=str(raw.get("source_tier", "")),
            data_category=str(raw.get("data_category", "")),
            pii_risk=str(raw.get("pii_risk", "")),
            raw_payload_storage_policy=str(raw.get("raw_payload_storage_policy", "")),
            api_visibility_policy=str(raw.get("api_visibility_policy", "")),
            geography_normalization_policy=str(raw.get("geography_normalization_policy", "")),
        )

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "publisher": self.publisher,
            "source_url": self.source_url,
            "terms_url": self.terms_url,
            "license_or_terms_summary": self.license_or_terms_summary,
            "allowed_use": list(self.allowed_use),
            "redistribution_limits": self.redistribution_limits,
            "attribution": self.attribution,
            "requires_api_key": self.requires_api_key,
            "enabled_by_default": self.enabled_by_default,
            "live_fetch_default": self.live_fetch_default,
            "update_frequency": self.update_frequency,
            "freshness_sla_hours": self.freshness_sla_hours,
            "connector": self.connector,
            "raw_contract": self.raw_contract,
            "silver_contract": self.silver_contract,
            "graph_contract": self.graph_contract,
            "owner": self.owner,
            "review_status": self.review_status,
            "source_tier": self.source_tier,
            "data_category": self.data_category,
            "pii_risk": self.pii_risk,
            "payload_storage_policy": self.raw_payload_storage_policy,
            "api_visibility_policy": self.api_visibility_policy,
            "geography_normalization_policy": self.geography_normalization_policy,
        }


@dataclass(frozen=True)
class SourceRegistry:
    registry_version: str
    generated_at: str
    sources: tuple[SourceEntry, ...]

    def source_ids(self) -> list[str]:
        return [source.source_id for source in self.sources]

    def get(self, source_id: str) -> SourceEntry:
        for source in self.sources:
            if source.source_id == source_id:
                return source
        raise KeyError(source_id)
