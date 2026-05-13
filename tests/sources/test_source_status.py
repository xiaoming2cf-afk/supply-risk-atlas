from __future__ import annotations

from sra_core.sources import (
    connector_status_for_source,
    load_semiconductor_source_registry,
    source_status_for_source,
)


def test_tier_zero_fixture_sources_are_enabled_fixture_sources() -> None:
    registry = load_semiconductor_source_registry()

    for source_id in [
        "eto_cset_advanced_semiconductor_supply_chain",
        "wsts_historical_billings",
        "global_trade_alert_semiconductor_export_controls",
        "gdelt_semiconductor_events",
    ]:
        source = registry.get(source_id)
        assert connector_status_for_source(source) == "fixture_connector"
        assert source_status_for_source(source) == "enabled_fixture"


def test_disabled_connector_candidates_require_review() -> None:
    registry = load_semiconductor_source_registry()

    for source_id in [
        "sec_edgar_lite",
        "gdelt_semiconductor_lite",
        "wits_trade_tariff_lite",
        "usgs_mineral_commodity_summaries_lite",
        "consolidated_screening_list_lite",
    ]:
        source = registry.get(source_id)
        assert connector_status_for_source(source) == "disabled_review_required"
        assert source_status_for_source(source) == "disabled_review_required"


def test_deferred_sources_are_never_fetchable_by_default() -> None:
    source = load_semiconductor_source_registry().get("company_private_order_data")

    assert connector_status_for_source(source) == "deferred_not_allowed"
    assert source_status_for_source(source) == "deferred_paid_or_proprietary"
    assert source.enabled_by_default is False
    assert source.live_fetch_default is False
