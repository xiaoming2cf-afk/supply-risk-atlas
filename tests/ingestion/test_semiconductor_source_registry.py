from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "configs" / "sources" / "semiconductor.yaml"
SCHEMA_PATH = ROOT / "data_contracts" / "ingestion_schema" / "semiconductor_source_registry.schema.json"

EXPECTED_SOURCE_IDS = [
    "eto_cset_advanced_semiconductor_supply_chain",
    "wsts_historical_billings",
    "global_trade_alert_semiconductor_export_controls",
    "gdelt_semiconductor_events",
    "sec_edgar_lite",
    "gdelt_semiconductor_lite",
    "un_comtrade_semiconductor_trade_lite",
    "world_bank_wits_trade_tariff_lite",
    "usgs_earthquake_lite",
    "nga_world_port_index_lite",
    "ofac_sanctions_list_lite",
    "bis_export_controls_lite",
    "federal_register_export_controls_lite",
    "world_bank_macro_indicators_lite",
    "ourairports_lite",
    "openalex_crossref_literature_lite",
    "company_annual_report_manual_upload",
    "customs_trade_manual_upload",
    "paid_semi_market_data",
    "proprietary_factset_supply_chain",
    "bloomberg_supply_chain",
    "wind_or_choice_private_data",
    "company_private_order_data",
]
DISABLED_BY_DEFAULT = set(EXPECTED_SOURCE_IDS[4:])
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
}


def _load_registry() -> dict:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_registry_declares_expanded_semiconductor_public_source_catalog() -> None:
    sources = _load_registry()["sources"]

    assert [source["source_id"] for source in sources] == EXPECTED_SOURCE_IDS
    assert len({source["source_id"] for source in sources}) == len(EXPECTED_SOURCE_IDS)


def test_registry_entries_have_required_governance_fields() -> None:
    for source in _load_registry()["sources"]:
        missing = sorted(field for field in REQUIRED_SOURCE_FIELDS if field not in source)
        assert missing == [], f"{source['source_id']} missing {missing}"

        assert source["publisher"]
        assert source["source_url"].startswith("https://")
        assert source["terms_url"].startswith("https://")
        assert source["allowed_use"]
        assert source["freshness_sla_hours"] > 0
        assert source["live_fetch_default"] is False
        assert source["connector"]
        assert source["raw_contract"]
        assert source["silver_contract"]
        assert source["graph_contract"]
        assert source["owner"]
        assert source["review_status"]
        assert source["source_tier"] in {"tier_0", "tier_1", "tier_2", "tier_3"}
        assert source["data_category"]
        assert source["raw_payload_storage_policy"] == "hash_and_summary_only"
        assert source["api_visibility_policy"] in {
            "summary_and_lineage_only",
            "registry_only",
        }


def test_registry_default_enablement_is_explicit() -> None:
    for source in _load_registry()["sources"]:
        expected = source["source_id"] not in DISABLED_BY_DEFAULT
        assert source["enabled_by_default"] is expected


def test_deferred_sources_are_registry_only_and_not_fetchable_by_default() -> None:
    for source in _load_registry()["sources"]:
        if source["source_tier"] != "tier_3":
            continue
        assert source["enabled_by_default"] is False
        assert source["live_fetch_default"] is False
        assert source["connector"] == "deferred:not_allowed"
        assert source["api_visibility_policy"] == "registry_only"


def test_schema_requires_the_governed_registry_fields() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    item_schema = schema["properties"]["sources"]["items"]

    assert set(item_schema["required"]) == REQUIRED_SOURCE_FIELDS
    assert item_schema["properties"]["source_id"]["enum"] == EXPECTED_SOURCE_IDS
