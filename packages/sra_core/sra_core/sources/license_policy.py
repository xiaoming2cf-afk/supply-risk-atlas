from __future__ import annotations


def license_terms_status(source: dict[str, object]) -> str:
    terms_url = str(source.get("terms_url") or "")
    summary = str(source.get("license_or_terms_summary") or "")
    limits = str(source.get("redistribution_limits") or "")
    if not terms_url.startswith("https://") or not summary:
        return "terms_missing"
    if "raw" in limits.lower() and "not" in limits.lower():
        return "raw_redistribution_disallowed"
    return "terms_registered"


def license_policy_summary(source: dict[str, object]) -> dict[str, object]:
    return {
        "source_id": source.get("source_id"),
        "terms_url": source.get("terms_url"),
        "license_or_terms_summary": source.get("license_or_terms_summary"),
        "redistribution_limits": source.get("redistribution_limits"),
        "allowed_use": list(source.get("allowed_use") or []),
        "status": license_terms_status(source),
    }

