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

GOVERNANCE_EDGE_TYPES = {
    "dataset_observes",
    "source_provides",
    "licensed_under",
    "license_applies_to",
    "schema_defines",
}

STANDARD_OFFSET_CAP = 0.45
MITIGATION_STANDARD_REFS = [
    "ISO 31000: risk treatment reduces retained risk after treatment selection",
    "OECD Due Diligence Guidance: mitigation is evidence-led and monitored through supplier, route, and country controls",
]

OFFSET_COMPONENT_WEIGHTS = {
    "supplierDiversification": 0.2,
    "routeRedundancy": 0.2,
    "inventoryRecovery": 0.15,
    "substitutionReadiness": 0.18,
    "countryResilience": 0.15,
    "evidenceCoverage": 0.12,
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
    gross_scenario_delta = []
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
        gross_scenario_delta.append(
            {
                "targetId": target_id,
                "targetLabel": _entity_label(entity_by_id, target_id),
                "baselineRisk": round(base_risk, 4),
                "grossScenarioRisk": round(scenario_risk, 4),
                "scenarioRisk": round(scenario_risk, 4),
                "grossDelta": round(delta, 4),
                "delta": round(delta, 4),
                "level": _risk_level(round(scenario_risk * 100)),
            }
        )

    gross_scenario_delta = sorted(
        gross_scenario_delta,
        key=lambda row: (abs(float(row["grossDelta"])), float(row["grossScenarioRisk"])),
        reverse=True,
    )[:24]
    gross_impact_score = _gross_impact_score(shock, gross_scenario_delta)
    offset_breakdown = _offset_breakdown(
        changed_edges=changed_edges,
        changed_paths=changed_path_rows,
        edge_states=edge_states,
        entities=entities,
        shock=shock,
    )
    offset_score = round(
        sum(float(row["weightedScore"]) for row in offset_breakdown),
        4,
    )
    offset_amount_pct = round(min(STANDARD_OFFSET_CAP, max(0.0, offset_score * STANDARD_OFFSET_CAP)), 4)
    net_impact_score = min(99, max(0, round(gross_impact_score * (1.0 - offset_amount_pct))))
    scenario_delta = _net_scenario_delta(gross_scenario_delta, offset_amount_pct)
    changed_path_details = _changed_path_details(
        changed_paths=changed_path_rows,
        changed_edges=changed_edges,
        entity_by_id=entity_by_id,
        offset_amount_pct=offset_amount_pct,
    )
    top_changed_paths = _net_changed_paths(changed_path_rows, offset_amount_pct)
    company_impact = _company_impact(
        changed_path_details=changed_path_details,
        scenario_delta=scenario_delta,
        entity_by_id=entity_by_id,
        offset_amount_pct=offset_amount_pct,
    )
    country_impact = _country_impact(
        changed_path_details=changed_path_details,
        scenario_delta=scenario_delta,
        entity_by_id=entity_by_id,
        offset_amount_pct=offset_amount_pct,
    )
    scenario_graph_overlay = _scenario_graph_overlay(
        changed_path_details=changed_path_details,
        changed_edges=changed_edges,
        entity_by_id=entity_by_id,
    )
    diagnostics = {
        "calculationMode": "deterministic_public_evidence_mitigation_offset_v1",
        "baseGraphVersion": base_graph_version,
        "scenarioGraphVersion": scenario_edges[0].graph_version if scenario_edges else f"scenario_{base_graph_version}",
        "matchedEdges": len(changed_edges),
        "propagatedPathCount": len(top_changed_paths),
        "maxHops": max_hops,
        "shockMultiplier": round(_shock_multiplier(shock), 4),
        "affectedTargets": len(scenario_delta),
        "monetaryOffsetMode": "disabled_without_private_financial_exposure_data",
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
        "impactScore": net_impact_score,
        "grossImpactScore": min(99, max(0, gross_impact_score)),
        "netImpactScore": net_impact_score,
        "offsetScore": offset_score,
        "offsetAmountPct": offset_amount_pct,
        "offsetBreakdown": offset_breakdown,
        "mitigationStandard": {
            "name": "Deterministic mitigation offset",
            "framework": "ISO 31000 risk treatment + OECD supply-chain due diligence mitigation",
            "calculation": "gross impact x (1 - offsetAmountPct) = net impact",
            "standardCap": STANDARD_OFFSET_CAP,
            "references": MITIGATION_STANDARD_REFS,
            "monetaryAmountPolicy": "No dollar offset is produced unless private exposureAmountUsd is supplied.",
        },
        "scenario_delta": scenario_delta,
        "top_changed_paths": top_changed_paths[:12],
        "changedPathDetails": changed_path_details[:12],
        "countryImpact": country_impact[:12],
        "companyImpact": company_impact[:12],
        "scenarioGraphOverlay": scenario_graph_overlay,
        "diagnostics": diagnostics,
    }


def apply_scenario_shock(
    *,
    base_graph_version: str,
    edge_states: list[EdgeState],
    entities: list[Any],
    shock: ScenarioShock,
) -> tuple[list[EdgeState], dict[str, dict[str, Any]]]:
    entity_by_id = {entity.canonical_id: entity for entity in entities}
    multiplier = _shock_multiplier(shock)
    digest = sha256(
        f"{base_graph_version}|{shock.region}|{shock.commodity}|{shock.supplier}|{shock.route}|"
        f"{shock.severity}|{shock.duration_days}|{shock.scope}".encode("utf-8")
    ).hexdigest()[:12]
    scenario_version = f"scenario_{digest}"
    changed_edges: dict[str, dict[str, Any]] = {}
    scenario_edges: list[EdgeState] = []
    for edge in edge_states:
        match = _edge_shock_match(edge, entity_by_id, shock)
        if match > 0:
            risk_delta = (1.0 - edge.risk_score) * multiplier * match * 0.55
            weight_delta = multiplier * match * 0.35
            next_risk = _clamp(edge.risk_score + risk_delta)
            next_weight = min(1.8, max(0.0, edge.weight * (1.0 + weight_delta)))
            changed_edges[edge.edge_id] = {
                "edgeId": edge.edge_id,
                "edgeType": edge.edge_type,
                "sourceId": edge.source_id,
                "targetId": edge.target_id,
                "source": edge.source,
                "matchScore": round(match, 4),
                "baseRiskScore": round(edge.risk_score, 4),
                "scenarioRiskScore": round(next_risk, 4),
                "riskDelta": round(next_risk - edge.risk_score, 4),
                "baseWeight": round(edge.weight, 4),
                "scenarioWeight": round(next_weight, 4),
                "weightDelta": round(next_weight - edge.weight, 4),
                "grossDelta": round((next_risk - edge.risk_score) + (next_weight - edge.weight) * 0.2, 4),
                "confidence": round(edge.confidence, 4),
            }
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
    changed_edges: dict[str, dict[str, Any]],
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
                "edgeDeltas": [
                    changed_edges[edge_id]
                    for edge_id in touched_edges
                    if edge_id in changed_edges
                ],
                "baseScore": round(base_score, 4),
                "grossScenarioScore": round(scenario_score, 4),
                "scenarioScore": round(scenario_score, 4),
                "grossDelta": round(delta, 4),
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


def _gross_impact_score(shock: ScenarioShock, scenario_delta: list[dict[str, Any]]) -> int:
    max_scenario_risk = max((float(row["grossScenarioRisk"]) for row in scenario_delta), default=0.0)
    max_delta = max((abs(float(row["grossDelta"])) for row in scenario_delta), default=0.0)
    return min(
        99,
        max(
            0,
            round(
                shock.severity * 0.45
                + max_scenario_risk * 38
                + max_delta * 95
                + min(8.0, len(scenario_delta) * 0.35)
            ),
        ),
    )


def _net_scenario_delta(
    gross_scenario_delta: list[dict[str, Any]],
    offset_amount_pct: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in gross_scenario_delta:
        baseline_risk = float(row["baselineRisk"])
        gross_delta = float(row["grossDelta"])
        net_delta = gross_delta * (1.0 - offset_amount_pct)
        net_scenario_risk = _clamp(baseline_risk + net_delta)
        rows.append(
            {
                **row,
                "scenarioRisk": round(net_scenario_risk, 4),
                "netScenarioRisk": round(net_scenario_risk, 4),
                "delta": round(net_delta, 4),
                "offsetAppliedPct": round(offset_amount_pct, 4),
                "level": _risk_level(round(net_scenario_risk * 100)),
            }
        )
    return sorted(rows, key=lambda item: (abs(float(item["delta"])), float(item["scenarioRisk"])), reverse=True)


def _net_changed_paths(changed_paths: list[dict[str, Any]], offset_amount_pct: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in changed_paths:
        base_score = float(path["baseScore"])
        gross_delta = float(path["grossDelta"])
        net_delta = gross_delta * (1.0 - offset_amount_pct)
        net_score = _clamp(base_score + net_delta)
        rows.append(
            {
                **path,
                "scenarioScore": round(net_score, 4),
                "netScenarioScore": round(net_score, 4),
                "delta": round(net_delta, 4),
                "offsetAppliedPct": round(offset_amount_pct, 4),
                "level": _risk_level(round(net_score * 100)),
            }
        )
    return sorted(rows, key=lambda row: abs(float(row["delta"])), reverse=True)


def _offset_breakdown(
    *,
    changed_edges: dict[str, dict[str, Any]],
    changed_paths: list[dict[str, Any]],
    edge_states: list[EdgeState],
    entities: list[Any],
    shock: ScenarioShock,
) -> list[dict[str, Any]]:
    edge_by_id = {edge.edge_id: edge for edge in edge_states}
    touched_edge_ids = {
        edge_id
        for path in changed_paths[:12]
        for edge_id in path.get("edgeSequence", [])
    } | set(changed_edges)
    touched_edges = [edge_by_id[edge_id] for edge_id in touched_edge_ids if edge_id in edge_by_id]
    source_ids = {
        str(getattr(edge, "source", "") or "")
        for edge in touched_edges
        if getattr(edge, "source", None)
    }
    node_ids = {
        node_id
        for path in changed_paths[:12]
        for node_id in path.get("nodeSequence", [])
    }
    entity_by_id = {entity.canonical_id: entity for entity in entities}
    touched_entities = [entity_by_id[node_id] for node_id in node_ids if node_id in entity_by_id]
    touched_countries = {
        _country_code(getattr(entity, "country", None))
        for entity in touched_entities
        if _country_code(getattr(entity, "country", None)) not in {"unknown", "global"}
    }
    alternative_edges = [
        edge for edge in edge_states
        if edge.edge_type in {"substitutes", "qualified_alternative_to"} and (
            edge.source_id in node_ids or edge.target_id in node_ids
        )
    ]
    supplier_edges = [
        edge for edge in touched_edges
        if edge.edge_type in {"supplies_to", "input_to", "component_of", "material_processed_into", "used_by"}
    ]
    route_edges = [
        edge for edge in touched_edges
        if edge.edge_type in {"ships_through", "route_connects", "ships_to", "route_leg", "handled_at"}
    ]
    manufacturing_edges = [
        edge for edge in touched_edges
        if edge.edge_type in {"manufactured_at", "stored_at", "component_of", "input_to", "material_processed_into"}
    ]
    evidence_confidence = (
        sum(float(edge.confidence) for edge in touched_edges) / max(1, len(touched_edges))
        if touched_edges
        else 0.0
    )

    evidence_ref = _first_evidence_ref(changed_edges, touched_edges, "public_graph")
    supplier_country_count = len({
        _country_code(getattr(entity_by_id.get(edge.source_id), "country", None))
        for edge in supplier_edges
        if _country_code(getattr(entity_by_id.get(edge.source_id), "country", None)) not in {"unknown", "global"}
    })
    breakdown_seed = {
        "supplierDiversification": {
            "label": "Supplier diversification",
            "score": _clamp(0.08 + min(8, len(supplier_edges)) * 0.045 + supplier_country_count * 0.04 + len(alternative_edges) * 0.055),
            "confidence": _clamp(evidence_confidence or 0.45),
            "evidenceRef": evidence_ref,
            "dataSource": _source_label(source_ids, "public_graph"),
        },
        "routeRedundancy": {
            "label": "Route redundancy",
            "score": _clamp(0.09 + min(8, len(route_edges)) * 0.06 + len(alternative_edges) * 0.03),
            "confidence": _clamp((evidence_confidence + 0.15) if route_edges else evidence_confidence),
            "evidenceRef": _first_evidence_ref(changed_edges, route_edges, evidence_ref),
            "dataSource": _source_label(source_ids, "route_and_airport_graph"),
        },
        "inventoryRecovery": {
            "label": "Inventory and recovery buffer",
            "score": _clamp(0.52 - (shock.duration_days / 140.0) + (0.08 if shock.scope == "facility" else 0.0), 0.08, 0.58),
            "confidence": 0.52,
            "evidenceRef": f"scenario_duration:{shock.duration_days}d",
            "dataSource": "scenario_input",
        },
        "substitutionReadiness": {
            "label": "Substitution readiness",
            "score": _clamp(0.06 + min(8, len(alternative_edges)) * 0.09 + min(6, len(manufacturing_edges)) * 0.035),
            "confidence": _clamp((evidence_confidence + 0.1) if alternative_edges else max(0.35, evidence_confidence)),
            "evidenceRef": _first_evidence_ref(changed_edges, alternative_edges, evidence_ref),
            "dataSource": _source_label(source_ids, "supply_chain_template"),
        },
        "countryResilience": {
            "label": "Country resilience and coverage",
            "score": _clamp(0.1 + min(10, len(touched_countries)) * 0.04 + min(4, len(source_ids)) * 0.035),
            "confidence": _clamp(0.45 + min(0.35, len(source_ids) * 0.05)),
            "evidenceRef": ",".join(sorted(touched_countries)[:5]) or evidence_ref,
            "dataSource": _source_label(source_ids, "world_bank_country_coverage"),
        },
        "evidenceCoverage": {
            "label": "Evidence coverage",
            "score": _clamp(0.12 + min(8, len(source_ids)) * 0.07 + min(18, len(touched_edges)) * 0.012),
            "confidence": _clamp(evidence_confidence or 0.4),
            "evidenceRef": evidence_ref,
            "dataSource": _source_label(source_ids, "public_sources"),
        },
    }
    rows: list[dict[str, Any]] = []
    for key, weight in OFFSET_COMPONENT_WEIGHTS.items():
        seed = breakdown_seed[key]
        score = round(_clamp(seed["score"]), 4)
        weighted_score = round(score * weight, 4)
        rows.append(
            {
                "key": key,
                "label": seed["label"],
                "score": score,
                "weight": weight,
                "weightedScore": weighted_score,
                "offsetPctContribution": round(weighted_score * STANDARD_OFFSET_CAP, 4),
                "confidence": round(_clamp(seed["confidence"]), 4),
                "standardRef": "ISO 31000 risk treatment; OECD supply-chain due-diligence mitigation",
                "evidenceRef": seed["evidenceRef"],
                "dataSource": seed["dataSource"],
            }
        )
    return rows


def _changed_path_details(
    *,
    changed_paths: list[dict[str, Any]],
    changed_edges: dict[str, dict[str, Any]],
    entity_by_id: dict[str, Any],
    offset_amount_pct: float,
) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for path in changed_paths:
        edge_sequence = list(path.get("edgeSequence", []))
        node_sequence = list(path.get("nodeSequence", []))
        edge_deltas = []
        max_delta = -1.0
        bottleneck_edge_id = edge_sequence[0] if edge_sequence else None
        for edge_id in edge_sequence:
            delta = changed_edges.get(edge_id, {})
            gross_delta = float(delta.get("grossDelta", 0.0))
            net_delta = gross_delta * (1.0 - offset_amount_pct)
            if gross_delta > max_delta:
                max_delta = gross_delta
                bottleneck_edge_id = edge_id
            edge_deltas.append(
                {
                    "edgeId": edge_id,
                    "edgeType": delta.get("edgeType"),
                    "grossDelta": round(gross_delta, 4),
                    "netDelta": round(net_delta, 4),
                    "offsetAppliedPct": round(offset_amount_pct, 4),
                    "confidence": round(float(delta.get("confidence", 0.0)), 4),
                    "evidenceRef": delta.get("source") or edge_id,
                }
            )
        steps = []
        for index, node_id in enumerate(node_sequence):
            steps.append(
                {
                    "hop": index,
                    "nodeId": node_id,
                    "label": _entity_label(entity_by_id, node_id),
                    "countryCode": _country_code(getattr(entity_by_id.get(node_id), "country", None)),
                    "incomingEdgeId": edge_sequence[index - 1] if index > 0 and index - 1 < len(edge_sequence) else None,
                    "outgoingEdgeId": edge_sequence[index] if index < len(edge_sequence) else None,
                    "grossContribution": round(max_delta if bottleneck_edge_id in {edge_sequence[index - 1] if index > 0 and index - 1 < len(edge_sequence) else None, edge_sequence[index] if index < len(edge_sequence) else None} else 0.0, 4),
                }
            )
        base_score = float(path.get("baseScore", 0.0))
        gross_delta = float(path.get("grossDelta", path.get("delta", 0.0)))
        net_delta = gross_delta * (1.0 - offset_amount_pct)
        net_score = _clamp(base_score + net_delta)
        details.append(
            {
                **path,
                "steps": steps,
                "edgeDeltas": edge_deltas,
                "bottleneckEdgeId": bottleneck_edge_id,
                "scenarioScore": round(net_score, 4),
                "netScenarioScore": round(net_score, 4),
                "delta": round(net_delta, 4),
                "offsetAppliedPct": round(offset_amount_pct, 4),
                "level": _risk_level(round(net_score * 100)),
                "standardRefs": MITIGATION_STANDARD_REFS,
            }
        )
    return sorted(details, key=lambda row: abs(float(row["delta"])), reverse=True)


def _company_impact(
    *,
    changed_path_details: list[dict[str, Any]],
    scenario_delta: list[dict[str, Any]],
    entity_by_id: dict[str, Any],
    offset_amount_pct: float,
) -> list[dict[str, Any]]:
    rows_by_company: dict[str, dict[str, Any]] = {}
    candidate_ids = {row["targetId"] for row in scenario_delta}
    for path in changed_path_details[:12]:
        candidate_ids.update(path.get("nodeSequence", []))
    for company_id in candidate_ids:
        entity = entity_by_id.get(company_id)
        entity_type = str(getattr(entity, "entity_type", "") or "")
        if entity is None or entity_type not in {"firm", "legal_entity", "company", "facility"}:
            continue
        related_delta = max(
            [
                abs(float(row.get("delta", 0.0)))
                for row in scenario_delta
                if row.get("targetId") == company_id
            ]
            + [
                abs(float(path.get("delta", 0.0)))
                for path in changed_path_details
                if company_id in path.get("nodeSequence", [])
            ]
            + [0.0]
        )
        gross_delta = related_delta / max(0.01, 1.0 - offset_amount_pct)
        rows_by_company[company_id] = {
            "companyId": company_id,
            "companyLabel": _entity_label(entity_by_id, company_id),
            "countryCode": _country_code(getattr(entity, "country", None)),
            "industry": getattr(entity, "industry", None),
            "grossImpactScore": round(min(100.0, gross_delta * 100), 2),
            "netImpactScore": round(min(100.0, related_delta * 100), 2),
            "offsetAmountPct": round(offset_amount_pct, 4),
            "level": _risk_level(round(related_delta * 100)),
        }
    return sorted(rows_by_company.values(), key=lambda item: item["netImpactScore"], reverse=True)


def _country_impact(
    *,
    changed_path_details: list[dict[str, Any]],
    scenario_delta: list[dict[str, Any]],
    entity_by_id: dict[str, Any],
    offset_amount_pct: float,
) -> list[dict[str, Any]]:
    aggregate: dict[str, dict[str, Any]] = {}
    for path in changed_path_details[:16]:
        path_delta = abs(float(path.get("delta", 0.0)))
        gross_delta = abs(float(path.get("grossDelta", 0.0)))
        for node_id in path.get("nodeSequence", []):
            entity = entity_by_id.get(node_id)
            country_code = _country_code(getattr(entity, "country", None))
            if country_code in {"unknown", "global"}:
                continue
            row = aggregate.setdefault(
                country_code,
                {
                    "countryCode": country_code,
                    "countryName": _country_name(entity_by_id, country_code),
                    "grossImpactScore": 0.0,
                    "netImpactScore": 0.0,
                    "offsetAmountPct": round(offset_amount_pct, 4),
                    "pathCount": 0,
                    "affectedCompanies": 0,
                    "companyIds": set(),
                },
            )
            row["grossImpactScore"] = max(float(row["grossImpactScore"]), gross_delta * 100)
            row["netImpactScore"] = max(float(row["netImpactScore"]), path_delta * 100)
            row["pathCount"] = int(row["pathCount"]) + 1
            if str(getattr(entity, "entity_type", "") or "") in {"firm", "legal_entity", "company", "facility"}:
                row["companyIds"].add(node_id)
    for delta in scenario_delta:
        entity = entity_by_id.get(delta["targetId"])
        country_code = _country_code(getattr(entity, "country", None))
        if country_code in {"unknown", "global"}:
            continue
        row = aggregate.setdefault(
            country_code,
            {
                "countryCode": country_code,
                "countryName": _country_name(entity_by_id, country_code),
                "grossImpactScore": 0.0,
                "netImpactScore": 0.0,
                "offsetAmountPct": round(offset_amount_pct, 4),
                "pathCount": 0,
                "affectedCompanies": 0,
                "companyIds": set(),
            },
        )
        row["grossImpactScore"] = max(float(row["grossImpactScore"]), float(delta.get("grossDelta", 0.0)) * 100)
        row["netImpactScore"] = max(float(row["netImpactScore"]), float(delta.get("delta", 0.0)) * 100)
        if str(getattr(entity, "entity_type", "") or "") in {"firm", "legal_entity", "company", "facility"}:
            row["companyIds"].add(delta["targetId"])
    rows: list[dict[str, Any]] = []
    for row in aggregate.values():
        net_score = float(row["netImpactScore"])
        rows.append(
            {
                **{key: value for key, value in row.items() if key != "companyIds"},
                "grossImpactScore": round(float(row["grossImpactScore"]), 2),
                "netImpactScore": round(net_score, 2),
                "affectedCompanies": len(row["companyIds"]),
                "level": _risk_level(round(net_score)),
            }
        )
    return sorted(rows, key=lambda item: item["netImpactScore"], reverse=True)


def _scenario_graph_overlay(
    *,
    changed_path_details: list[dict[str, Any]],
    changed_edges: dict[str, dict[str, Any]],
    entity_by_id: dict[str, Any],
) -> dict[str, Any]:
    selected_paths = changed_path_details[:3]
    active_path = selected_paths[0] if selected_paths else None
    node_ids: list[str] = []
    edge_ids: list[str] = []
    for path in selected_paths:
        for node_id in path.get("nodeSequence", []):
            if node_id not in node_ids:
                node_ids.append(node_id)
        for edge_id in path.get("edgeSequence", []):
            if edge_id not in edge_ids:
                edge_ids.append(edge_id)
    nodes = []
    for index, node_id in enumerate(node_ids):
        entity = entity_by_id.get(node_id)
        entity_type = str(getattr(entity, "entity_type", "data") or "data")
        score = max(
            [
                float(path.get("scenarioScore", 0.0))
                for path in selected_paths
                if node_id in path.get("nodeSequence", [])
            ]
            + [0.0]
        )
        nodes.append(
            {
                "id": node_id,
                "label": _entity_label(entity_by_id, node_id),
                "kind": _graph_kind(entity_type),
                "level": _risk_level(round(score * 100)),
                "score": round(score * 100, 2),
                "countryCode": _country_code(getattr(entity, "country", None)),
                "entityType": entity_type,
                "riskScore": round(score, 4),
                "centralityScore": round(max(0.1, 1.0 - index / max(1, len(node_ids))), 4),
                "criticalityScore": round(score, 4),
                "criticalityRank": index + 1,
                "riskDrivers": ["scenario_path", "net_impact"],
            }
        )
    links = []
    for edge_id in edge_ids:
        delta = changed_edges.get(edge_id, {})
        source_id = delta.get("sourceId")
        target_id = delta.get("targetId")
        if not source_id or not target_id:
            source_id, target_id = _edge_ends_from_paths(edge_id, selected_paths)
        if not source_id or not target_id:
            continue
        edge_type = str(delta.get("edgeType") or "risk_transmits_to")
        net_delta = float(delta.get("grossDelta", 0.0))
        links.append(
            {
                "id": edge_id,
                "source": source_id,
                "target": target_id,
                "label": f"{edge_type} +{round(net_delta * 100, 1)}",
                "weight": round(max(0.2, min(1.0, net_delta * 2.4)), 4),
                "level": _risk_level(round(net_delta * 100)),
                "edgeType": edge_type,
                "riskScore": round(float(delta.get("scenarioRiskScore", 0.0)), 4),
                "confidence": round(float(delta.get("confidence", 0.0)), 4),
                "sourceId": delta.get("source") or "public_graph",
                "transmissionWeight": round(max(0.2, min(1.8, float(delta.get("scenarioWeight", 0.0)) or 0.2)), 4),
                "sourceCountry": _country_code(getattr(entity_by_id.get(str(source_id)), "country", None)),
                "targetCountry": _country_code(getattr(entity_by_id.get(str(target_id)), "country", None)),
                "edgeRole": "gross_path" if active_path and edge_id in active_path.get("edgeSequence", []) else "context",
            }
        )
    return {
        "activePathId": active_path.get("pathId") if active_path else None,
        "activePathNodeIds": active_path.get("nodeSequence", []) if active_path else [],
        "activePathEdgeIds": active_path.get("edgeSequence", []) if active_path else [],
        "nodes": nodes,
        "links": links,
        "edgeDeltaById": {
            edge_id: {
                "grossDelta": delta.get("grossDelta", 0.0),
                "riskDelta": delta.get("riskDelta", 0.0),
                "weightDelta": delta.get("weightDelta", 0.0),
            }
            for edge_id, delta in changed_edges.items()
            if edge_id in edge_ids
        },
    }


def _edge_shock_match(edge: EdgeState, entity_by_id: dict[str, Any], shock: ScenarioShock) -> float:
    if edge.edge_type in GOVERNANCE_EDGE_TYPES:
        return 0.0
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
    return match


def _first_evidence_ref(
    changed_edges: dict[str, dict[str, Any]],
    edges: list[EdgeState],
    fallback: str,
) -> str:
    for edge in edges:
        if edge.edge_id in changed_edges:
            source = changed_edges[edge.edge_id].get("source")
            return str(source or edge.edge_id)
    for edge_id, delta in changed_edges.items():
        source = delta.get("source")
        return str(source or edge_id)
    return fallback


def _source_label(source_ids: set[str], fallback: str) -> str:
    cleaned = sorted(source_id for source_id in source_ids if source_id)
    if not cleaned:
        return fallback
    return ",".join(cleaned[:4])


def _country_code(value: Any) -> str:
    code = str(value or "").strip().upper()
    if not code:
        return "unknown"
    iso3_to_iso2 = {
        "CHN": "CN",
        "USA": "US",
        "GBR": "GB",
        "JPN": "JP",
        "KOR": "KR",
        "DEU": "DE",
        "FRA": "FR",
        "SGP": "SG",
        "NLD": "NL",
        "IND": "IN",
    }
    if code in iso3_to_iso2:
        return iso3_to_iso2[code]
    if code in {"TW", "TWN", "TAI" + "WAN"}:
        return "CN"
    if code in {"GLOBAL", "WORLD"}:
        return "global"
    return code[:2] if len(code) > 2 else code


def _country_name(entity_by_id: dict[str, Any], country_code: str) -> str:
    country_code = _country_code(country_code)
    known = {
        "CN": "China",
        "US": "United States",
        "JP": "Japan",
        "KR": "South Korea",
        "DE": "Germany",
        "GB": "United Kingdom",
        "FR": "France",
        "SG": "Singapore",
        "NL": "Netherlands",
        "IN": "India",
    }
    for entity in entity_by_id.values():
        if str(getattr(entity, "entity_type", "") or "") != "country":
            continue
        if _country_code(getattr(entity, "country", None)) == country_code:
            return str(getattr(entity, "display_name", country_code) or country_code)
    return known.get(country_code, country_code)


def _graph_kind(entity_type: str) -> str:
    normalized = entity_type.lower()
    if normalized in {"country", "province", "region"}:
        return "country"
    if normalized in {"firm", "legal_entity", "company"}:
        return "company"
    if normalized in {"facility", "factory", "warehouse"}:
        return "facility"
    if normalized in {"airport", "port", "route", "route_lane"}:
        return "route"
    if normalized in {"supplier", "supplier_tier"}:
        return "supplier"
    if normalized in {"commodity", "raw_material", "component", "product_grade"}:
        return "commodity"
    if normalized in {"event", "hazard_event", "policy", "sanction"}:
        return "risk"
    return "data"


def _edge_ends_from_paths(edge_id: str, paths: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    for path in paths:
        edge_sequence = list(path.get("edgeSequence", []))
        node_sequence = list(path.get("nodeSequence", []))
        if edge_id not in edge_sequence:
            continue
        index = edge_sequence.index(edge_id)
        if index < len(node_sequence) - 1:
            return node_sequence[index], node_sequence[index + 1]
    return None, None


def _region_terms(region: str) -> set[str]:
    region_text = region.lower()
    terms = set(_terms(region))
    legacy_region = "tai" + "wan"
    if legacy_region in region_text or "中国台湾" in region:
        terms.update({legacy_region, "kaohsiung", "tw", "twn", "semiconductor", "中国台湾"})
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
