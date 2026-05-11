from __future__ import annotations

import random
from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.contracts.semiconductor import SemiriskGraphSnapshot

from .monte_carlo import run_forward_monte_carlo
from .plausibility import explanation_for_shocks, plausibility_cost
from .scenario_schema import (
    FIXTURE_GRAPH_WARNING,
    REVERSE_SIMULATION_VERSION,
    ScenarioValidationError,
    normalize_reverse_request,
    stable_run_id,
)
from .shock_candidates import generate_shock_candidates


def run_reverse_stress(
    payload: dict[str, Any],
    *,
    snapshot: SemiriskGraphSnapshot | None = None,
) -> dict[str, Any]:
    request = normalize_reverse_request(payload)
    graph = snapshot or build_semiconductor_fixture_snapshot(as_of_time=request["as_of_time"])
    if request.get("graph_version") and request["graph_version"] != graph.graph_version:
        raise ScenarioValidationError("requested graph_version is not available in fixture graph", field="graph_version")
    candidates = generate_shock_candidates(
        graph,
        candidate_scope=request["candidate_scope"],
        allowed_shock_types=request["allowed_shock_types"],
        forbidden_shock_types=request["forbidden_shock_types"],
        limit=max(8, int(request["beam_width"])),
    )
    if not candidates:
        raise ScenarioValidationError("candidate scope produced no fixture graph shock candidates", field="candidate_scope")

    run_id = stable_run_id(
        "rev",
        {
            "request": request,
            "graph_version": graph.graph_version,
            "source_manifest_id": graph.source_manifest_id,
        },
    )
    evaluated: list[dict[str, Any]] = []
    beam: list[tuple[dict[str, Any], ...]] = []
    for size in range(1, int(request["max_combination_size"]) + 1):
        combinations = _expand(candidates, beam, int(request["beam_width"]), size)
        scored = [_evaluate_combo(combo, request, graph) for combo in combinations]
        evaluated.extend(scored)
        beam = [tuple(row["_raw_shocks"]) for row in _rank(scored)[: int(request["beam_width"])]]

    ranked = _rank(evaluated)[: int(request["beam_width"])]
    for row in ranked:
        row.pop("_raw_shocks", None)
    baseline = _baseline_comparison(candidates, request, graph)
    evidence_refs = _evidence_refs(ranked)
    best = ranked[0] if ranked else {}
    return {
        "run_id": run_id,
        "seed": int(request["seed"]),
        "graph_version": graph.graph_version,
        "source_manifest_id": graph.source_manifest_id,
        "simulation_version": REVERSE_SIMULATION_VERSION,
        "timestamp": request["as_of_time"],
        "failure_threshold_input": request["failure_threshold_input"],
        "failure_threshold_normalized": request["failure_threshold_normalized"],
        "threshold_metric_basis": request["threshold_metric_basis"],
        "loss_mode": request["loss_mode"],
        "propagation_mode": request["propagation_mode"],
        "ranked_shock_sets": ranked,
        "expected_loss": best.get("expected_loss"),
        "cvar95": best.get("cvar95"),
        "plausibility_cost": best.get("plausibility_cost"),
        "affected_nodes": best.get("affected_nodes", []),
        "affected_paths": best.get("affected_paths", []),
        "explanation": best.get("explanation", "No shock set reached the requested threshold."),
        "evidence_refs": evidence_refs,
        "baseline_comparison": baseline,
        "warnings": [
            FIXTURE_GRAPH_WARNING,
            "reverse_stress:resilience_planning_only",
            "policy_shocks_require_compliance_review",
            *request.get("threshold_warnings", []),
        ],
        "assumptions": ["Candidate shocks are derived from fixture graph evidence and evaluated through the forward Monte Carlo engine."],
        "input": request,
        "fixture_graph": True,
    }


def _expand(
    candidates: list[dict[str, Any]],
    beam: list[tuple[dict[str, Any], ...]],
    beam_width: int,
    size: int,
) -> list[tuple[dict[str, Any], ...]]:
    if size == 1:
        return [(candidate,) for candidate in candidates]
    seeds = beam or [(candidate,) for candidate in candidates[:beam_width]]
    unique: dict[tuple[str, ...], tuple[dict[str, Any], ...]] = {}
    for combo in seeds:
        used = {item["shock_id"] for item in combo}
        for candidate in candidates:
            if candidate["shock_id"] in used:
                continue
            next_combo = tuple(sorted((*combo, candidate), key=lambda item: item["shock_id"]))
            unique[tuple(item["shock_id"] for item in next_combo)] = next_combo
    return list(unique.values())


