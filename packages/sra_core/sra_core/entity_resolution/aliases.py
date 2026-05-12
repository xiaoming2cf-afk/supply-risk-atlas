from __future__ import annotations

import re

from sra_core.entity_resolution.resolution_result import ResolutionResult, unresolved_result


def normalize_alias(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    return " ".join(normalized.split())


def resolve_from_alias_map(
    value: str,
    alias_map: dict[str, tuple[str, float]],
    *,
    method: str,
    source_refs: tuple[str, ...] = (),
    approximate_warning: str = "approximate_alias_resolution",
) -> ResolutionResult:
    normalized = normalize_alias(value)
    if normalized in alias_map:
        resolved_id, confidence = alias_map[normalized]
        warning = approximate_warning if confidence < 0.9 else None
        return ResolutionResult(
            original=value,
            resolved_id=resolved_id,
            confidence=confidence,
            method=method,
            source_refs=source_refs,
            warning=warning,
        )
    return unresolved_result(
        value,
        method=method,
        warning="unresolved_low_confidence_mention",
    )
