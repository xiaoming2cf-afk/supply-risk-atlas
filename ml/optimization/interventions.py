from __future__ import annotations

from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.risk_scoring.semirisk_score import rank_risk_portfolio
from ml.simulation.monte_carlo import run_forward_monte_carlo
from ml.simulation.scenario_schema import FIXTURE_GRAPH_WARNING, stable_run_id
from sra_core.contracts.semiconductor import SemiriskGraphSnapshot

from .baselines import baseline_comparison
from .constraints import normalize_optimization_request, validate_action
from .objectives import resilience_roi, risk_adjusted_value


OPTIMIZATION_VERSION = "semirisk_intervention_optimizer_v0.1"

ACTION_LIBRARY = {
    "add_alternative_supplier": {"cost": 30, "expected": 4.2, "cvar": 5.4, "target_types": {"company", "material", "chemical"}},
    "increase_inventory_buffer": {"cost": 18, "expected": 3.4, "cvar": 4.6, "target_types": {"material", "chemical", "equipment"}},
    "regional_diversification": {"cost": 35, "expected": 4.8, "cvar": 5.8, "target_types": {"country", "company", "facility"}},
    "improve_recovery_rate": {"cost": 22, "expected": 3.8, "cvar": 4.2, "target_types": {"facility", "company", "process_stage"}},
    "add_policy_monitoring": {"cost": 12, "expected": 1.4, "cvar": 2.8, "target_types": {"policy_event", "company", "country"}},
    "route_redundancy": {"cost": 24, "expected": 3.2, "cvar": 4.4, "target_types": {"route", "country", "company"}},
    "qualify_backup_material": {"cost": 26, "expected": 4.0, "cvar": 5.0, "target_types": {"material", "chemical", "product_grade"}},
}


def run_intervention_optimization(
    payload: dict[str, Any],
    *,
    snapshot: SemiriskGraphSnapshot | None = None,
) -> dict[str, Any]:
    request = normalize_optimization_request(payload)
    graph = snapshot or build_semiconductor_fixture_snapshot(as_of_time=request["as_of_time"])
    if request.get("graph_version") and request["graph_version"] != graph.graph_version:
        raise ValueError("requested graph_version is not available in fixture graph")
    scenario_payloads, context_type = _scenario_payloads(graph, request)
    before_runs = [
        run_forward_monte_carlo({**payload, "seed": int(request["seed"]) + index}, snapshot=graph)
        for index, payload in enumerate(scenario_payloads)
    ]
    before = _aggregate_runs(before_runs)
    candidates = _candidate_actions(graph, request, before_runs[0] if before_runs else {})
    selected: list[dict[str, Any]] = []
    cost = 0.0
    for action in sorted(
        candidates,
        key=lambda item: (-risk_adjusted_value(item, risk_aversion_beta=float(request["risk_aversion_beta"])), item["action_id"]),
    ):
        if len(selected) >= int(request["max_actions"]):
            break
        if not validate_action(action, request, cost):
            continue
        selected.append(action)
        cost += float(action["cost"])

    effect_fraction = _intervention_effect_fraction(selected)
    after_payloads = [
        _apply_interventions_to_scenario(payload, effect_fraction, selected)
        for payload in scenario_payloads
    ]
    after_runs = [
        run_forward_monte_carlo({**payload, "seed": int(request["seed"]) + 1000 + index}, snapshot=graph)
        for index, payload in enumerate(after_payloads)
    ] if after_payloads else []
    after = _aggregate_runs(after_runs)
    expected_reduction = min(float(before["expected_loss"] or 0.0) * 0.7, sum(float(action["expected_loss_reduction"]) for action in selected))
    cvar_reduction = min(float(before["cvar_95"] or 0.0) * 0.7, sum(float(action["cvar95_reduction"]) for action in selected))
    heuristic_after_expected = round(max(0.0, float(before["expected_loss"] or 0.0) - expected_reduction), 4)
    heuristic_after_cvar = round(max(0.0, float(before["cvar_95"] or 0.0) - cvar_reduction), 4)
    run_id = stable_run_id(
        "opt",
        {
            "request": request,
            "graph_version": graph.graph_version,
            "source_manifest_id": graph.source_manifest_id,
            "actions": [action["action_id"] for action in selected],
            "scenario_payloads": scenario_payloads,
        },
    )
    evidence_refs = _unique_refs([ref for action in selected for ref in action["evidence_refs"]])
    return {
        "run_id": run_id,
        "seed": int(request["seed"]),
        "graph_version": graph.graph_version,
        "source_manifest_id": graph.source_manifest_id,
        "optimization_version": OPTIMIZATION_VERSION,
        "timestamp": request["as_of_time"],
        "optimization_context_type": context_type,
        "scenario_count": len(scenario_payloads),
        "baseline_run_ids": [run["run_id"] for run in before_runs],
        "before_simulation_run_ids": [run["run_id"] for run in before_runs],
        "after_simulation_run_ids": [run["run_id"] for run in after_runs],
        "recommended_actions": selected,
        "before_expected_loss": before["expected_loss"],
        "after_expected_loss": after["expected_loss"],
        "before_cvar95": before["cvar_95"],
        "after_cvar95": after["cvar_95"],
        "heuristic_estimated_after_expected_loss": heuristic_after_expected,
        "heuristic_estimated_after_cvar95": heuristic_after_cvar,
        "cost": round(cost, 4),
        "budget": request["budget"],
        "resilience_roi": resilience_roi(float(before["cvar_95"] or 0.0), float(after["cvar_95"] or 0.0), cost),
        "affected_paths_reduced": [path["path_id"] for run in before_runs for path in run.get("top_transmission_paths", [])[:5]][:8],
        "baseline_comparison": baseline_comparison(candidates, selected, request),
        "assumptions": [
            "Greedy risk-adjusted selection over fixture graph candidate actions.",
            "Before/after metrics are rerun through forward Monte Carlo with intervention-adjusted scenario parameters.",
            "Heuristic estimates are disclosed separately and are not the before/after source of truth.",
            "Effects are normalized resilience loss reductions, not financial savings.",
        ],
        "constraints": [
            f"budget <= {request['budget']}",
            f"max_actions <= {request['max_actions']}",
            "compliance_constraints:no_illegal_workarounds",
        ],
        "evidence_refs": evidence_refs,
        "warnings": [FIXTURE_GRAPH_WARNING, "optimization_fixture_graph:resilience_planning_only"],
        "fixture_graph": True,
    }


