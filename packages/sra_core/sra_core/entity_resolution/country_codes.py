from __future__ import annotations

from sra_core.entity_resolution.aliases import resolve_from_alias_map
from sra_core.entity_resolution.resolution_result import ResolutionResult


COUNTRY_ALIASES: dict[str, tuple[str, float]] = {
    "taiwan": ("country:TW", 0.95),
    "chinese taipei": ("country:TW", 0.86),
    "tw": ("country:TW", 0.98),
    "twn": ("country:TW", 0.98),
    "united states": ("country:US", 0.98),
    "usa": ("country:US", 0.98),
    "us": ("country:US", 0.98),
    "south korea": ("country:KR", 0.95),
    "korea rep": ("country:KR", 0.86),
    "kr": ("country:KR", 0.98),
    "netherlands": ("country:NL", 0.98),
    "nl": ("country:NL", 0.98),
    "japan": ("country:JP", 0.98),
    "jp": ("country:JP", 0.98),
}


def resolve_country(value: str, *, source_refs: tuple[str, ...] = ()) -> ResolutionResult:
    return resolve_from_alias_map(
        value,
        COUNTRY_ALIASES,
        method="country_alias_exact",
        source_refs=source_refs,
    )

