from __future__ import annotations

import random
from typing import Any

from .constraints import validate_action


def baseline_comparison(
    candidates: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    request: dict[str, Any],
) -> list[dict[str, Any]]:
    rng = random.Random(int(request["seed"]))
    feasible = [action for action in candidates if validate_action(action, request, 0.0)]
    random_action = rng.choice(feasible) if feasible else None
    highest = max(feasible, key=lambda action: float(action.get("target_risk_score", 0.0)), default=None)
    cheapest = min(feasible, key=lambda action: float(action.get("cost", 999999)), default=None)
    return [
        _row("random_intervention", random_action),
        _row("highest_risk_score_protection", highest),
        _row("cheapest_first", cheapest),
        {
            "baseline": "proposed_risk_adjusted_greedy_optimizer",
            "action_count": len(selected),
            "cost": round(sum(float(action["cost"]) for action in selected), 4),
            "expected_loss_reduction": round(sum(float(action["expected_loss_reduction"]) for action in selected), 4),
            "cvar95_reduction": round(sum(float(action["cvar95_reduction"]) for action in selected), 4),
        },
    ]


def _row(name: str, action: dict[str, Any] | None) -> dict[str, Any]:
    if action is None:
        return {"baseline": name, "action_count": 0, "cost": 0, "expected_loss_reduction": 0, "cvar95_reduction": 0}
    return {
        "baseline": name,
        "action_count": 1,
        "cost": action["cost"],
        "expected_loss_reduction": action["expected_loss_reduction"],
        "cvar95_reduction": action["cvar95_reduction"],
    }