def _evaluate_combo(
    combo: tuple[dict[str, Any], ...],
    request: dict[str, Any],
    graph: SemiriskGraphSnapshot,
) -> dict[str, Any]:
    severity = min(0.98, sum(float(item["severity"]) for item in combo) / len(combo) + 0.04 * (len(combo) - 1))
    duration = sum(float(item["duration_days"]) for item in combo) / len(combo)
    scenario_type = "export_control" if any(item["shock_type"] == "policy" for item in combo) else "material_shortage"
    seed_offset = sum(ord(char) for item in combo for char in str(item["shock_id"])) % 10007
    forward = run_forward_monte_carlo(
        {
            "scenario_type": scenario_type,
            "targets": [str(item["target_id"]) for item in combo],
            "severity_distribution": {"type": "fixed", "params": {"value": severity}},
            "duration_days_distribution": {"type": "fixed", "params": {"value": duration}},
            "iterations": int(request["iterations_per_candidate"]),
            "seed": int(request["seed"]) + seed_offset,
            "as_of_time": request["as_of_time"],
            "graph_version": graph.graph_version,
            "loss_mode": request["loss_mode"],
            "propagation_mode": request["propagation_mode"],
            "functionality_metric": request["functionality_metric"],
            "weighting_method": request["weighting_method"],
            "assumptions": ["Reverse stress candidate evaluation uses the forward Monte Carlo engine."],
        },
        snapshot=graph,
    )
    metric_value = _metric_value(str(request["target_metric"]), forward)
    cost = round(sum(plausibility_cost(item, combination_size=len(combo)) for item in combo), 4)
    return {
        "shock_set_id": stable_run_id("shockset", [item["shock_id"] for item in combo]),
        "shocks": [{key: value for key, value in item.items() if key != "evidence_refs"} for item in combo],
        "_raw_shocks": combo,
        "expected_loss": forward["expected_loss"],
        "cvar95": forward["cvar_95"],
        "threshold_met": bool(metric_value is not None and metric_value >= float(request["failure_threshold_normalized"])),
        "plausibility_cost": cost,
        "affected_nodes": forward["affected_nodes"],
        "affected_paths": forward["top_transmission_paths"],
        "explanation": (
            f"{explanation_for_shocks(list(combo))} "
            f"Evaluated with loss_mode={request['loss_mode']} and propagation_mode={request['propagation_mode']} "
            "over affected functionality and critical dependency pathways."
        ),
        "evidence_refs": _unique_refs([ref for item in combo for ref in item["evidence_refs"]] + forward["evidence_refs"]),
        "loss_mode": request["loss_mode"],
        "propagation_mode": request["propagation_mode"],
        "threshold_metric_basis": request["threshold_metric_basis"],
        "assumptions": ["Compliance-safe stress planning; no illegal workaround recommendation is implied."],
    }


def _metric_value(metric: str, forward: dict[str, Any]) -> float | None:
    if metric == "cvar95_loss":
        return forward.get("cvar_95")
    if metric == "capacity_loss":
        return forward.get("capacity_functionality_loss")
    if metric == "demand_fulfillment_loss":
        return forward.get("demand_fulfillment_loss")
    if metric == "affected_critical_nodes":
        return float(len(forward.get("affected_nodes", [])))
    return forward.get("expected_loss")


def _rank(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            1 if row.get("threshold_met") else 0,
            -float(row.get("plausibility_cost") or 999),
            float(row.get("cvar95") or 0.0),
            float(row.get("expected_loss") or 0.0),
            str(row.get("shock_set_id")),
        ),
        reverse=True,
    )


def _baseline_comparison(candidates: list[dict[str, Any]], request: dict[str, Any], graph: SemiriskGraphSnapshot) -> list[dict[str, Any]]:
    rng = random.Random(int(request["seed"]))
    random_candidate = rng.choice(candidates)
    highest_candidate = candidates[0]
    rows = []
    for label, combo in [
        ("random_shock_set", (random_candidate,)),
        ("highest_criticality_shock_set", (highest_candidate,)),
    ]:
        evaluated = _evaluate_combo(combo, request, graph)
        rows.append(
            {
                "baseline": label,
                "expected_loss": evaluated["expected_loss"],
                "cvar95": evaluated["cvar95"],
                "plausibility_cost": evaluated["plausibility_cost"],
                "threshold_met": evaluated["threshold_met"],
            }
        )
    rows.append({"baseline": "proposed_reverse_stress_search", "method": "greedy_beam_search"})
    return rows


def _evidence_refs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _unique_refs([ref for row in rows for ref in row.get("evidence_refs", [])])


def _unique_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {}
    for ref in refs:
        by_key[(ref.get("source_id"), ref.get("source_record_id"), ref.get("payload_hash"), ref.get("edge_id"))] = ref
    return [by_key[key] for key in sorted(by_key)]
