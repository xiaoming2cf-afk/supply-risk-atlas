from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Any

from graph_kernel.semiconductor_snapshot import build_semiconductor_fixture_snapshot, neighborhood
from ml.optimization.interventions import OPTIMIZATION_VERSION, run_intervention_optimization
from ml.risk_scoring.semirisk_score import FEATURE_VERSION, score_semirisk_entity
from ml.simulation.monte_carlo import run_forward_monte_carlo
from ml.simulation.reverse_stress import run_reverse_stress
from ml.simulation.scenario_schema import FORWARD_SIMULATION_VERSION, REVERSE_SIMULATION_VERSION


REPORT_VERSION = "semirisk_investigation_report_v0.1"


def generate_investigation_report(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request = dict(payload or {})
    entity_id = str(request.get("entity_id") or "company:tsmc")
    report_format = str(request.get("format") or "json").lower()
    graph = build_semiconductor_fixture_snapshot()
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    risk = score_semirisk_entity(entity_id, snapshot=graph) if request.get("include_entity_risk", True) else None
    graph_context = neighborhood(graph, node_id=entity_id, depth=1)
    forward = (
        run_forward_monte_carlo(request["forward_scenario_payload"], snapshot=graph)
        if isinstance(request.get("forward_scenario_payload"), dict)
        else None
    )
    reverse = (
        run_reverse_stress(request["reverse_stress_payload"], snapshot=graph)
        if isinstance(request.get("reverse_stress_payload"), dict)
        else None
    )
    optimization = (
        run_intervention_optimization(request["optimization_payload"], snapshot=graph)
        if isinstance(request.get("optimization_payload"), dict)
        else None
    )
    report_id = _stable_report_id(entity_id, graph.graph_version, graph.source_manifest_id, report_format, forward, reverse, optimization)
    report = {
        "report_id": report_id,
        "report_version": REPORT_VERSION,
        "generated_at": generated_at,
        "entity": risk["entity"] if risk else _entity_from_graph(graph_context),
        "risk_score": risk,
        "forward_stress": forward,
        "reverse_stress": reverse,
        "intervention_optimization": optimization,
        "evidence_summary": _evidence_summary(risk, forward, reverse, optimization),
        "graph_context": {
            "node_id": graph_context["node_id"],
            "depth": graph_context["depth"],
            "node_count": len(graph_context["nodes"]),
            "edge_count": len(graph_context["edges"]),
            "nodes": [
                {"node_id": node["node_id"], "node_type": node["node_type"], "canonical_name": node["canonical_name"]}
                for node in graph_context["nodes"]
            ],
            "edges": [
                {"edge_id": edge["edge_id"], "edge_type": edge["edge_type"], "source_node_id": edge["source_node_id"], "target_node_id": edge["target_node_id"]}
                for edge in graph_context["edges"]
            ],
        },
        "versions": {
            "graph_version": graph.graph_version,
            "source_manifest_id": graph.source_manifest_id,
            "feature_version": FEATURE_VERSION if risk else None,
            "simulation_version": _first_present(forward, reverse, key="simulation_version"),
            "optimization_version": optimization.get("optimization_version") if optimization else None,
            "report_version": REPORT_VERSION,
        },
        "methodology": _methodology_section(risk, forward, reverse, optimization),
        "formula_sources": _formula_source_section(risk, forward, reverse, optimization),
        "model_limitations": [
            "Fixture graph is not production-ready.",
            "Risk score uses fixture proxy likelihood, impact, and vulnerability inputs because calibrated production data is unavailable.",
            "Simulation losses are normalized resilience loss scores, not dollar losses.",
            "Intervention before/after values are generated from bounded fixture Monte Carlo reruns.",
        ],
        "warnings": sorted({
            "fixture_graph:not_production_ready",
            "not_financial_loss",
            "not_production_decision",
            *(_warnings(risk)),
            *(_warnings(forward)),
            *(_warnings(reverse)),
            *(_warnings(optimization)),
        }),
        "assumptions": [
            "Report uses fixture/promoted test graph outputs only.",
            "No raw source payloads, credentials, private diagnostics, or private exposure data are included.",
        ],
        "limitations": [
            "Not a production readiness report.",
            "Forward, reverse, and optimization sections appear only when request payloads are supplied.",
            "Formula refs identify source principles and implemented proxy formulas; they are not calibrated authoritative coefficients.",
        ],
        "compliance_note": "Use this report for resilience planning, monitoring, approved qualification, diversification, and compliance review.",
        "raw_payload_excluded": True,
        "private_diagnostics_excluded": True,
    }
    if report_format == "markdown":
        return {**report, "format": "markdown", "markdown": _markdown(report)}
    return {**report, "format": "json"}


def _stable_report_id(entity_id: str, graph_version: str, source_manifest_id: str, report_format: str, *sections: Any) -> str:
    material = repr((entity_id, graph_version, source_manifest_id, report_format, sections)).encode("utf-8")
    return f"report_{sha256(material).hexdigest()[:16]}"


def _entity_from_graph(graph_context: dict[str, Any]) -> dict[str, Any]:
    node = next((item for item in graph_context["nodes"] if item["node_id"] == graph_context["node_id"]), None)
    return node or {"node_id": graph_context["node_id"]}


def _evidence_summary(*sections: Any) -> list[dict[str, Any]]:
    rows = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        refs = section.get("evidence_refs") or []
        rows.append(
            {
                "section": section.get("simulation_version") or section.get("optimization_version") or section.get("feature_version") or "graph_context",
                "evidence_ref_count": len(refs),
            }
        )
    return rows


def _warnings(section: Any) -> list[str]:
    return list(section.get("warnings", [])) if isinstance(section, dict) else []


def _first_present(*sections: Any, key: str) -> str | None:
    for section in sections:
        if isinstance(section, dict) and section.get(key):
            return str(section[key])
    return None


def _methodology_section(risk: Any, forward: Any, reverse: Any, optimization: Any) -> dict[str, Any]:
    return {
        "risk_scoring_method": risk.get("scoring_method") if isinstance(risk, dict) else None,
        "weighting_method": risk.get("weighting_method") if isinstance(risk, dict) else None,
        "calibration_status": risk.get("calibration_status") if isinstance(risk, dict) else "fixture_proxy_not_calibrated",
        "loss_mode": _first_present(forward, reverse, key="loss_mode"),
        "propagation_mode": _first_present(forward, reverse, key="propagation_mode"),
        "resilience_integral_loss": forward.get("resilience_integral_loss") if isinstance(forward, dict) else None,
        "functionality_curve_summary": forward.get("functionality_curve_summary") if isinstance(forward, dict) else None,
        "hhi_concentration_summary": risk.get("concentration") if isinstance(risk, dict) else None,
        "optimization_context_type": optimization.get("optimization_context_type") if isinstance(optimization, dict) else None,
    }


def _formula_source_section(*sections: Any) -> dict[str, Any]:
    refs = sorted(
        {
            ref
            for section in sections
            if isinstance(section, dict)
            for ref in section.get("formula_refs", [])
        }
    )
    return {
        "formula_refs": refs,
        "source_principle_note": "Formula refs identify literature/government source principles and implemented fixture proxy formulas; uncalibrated coefficients are not presented as authoritative.",
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Investigation Report {report['report_id']}",
        "",
        f"Generated: {report['generated_at']}",
        f"Entity: {report['entity'].get('canonical_name', report['entity'].get('node_id', 'unavailable'))}",
        "",
        "## Versions",
        "",
    ]
    for key, value in report["versions"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend([
        "",
        "## Methodology",
        "",
        f"- Risk scoring method: `{report['methodology'].get('risk_scoring_method')}`",
        f"- Weighting method: `{report['methodology'].get('weighting_method')}`",
        f"- Calibration status: `{report['methodology'].get('calibration_status')}`",
        f"- Loss mode: `{report['methodology'].get('loss_mode')}`",
        f"- Propagation mode: `{report['methodology'].get('propagation_mode')}`",
        f"- Resilience integral loss: `{report['methodology'].get('resilience_integral_loss')}`",
        "",
        "## Formula Sources",
        "",
    ])
    for ref in report["formula_sources"]["formula_refs"]:
        lines.append(f"- `{ref}`")
    lines.extend([
        "",
        "## Model Limitations",
        "",
        *[f"- {limitation}" for limitation in report["model_limitations"]],
        "",
        "## Risk Score",
        "",
        f"- Score: `{report['risk_score'].get('score') if report.get('risk_score') else 'not included'}`",
        f"- Level: `{report['risk_score'].get('level') if report.get('risk_score') else 'not included'}`",
        "",
        "## Evidence Summary",
        "",
    ])
    for row in report["evidence_summary"]:
        lines.append(f"- {row['section']}: {row['evidence_ref_count']} evidence refs")
    lines.extend([
        "",
        "## Warnings",
        "",
        *[f"- {warning}" for warning in report["warnings"]],
        "",
        "## Compliance Note",
        "",
        report["compliance_note"],
        "",
        f"raw_payload_excluded: {str(report['raw_payload_excluded']).lower()}",
        f"private_diagnostics_excluded: {str(report['private_diagnostics_excluded']).lower()}",
    ])
    return "\n".join(lines)
