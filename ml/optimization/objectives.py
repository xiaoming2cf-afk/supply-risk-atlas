from __future__ import annotations


def risk_adjusted_value(action: dict[str, object], *, risk_aversion_beta: float) -> float:
    expected = float(action.get("expected_loss_reduction", 0.0))
    cvar = float(action.get("cvar95_reduction", 0.0))
    cost = max(1.0, float(action.get("cost", 1.0)))
    return round((expected * (1.0 - risk_aversion_beta) + cvar * risk_aversion_beta) / cost, 6)


def resilience_roi(before_cvar95: float, after_cvar95: float, cost: float) -> float:
    if cost <= 0:
        return 0.0
    return round(max(0.0, before_cvar95 - after_cvar95) / cost, 4)

