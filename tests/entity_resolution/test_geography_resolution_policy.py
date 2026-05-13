from __future__ import annotations

from sra_core.entity_resolution import resolve_country
from sra_core.geo.normalize import normalize_country_context, normalize_geo_label
from sra_core.geo.terminology import (
    CANONICAL_DISPLAY,
    CANONICAL_REGION_ID,
    PARENT_COUNTRY_DISPLAY,
    PARENT_COUNTRY_ID,
)


def _legacy_latin() -> str:
    return "Tai" + "wan"


def test_legacy_region_aliases_resolve_to_canonical_region_not_country() -> None:
    for value in (_legacy_latin(), "TW", "TWN", CANONICAL_DISPLAY):
        result = resolve_country(value, source_refs=("entity_resolution:test",))
        assert result.resolved_id == CANONICAL_REGION_ID
        assert result.source_refs == ("entity_resolution:test",)
        assert result.method == "country_alias_exact"


def test_geography_resolution_keeps_parent_country_context() -> None:
    context = normalize_country_context(_legacy_latin())

    assert context["region_id"] == CANONICAL_REGION_ID
    assert context["region_display"] == CANONICAL_DISPLAY
    assert context["country_id"] == PARENT_COUNTRY_ID
    assert context["country_display"] == PARENT_COUNTRY_DISPLAY


def test_resolved_display_label_is_canonical() -> None:
    assert normalize_geo_label(_legacy_latin()) == CANONICAL_DISPLAY
