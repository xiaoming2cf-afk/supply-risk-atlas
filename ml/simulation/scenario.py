from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from graph_kernel.path_index import build_path_index
from sra_core.contracts.domain import EdgeState


TRANSMISSION_EDGE_TYPES = {
    "risk_transmits_to",
    "event_affects",
    "ships_through",
    "route_connects",
    "produces",
    "supplies_to",
    "component_of",
    "input_to",
    "material_processed_into",
    "manufactured_at",
    "stored_at",
    "ships_to",
    "route_leg",
    "handled_at",
    "used_by",
    "substitutes",
    "qualified_alternative_to",
}

MAX_SHOCK_TEXT_LENGTH = 160
MAX_SHOCK_TERM_COUNT = 24
MAX_SHOCK_TERM_LENGTH = 64


@dataclass(frozen=True)
class ScenarioShock:
    region: str = "Red Sea / East Asia corridor"
    commodity: str = "advanced semiconductor components"
    supplier: str | None = None
    route: str | None = None
    severity: int = 72
    duration_days: int = 28
    scope: str = "regional"


def build_scenario_simulation(
    *,
    base_graph_version: str,
    edge_states: list[EdgeState],
    entities: list[Any],
    predictions: list[Any],
    shock: ScenarioShock,
    max_hops: int = 4,
) -> dict[str, Any]:
    entity_by_id = {entity.canonical_id: entity for entity in entities}
    base_paths = build_path_index(edge_states, max_hops=max_hops)
    scenario_edges, changed_edges = apply_scenario_shock(
        base_graph_version=base_graph_version,
        edge_states=edge_states,
        entities=entities,
        shock=shock,
    )
    scenario_paths = build_path_index(scenario_edges, max_hops=max_hops)
    base_pressure = _target_path_pressure(base_paths)
    scenario_pressure = _target_path_pressure(scenario_paths)
    changed_path_rows = _changed_paths(base_paths, scenario_paths, changed_edges, entity_by_id)

    prediction_by_target = {prediction.target_id: prediction for prediction in predictions}
    target_ids = sorted(
        set(base_pressure)
        | set(scenario_pressure)
        | set(prediction_by_target)
    )
    scenario_delta = []
    for target_id in target_ids:
        prediction = prediction_by_target.get(target_id)
        base_risk = float(prediction.risk_score) if prediction else min(1.0, base_pressure.get(target_id, 0.0))
        pressure_delta = scenario_pressure.get(target_id, 0.0) - base_pressure.get(target_id, 0.0)
        if abs(pressure_delta) < 0.002 and target_id not in prediction_by_target:
            continue
        scenario_risk = _clamp(base_risk + pressure_delta * 0.45)
        delta = scenario_risk - base_risk
        if abs(delta) < 0.002:
            continue
        scenario_delta.append(
            {
                "targetId": target_id,
                "targetLabel": _entity_label(entity_by_id, target_id),
                "baselineRisk": round(base_risk, 4),
                "scenarioRisk": round(scenario_risk, 4),
                "delta": round(delta, 4),
                "level": _risk_level(round(scenario_risk * 100)),
            }
        )

    scenario_delta = sorted(
        scenario_delta,
        key=lambda row: (abs(float(row["delta"])), float(row["scenarioRisk"])),
        reverse=True,
    )[:24]
    max_scenario_risk = max((float(row["scenarioRisk"]) for row in scenario_delta), default=0.0)
    max_delta = max((abs(float(row["delta"])) for row in scenario_delta), default=0.0)
    impact_score = round(
        shock.severity * 0.45
        + max_scenario_risk * 38
        + max_delta * 95
        + min(8.0, len(scenario_delta) * 0.35)
    )
    diagnostics = {
        "engine": "graph_propagation_v1",
        "baseGraphVersion": base_graph_version,
        "scenarioGraphVersion": scenario_edges[0].graph_version if scenario_edges else f"scenario_{base_graph_version}",
        "matchedEdges": len(changed_edges),
        "propagatedPathCount": len(changed_path_rows),
        "maxHops": max_hops,
        "shockMultiplier": round(_shock_multiplier(shock), 4),
        "affectedTargets": len(scenario_delta),
        "revenueAtRiskMode": "not_estimated_without_private_financial_exposure_data",
    }
    return {
        "input": {
            "region": shock.region,
            "commodity": shock.commodity,
            "supplier": shock.supplier,
            "route": shock.route,
            "severity": shock.severity,
            "durationDays": shock.duration_days,
            "scope": shock.scope,
        },
        "impactScore": min(99, max(0, impact_score)),
        "scenario_delta": scenario_delta,
        "top_changed_paths": changed_path_rows[:12],
        "diagnostics": diagnostics,
    }


