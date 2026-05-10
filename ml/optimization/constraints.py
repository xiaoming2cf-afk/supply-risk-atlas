from __future__ import annotations

from typing import Any


ALLOWED_INTERVENTION_TYPES = {
    "add_alternative_supplier",
    "increase_inventory_buffer",
    "regional_diversification",
    "improve_recovery_rate",
    "add_policy_monitoring",
    "route_redundancy",
    "qualify_backup_material",
}


def normalize_optimization_request(payload: dict[str, Any] | None) -> dict[str, Any]:
    raw = dict(payload or {})
    budget = max(0.0, float(raw.get("budget", 100)))
    max_actions = max(1, min(int(raw.get("max_actions", 5)), 20))
    allowed = raw.get("allowed_intervention_types")
    if not isinstance(allowed, list) or not allowed:
        allowed_types = sorted(ALLOWED_INTERVENTION_TYPES)
    else:
        allowed_types = [str(item) for item in allowed if str(item) in ALLOWED_INTERVENTION_TYPES]
    if not allowed_types:
        allowed_types = sorted(ALLOWED_INTERVENTION_TYPES)
    compliance = raw.get("compliance_constraints") if isinstance(raw.get("compliance_constraints"), dict) else {}
    return {
        "graph_version": raw.get("graph_version"),
        "scenario_run": raw.get("scenario_run"),
        "reverse_stress_run": raw.get("reverse_stress_run"),
        "scenario_set": raw.get("scenario_set") if isinstance(raw.get("scenario_set"), list) else [],
        "budget": budget,
        "allowed_intervention_types": allowed_types,
        "max_actions": max_actions,
        "risk_aversion_beta": max(0.0, min(1.0, float(raw.get("risk_aversion_beta", 0.7)))),
        "compliance_constraints": {
            "no_export_control_evasion": bool(compliance.get("no_export_control_evasion", True)),
            "no_sanctions_circumvention": bool(compliance.get("no_sanctions_circumvention", True)),
        },
        "seed": int(raw.get("seed", 42)),
        "as_of_time": str(raw.get("as_of_time") or "2026-05-01T00:00:00Z"),
    }


def validate_action(action: dict[str, Any], request: dict[str, Any], current_cost: float) -> bool:
    return (
        action["intervention_type"] in request["allowed_intervention_types"]
        and current_cost + float(action["cost"]) <= float(request["budget"]) + 1e-9
    )

