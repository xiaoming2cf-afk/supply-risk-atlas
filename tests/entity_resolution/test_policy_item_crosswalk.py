from __future__ import annotations

from sra_core.entity_resolution import resolve_policy_item


def test_policy_item_crosswalk_resolves_key_semiconductor_items() -> None:
    assert resolve_policy_item("EUV").resolved_id == "policy_item:euv_lithography"
    assert resolve_policy_item("advanced computing chips").resolved_id == (
        "policy_item:advanced_computing_chips"
    )
    assert resolve_policy_item("photoresist").resolved_id == "policy_item:photoresist_chemicals"


def test_approximate_policy_item_mapping_includes_warning() -> None:
    result = resolve_policy_item("chemicals")

    assert result.confidence < 0.8
    assert result.warning == "policy_item_mapping_is_approximate"


def test_unknown_policy_item_stays_unresolved() -> None:
    result = resolve_policy_item("ambiguous widget")

    assert result.resolved_id is None
    assert result.warning == "unresolved_low_confidence_mention"