def apply_scenario_shock(
    *,
    base_graph_version: str,
    edge_states: list[EdgeState],
    entities: list[Any],
    shock: ScenarioShock,
) -> tuple[list[EdgeState], dict[str, float]]:
    entity_by_id = {entity.canonical_id: entity for entity in entities}
    multiplier = _shock_multiplier(shock)
    digest = sha256(
        f"{base_graph_version}|{shock.region}|{shock.commodity}|{shock.supplier}|{shock.route}|"
        f"{shock.severity}|{shock.duration_days}|{shock.scope}".encode("utf-8")
    ).hexdigest()[:12]
    scenario_version = f"scenario_{digest}"
    changed_edges: dict[str, float] = {}
    scenario_edges: list[EdgeState] = []
    for edge in edge_states:
        match = _edge_shock_match(edge, entity_by_id, shock)
        if match > 0:
            risk_delta = (1.0 - edge.risk_score) * multiplier * match * 0.55
            weight_delta = multiplier * match * 0.35
            next_risk = _clamp(edge.risk_score + risk_delta)
            next_weight = min(1.8, max(0.0, edge.weight * (1.0 + weight_delta)))
            changed_edges[edge.edge_id] = round((next_risk - edge.risk_score) + (next_weight - edge.weight) * 0.2, 4)
            scenario_edges.append(
                edge.model_copy(
                    update={
                        "risk_score": next_risk,
                        "weight": next_weight,
                        "graph_version": scenario_version,
                    }
                )
            )
            continue
        scenario_edges.append(edge.model_copy(update={"graph_version": scenario_version}))
    return scenario_edges, changed_edges


def normalize_scenario_shock(payload: dict[str, Any] | None) -> ScenarioShock:
    payload = payload or {}
    return ScenarioShock(
        region=_bounded_text(payload.get("region"), "Red Sea / East Asia corridor"),
        commodity=_bounded_text(payload.get("commodity"), "advanced semiconductor components"),
        supplier=_optional_text(payload.get("supplier")),
        route=_optional_text(payload.get("route")),
        severity=_clamp_int(payload.get("severity"), 10, 100, 72),
        duration_days=_clamp_int(payload.get("durationDays") or payload.get("duration_days"), 3, 90, 28),
        scope=str(payload.get("scope")) if payload.get("scope") in {"facility", "regional", "global"} else "regional",
    )


def _changed_paths(
    base_paths: list[Any],
    scenario_paths: list[Any],
    changed_edges: dict[str, float],
    entity_by_id: dict[str, Any],
) -> list[dict[str, Any]]:
    base_by_id = {path.path_id: path for path in base_paths}
    rows: list[dict[str, Any]] = []
    for path in scenario_paths:
        touched_edges = [edge_id for edge_id in path.edge_sequence if edge_id in changed_edges]
        if not touched_edges:
            continue
        base_score = _path_score(base_by_id.get(path.path_id)) if path.path_id in base_by_id else 0.0
        scenario_score = _path_score(path)
        delta = scenario_score - base_score
        if abs(delta) < 0.001:
            continue
        rows.append(
            {
                "pathId": path.path_id,
                "sourceId": path.source_id,
                "targetId": path.target_id,
                "sourceLabel": _entity_label(entity_by_id, path.source_id),
                "targetLabel": _entity_label(entity_by_id, path.target_id),
                "nodeSequence": list(path.node_sequence),
                "edgeSequence": list(path.edge_sequence),
                "changedEdges": touched_edges,
                "baseScore": round(base_score, 4),
                "scenarioScore": round(scenario_score, 4),
                "delta": round(delta, 4),
                "level": _risk_level(round(scenario_score * 100)),
            }
        )
    return sorted(rows, key=lambda row: abs(float(row["delta"])), reverse=True)


def _target_path_pressure(paths: list[Any]) -> dict[str, float]:
    pressure: dict[str, float] = {}
    for path in paths:
        if not any(edge_type in TRANSMISSION_EDGE_TYPES for edge_type in path.meta_path.split(">")):
            continue
        pressure[path.target_id] = pressure.get(path.target_id, 0.0) + _path_score(path)
    return {target_id: min(1.0, value) for target_id, value in pressure.items()}


def _path_score(path: Any | None) -> float:
    if path is None:
        return 0.0
    return _clamp(path.path_risk) * _clamp(path.path_confidence) * max(0.12, float(path.path_weight or 0.0))


