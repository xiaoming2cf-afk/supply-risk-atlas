from __future__ import annotations


FIXTURE_SOURCE_IDS = {
    "eto_cset_advanced_semiconductor_supply_chain",
    "wsts_historical_billings",
    "global_trade_alert_semiconductor_export_controls",
    "gdelt_semiconductor_events",
}


def connector_status(source: dict[str, object]) -> str:
    source_id = str(source.get("source_id") or "")
    connector = str(source.get("connector") or "").strip().lower()
    enabled = bool(source.get("enabled_by_default"))
    review_status = str(source.get("review_status") or "").lower()
    if not enabled or connector.startswith("disabled") or "disabled" in review_status:
        return "disabled_review_required"
    if source_id in FIXTURE_SOURCE_IDS:
        return "fixture_connector"
    if connector.startswith("unavailable"):
        return "live_connector_unavailable"
    return "live_connector_available"


def source_runtime_status(source: dict[str, object]) -> str:
    status = connector_status(source)
    if status == "disabled_review_required":
        return "disabled"
    if status == "live_connector_unavailable":
        return "unavailable"
    return "enabled"

