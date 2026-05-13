from __future__ import annotations

from sra_core.entity_resolution.aliases import resolve_from_alias_map
from sra_core.entity_resolution.resolution_result import ResolutionResult


COMMODITY_CROSSWALK: dict[str, tuple[str, float]] = {
    "854231": ("commodity:integrated_circuits_processors", 0.9),
    "integrated circuits": ("commodity:integrated_circuits_processors", 0.74),
    "854232": ("commodity:memory_integrated_circuits", 0.9),
    "memory": ("commodity:memory_integrated_circuits", 0.72),
    "854233": ("commodity:amplifier_integrated_circuits", 0.88),
    "854239": ("commodity:other_integrated_circuits", 0.86),
    "848620": ("commodity:semiconductor_manufacturing_machines", 0.92),
    "semiconductor manufacturing machines": (
        "commodity:semiconductor_manufacturing_machines",
        0.9,
    ),
    "381800": ("commodity:doped_chemical_elements_electronics", 0.78),
    "370790": ("commodity:photoresist_related_chemical_proxy", 0.7),
    "280461": ("commodity:high_purity_silicon_proxy", 0.72),
}


def resolve_commodity(value: str, *, source_refs: tuple[str, ...] = ()) -> ResolutionResult:
    return resolve_from_alias_map(
        value,
        COMMODITY_CROSSWALK,
        method="semiconductor_hs_proxy_crosswalk",
        source_refs=source_refs,
        approximate_warning="commodity_mapping_is_proxy",
    )

