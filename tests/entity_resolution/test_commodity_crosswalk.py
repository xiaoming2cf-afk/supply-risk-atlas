from __future__ import annotations

from sra_core.entity_resolution import resolve_commodity


def test_hs_code_crosswalk_resolves_semiconductor_proxy_codes() -> None:
    assert resolve_commodity("854231").resolved_id == "commodity:integrated_circuits_processors"
    assert resolve_commodity("848620").resolved_id == (
        "commodity:semiconductor_manufacturing_machines"
    )
    assert resolve_commodity("370790").resolved_id == "commodity:photoresist_related_chemical_proxy"


def test_proxy_commodity_mappings_carry_warning_when_approximate() -> None:
    result = resolve_commodity("370790")

    assert result.confidence < 0.8
    assert result.warning == "commodity_mapping_is_proxy"


def test_unknown_commodity_code_stays_unresolved() -> None:
    result = resolve_commodity("999999")

    assert result.resolved_id is None
    assert result.warning == "unresolved_low_confidence_mention"