def _baseline_forward(graph: SemiriskGraphSnapshot, request: dict[str, Any]) -> dict[str, Any]:
    target = "company:tsmc"
    return run_forward_monte_carlo(
        {
            "scenario_type": "material_shortage",
            "targets": [target],
            "severity_distribution": {"type": "fixed", "params": {"value": 0.72}},
            "duration_days_distribution": {"type": "fixed", "params": {"value": 28}},
            "iterations": min(120, max(20, int(request.get("iterations", 80) or 80))),
            "seed": int(request["seed"]),
            "as_of_time": request["as_of_time"],
            "graph_version": graph.graph_version,
            "assumptions": ["Optimization baseline uses fixed fixture forward stress scenario."],
        },
        snapshot=graph,
    )


def _scenario_payloads(graph: SemiriskGraphSnapshot, request: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    if request.get("scenario_set"):
        return [_normalize_context_payload(item, graph, request) for item in request["scenario_set"] if isinstance(item, dict)], "scenario_set"
    if request.get("forward_scenario_payload"):
        return [_normalize_context_payload(request["forward_scenario_payload"], graph, request)], "forward_scenario_payload"
    if request.get("reverse_stress_payload"):
        from ml.simulation.reverse_stress import run_reverse_stress

        reverse = run_reverse_stress(request["reverse_stress_payload"], snapshot=graph)
        payloads = []
        for index, shock_set in enumerate(reverse.get("ranked_shock_sets", [])[:3]):
            targets = [str(shock.get("target_id")) for shock in shock_set.get("shocks", []) if shock.get("target_id")]
            if not targets:
                continue
            payloads.append(
                _normalize_context_payload(
                    {
                        "scenario_type": "export_control" if any(str(shock.get("shock_type")) == "policy" for shock in shock_set.get("shocks", [])) else "material_shortage",
                        "targets": targets,
                        "severity_distribution": {"type": "fixed", "params": {"value": min(0.95, float(shock_set.get("cvar95") or 35) / 100.0)}},
                        "duration_days_distribution": {"type": "fixed", "params": {"value": 28 + index * 3}},
                    },
                    graph,
                    request,
                )
            )
        return payloads or [_baseline_forward_payload(graph, request)], "reverse_stress_payload"
    return [_baseline_forward_payload(graph, request)], "default_fixture_scenario"


def _baseline_forward_payload(graph: SemiriskGraphSnapshot, request: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_type": "material_shortage",
        "targets": ["company:tsmc"],
        "severity_distribution": {"type": "fixed", "params": {"value": 0.72}},
        "duration_days_distribution": {"type": "fixed", "params": {"value": 28}},
        "iterations": min(120, max(20, int(request.get("iterations", 80) or 80))),
        "seed": int(request["seed"]),
        "as_of_time": request["as_of_time"],
        "graph_version": graph.graph_version,
        "loss_mode": "resilience_integral_loss",
        "propagation_mode": "auto_semiconductor",
        "functionality_metric": "capacity_fulfillment",
        "weighting_method": "literature_proxy_not_calibrated",
        "assumptions": ["Optimization baseline uses fixed fixture forward stress scenario."],
    }


def _normalize_context_payload(payload: dict[str, Any], graph: SemiriskGraphSnapshot, request: dict[str, Any]) -> dict[str, Any]:
    base = _baseline_forward_payload(graph, request)
    merged = {**base, **payload}
    merged["iterations"] = min(300, max(20, int(merged.get("iterations") or 80)))
    merged["as_of_time"] = str(merged.get("as_of_time") or request["as_of_time"])
    merged["graph_version"] = graph.graph_version
    merged.setdefault("loss_mode", "resilience_integral_loss")
    merged.setdefault("propagation_mode", "auto_semiconductor")
    merged.setdefault("functionality_metric", "capacity_fulfillment")
    merged.setdefault("weighting_method", "literature_proxy_not_calibrated")
    return merged


def _aggregate_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    if not runs:
        return {"expected_loss": 0.0, "cvar_95": 0.0}
    return {
        "expected_loss": round(sum(float(run.get("expected_loss") or 0.0) for run in runs) / len(runs), 4),
        "cvar_95": round(sum(float(run.get("cvar_95") or 0.0) for run in runs) / len(runs), 4),
    }


def _intervention_effect_fraction(actions: list[dict[str, Any]]) -> float:
    if not actions:
        return 0.0
    return min(0.45, sum(float(action.get("cvar95_reduction", 0.0)) for action in actions) / 180.0)


def _apply_interventions_to_scenario(payload: dict[str, Any], effect_fraction: float, actions: list[dict[str, Any]]) -> dict[str, Any]:
    adjusted = {**payload}
    adjusted["severity_distribution"] = _scale_distribution(payload.get("severity_distribution"), 1.0 - effect_fraction)
    adjusted["duration_days_distribution"] = _scale_distribution(payload.get("duration_days_distribution"), 1.0 - min(0.35, effect_fraction / 2.0), minimum=1.0)
    adjusted["assumptions"] = [
        *list(payload.get("assumptions", [])),
        f"Applied {len(actions)} selected interventions to scenario severity/duration proxies before rerunning Monte Carlo.",
    ]
    return adjusted


def _scale_distribution(spec: Any, factor: float, *, minimum: float = 0.0) -> dict[str, Any]:
    if not isinstance(spec, dict):
        return {"type": "fixed", "params": {"value": max(minimum, 0.0)}}
    params = dict(spec.get("params") if isinstance(spec.get("params"), dict) else {})
    for key in ["value", "min", "max", "mode", "mean", "scale"]:
        if key in params:
            params[key] = max(minimum, float(params[key]) * factor)
    return {"type": spec.get("type", "fixed"), "params": params}


def _candidate_actions(graph: SemiriskGraphSnapshot, request: dict[str, Any], before: dict[str, Any]) -> list[dict[str, Any]]:
    risk_rows = rank_risk_portfolio(snapshot=graph, node_type=None, limit=100)["scores"]
    risk_by_node = {row["node_id"]: row for row in risk_rows}
    evidence_by_node = _evidence_by_node(graph)
    nodes = sorted(graph.nodes, key=lambda node: (-float(risk_by_node.get(node.node_id, {}).get("score", 35)), node.node_id))
    candidates: list[dict[str, Any]] = []
    for node in nodes:
        risk_score = float(risk_by_node.get(node.node_id, {}).get("score", 35.0))
        for action_type in request["allowed_intervention_types"]:
            spec = ACTION_LIBRARY[action_type]
            if node.node_type not in spec["target_types"]:
                continue
            effect_multiplier = 0.65 + risk_score / 200.0
            action = {
                "action_id": f"action:{action_type}:{node.node_id}",
                "intervention_type": action_type,
                "target_id": node.node_id,
                "target_type": node.node_type,
                "target_label": node.canonical_name,
                "cost": float(spec["cost"]),
                "expected_effect": f"Reduce normalized propagation around {node.canonical_name}",
                "expected_loss_reduction": round(float(spec["expected"]) * effect_multiplier, 4),
                "cvar95_reduction": round(float(spec["cvar"]) * effect_multiplier, 4),
                "target_risk_score": risk_score,
                "assumptions": ["Fixture evidence-backed effect size; requires operational validation before production use."],
                "constraints": ["Must follow applicable trade, safety, supplier qualification, and compliance review requirements."],
                "evidence_refs": evidence_by_node.get(node.node_id, before.get("evidence_refs", []))[:5],
                "compliance_note": "Use approved resilience planning, monitoring, qualification, and diversification controls only.",
            }
            candidates.append(action)
    return candidates


def _evidence_by_node(graph: SemiriskGraphSnapshot) -> dict[str, list[dict[str, Any]]]:
    mapping: dict[str, list[dict[str, Any]]] = {}
    for edge in graph.edges:
        refs = [
            {
                "edge_id": edge.edge_id,
                "source_id": ref.source_id,
                "source_record_id": ref.source_record_id,
                "payload_hash": ref.payload_hash,
                "provenance_url": ref.provenance_url,
            }
            for ref in edge.provenance_refs
        ]
        mapping.setdefault(edge.source_node_id, []).extend(refs)
        mapping.setdefault(edge.target_node_id, []).extend(refs)
    return {node_id: _unique_refs(refs) for node_id, refs in mapping.items()}


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {}
    for ref in refs:
        by_key[(ref.get("source_id"), ref.get("source_record_id"), ref.get("payload_hash"), ref.get("edge_id"))] = ref
    return [by_key[key] for key in sorted(by_key)]
