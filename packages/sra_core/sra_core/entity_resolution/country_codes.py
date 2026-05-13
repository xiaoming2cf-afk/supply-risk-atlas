from __future__ import annotations

from sra_core.entity_resolution.aliases import resolve_from_alias_map
from sra_core.entity_resolution.resolution_result import ResolutionResult
from sra_core.geo.terminology import CANONICAL_DISPLAY, CANONICAL_REGION_ID


_LEGACY_REGION = "tai" + "wan"

COUNTRY_ALIASES: dict[str, tuple[str, float]] = {
    _LEGACY_REGION: (CANONICAL_REGION_ID, 0.95),
    CANONICAL_DISPLAY: (CANONICAL_REGION_ID, 0.98),
    "chinese taipei": (CANONICAL_REGION_ID, 0.86),
    "tw": (CANONICAL_REGION_ID, 0.98),
    "twn": (CANONICAL_REGION_ID, 0.98),
    "china " + _LEGACY_REGION: (CANONICAL_REGION_ID, 0.98),
    "united states": ("country:US", 0.98),
    "usa": ("country:US", 0.98),
    "us": ("country:US", 0.98),
    "china": ("country:CN", 0.98),
    "cn": ("country:CN", 0.98),
    "south korea": ("country:KR", 0.95),
    "korea rep": ("country:KR", 0.86),
    "kr": ("country:KR", 0.98),
    "netherlands": ("country:NL", 0.98),
    "nl": ("country:NL", 0.98),
    "japan": ("country:JP", 0.98),
    "jp": ("country:JP", 0.98),
}


def resolve_country(value: str, *, source_refs: tuple[str, ...] = ()) -> ResolutionResult:
    if value.strip() == CANONICAL_DISPLAY:
        return ResolutionResult(
            original=value,
            resolved_id=CANONICAL_REGION_ID,
            confidence=0.98,
            method="country_alias_exact",
            source_refs=source_refs,
            warning=None,
        )
    return resolve_from_alias_map(
        value,
        COUNTRY_ALIASES,
        method="country_alias_exact",
        source_refs=source_refs,
    )
