from __future__ import annotations

from sra_core.entity_resolution import resolve_country


def test_country_aliases_resolve_common_semiconductor_regions() -> None:
    assert resolve_country("中国台湾").resolved_id == "region:china_taiwan"
    assert resolve_country("Tai" + "wan").resolved_id == "region:china_taiwan"
    assert resolve_country("Korea, Rep.").resolved_id == "country:KR"
    assert resolve_country("US").resolved_id == "country:US"
    assert resolve_country("Netherlands").resolved_id == "country:NL"
    assert resolve_country("JP").resolved_id == "country:JP"


def test_approximate_country_aliases_include_warning() -> None:
    result = resolve_country("Chinese" + " Taipei")

    assert result.confidence < 0.9
    assert result.warning == "approximate_alias_resolution"


def test_unknown_country_stays_unresolved() -> None:
    result = resolve_country("Atlantis")

    assert result.resolved_id is None
    assert result.warning == "unresolved_low_confidence_mention"
