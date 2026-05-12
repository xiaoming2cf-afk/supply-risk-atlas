from __future__ import annotations

from sra_core.entity_resolution.aliases import resolve_from_alias_map
from sra_core.entity_resolution.resolution_result import ResolutionResult


POLICY_ITEM_CROSSWALK: dict[str, tuple[str, float]] = {
    "euv": ("policy_item:euv_lithography", 0.9),
    "euv lithography": ("policy_item:euv_lithography", 0.94),
    "lithography": ("policy_item:lithography_equipment", 0.78),
    "semiconductor manufacturing equipment": (
        "policy_item:semiconductor_manufacturing_equipment",
        0.88,
    ),
    "advanced computing chips": ("policy_item:advanced_computing_chips", 0.9),
    "hbm": ("policy_item:hbm_memory", 0.88),
    "memory": ("policy_item:memory", 0.72),
    "photoresist": ("policy_item:photoresist_chemicals", 0.86),
    "chemicals": ("policy_item:semiconductor_chemicals", 0.7),
}


def resolve_policy_item(value: str, *, source_refs: tuple[str, ...] = ()) -> ResolutionResult:
    return resolve_from_alias_map(
        value,
        POLICY_ITEM_CROSSWALK,
        method="policy_item_crosswalk",
        source_refs=source_refs,
        approximate_warning="policy_item_mapping_is_approximate",
    )

