from __future__ import annotations

from typing import Any
from uuid import uuid4

try:
    from fastapi import Body, FastAPI, Header, Query, Request
    from fastapi.exceptions import RequestValidationError
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except Exception:  # pragma: no cover - allows contract tests without FastAPI installed
    Body = None  # type: ignore[assignment]
    CORSMiddleware = None  # type: ignore[assignment]
    FastAPI = None  # type: ignore[assignment]
    Header = None  # type: ignore[assignment]
    Query = None  # type: ignore[assignment]
    Request = Any  # type: ignore[assignment]
    RequestValidationError = None  # type: ignore[assignment]
    JSONResponse = None  # type: ignore[assignment]

from graph_kernel.graph_diff import diff_edge_states
from graph_kernel.path_index import build_path_index
from ml.models.dchgt_sc import DCHGTSCSkeleton
from ml.simulation.counterfactual import build_counterfactual_edges
from sra_core.api.envelope import make_envelope as build_envelope
from sra_core.api.envelope import make_error_envelope
from sra_core.contracts.domain import (
    ExplanationRequest,
    PredictionRequest,
    ReportRequest,
    SimulationRequest,
    VersionMetadata,
)
from sra_core.pipeline import default_metadata, run_synthetic_pipeline


def make_envelope(
    data: Any,
    metadata: VersionMetadata | None = None,
    request_id: str | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline() if metadata is None else None
    return build_envelope(
        data,
        metadata=metadata or default_metadata(result),  # type: ignore[arg-type]
        request_id=request_id or f"req_{uuid4().hex[:12]}",
        warnings=warnings,
    )


def make_error(
    code: str,
    message: str,
    request_id: str | None = None,
    field: str | None = None,
    metadata: VersionMetadata | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline() if metadata is None else None
    return make_error_envelope(
        code,
        message,
        metadata=metadata or default_metadata(result),  # type: ignore[arg-type]
        request_id=request_id or f"req_{uuid4().hex[:12]}",
        field=field,
    )


def route_health(request_id: str | None = None) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    return make_envelope(
        {
            "service": "supply-risk-atlas-api",
            "status": "ok",
            "quality_gates": [
                "contract",
                "leakage",
                "graph_invariant",
                "snapshot_determinism",
                "api_envelope",
            ],
            "graph_version": result.snapshot.graph_version,
        },
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_entities(
    entity_type: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    entities = result.synthetic.entities
    if entity_type:
        entities = [entity for entity in entities if entity.entity_type == entity_type]
    return make_envelope(
        [entity.model_dump(mode="json") for entity in entities],
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_entity(entity_id: str, request_id: str | None = None) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    entity = _find_entity(result, entity_id)
    if entity is None:
        raise LookupError(f"Entity not found: {entity_id}")
    return make_envelope(
        entity.model_dump(mode="json"),
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_graph_snapshots(request_id: str | None = None) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    paths = build_path_index(result.edge_states)
    return make_envelope(
        {
            "snapshot": result.snapshot.model_dump(mode="json"),
            "edge_states": [edge.model_dump(mode="json") for edge in result.edge_states],
            "path_index": [path.model_dump(mode="json") for path in paths[:20]],
        },
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_graph_diff(request_id: str | None = None) -> dict[str, Any]:
    earlier = run_synthetic_pipeline()
    later = run_synthetic_pipeline()
    return make_envelope(
        diff_edge_states(earlier.edge_states, later.edge_states),
        metadata=default_metadata(later),
        request_id=request_id,
    )


def route_features(entity_id: str | None = None, request_id: str | None = None) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    features = result.features
    if entity_id:
        features = [feature for feature in features if feature.entity_id == entity_id]
        if not features:
            raise LookupError(f"Features not found for entity: {entity_id}")
    return make_envelope(
        [feature.model_dump(mode="json") for feature in features],
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_labels(target_id: str | None = None, request_id: str | None = None) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    labels = result.labels
    if target_id:
        labels = [label for label in labels if label.target_id == target_id]
        if not labels:
            raise LookupError(f"Labels not found for target: {target_id}")
    return make_envelope(
        {
            "labels": [label.model_dump(mode="json") for label in labels],
            "quality": result.label_quality,
        },
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_predictions(
    prediction_request: PredictionRequest | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    predictions = result.predictions
    if prediction_request and prediction_request.target_id:
        predictions = [
            prediction
            for prediction in predictions
            if prediction.target_id == prediction_request.target_id
        ]
        if not predictions:
            raise LookupError(f"Predictions not found for target: {prediction_request.target_id}")
    return make_envelope(
        [prediction.model_dump(mode="json") for prediction in predictions],
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_explanations(
    explanation_request: ExplanationRequest | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    explanations = result.explanations
    if explanation_request:
        if explanation_request.prediction_id:
            explanations = [
                explanation
                for explanation in explanations
                if explanation.prediction_id == explanation_request.prediction_id
            ]
        elif explanation_request.target_id:
            prediction_ids = {
                prediction.prediction_id
                for prediction in result.predictions
                if prediction.target_id == explanation_request.target_id
            }
            explanations = [
                explanation
                for explanation in explanations
                if explanation.prediction_id in prediction_ids
            ]
        if not explanations:
            raise LookupError("Explanations not found for request")
    return make_envelope(
        [explanation.model_dump(mode="json") for explanation in explanations],
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_simulations(
    intervention_type: str = "close_port",
    target_id: str = "port_kaohsiung",
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    counterfactual = build_counterfactual_edges(
        base_graph_version=result.snapshot.graph_version,
        edge_states=result.edge_states,
        intervention_type=intervention_type,
        target_id=target_id,
    )
    base_risk = sum(edge.risk_score for edge in result.edge_states)
    cf_risk = sum(edge.risk_score for edge in counterfactual.edge_states)
    return make_envelope(
        {
            "intervention_type": intervention_type,
            "target_id": target_id,
            "base_graph_version": result.snapshot.graph_version,
            "counterfactual_graph_version": counterfactual.counterfactual_graph_version,
            "removed_edges": counterfactual.removed_edges,
            "risk_delta": cf_risk - base_risk,
        },
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_reports(
    report_request: ReportRequest | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    target_id = report_request.target_id if report_request else None
    predictions = result.predictions
    if target_id:
        predictions = [
            prediction
            for prediction in predictions
            if prediction.target_id == target_id
        ]
        if not predictions:
            raise LookupError(f"Report target not found: {target_id}")
    section_names = report_request.include_sections if report_request else []
    top_predictions = sorted(predictions, key=lambda pred: pred.risk_score, reverse=True)[:3]
    return make_envelope(
        {
            "title": "Synthetic Global Industrial Risk Brief",
            "report_type": report_request.report_type if report_request else "brief",
            "as_of_time": result.snapshot.as_of_time.isoformat(),
            "graph_version": result.snapshot.graph_version,
            "summary": (
                "Synthetic pipeline generated a reproducible graph snapshot, "
                "risk features, labels, predictions, and explanation records."
            ),
            "sections": section_names or ["overview", "top_risks", "evidence"],
            "top_risks": [prediction.model_dump(mode="json") for prediction in top_predictions],
            "evidence": ["synthetic_edge_events", "feature_factory", "baseline_model"],
        },
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_model_lab(request_id: str | None = None) -> dict[str, Any]:
    return make_envelope(DCHGTSCSkeleton().describe(), request_id=request_id)


def route_dashboard_page(page_id: str, request_id: str | None = None) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    payloads = _dashboard_payloads()
    if page_id not in payloads:
        raise LookupError(f"Dashboard page not found: {page_id}")
    return make_envelope(
        payloads[page_id],
        metadata=default_metadata(result),
        request_id=request_id,
    )


def route_shock_simulator(
    payload: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_synthetic_pipeline()
    return make_envelope(
        _calculate_dashboard_shock(payload or {}),
        metadata=default_metadata(result),
        request_id=request_id,
    )


def _dashboard_payloads() -> dict[str, dict[str, Any]]:
    return {
        "global-risk-cockpit": {
            "lastUpdated": "2026-04-30 08:18 CDT",
            "operatingMode": "real",
            "metrics": [
                {
                    "id": "global-index",
                    "label": "Global risk index",
                    "value": 78,
                    "unit": "/100",
                    "delta": 6.4,
                    "trend": "up",
                    "level": "severe",
                    "detail": "Port congestion and rare earth exposure raised the composite index.",
                },
                {
                    "id": "watched-suppliers",
                    "label": "Suppliers watched",
                    "value": 12840,
                    "displayValue": "12.8k",
                    "delta": 2.1,
                    "trend": "up",
                    "level": "guarded",
                    "detail": "Coverage spans tier-1 and tier-2 electronics, chemicals, and logistics.",
                },
                {
                    "id": "revenue-at-risk",
                    "label": "Revenue at risk",
                    "value": 34800000000,
                    "displayValue": "$34.8B",
                    "delta": 9.8,
                    "trend": "up",
                    "level": "severe",
                    "detail": "Near-term risk is concentrated in semiconductors and battery inputs.",
                },
                {
                    "id": "model-confidence",
                    "label": "Model confidence",
                    "value": 91,
                    "unit": "%",
                    "delta": 1.2,
                    "trend": "up",
                    "level": "low",
                    "detail": "Evidence coverage improved after graph build 2026.04.30-candidate.",
                },
            ],
            "hotspots": [
                {
                    "id": "taiwan-strait",
                    "label": "Taiwan Strait",
                    "region": "East Asia",
                    "level": "critical",
                    "score": 92,
                    "x": 73,
                    "y": 48,
                    "drivers": ["Semiconductor bottleneck", "Naval routing alerts", "Insurance spread widening"],
                },
                {
                    "id": "suez-red-sea",
                    "label": "Suez / Red Sea",
                    "region": "MENA",
                    "level": "severe",
                    "score": 81,
                    "x": 53,
                    "y": 51,
                    "drivers": ["Container reroutes", "Freight rate shock", "Lead-time variance"],
                },
                {
                    "id": "panama-canal",
                    "label": "Panama Canal",
                    "region": "Central America",
                    "level": "elevated",
                    "score": 64,
                    "x": 29,
                    "y": 57,
                    "drivers": ["Drought restrictions", "Slot scarcity"],
                },
            ],
            "incidents": [
                {
                    "id": "inc-1029",
                    "title": "Foundry wafer allocation tightens after rolling power curbs",
                    "region": "East Asia",
                    "level": "critical",
                    "startedAt": "2026-04-30T06:10:00-05:00",
                    "affectedCompanies": 142,
                    "signalStrength": 0.94,
                },
                {
                    "id": "inc-1027",
                    "title": "Container dwell time exceeds 7-day threshold on Red Sea diversion lanes",
                    "region": "MENA",
                    "level": "severe",
                    "startedAt": "2026-04-30T04:40:00-05:00",
                    "affectedCompanies": 88,
                    "signalStrength": 0.86,
                },
            ],
            "corridors": [
                {
                    "id": "cor-1",
                    "source": "Shenzhen",
                    "target": "Los Angeles",
                    "commodity": "Consumer electronics",
                    "level": "severe",
                    "score": 82,
                    "volumeShare": 0.21,
                },
                {
                    "id": "cor-2",
                    "source": "Kaohsiung",
                    "target": "Rotterdam",
                    "commodity": "Advanced logic chips",
                    "level": "critical",
                    "score": 91,
                    "volumeShare": 0.34,
                },
            ],
        },
        "graph-explorer": {
            "selectedNodeId": "c-apex",
            "filters": ["company", "supplier", "facility", "commodity", "route", "country"],
            "nodes": [
                {
                    "id": "c-apex",
                    "label": "Apex Mobility",
                    "kind": "company",
                    "level": "severe",
                    "score": 79,
                    "x": 49,
                    "y": 47,
                    "metadata": {"sector": "EV platforms", "exposure": "$7.4B", "tier": "target"},
                },
                {
                    "id": "s-orion",
                    "label": "Orion Cells",
                    "kind": "supplier",
                    "level": "critical",
                    "score": 91,
                    "x": 27,
                    "y": 26,
                    "metadata": {"country": "Taiwan", "dependency": "42%", "tier": 1},
                },
                {
                    "id": "f-kaohsiung",
                    "label": "Kaohsiung Fab 12",
                    "kind": "facility",
                    "level": "critical",
                    "score": 94,
                    "x": 18,
                    "y": 62,
                    "metadata": {"utilization": "96%", "substitute": "none"},
                },
                {
                    "id": "m-lithium",
                    "label": "Lithium carbonate",
                    "kind": "commodity",
                    "level": "elevated",
                    "score": 69,
                    "x": 74,
                    "y": 27,
                    "metadata": {"inventory": "31 days", "volatility": "high"},
                },
                {
                    "id": "r-red-sea",
                    "label": "Red Sea lane",
                    "kind": "route",
                    "level": "severe",
                    "score": 83,
                    "x": 78,
                    "y": 63,
                    "metadata": {"delay": "11.6 days", "freight": "+38%"},
                },
            ],
            "links": [
                {"id": "l1", "source": "c-apex", "target": "s-orion", "label": "tier-1 dependency", "weight": 0.8, "level": "severe"},
                {"id": "l2", "source": "s-orion", "target": "f-kaohsiung", "label": "sole-source fab", "weight": 0.9, "level": "critical"},
                {"id": "l3", "source": "c-apex", "target": "m-lithium", "label": "input exposure", "weight": 0.5, "level": "elevated"},
                {"id": "l4", "source": "c-apex", "target": "r-red-sea", "label": "shipping lane", "weight": 0.64, "level": "severe"},
            ],
        },
        "company-risk-360": {
            "selectedCompanyId": "apex-mobility",
            "companies": [
                {
                    "id": "apex-mobility",
                    "name": "Apex Mobility",
                    "ticker": "APXM",
                    "sector": "Electric vehicles",
                    "headquarters": "Detroit, US",
                    "riskScore": 79,
                    "confidence": 0.91,
                    "level": "severe",
                    "revenueAtRiskUsd": 7400000000,
                    "topDrivers": ["Battery cell sole-source exposure", "Advanced logic dependency", "Red Sea shipping delay"],
                    "mitigations": ["Qualify Vietnam battery pack line", "Forward-buy power modules", "Lock alternate Gulf routing"],
                    "suppliers": [
                        {
                            "id": "sup-1",
                            "supplier": "Orion Cells",
                            "country": "Taiwan",
                            "category": "Battery cells",
                            "spendShare": 0.42,
                            "dependency": 0.76,
                            "level": "critical",
                            "leadTimeDays": 61,
                        },
                        {
                            "id": "sup-2",
                            "supplier": "Kestrel Logic",
                            "country": "South Korea",
                            "category": "ADAS silicon",
                            "spendShare": 0.18,
                            "dependency": 0.63,
                            "level": "severe",
                            "leadTimeDays": 44,
                        },
                    ],
                },
                {
                    "id": "northstar-devices",
                    "name": "Northstar Devices",
                    "ticker": "NSDV",
                    "sector": "Medical devices",
                    "headquarters": "Minneapolis, US",
                    "riskScore": 63,
                    "confidence": 0.84,
                    "level": "elevated",
                    "revenueAtRiskUsd": 2300000000,
                    "topDrivers": ["Sterile resin feedstock", "Single port import lane"],
                    "mitigations": ["Pre-clear alternate resin", "Add EU safety stock"],
                    "suppliers": [
                        {
                            "id": "sup-3",
                            "supplier": "Helio Polymers",
                            "country": "Germany",
                            "category": "Medical resin",
                            "spendShare": 0.29,
                            "dependency": 0.58,
                            "level": "elevated",
                            "leadTimeDays": 37,
                        },
                    ],
                },
            ],
        },
        "path-explainer": {
            "selectedPathId": "path-apex-logic",
            "paths": [
                {
                    "id": "path-apex-logic",
                    "title": "Foundry outage to Apex Mobility ADAS supply",
                    "targetCompany": "Apex Mobility",
                    "scoreMove": 8.7,
                    "confidence": 0.89,
                    "summary": "A critical fab node links the regional shock to a high-value ADAS dependency.",
                    "steps": [
                        {"id": "step-1", "label": "Taiwan Strait shock", "kind": "route", "level": "critical", "contribution": 24, "evidence": "Event sourcing records a high-confidence routing disruption."},
                        {"id": "step-2", "label": "Kaohsiung Fab 12", "kind": "facility", "level": "critical", "contribution": 31, "evidence": "Facility utilization and supplier concentration amplify exposure."},
                        {"id": "step-3", "label": "Orion Cells", "kind": "supplier", "level": "severe", "contribution": 18, "evidence": "Supplier edge confidence is above 0.9 in the active snapshot."},
                    ],
                }
            ],
        },
        "causal-evidence-board": {
            "activeClaimId": "claim-1",
            "evidence": [
                {
                    "id": "claim-1",
                    "claim": "Port closure causes lead-time expansion for tier-1 electronics suppliers",
                    "source": "event-study registry",
                    "method": "event-study",
                    "confidence": 0.84,
                    "level": "severe",
                    "lastReviewed": "2026-04-30",
                    "disagreement": 0.16,
                },
                {
                    "id": "claim-2",
                    "claim": "Supplier distress is not explained by equity beta alone",
                    "source": "negative-control audit",
                    "method": "diff-in-diff",
                    "confidence": 0.78,
                    "level": "elevated",
                    "lastReviewed": "2026-04-29",
                    "disagreement": 0.22,
                },
            ],
        },
        "graph-version-studio": {
            "baselineVersionId": "g_2026_04_29",
            "candidateVersionId": "g_2026_04_30",
            "versions": [
                {"id": "g_2026_04_29", "label": "2026.04.29 promoted", "createdAt": "2026-04-29T08:00:00-05:00", "author": "graphops", "status": "promoted", "nodes": 12840, "edges": 42110, "schemaChanges": 0, "riskScoreDelta": 0.0, "validationPassRate": 0.992},
                {"id": "g_2026_04_30", "label": "2026.04.30 candidate", "createdAt": "2026-04-30T08:00:00-05:00", "author": "graphops", "status": "candidate", "nodes": 12962, "edges": 42880, "schemaChanges": 2, "riskScoreDelta": 4.8, "validationPassRate": 0.987},
            ],
            "diffRows": [
                {"id": "diff-1", "area": "Supplier edges", "change": "Added tier-2 electronics evidence", "severity": "elevated", "count": 770},
                {"id": "diff-2", "area": "Port status", "change": "Updated delay state and confidence", "severity": "severe", "count": 38},
            ],
        },
        "system-health-center": {
            "services": [
                {"id": "svc-api", "service": "Risk API", "owner": "platform", "status": "operational", "latencyMs": 72, "freshnessMinutes": 4, "errorRate": 0.001},
                {"id": "svc-graph", "service": "Graph query", "owner": "graph", "status": "operational", "latencyMs": 144, "freshnessMinutes": 8, "errorRate": 0.004},
                {"id": "svc-ingest", "service": "Signal ingest", "owner": "data", "status": "degraded", "latencyMs": 391, "freshnessMinutes": 17, "errorRate": 0.019},
            ],
            "stages": [
                {"id": "stage-1", "label": "Raw feeds", "status": "complete", "processed": 2417000, "total": 2417000},
                {"id": "stage-2", "label": "Entity resolution", "status": "running", "processed": 3981000, "total": 4210000},
                {"id": "stage-3", "label": "Graph materialization", "status": "queued", "processed": 0, "total": 1},
            ],
            "logs": [
                "08:18:41 ingest:data-contracts accepted 18 upstream schema changes",
                "08:17:55 resolver:entity-match recalibrated supplier aliases above 0.93 confidence",
                "08:16:20 graphops:snapshot checksum verified for g_2026_04_30",
            ],
        },
    }


def _calculate_dashboard_shock(payload: dict[str, Any]) -> dict[str, Any]:
    input_payload = {
        "region": str(payload.get("region") or "Taiwan Strait"),
        "commodity": str(payload.get("commodity") or "advanced semiconductor components"),
        "severity": _clamp_int(payload.get("severity"), 10, 100, 72),
        "durationDays": _clamp_int(payload.get("durationDays"), 3, 90, 28),
        "scope": payload.get("scope") if payload.get("scope") in {"facility", "regional", "global"} else "regional",
    }
    scope_multiplier = {"facility": 0.78, "regional": 1.1, "global": 1.35}[input_payload["scope"]]
    duration_factor = min(1.6, input_payload["durationDays"] / 35)
    impact_score = min(99, round(input_payload["severity"] * 0.62 * scope_multiplier + duration_factor * 18))
    level = _dashboard_risk_level(impact_score)
    return {
        "input": input_payload,
        "impactScore": impact_score,
        "ebitdaAtRiskUsd": round(impact_score * 42000000 * scope_multiplier),
        "timeToRecoveryDays": round(input_payload["durationDays"] * (0.9 + scope_multiplier / 3)),
        "affectedCompanies": round(impact_score * (2.1 if input_payload["scope"] == "global" else 1.45)),
        "affectedPaths": [
            {"id": "shock-path-1", "label": f"{input_payload['region']} -> Apex Mobility", "impact": impact_score, "level": level},
            {"id": "shock-path-2", "label": f"{input_payload['commodity']} logistics dependency", "impact": max(18, impact_score - 14), "level": _dashboard_risk_level(impact_score - 14)},
            {"id": "shock-path-3", "label": "Alternate supplier qualification queue", "impact": max(12, impact_score - 28), "level": _dashboard_risk_level(impact_score - 28)},
        ],
        "recommendations": [
            "Activate alternate routing for critical shipments",
            "Raise safety stock on exposed components",
            "Prioritize supplier qualification with lower shared exposure",
        ],
    }


def _clamp_int(value: Any, minimum: int, maximum: int, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _dashboard_risk_level(score: int) -> str:
    if score >= 88:
        return "critical"
    if score >= 74:
        return "severe"
    if score >= 58:
        return "elevated"
    if score >= 40:
        return "guarded"
    return "low"


def create_app() -> Any:
    if FastAPI is None:
        return None
    app = FastAPI(title="SupplyRiskAtlas API", version="0.1.0")
    if CORSMiddleware is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.exception_handler(LookupError)
    async def lookup_error_handler(request: Request, exc: LookupError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content=make_error(
                "not_found",
                str(exc),
                request_id=_request_id_from_request(request),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=make_error(
                "validation_error",
                f"Request validation failed: {len(exc.errors())} error(s).",
                request_id=_request_id_from_request(request),
                field="body",
            ),
        )

    @app.get("/health", include_in_schema=False)
    @app.get("/api/v1/health")
    def http_health(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_health(request_id=x_request_id)

    @app.get("/entities", include_in_schema=False)
    @app.get("/api/v1/entities")
    def http_entities(
        entity_type: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_entities(entity_type=entity_type, request_id=x_request_id)

    @app.get("/entities/{entity_id}", include_in_schema=False)
    @app.get("/api/v1/entities/{entity_id}")
    def http_entity(
        entity_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_entity(entity_id, request_id=x_request_id)

    @app.get("/graph", include_in_schema=False)
    @app.get("/api/v1/graph")
    @app.get("/api/v1/graph/snapshots")
    def http_graph(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_graph_snapshots(request_id=x_request_id)

    @app.get("/api/v1/graph/diff")
    def http_graph_diff(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_graph_diff(request_id=x_request_id)

    @app.get("/features", include_in_schema=False)
    @app.get("/api/v1/features")
    def http_features(
        entity_id: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_features(entity_id=entity_id, request_id=x_request_id)

    @app.get("/features/{entity_id}", include_in_schema=False)
    @app.get("/api/v1/features/{entity_id}")
    def http_feature_detail(
        entity_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_features(entity_id=entity_id, request_id=x_request_id)

    @app.get("/labels", include_in_schema=False)
    @app.get("/api/v1/labels")
    def http_labels(
        target_id: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_labels(target_id=target_id, request_id=x_request_id)

    @app.get("/labels/{target_id}", include_in_schema=False)
    @app.get("/api/v1/labels/{target_id}")
    def http_label_detail(
        target_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_labels(target_id=target_id, request_id=x_request_id)

    @app.get("/predictions", include_in_schema=False)
    @app.get("/api/v1/predictions")
    def http_predictions(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_predictions(request_id=x_request_id)

    @app.post("/predictions", include_in_schema=False)
    @app.post("/api/v1/predictions")
    def http_create_prediction(
        payload: PredictionRequest | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_predictions(
            prediction_request=payload or PredictionRequest(),
            request_id=x_request_id,
        )

    @app.get("/predictions/{target_id}", include_in_schema=False)
    @app.get("/api/v1/predictions/{target_id}")
    def http_prediction_detail(
        target_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_predictions(
            prediction_request=PredictionRequest(target_id=target_id),
            request_id=x_request_id,
        )

    @app.get("/explanations", include_in_schema=False)
    @app.get("/api/v1/explanations")
    def http_explanations(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_explanations(request_id=x_request_id)

    @app.post("/explanations", include_in_schema=False)
    @app.post("/api/v1/explanations")
    def http_create_explanation(
        payload: ExplanationRequest | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_explanations(
            explanation_request=payload or ExplanationRequest(),
            request_id=x_request_id,
        )

    @app.get("/explanations/{target_id}", include_in_schema=False)
    @app.get("/api/v1/explanations/{target_id}")
    def http_explanation_detail(
        target_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_explanations(
            explanation_request=ExplanationRequest(target_id=target_id),
            request_id=x_request_id,
        )

    @app.get("/simulations", include_in_schema=False)
    @app.get("/api/v1/simulations")
    def http_simulations(
        intervention_type: str = Query(default="close_port"),
        target_id: str = Query(default="port_kaohsiung"),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_simulations(
            intervention_type=intervention_type,
            target_id=target_id,
            request_id=x_request_id,
        )

    @app.post("/simulations", include_in_schema=False)
    @app.post("/api/v1/simulations")
    def http_create_simulation(
        payload: SimulationRequest | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        payload = payload or SimulationRequest()
        return route_simulations(
            intervention_type=payload.intervention_type,
            target_id=payload.target_id,
            request_id=x_request_id,
        )

    @app.get("/reports", include_in_schema=False)
    @app.get("/api/v1/reports")
    def http_reports(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_reports(request_id=x_request_id)

    @app.post("/reports", include_in_schema=False)
    @app.post("/api/v1/reports")
    def http_create_report(
        payload: ReportRequest | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_reports(report_request=payload or ReportRequest(), request_id=x_request_id)

    @app.get("/reports/{target_id}", include_in_schema=False)
    @app.get("/api/v1/reports/{target_id}")
    def http_report_detail(
        target_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_reports(
            report_request=ReportRequest(report_type="entity", target_id=target_id),
            request_id=x_request_id,
        )

    @app.get("/api/v1/admin/model-lab")
    def http_model_lab(x_request_id: str | None = Header(default=None)) -> dict[str, Any]:
        return route_model_lab(request_id=x_request_id)

    @app.get("/api/v1/dashboard/{page_id}")
    def http_dashboard_page(
        page_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_dashboard_page(page_id=page_id, request_id=x_request_id)

    @app.post("/api/v1/dashboard/shock-simulator")
    def http_dashboard_shock_simulator(
        payload: dict[str, Any] | None = Body(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_shock_simulator(payload=payload, request_id=x_request_id)

    return app


def _find_entity(result: Any, entity_id: str) -> Any | None:
    return next(
        (entity for entity in result.synthetic.entities if entity.canonical_id == entity_id),
        None,
    )


def _request_id_from_request(request: Request) -> str | None:
    return request.headers.get("x-request-id")


app = create_app()
