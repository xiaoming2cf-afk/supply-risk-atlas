from __future__ import annotations

from sra_core.sources import load_semiconductor_source_registry, source_registry_readiness


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


def test_runtime_loads_governed_semiconductor_registry_without_network() -> None:
    registry = load_semiconductor_source_registry()

    assert registry.registry_version == "semiconductor-source-registry-v0.2"
    assert registry.source_ids() == EXPECTED_SOURCE_IDS
    assert len(registry.sources) == 23


def test_source_registry_readiness_summarizes_enabled_disabled_and_deferred_sources() -> None:
    readiness = source_registry_readiness()

    assert readiness["status"] == "degraded"
    assert readiness["source_count"] == 23
    assert readiness["enabled_count"] == 4
    assert readiness["live_default_count"] == 0
    assert readiness["deferred_count"] == 5
    assert readiness["source_tier_counts"] == {
        "tier_0": 4,
        "tier_1": 8,
        "tier_2": 6,
        "tier_3": 5,
    }
    assert "live_fetch_disabled_by_default" in readiness["warnings"]
    assert "payload_storage_disabled_by_default" in readiness["warnings"]


def test_runtime_rows_are_api_visible_summaries_without_raw_payloads() -> None:
    readiness = source_registry_readiness()

    for row in readiness["sources"]:
        assert "raw_payload" not in row
        assert "secret" not in row
        assert row["live_fetch_default"] is False
        assert row["license_policy"]["payload_storage_allowed"] is False
