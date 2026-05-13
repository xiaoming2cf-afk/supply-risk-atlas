from __future__ import annotations

from sra_core.sources import license_policy_for_source, load_semiconductor_source_registry


def test_license_policy_allows_summary_lineage_but_not_raw_payload_by_default() -> None:
    source = load_semiconductor_source_registry().get("sec_edgar_lite")
    policy = license_policy_for_source(source)

    assert policy["api_visible_summary_allowed"] is True
    assert policy["raw_payload_storage_allowed"] is False
    assert policy["attribution_required"] is True
    assert "summaries and lineage" in policy["manual_review_note"].lower()


def test_terms_review_sources_are_blocked_from_live_use() -> None:
    source = load_semiconductor_source_registry().get("ourairports_lite")
    policy = license_policy_for_source(source)

    assert policy["terms_review_required"] is True
    assert policy["raw_payload_storage_allowed"] is False
    assert policy["redistribution_allowed"] is False


def test_paid_and_proprietary_sources_are_registry_only() -> None:
    registry = load_semiconductor_source_registry()
    for source_id in [
        "paid_semi_market_data",
        "paid_semiconductor_market_data",
        "proprietary_factset_supply_chain",
        "bloomberg_supply_chain",
        "wind_or_choice_private_data",
        "company_private_order_data",
    ]:
        policy = license_policy_for_source(registry.get(source_id))
        assert policy["terms_review_required"] is True
        assert policy["raw_payload_storage_allowed"] is False
        assert policy["redistribution_allowed"] is False
        assert "registry-only" in policy["manual_review_note"]
