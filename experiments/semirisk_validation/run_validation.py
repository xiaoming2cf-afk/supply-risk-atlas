from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot
from ml.optimization.interventions import OPTIMIZATION_VERSION, run_intervention_optimization
from ml.risk_scoring.risk_framework import FEATURE_VERSION as LITERATURE_FEATURE_VERSION
from ml.risk_scoring.semirisk_score import (
    HEURISTIC_FEATURE_VERSION,
    RiskScoreUnavailable,
    score_semirisk_entity,
    score_semirisk_entity_heuristic,
)
from ml.simulation.monte_carlo import run_forward_monte_carlo
from ml.simulation.scenario_schema import FORWARD_SIMULATION_VERSION, REVERSE_SIMULATION_VERSION
from ml.validation.ablation import ablation_rows
from ml.validation.sensitivity import hhi_sensitivity_rows
from ml.validation.stability import (
    explain_rank_disagreements,
    rank_items,
    score_deltas,
    spearman_rank_correlation,
)

DEFAULT_CONFIG = ROOT / "experiments" / "semirisk_validation" / "configs" / "base.yaml"
DEFAULT_OUTPUT_DIR = ROOT / "experiments" / "semirisk_validation" / "outputs"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic SemiRisk fixture validation experiments.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    config_path = Path(args.config)
    output_dir = Path(args.output_dir)
    config_text = config_path.read_text(encoding="utf-8")
    config = json.loads(config_text)
    if args.seed is not None:
        config["seed"] = args.seed
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot = build_semiconductor_fixture_snapshot(as_of_time=str(config["as_of_time"]))
    effective_config_text = json.dumps(config, sort_keys=True)
    results = run_all_experiments(snapshot, config, config_text=effective_config_text)
    for name, payload in results.items():
        write_json(output_dir / f"{name}.json", payload)
        write_csv(output_dir / f"{name}.csv", rows_for_csv(payload))
    return 0


def run_all_experiments(snapshot: Any, config: dict[str, Any], *, config_text: str) -> dict[str, Any]:
    risk = risk_method_comparison(snapshot, config)
    hhi = hhi_sensitivity_rows(
        snapshot,
        node_ids=config["hhi"]["node_ids"],
        global_reference_hhi_values=config["hhi"]["global_reference_hhi_values"],
        threshold_pairs=config["hhi"]["threshold_pairs"],
    )
    loss = loss_mode_comparison(snapshot, config)
    propagation = propagation_mode_comparison(snapshot, config)
    optimizer = optimizer_context_consistency(snapshot, config)
    ablation = {
        "rows": compact_ablation_rows(ablation_rows(
            snapshot,
            node_ids=list(config["ablation"]["node_ids"]),
            factors=list(config["ablation"]["factors"]),
        )),
        "warnings": ["fixture_graph:not_production_ready", "ablation_fixture_proxy:not_calibrated"],
    }
    manifest = build_manifest(snapshot, config, config_text=config_text)
    common = {
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "feature_version": LITERATURE_FEATURE_VERSION,
        "simulation_version": FORWARD_SIMULATION_VERSION,
        "optimization_version": OPTIMIZATION_VERSION,
        "seed": config["seed"],
        "fixture_graph": True,
        "warnings": ["fixture_graph:not_production_ready", "validation_fixture_proxy:not_calibrated"],
    }
    return {
        "risk_method_comparison": {**common, **risk},
        "hhi_sensitivity": {**common, "rows": compact_reference_rows(hhi)},
        "loss_mode_comparison": {**common, "rows": loss},
        "propagation_mode_comparison": {**common, "rows": propagation},
        "optimizer_context_consistency": {**common, "rows": optimizer},
        "ablation_study": {**common, **ablation},
        "manifest": manifest,
    }


