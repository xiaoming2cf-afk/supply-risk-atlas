from __future__ import annotations

from sra_core.entity_resolution import normalize_alias, resolve_company


def test_normalize_alias_removes_punctuation_and_case() -> None:
    assert normalize_alias("TSMC / 台积电, Ltd.") == "tsmc ltd"


def test_company_alias_resolution_returns_confidence_and_source_refs() -> None:
    result = resolve_company("ASML Holding", source_refs=("sec_edgar_lite:asml",))

    assert result.resolved_id == "company:asml"
    assert result.confidence >= 0.95
    assert result.method == "company_alias_exact"
    assert result.source_refs == ("sec_edgar_lite:asml",)
    assert result.warning is None


def test_company_aliases_cover_requested_semiconductor_firms() -> None:
    expected = {
        "TSMC": "company:tsmc",
        "TSMC / 台积电": "company:tsmc",
        "ASML Holding": "company:asml",
        "Samsung": "company:samsung_electronics",
        "Samsung Electronics": "company:samsung_electronics",
        "Intel Corporation": "company:intel",
        "Applied Materials": "company:applied_materials",
    }

    for alias, resolved_id in expected.items():
        result = resolve_company(alias, source_refs=("node_catalog:test",))
        assert result.resolved_id == resolved_id
        assert result.confidence >= 0.9
        assert result.source_refs == ("node_catalog:test",)


def test_low_confidence_unknown_company_stays_unresolved() -> None:
    result = resolve_company("Unverified Local Supplier")

    assert result.resolved is False
    assert result.resolved_id is None
    assert result.warning == "unresolved_low_confidence_mention"
