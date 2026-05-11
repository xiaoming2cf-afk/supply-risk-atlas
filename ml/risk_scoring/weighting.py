from __future__ import annotations

from math import prod
from typing import Iterable


HEURISTIC_COMPONENT_WEIGHTS: dict[str, float] = {
    "exposure_score": 0.25,
    "criticality_score": 0.25,
    "substitution_gap": 0.15,
    "policy_risk": 0.15,
    "event_pressure": 0.10,
    "market_pressure": 0.10,
}

HEURISTIC_WEIGHTING_METHOD = "fixed_manual_weights"
HEURISTIC_WEIGHT_SOURCE = "heuristic_unvalidated"
HEURISTIC_CALIBRATION_STATUS = "not_calibrated"
DEFAULT_WEIGHTING_METHOD = "literature_proxy_not_calibrated"


def clamp01(value: float | int | None) -> float:
    if value is None:
        return 0.0
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def clamp_score(value: float | int | None) -> float:
    return round(clamp01((float(value) if value is not None else 0.0) / 100.0) * 100.0, 2)


def noisy_or(values: Iterable[float]) -> float:
    bounded = [clamp01(value) for value in values]
    if not bounded:
        return 0.0
    return clamp01(1.0 - prod(1.0 - value for value in bounded))


def bounded_mean(values: Iterable[float]) -> float:
    bounded = [clamp01(value) for value in values]
    if not bounded:
        return 0.0
    return clamp01(sum(bounded) / len(bounded))


def max_or_zero(values: Iterable[float]) -> float:
    bounded = [clamp01(value) for value in values]
    return max(bounded) if bounded else 0.0
