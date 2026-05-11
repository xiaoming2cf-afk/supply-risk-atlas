from __future__ import annotations

import random
from statistics import mean
from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from sra_core.contracts.semiconductor import SemiriskGraphSnapshot

from .functionality import summarize_functionality_curve
from .loss_functions import compute_loss_components
from .metrics import cvar_95, loss_distribution_summary, percentile
from .propagation import (
    resolve_targets,
    summarize_affected_nodes,
    top_transmission_paths,
    propagate_loss,
)
from .scenario_schema import (
    FIXTURE_GRAPH_WARNING,
    FORWARD_SIMULATION_VERSION,
    SCENARIO_MULTIPLIERS,
    ScenarioValidationError,
    normalize_forward_request,
    normalize_severity,
    sample_distribution,
    stable_run_id,
)


def run_forward_monte_carlo(
    payload: dict[str, Any],
    *,
    snapshot: SemiriskGraphSnapshot | None = None,
) -> dict[str, Any]:
    request = normalize_forward_request(payload)
    graph = snapshot or build_semiconductor_fixture_snapshot(as_of_time=request["as_of_time"])
    if request.get("graph_version") and request["graph_version"] != graph.graph_version:
        raise ScenarioValidationError("requested graph_version is not available in fixture graph", field="graph_version")
    targets = resolve_targets(graph, request["targets"])
    if not targets:
        raise ScenarioValidationError("none of the requested targets resolved in the fixture graph", field="targets")

    run_id = stable_run_id(
        "fwd",
        {
            "request": request,
            "graph_version": graph.graph_version,
            "source_manifest_id": graph.source_manifest_id,
        },
    )
    rng = random.Random(int(request["seed"]))
    losses: list[float] = []
    loss_component_rows: list[dict[str, Any]] = []
    iteration_losses: list[dict[str, float]] = []
    traces: list[dict[str, Any]] = []
    durations: list[float] = []
    multiplier = SCENARIO_MULTIPLIERS[request["scenario_type"]]

    requested_iterations = int(request["iterations"])
    deterministic_fixed_inputs = (
        request["severity_distribution"].get("type") == "fixed"
        and request["duration_days_distribution"].get("type") == "fixed"
    )
    effective_iterations = 1 if deterministic_fixed_inputs else requested_iterations

    for _ in range(effective_iterations):
        severity = normalize_severity(sample_distribution(request["severity_distribution"], rng, default=0.72))
        duration_days = max(1.0, float(sample_distribution(request["duration_days_distribution"], rng, default=28.0)))
        durations.append(duration_days)
        initial = {node_id: min(1.0, severity * multiplier) for node_id in targets}
        node_losses, trace_rows = propagate_loss(
            graph,
            initial_losses=initial,
            duration_days=duration_days,
            propagation_mode=request["propagation_mode"],
        )
        iteration_losses.append(node_losses)
        traces.extend(trace_rows)
        loss_row = compute_loss_components(
            graph,
            node_losses,
            duration_days=duration_days,
            loss_mode=request["loss_mode"],
            functionality_metric=request["functionality_metric"],
            weighting_method=request["weighting_method"],
        )
        loss_component_rows.append(loss_row)
        losses.append(round(float(loss_row["primary_loss"]), 4))
    if deterministic_fixed_inputs and losses and requested_iterations > 1:
        losses = losses * requested_iterations

    affected_nodes = summarize_affected_nodes(graph, iteration_losses)
    transmission_paths = top_transmission_paths(graph, traces)
    evidence_refs = _evidence_refs(affected_nodes, transmission_paths)
    expected_loss = round(mean(losses), 4) if losses else None
    average_loss_components = _average_loss_components(loss_component_rows)
    representative_curve = loss_component_rows[0]["functionality_curve"] if loss_component_rows else []
    average_duration = mean(durations) if durations else 0.0
    assumptions = list(request["assumptions"]) or [
        "Outputs are normalized loss scores because licensed private exposure data is not available.",
        "Missing inventory buffers, substitutability, and recovery rates use conservative deterministic defaults.",
    ]
    warnings = [
        FIXTURE_GRAPH_WARNING,
        "fixture_graph:promoted_test_graph_only",
        "no_dollar_loss_without_private_exposure_data",
    ]
    return {
        "run_id": run_id,
        "seed": int(request["seed"]),
        "graph_version": graph.graph_version,
        "source_manifest_id": graph.source_manifest_id,
        "simulation_version": FORWARD_SIMULATION_VERSION,
        "timestamp": request["as_of_time"],
        "scenario_type": request["scenario_type"],
        "expected_loss": expected_loss,
        "p50_loss": percentile(losses, 0.50),
        "p90_loss": percentile(losses, 0.90),
        "p95_loss": percentile(losses, 0.95),
        "cvar_95": cvar_95(losses),
        "time_to_recover_days": round(average_duration * (1.0 + (expected_loss or 0.0) / 120.0), 2),
        "time_to_survive_days": round(max(1.0, average_duration * max(0.35, 1.0 - (expected_loss or 0.0) / 150.0)), 2),
        "loss_mode": request["loss_mode"],
        "propagation_mode": request["propagation_mode"],
        "functionality_metric": request["functionality_metric"],
        "functionality_curve": representative_curve,
        "functionality_curve_summary": summarize_functionality_curve(representative_curve),
        "resilience_integral_loss": average_loss_components.get("resilience_integral_loss"),
        "graph_weighted_loss": average_loss_components.get("graph_weighted_loss"),
        "demand_fulfillment_loss": average_loss_components.get("demand_fulfillment_loss"),
        "capacity_functionality_loss": average_loss_components.get("capacity_functionality_loss"),
        "affected_mean": average_loss_components.get("affected_mean"),
        "weight_basis": loss_component_rows[0]["weight_basis"] if loss_component_rows else {},
        "formula_refs": sorted({ref for row in loss_component_rows for ref in row.get("formula_refs", [])}),
        "calibration_status": "fixture_proxy_not_calibrated",
        "affected_nodes": affected_nodes,
        "top_transmission_paths": transmission_paths,
        "loss_distribution_summary": loss_distribution_summary(losses),
        "warnings": sorted(set([*warnings, *[warning for row in loss_component_rows for warning in row.get("warnings", [])]])),
        "assumptions": sorted(set([*assumptions, *[assumption for row in loss_component_rows for assumption in row.get("assumptions", [])]])),
        "evidence_refs": evidence_refs,
        "input": request,
        "fixture_graph": True,
    }


def _evidence_refs(affected_nodes: list[dict[str, Any]], paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for node in affected_nodes:
        refs.extend(node.get("evidence_refs", []))
    for path in paths:
        refs.extend(path.get("evidence_refs", []))
    by_key = {}
    for ref in refs:
        by_key[(ref.get("source_id"), ref.get("source_record_id"), ref.get("payload_hash"), ref.get("edge_id"))] = ref
    return [by_key[key] for key in sorted(by_key)]


def _average_loss_components(rows: list[dict[str, Any]]) -> dict[str, float]:
    fields = [
        "resilience_integral_loss",
        "graph_weighted_loss",
        "demand_fulfillment_loss",
        "capacity_functionality_loss",
        "affected_mean",
    ]
    result: dict[str, float] = {}
    for field in fields:
        values = [float(row[field]) for row in rows if row.get(field) is not None]
        result[field] = round(mean(values), 4) if values else 0.0
    return result
