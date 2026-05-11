from __future__ import annotations

from math import prod
from typing import Iterable


FORMULA_REFS = {
    "max": ["legacy_max_overwrite_baseline"],
    "additive_cap": ["multi_source_additive_cap"],
    "noisy_or": ["probabilistic_noisy_or_exposure_accumulation"],
    "leontief_bottleneck": ["production_shortage_interdependency_perfect_complements"],
    "psi_recursive": ["recursive_production_shortage_interdependency"],
    "auto_semiconductor": [
        "production_network_input_output_propagation",
        "production_shortage_interdependency_perfect_complements",
        "probabilistic_noisy_or_exposure_accumulation",
    ],
}

AGGREGATION_FORMULAS = {
    "max": "loss_j = max(own_loss_j, max_i contribution_ij)",
    "additive_cap": "loss_j = min(1, own_loss_j + sum_i contribution_ij)",
    "noisy_or": "loss_j = 1 - product_i(1 - contribution_ij)",
    "leontief_bottleneck": "availability_j = min_k availability_k / requirement_k; loss_j = 1 - availability_j",
    "psi_recursive": "recursive higher-order production shortage propagation over graph depth",
    "auto_semiconductor": "critical input edges use leontief bottleneck; event/policy exposure uses noisy-or; other links use additive cap",
}


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def aggregate_loss(own_loss: float, contributions: Iterable[float], *, mode: str) -> float:
    values = [clamp01(value) for value in contributions if value > 0]
    base = clamp01(own_loss)
    if not values:
        return base
    if mode == "max":
        return max(base, max(values))
    if mode == "additive_cap":
        return clamp01(base + sum(values))
    if mode == "noisy_or":
        return clamp01(1.0 - ((1.0 - base) * prod(1.0 - value for value in values)))
    if mode in {"leontief_bottleneck", "psi_recursive"}:
        worst_input_availability = min(1.0 - value for value in values)
        bottleneck_loss = clamp01(1.0 - worst_input_availability)
        if mode == "psi_recursive":
            bottleneck_loss = clamp01(bottleneck_loss + 0.15 * sum(values) / len(values))
        return max(base, bottleneck_loss)
    raise ValueError(f"unsupported propagation mode: {mode}")


def mode_for_edge_type(edge_type: str, requested_mode: str) -> str:
    if requested_mode != "auto_semiconductor":
        return requested_mode
    if edge_type in {"requires", "depends_on"}:
        return "leontief_bottleneck"
    if edge_type in {"restricted_by", "impacted_by"}:
        return "noisy_or"
    return "additive_cap"
