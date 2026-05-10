from __future__ import annotations

from typing import Any


def plausibility_cost(shock: dict[str, Any], *, combination_size: int = 1) -> float:
    severity = _normalize(float(shock.get("severity", 0.7)))
    confidence = _normalize(float(shock.get("confidence", 0.55)))
    scope_penalty = {
        "country": 0.18,
        "material": 0.12,
        "equipment": 0.14,
        "process_stage": 0.12,
        "company": 0.10,
        "facility": 0.08,
        "route": 0.10,
        "demand": 0.13,
        "policy": 0.16,
        "risk_event": 0.14,
    }.get(str(shock.get("shock_type", "")), 0.15)
    return round(max(0.0, severity * 0.48 + (1.0 - confidence) * 0.26 + scope_penalty + max(0, combination_size - 1) * 0.08), 4)


def explanation_for_shocks(shocks: list[dict[str, Any]]) -> str:
    if not shocks:
        return "No plausible shock set could be evaluated from the available fixture graph."
    names = [str(shock.get("label") or shock.get("target_id")) for shock in shocks]
    return (
        "Reverse stress search found a compliance-safe resilience-planning shock set around "
        + " + ".join(names)
        + " that can breach or approach the requested normalized failure threshold."
    )


def _normalize(value: float) -> float:
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

