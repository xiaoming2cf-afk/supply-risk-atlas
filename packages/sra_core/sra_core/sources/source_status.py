from __future__ import annotations

from collections import Counter
from typing import Any

from sra_core.sources.models import SourceEntry


def connector_status_for_source(source: SourceEntry) -> str:
    connector = source.connector.lower()
    review_status = source.review_status.lower()

    if source.source_tier == "tier_3" or connector.startswith("deferred:"):
        return "deferred_not_allowed"
    if "review_required" in connector or "review_required" in review_status:
        return "disabled_review_required"
    if connector.startswith("fixture:"):
        return "fixture_connector"
    if connector.startswith("promoted:"):
        return "promoted_connector"
    if connector.startswith("live:") and source.live_fetch_default:
        return "live_connector_available"
    if connector.startswith("unavailable:"):
        return "live_connector_unavailable"
    if connector.startswith("disabled:"):
        return "disabled_review_required"
    return "live_connector_unavailable"


def source_status_for_source(source: SourceEntry) -> str:
    connector_status = connector_status_for_source(source)
    review_status = source.review_status.lower()

    if source.source_tier == "tier_3" or connector_status == "deferred_not_allowed":
        return "deferred_paid_or_proprietary"
    if "terms_review" in review_status:
        return "unavailable_terms_review"
    if connector_status == "fixture_connector" and source.enabled_by_default:
        return "enabled_fixture"
    if connector_status == "promoted_connector" and source.enabled_by_default:
        return "enabled_promoted"
    if connector_status == "live_connector_available" and source.enabled_by_default:
        return "enabled_live_available"
    if connector_status == "live_connector_unavailable":
        return "live_unavailable"
    return "disabled_review_required"


def summarize_status_counts(sources: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(source.get("status", "unknown")) for source in sources))


def summarize_connector_counts(sources: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(source.get("connector_status", "unknown")) for source in sources))