def risk_method_comparison(snapshot: Any, config: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    node_types = set(config.get("risk_node_types", []))
    for node in snapshot.nodes:
        if node_types and node.node_type not in node_types:
            continue
        try:
            heuristic = score_semirisk_entity_heuristic(node.node_id, snapshot=snapshot)
            literature = score_semirisk_entity(node.node_id, snapshot=snapshot)
        except RiskScoreUnavailable:
            continue
        rows.append(
            {
                "node_id": node.node_id,
                "canonical_name": node.canonical_name,
                "node_type": node.node_type,
                "heuristic_score": heuristic["score"],
                "heuristic_level": heuristic["level"],
                "literature_score": literature["score"],
                "literature_level": literature["level"],
                "score_delta": round(float(literature["score"]) - float(heuristic["score"]), 4),
                "heuristic_feature_version": heuristic["feature_version"],
                "literature_feature_version": literature["feature_version"],
            }
        )
    heuristic_ranked = rank_items(
        [{"node_id": row["node_id"], "score": row["heuristic_score"], **row} for row in rows]
    )
    literature_ranked = rank_items(
        [{"node_id": row["node_id"], "score": row["literature_score"], **row} for row in rows]
    )
    return {
        "top_heuristic": heuristic_ranked[: int(config["top_n"])],
        "top_literature": literature_ranked[: int(config["top_n"])],
        "rank_correlation": spearman_rank_correlation(heuristic_ranked, literature_ranked),
        "score_deltas": score_deltas(
            [{"node_id": row["node_id"], "score": row["heuristic_score"]} for row in rows],
            [{"node_id": row["node_id"], "score": row["literature_score"]} for row in rows],
        ),
        "disagreements": explain_rank_disagreements(heuristic_ranked, literature_ranked),
        "rows": rows,
    }


def loss_mode_comparison(snapshot: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in config["scenarios"]:
        for loss_mode in config["loss_modes"]:
            result = run_forward_monte_carlo(
                scenario_payload(config, scenario, loss_mode=loss_mode),
                snapshot=snapshot,
            )
            rows.append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "scenario_type": scenario["scenario_type"],
                    "targets": ",".join(scenario["targets"]),
                    "loss_mode": loss_mode,
                    "expected_loss": result["expected_loss"],
                    "p95_loss": result["p95_loss"],
                    "cvar_95": result["cvar_95"],
                    "functionality_curve_summary": result["functionality_curve_summary"],
                    "run_id": result["run_id"],
                    "formula_refs": result["formula_refs"],
                    "warnings": result["warnings"],
                }
            )
    worst_rank = {
        (row["scenario_id"], row["loss_mode"]): index + 1
        for index, row in enumerate(sorted(rows, key=lambda item: (-float(item["cvar_95"]), str(item["scenario_id"]), str(item["loss_mode"]))))
    }
    for row in rows:
        row["worst_scenario_rank"] = worst_rank[(row["scenario_id"], row["loss_mode"])]
    return rows


