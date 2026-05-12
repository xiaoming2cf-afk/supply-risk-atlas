from __future__ import annotations

from typing import Any

from sra_core.sources.models import SourceEntry


def license_policy_for_source(source: SourceEntry) -> dict[str, Any]:
    review_status = source.review_status.lower()
    storage_policy = source.raw_payload_storage_policy.lower()
    visibility_policy = source.api_visibility_policy.lower()
    summary = source.license_or_terms_summary.lower()
    tier = source.source_tier

    deferred = tier == "tier_3" or "deferred" in review_status
    terms_review_required = (
        "terms_review" in review_status
        or "unclear" in summary
        or "review" in storage_policy
        or source.terms_url.endswith("terms-review-required")
    )
    raw_payload_storage_allowed = storage_policy in {"allow_raw_payload", "explicit_policy_allows_raw"}
    api_visible_summary_allowed = visibility_policy in {
        "summary_and_lineage_only",
        "summary_only",
        "metadata_only",
        "registry_only",
    }
    redistribution_allowed = (
        not deferred
        and not terms_review_required
        and "do not redistribute raw" not in source.redistribution_limits.lower()
    )

    if deferred:
        manual_review_note = "Deferred paid/proprietary source; registry-only and never fetched by default."
    elif terms_review_required:
        manual_review_note = "Terms review required before live ingestion or redistribution."
    else:
        manual_review_note = "API-visible summaries and lineage are allowed by this registry policy."

    return {
        "api_visible_summary_allowed": api_visible_summary_allowed and not raw_payload_storage_allowed,
        "raw_payload_storage_allowed": raw_payload_storage_allowed and not deferred,
        "redistribution_allowed": redistribution_allowed,
        "attribution_required": bool(source.attribution and source.attribution != "deferred"),
        "terms_review_required": terms_review_required or deferred,
        "manual_review_note": manual_review_note,
    }

