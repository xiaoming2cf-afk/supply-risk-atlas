from __future__ import annotations

from statistics import mean
from typing import Any

from sra_core.contracts.semiconductor import SemiriskGraphSnapshot

from .functionality import FORMULA_REFS as FUNCTIONALITY_FORMULA_REFS
from .functionality import build_functionality_curve, resilience_integral_loss


LOSS_FORMULA_REFS = [
    *FUNCTIONALITY_FORMULA_REFS,
    "production_network_input_output_propagation",
    "oecd_supply_chain_resilience_critical_dependency",
]


def compute_loss_components(
    snapshot: SemiriskGraphSnapshot,
    node_losses: dict[str, float],
    *,
    duration_days: float,
    loss_mode: str = "resilience_integral_loss",
    functionality_metric: str = "capacity_fulfillment",
    weighting_method: str = "literature_proxy_not_calibrated",
) -> dict[str, Any]:
    affected_values = [value for value in node_losses.values() if value >= 0.01]
    affected_mean = round((mean(affected_values) if affected_values else 0.0) * 100.0, 4)
    graph_weighted = _graph_weighted_loss(snapshot, node_losses)
    demand_loss = _demand_fulfillment_loss(snapshot, node_losses)
    capacity_loss = _capacity_functionality_loss(snapshot, node_losses)
    curve_seed_loss = max(graph_weighted, demand_loss, capacity_loss) / 100.0
    curve = build_functionality_curve(
        initial_loss=curve_seed_loss,
        duration_days=duration_days,
        recovery_rate=_average_recovery_rate(snapshot, node_losses),
    )
    resilience_loss = resilience_integral_loss(curve)
    by_mode = {
        "affected_mean": affected_mean,
        "graph_weighted_loss": graph_weighted,
        "demand_fulfillment_loss": demand_loss,
        "resilience_integral_loss": resilience_loss,
        "capacity_functionality_loss": capacity_loss,
    }
    if loss_mode not in by_mode:
        raise ValueError(f"unsupported loss_mode: {loss_mode}")
    warnings = ["fixture_proxy_loss_weights", "not_financial_loss"]
    if loss_mode == "affected_mean":
        warnings.append("affected_mean:legacy_baseline")
    return {
        "primary_loss": by_mode[loss_mode],
        "loss_mode": loss_mode,
        "functionality_metric": functionality_metric,
        "functionality_curve": curve,
        "resilience_integral_loss": resilience_loss,
        "graph_weighted_loss": graph_weighted,
        "demand_fulfillment_loss": demand_loss,
        "capacity_functionality_loss": capacity_loss,
        "affected_mean": affected_mean,
        "weight_basis": {
            "weighting_method": weighting_method,
            "node_weight_basis": "fixture_graph_weighted_degree_and_product_capacity_proxy",
            "capacity_basis": "fixture_proxy_not_private_capacity_data",
        },
        "formula_refs": LOSS_FORMULA_REFS,
        "assumptions": [
            "Functionality uses fixture proxy demand/capacity weights because private exposure data is unavailable.",
            "Losses are normalized 0-100 resilience loss scores, not dollar losses.",
        ],
        "calibration_status": "fixture_proxy_not_calibrated",
        "warnings": warnings,
    }


def _graph_weighted_loss(snapshot: SemiriskGraphSnapshot, node_losses: dict[str, float]) -> float:
    weights = _node_weights(snapshot)
    numerator = sum(float(node_losses.get(node_id, 0.0)) * weight for node_id, weight in weights.items())
    denominator = sum(weights.values()) or 1.0
    return round(max(0.0, min(100.0, numerator / denominator * 100.0)), 4)


def _demand_fulfillment_loss(snapshot: SemiriskGraphSnapshot, node_losses: dict[str, float]) -> float:
    product_nodes = {
        node.node_id: 1.4 if node.node_type == "product_grade" else 1.0
        for node in snapshot.nodes
        if node.node_type in {"product_grade", "component", "process_stage", "company"}
    }
    if not product_nodes:
        return _graph_weighted_loss(snapshot, node_losses)
    numerator = sum(float(node_losses.get(node_id, 0.0)) * weight for node_id, weight in product_nodes.items())
    denominator = sum(product_nodes.values()) or 1.0
    return round(max(0.0, min(100.0, numerator / denominator * 100.0)), 4)


def _capacity_functionality_loss(snapshot: SemiriskGraphSnapshot, node_losses: dict[str, float]) -> float:
    capacity_nodes = {
        node.node_id: 1.25 if node.node_type in {"facility", "equipment", "process_stage"} else 1.0
        for node in snapshot.nodes
        if node.node_type in {"facility", "equipment", "process_stage", "company", "material", "chemical"}
    }
    if not capacity_nodes:
        return _graph_weighted_loss(snapshot, node_losses)
    numerator = sum(float(node_losses.get(node_id, 0.0)) * weight for node_id, weight in capacity_nodes.items())
    denominator = sum(capacity_nodes.values()) or 1.0
    return round(max(0.0, min(100.0, numerator / denominator * 100.0)), 4)


def _node_weights(snapshot: SemiriskGraphSnapshot) -> dict[str, float]:
    weights: dict[str, float] = {}
    for node in snapshot.nodes:
        degree_weight = sum(
            edge.weight * edge.confidence
            for edge in snapshot.edges
            if edge.source_node_id == node.node_id or edge.target_node_id == node.node_id
        )
        type_weight = 1.5 if node.node_type in {"company", "equipment", "material", "chemical", "product_grade"} else 1.0
        weights[node.node_id] = max(0.1, degree_weight * type_weight)
    return weights


def _average_recovery_rate(snapshot: SemiriskGraphSnapshot, node_losses: dict[str, float]) -> float:
    rates: list[float] = []
    node_by_id = {node.node_id: node for node in snapshot.nodes}
    for node_id, loss in node_losses.items():
        if loss < 0.01:
            continue
        try:
            rates.append(float(node_by_id[node_id].attributes.get("recovery_rate", 0.25)))
        except (KeyError, TypeError, ValueError):
            rates.append(0.25)
    if not rates:
        return 0.25
    return max(0.0, min(1.0, sum(rates) / len(rates)))