def propagation_mode_comparison(snapshot: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in config["scenarios"]:
        scenario_rows = []
        for propagation_mode in config["propagation_modes"]:
            result = run_forward_monte_carlo(
                scenario_payload(config, scenario, propagation_mode=propagation_mode),
                snapshot=snapshot,
            )
            scenario_rows.append(
                {
                    "scenario_id": scenario["scenario_id"],
                    "scenario_type": scenario["scenario_type"],
                    "targets": ",".join(scenario["targets"]),
                    "propagation_mode": propagation_mode,
                    "downstream_node_count": len(result["affected_nodes"]),
                    "cvar_95": result["cvar_95"],
                    "expected_loss": result["expected_loss"],
                "top_transmission_path_ids": [path["path_id"] for path in result["top_transmission_paths"][:3]],
                    "run_id": result["run_id"],
                    "formula_refs": result["formula_refs"],
                    "warnings": result["warnings"],
                }
            )
        max_row = next(row for row in scenario_rows if row["propagation_mode"] == "max")
        for row in scenario_rows:
            row["multi_source_accumulation_changes_results"] = (
                row["propagation_mode"] != "max"
                and (
                    row["downstream_node_count"] != max_row["downstream_node_count"]
                    or row["cvar_95"] != max_row["cvar_95"]
                )
            )
        rows.extend(scenario_rows)
    return rows


def optimizer_context_consistency(snapshot: Any, config: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = config["scenarios"]
    base = {
        "budget": config["optimizer"]["budget"],
        "max_actions": config["optimizer"]["max_actions"],
        "risk_aversion_beta": config["optimizer"]["risk_aversion_beta"],
        "seed": config["seed"],
        "as_of_time": config["as_of_time"],
    }
    payloads = [
        ("no_context", base),
        ("forward_scenario_payload", {**base, "forward_scenario_payload": scenario_payload(config, scenarios[0])}),
        ("scenario_set", {**base, "scenario_set": [scenario_payload(config, scenarios[0]), scenario_payload(config, scenarios[1])]}),
        (
            "reverse_stress_payload",
            {
                **base,
                "reverse_stress_payload": {
                    "target_metric": "cvar95_loss",
                    "failure_threshold": 35,
                    "candidate_scope": {"node_types": ["company", "equipment", "chemical", "product_grade"]},
                    "max_combination_size": 2,
                    "beam_width": 4,
                    "iterations_per_candidate": 20,
                    "seed": config["seed"],
                    "as_of_time": config["as_of_time"],
                },
            },
        ),
    ]
    rows = []
    for label, payload in payloads:
        result = run_intervention_optimization(payload, snapshot=snapshot)
        rows.append(
            {
                "context_label": label,
                "optimization_context_type": result["optimization_context_type"],
                "scenario_count": result["scenario_count"],
                "selected_actions": [action["action_id"] for action in result["recommended_actions"]],
                "before_cvar95": result["before_cvar95"],
                "after_cvar95": result["after_cvar95"],
                "before_simulation_run_ids": result["before_simulation_run_ids"],
                "after_simulation_run_ids": result["after_simulation_run_ids"],
                "outputs_differ_from_default": False,
                "run_id": result["run_id"],
                "warnings": result["warnings"],
            }
        )
    default = rows[0]
    for row in rows:
        row["outputs_differ_from_default"] = row["selected_actions"] != default["selected_actions"] or row["before_cvar95"] != default["before_cvar95"]
    return rows


def scenario_payload(
    config: dict[str, Any],
    scenario: dict[str, Any],
    *,
    loss_mode: str = "resilience_integral_loss",
    propagation_mode: str = "auto_semiconductor",
) -> dict[str, Any]:
    return {
        "scenario_type": scenario["scenario_type"],
        "targets": list(scenario["targets"]),
        "severity_distribution": {"type": "fixed", "params": {"value": scenario["severity"]}},
        "duration_days_distribution": {"type": "fixed", "params": {"value": scenario["duration_days"]}},
        "iterations": 120,
        "seed": config["seed"],
        "as_of_time": config["as_of_time"],
        "loss_mode": loss_mode,
        "propagation_mode": propagation_mode,
        "functionality_metric": "capacity_fulfillment",
        "weighting_method": "literature_proxy_not_calibrated",
        "assumptions": ["Fixture validation scenario; not production calibrated."],
    }


def build_manifest(snapshot: Any, config: dict[str, Any], *, config_text: str) -> dict[str, Any]:
    return {
        "git_commit": git_commit(),
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "feature_version": LITERATURE_FEATURE_VERSION,
        "heuristic_feature_version": HEURISTIC_FEATURE_VERSION,
        "simulation_version": FORWARD_SIMULATION_VERSION,
        "reverse_simulation_version": REVERSE_SIMULATION_VERSION,
        "optimization_version": OPTIMIZATION_VERSION,
        "seed": config["seed"],
        "config_hash": hashlib.sha256(config_text.encode("utf-8")).hexdigest()[:16],
        "fixture_graph": True,
        "warnings": ["fixture_graph:not_production_ready", "validation_outputs:not_production_decision"],
    }


def rows_for_csv(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        if isinstance(payload.get("rows"), list):
            return payload["rows"]
        if "score_deltas" in payload and isinstance(payload["score_deltas"], list):
            return payload["score_deltas"]
        return [payload]
    if isinstance(payload, list):
        return payload
    return [{"value": payload}]


def compact_reference_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted: list[dict[str, Any]] = []
    for row in rows:
        next_row = dict(row)
        source_refs = next_row.pop("source_refs", [])
        next_row["source_ref_count"] = len(source_refs) if isinstance(source_refs, list) else 0
        compacted.append(next_row)
    return compacted


def compact_ablation_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted: list[dict[str, Any]] = []
    for row in rows:
        next_row = dict(row)
        evidence_refs = next_row.pop("evidence_refs", [])
        next_row["evidence_ref_count"] = len(evidence_refs) if isinstance(evidence_refs, list) else 0
        compacted.append(next_row)
    return compacted


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    flattened = [flatten_row(row) for row in rows]
    fieldnames = sorted({key for row in flattened for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)


def flatten_row(row: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, (dict, list)):
            result[key] = json.dumps(value, sort_keys=True)
        else:
            result[key] = value
    return result


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
