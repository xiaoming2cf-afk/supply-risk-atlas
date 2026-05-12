from __future__ import annotations

from sra_core.sources.license_policy import license_policy_summary, license_terms_status
from sra_core.sources.registry import load_semiconductor_source_registry


def test_license_policy_reports_terms_and_redistribution_limits() -> None:
    registry = load_semiconductor_source_registry()
    source = next(item for item in registry["sources"] if item["source_id"] == "sec_edgar")
    policy = license_policy_summary(source)

    assert policy["source_id"] == "sec_edgar"
    assert policy["terms_url"].startswith("https://www.sec.gov/")
    assert policy["status"] in {"terms_registered", "raw_redistribution_disallowed"}
    assert "raw filing" in str(policy["redistribution_limits"]).lower()


def test_license_terms_missing_is_controlled_status() -> None:
    assert license_terms_status({"terms_url": "", "license_or_terms_summary": ""}) == "terms_missing"