def _edge_shock_match(edge: EdgeState, entity_by_id: dict[str, Any], shock: ScenarioShock) -> float:
    source = entity_by_id.get(edge.source_id)
    target = entity_by_id.get(edge.target_id)
    texts = [
        edge.edge_id,
        edge.edge_type,
        edge.source,
        edge.source_id,
        edge.target_id,
        _entity_text(source),
        _entity_text(target),
    ]
    haystack = " ".join(texts).lower()
    match = 0.0
    region_terms = _region_terms(shock.region)
    if any(term and term in haystack for term in region_terms):
        match = max(match, 0.85)
    commodity_terms = _terms(shock.commodity)
    if any(term and term in haystack for term in commodity_terms):
        match = max(match, 0.72)
    if shock.supplier and any(term and term in haystack for term in _terms(shock.supplier)):
        match = max(match, 0.95)
    if shock.route and any(term and term in haystack for term in _terms(shock.route)):
        match = max(match, 0.95)
    if edge.edge_type in {"ships_through", "route_connects", "ships_to", "route_leg", "handled_at"} and match > 0:
        match = min(1.0, match + 0.12)
    if edge.edge_type in {
        "supplies_to",
        "component_of",
        "input_to",
        "material_processed_into",
        "manufactured_at",
        "stored_at",
        "used_by",
    } and match > 0:
        match = min(1.0, match + 0.08)
    if edge.edge_type in {"substitutes", "qualified_alternative_to"} and match > 0:
        match = min(1.0, match + 0.04)
    if edge.edge_type in {"dataset_observes", "source_provides", "licensed_under"}:
        match *= 0.2
    return match


def _region_terms(region: str) -> set[str]:
    region_text = region.lower()
    terms = set(_terms(region))
    if "taiwan" in region_text:
        terms.update({"taiwan", "kaohsiung", "tw", "twn", "semiconductor"})
    if "red sea" in region_text or "suez" in region_text:
        terms.update({"red sea", "suez", "egypt", "eg", "shipping"})
    if "panama" in region_text:
        terms.update({"panama", "canal", "shipping"})
    if "rhine" in region_text:
        terms.update({"rhine", "germany", "de", "chemical"})
    return terms


def _terms(value: str) -> set[str]:
    normalized = value.lower().replace("/", " ").replace("-", " ")
    pieces: list[str] = []
    for raw_piece in normalized.split():
        piece = raw_piece.strip()[:MAX_SHOCK_TERM_LENGTH]
        if len(piece) >= 2 and piece not in pieces:
            pieces.append(piece)
        if len(pieces) >= MAX_SHOCK_TERM_COUNT:
            break
    base = value.strip().lower()[:MAX_SHOCK_TEXT_LENGTH]
    if base:
        pieces.append(base)
    return set(pieces)


def _entity_text(entity: Any | None) -> str:
    if entity is None:
        return ""
    external_ids = getattr(entity, "external_ids", {}) or {}
    return " ".join(
        [
            getattr(entity, "canonical_id", ""),
            getattr(entity, "entity_type", ""),
            getattr(entity, "display_name", ""),
            getattr(entity, "country", "") or "",
            getattr(entity, "industry", "") or "",
            *[str(value) for value in external_ids.values()],
        ]
    )


def _entity_label(entity_by_id: dict[str, Any], entity_id: str) -> str:
    entity = entity_by_id.get(entity_id)
    return getattr(entity, "display_name", entity_id) if entity is not None else entity_id


def _shock_multiplier(shock: ScenarioShock) -> float:
    scope = {"facility": 0.72, "regional": 1.0, "global": 1.22}.get(shock.scope, 1.0)
    duration = min(1.45, max(0.25, shock.duration_days / 35.0))
    return min(1.0, (shock.severity / 100.0) * scope * duration)


def _optional_text(value: Any) -> str | None:
    text = _bounded_text(value, "")
    return text or None


def _bounded_text(value: Any, default: str) -> str:
    text = " ".join(str(value or "").split())
    if not text:
        return default
    return text[:MAX_SHOCK_TEXT_LENGTH]


def _clamp(value: Any, lower: float = 0.0, upper: float = 1.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return lower
    return max(lower, min(upper, numeric))


def _clamp_int(value: Any, minimum: int, maximum: int, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _risk_level(score: int) -> str:
    if score >= 88:
        return "critical"
    if score >= 74:
        return "severe"
    if score >= 58:
        return "elevated"
    if score >= 40:
        return "guarded"
    return "low"
