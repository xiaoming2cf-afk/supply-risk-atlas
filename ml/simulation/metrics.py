from __future__ import annotations

from statistics import mean


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, float(value)))


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return round(ordered[0], 4)
    q = max(0.0, min(1.0, float(quantile)))
    rank = (len(ordered) - 1) * q
    lower_index = int(rank)
    upper_index = min(lower_index + 1, len(ordered) - 1)
    weight = rank - lower_index
    return round(ordered[lower_index] * (1.0 - weight) + ordered[upper_index] * weight, 4)


def cvar_95(values: list[float]) -> float | None:
    threshold = percentile(values, 0.95)
    if threshold is None:
        return None
    tail = [float(value) for value in values if float(value) >= threshold]
    return round(mean(tail or [threshold]), 4)


def loss_distribution_summary(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "p50": None,
            "p90": None,
            "p95": None,
            "cvar_95": None,
        }
    return {
        "count": len(values),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "mean": round(mean(values), 4),
        "p50": percentile(values, 0.50),
        "p90": percentile(values, 0.90),
        "p95": percentile(values, 0.95),
        "cvar_95": cvar_95(values),
    }

