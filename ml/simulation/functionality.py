from __future__ import annotations

from typing import Any


FORMULA_REFS = [
    "resilience_triangle_functionality_loss",
    "multi_component_supply_chain_resilience_functionality_loss",
]


def build_functionality_curve(
    *,
    initial_loss: float,
    duration_days: float,
    recovery_rate: float = 0.25,
    steps: int = 8,
) -> list[dict[str, float]]:
    steps = max(2, min(24, int(steps)))
    duration = max(1.0, float(duration_days))
    loss = max(0.0, min(1.0, float(initial_loss)))
    recovery = max(0.0, min(1.0, float(recovery_rate)))
    rows: list[dict[str, float]] = []
    for index in range(steps):
        fraction = index / (steps - 1)
        remaining_loss = loss * max(0.0, 1.0 - fraction * (0.55 + recovery))
        rows.append(
            {
                "t": round(duration * fraction, 4),
                "baseline_functionality": 1.0,
                "functionality": round(max(0.0, 1.0 - remaining_loss), 6),
            }
        )
    return rows


def resilience_integral_loss(functionality_curve: list[dict[str, Any]]) -> float:
    if not functionality_curve:
        return 0.0
    numerator = 0.0
    denominator = 0.0
    for index, point in enumerate(functionality_curve):
        if index == 0:
            continue
        previous = functionality_curve[index - 1]
        width = max(0.0, float(point["t"]) - float(previous["t"]))
        baseline_avg = (float(previous["baseline_functionality"]) + float(point["baseline_functionality"])) / 2.0
        actual_avg = (float(previous["functionality"]) + float(point["functionality"])) / 2.0
        numerator += max(0.0, baseline_avg - actual_avg) * width
        denominator += baseline_avg * width
    if denominator <= 0:
        return 0.0
    return round(max(0.0, min(100.0, (numerator / denominator) * 100.0)), 4)


def summarize_functionality_curve(curve: list[dict[str, Any]]) -> dict[str, float | int]:
    if not curve:
        return {"points": 0, "min_functionality": 1.0, "end_functionality": 1.0}
    values = [float(point["functionality"]) for point in curve]
    return {
        "points": len(curve),
        "min_functionality": round(min(values), 6),
        "end_functionality": round(values[-1], 6),
    }
