from __future__ import annotations

from sra_core.entity_resolution.aliases import resolve_from_alias_map
from sra_core.entity_resolution.resolution_result import ResolutionResult


COMPANY_ALIASES: dict[str, tuple[str, float]] = {
    "tsmc": ("company:tsmc", 0.98),
    "taiwan semiconductor manufacturing company": ("company:tsmc", 0.98),
    "taiwan semiconductor manufacturing co": ("company:tsmc", 0.94),
    "asml": ("company:asml", 0.98),
    "asml holding": ("company:asml", 0.98),
    "asml holding nv": ("company:asml", 0.96),
    "samsung": ("company:samsung_electronics", 0.9),
    "samsung electronics": ("company:samsung_electronics", 0.96),
    "intel": ("company:intel", 0.95),
    "intel corporation": ("company:intel", 0.98),
    "applied materials": ("company:applied_materials", 0.96),
    "applied materials inc": ("company:applied_materials", 0.95),
}


def resolve_company(value: str, *, source_refs: tuple[str, ...] = ()) -> ResolutionResult:
    return resolve_from_alias_map(
        value,
        COMPANY_ALIASES,
        method="company_alias_exact",
        source_refs=source_refs,
    )
