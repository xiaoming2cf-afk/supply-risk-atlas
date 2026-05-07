from __future__ import annotations

from threading import Lock
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
from sra_core.real_pipeline import real_metadata, run_public_real_pipeline


DEPLOYMENT_TARGET = "supply-risk-atlas-web.onrender.com"
TAIWAN_PROVINCE_DISPLAY = "中国台湾省"
TAIWAN_RAW_CODES = {"TW", "TWN"}
DASHBOARD_PAYLOAD_CACHE: dict[str, dict[str, dict[str, Any]]] = {}
DASHBOARD_PAYLOAD_CACHE_LOCK = Lock()


def metadata_for_result(result: Any) -> VersionMetadata:
    return real_metadata(result)


def entities_for_result(result: Any) -> list[Any]:
    return result.real.entities


def make_envelope(
    data: Any,
    metadata: VersionMetadata | None = None,
    request_id: str | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline() if metadata is None else None
    return build_envelope(
        data,
        metadata=metadata or metadata_for_result(result),  # type: ignore[arg-type]
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
    result = run_public_real_pipeline() if metadata is None else None
    return make_error_envelope(
        code,
        message,
        metadata=metadata or metadata_for_result(result),  # type: ignore[arg-type]
        request_id=request_id or f"req_{uuid4().hex[:12]}",
        field=field,
    )


def route_health(request_id: str | None = None) -> dict[str, Any]:
    result = run_public_real_pipeline()
    return make_envelope(
        {
            "service": "supply-risk-atlas-api",
            "status": "ok",
            "data_mode": "real",
            "deployment_target": DEPLOYMENT_TARGET,
            "source_manifest_ref": result.real.source_manifest_ref,
            "quality_gates": [
                "contract",
                "leakage",
                "graph_invariant",
                "snapshot_determinism",
                "api_envelope",
            ],
            "graph_version": result.snapshot.graph_version,
            "sources": [source.model_dump(mode="json") for source in result.real.sources],
            "freshness": [item.as_dict() for item in result.real.freshness],
        },
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_entities(
    entity_type: str | None = None,
    source_id: str | None = None,
    category: str | None = None,
    country: str | None = None,
    industry: str | None = None,
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
    entities = entities_for_result(result)
    if entity_type:
        entities = [entity for entity in entities if entity.entity_type == entity_type]
    source_ids_by_entity = _source_ids_by_entity(result)
    if source_id:
        entities = [
            entity
            for entity in entities
            if source_id in source_ids_by_entity.get(entity.canonical_id, set())
        ]
    if category:
        category_text = category.strip().lower()
        entities = [
            entity
            for entity in entities
            if category_text
            in " ".join(
                [
                    entity.entity_type,
                    entity.industry or "",
                    *[str(value) for value in entity.external_ids.values()],
                ]
            ).lower()
        ]
    if country:
        requested_raw_country = _raw_country_code(country) or str(country).strip().upper()
        requested_country = _country_code(country) or requested_raw_country
        if requested_raw_country == "TW":
            entities = [
                entity
                for entity in entities
                if str((entity.external_ids or {}).get("provinceCode") or "").upper() == "TW"
                or str((entity.external_ids or {}).get("sourceCountryCode") or "").upper() == "TW"
            ]
        else:
            entities = [
                entity
                for entity in entities
                if (_country_code_from_entity(entity) or "").upper() == requested_country
            ]
    if industry:
        industry_text = industry.strip().lower()
        entities = [
            entity
            for entity in entities
            if industry_text in (entity.industry or "").lower()
        ]
    if q:
        source_by_entity_id = _source_names_by_entity(result)
        entities = [
            entity
            for entity in entities
            if _matches_entity_query(entity, q, source_by_entity_id.get(entity.canonical_id, ""))
        ]
    entities = sorted(entities, key=_entity_result_sort_key)
    limit = _clamp_int(limit, 1, 500, 100)
    offset = max(0, offset)
    return make_envelope(
        [_entity_payload(entity) for entity in entities[offset : offset + limit]],
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_sources(
    source_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
    payload = _source_registry_payload(result)
    if source_id:
        sources = [source for source in payload["sources"] if source["id"] == source_id]
        if not sources:
            raise LookupError(f"Source not found: {source_id}")
        payload = {**payload, "sources": sources}
    return make_envelope(
        payload,
        metadata=metadata_for_result(result),
        request_id=request_id,
        warnings=_real_data_warnings(result),
    )


def route_lineage(
    source_id: str | None = None,
    target_id: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
    return make_envelope(
        _evidence_lineage_payload(result, source_id=source_id, target_id=target_id),
        metadata=metadata_for_result(result),
        request_id=request_id,
        warnings=_real_data_warnings(result),
    )


def route_entity(entity_id: str, request_id: str | None = None) -> dict[str, Any]:
    result = run_public_real_pipeline()
    entity = _find_entity(result, entity_id)
    if entity is None:
        raise LookupError(f"Entity not found: {entity_id}")
    return make_envelope(
        _entity_payload(entity),
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_graph_snapshots(request_id: str | None = None) -> dict[str, Any]:
    result = run_public_real_pipeline()
    paths = build_path_index(result.edge_states)
    return make_envelope(
        {
            "snapshot": result.snapshot.model_dump(mode="json"),
            "edge_states": [edge.model_dump(mode="json") for edge in result.edge_states],
            "path_index": [path.model_dump(mode="json") for path in paths[:20]],
            "source_manifest": {
                "manifest_ref": result.real.source_manifest_ref,
                "checksum": result.real.source_manifest_checksum,
                "sources": [source.source_id for source in result.real.sources],
                "freshness": [item.as_dict() for item in result.real.freshness],
            },
        },
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_graph_diff(request_id: str | None = None) -> dict[str, Any]:
    earlier = run_public_real_pipeline()
    later = run_public_real_pipeline()
    return make_envelope(
        diff_edge_states(earlier.edge_states, later.edge_states),
        metadata=metadata_for_result(later),
        request_id=request_id,
    )


def route_features(entity_id: str | None = None, request_id: str | None = None) -> dict[str, Any]:
    result = run_public_real_pipeline()
    features = result.features
    if entity_id:
        features = [feature for feature in features if feature.entity_id == entity_id]
        if not features:
            raise LookupError(f"Features not found for entity: {entity_id}")
    return make_envelope(
        [feature.model_dump(mode="json") for feature in features],
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_labels(target_id: str | None = None, request_id: str | None = None) -> dict[str, Any]:
    result = run_public_real_pipeline()
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
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_predictions(
    prediction_request: PredictionRequest | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
    prediction_payloads = _prediction_payloads(result, prediction_request)
    if prediction_request and prediction_request.target_id:
        if not prediction_payloads:
            raise LookupError(f"Predictions not found for target: {prediction_request.target_id}")
    return make_envelope(
        prediction_payloads,
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_explanations(
    explanation_request: ExplanationRequest | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
    explanations = _explanation_payloads(result)
    if explanation_request:
        if explanation_request.prediction_id:
            explanations = [
                explanation
                for explanation in explanations
                if explanation["prediction_id"] == explanation_request.prediction_id
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
                if explanation["prediction_id"] in prediction_ids
            ]
        if not explanations:
            raise LookupError("Explanations not found for request")
    return make_envelope(
        explanations,
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_simulations(
    intervention_type: str = "close_port",
    target_id: str = "port_kaohsiung",
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
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
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_reports(
    report_request: ReportRequest | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
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
            "title": "Public Real Data Industrial Risk Brief",
            "report_type": report_request.report_type if report_request else "brief",
            "as_of_time": result.snapshot.as_of_time.isoformat(),
            "graph_version": result.snapshot.graph_version,
            "summary": (
                "Public no-key sources generated a reproducible real graph snapshot, "
                "point-in-time features, baseline predictions, and lineage records."
            ),
            "sections": section_names or ["overview", "top_risks", "evidence"],
            "top_risks": [prediction.model_dump(mode="json") for prediction in top_predictions],
            "evidence": [
                result.real.source_manifest_ref,
                "source_registry",
                "point_in_time_public_graph",
                "feature_factory",
                "baseline_model",
            ],
        },
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def _path_transmission_score(path: Any) -> float:
    return _clamp_float(path.path_risk) * _clamp_float(path.path_confidence) * max(0.12, float(path.path_weight or 0.0))


def _ranked_paths_for_target(paths: list[Any], edge_states: list[Any], target_id: str, *, top_k: int = 5) -> list[Any]:
    edge_by_id = {edge.edge_id: edge for edge in edge_states}
    candidates: list[Any] = []
    for path in paths:
        if path.target_id != target_id:
            continue
        if len(set(path.node_sequence)) != len(path.node_sequence):
            continue
        edges = [edge_by_id.get(edge_id) for edge_id in path.edge_sequence]
        if not edges or any(edge is None for edge in edges):
            continue
        edge_types = [edge.edge_type for edge in edges if edge]
        if not any(edge_type in PRIMARY_TRANSMISSION_EDGE_TYPES for edge_type in edge_types):
            continue
        if any(edge_type in GOVERNANCE_EDGE_TYPES or edge_type.startswith("dataset_") for edge_type in edge_types):
            continue
        candidates.append(path)
    return sorted(candidates, key=lambda path: (_path_transmission_score(path), path.path_risk), reverse=True)[:top_k]


def _prediction_mechanism(top_paths: list[Any]) -> str:
    edge_types = {edge_type for path in top_paths for edge_type in path.meta_path.split(">")}
    if "event_affects" in edge_types:
        return "event_shock"
    if {"ships_through", "route_connects"} & edge_types:
        return "logistics_corridor"
    if "risk_transmits_to" in edge_types:
        return "supplier_dependency"
    if "policy_targets" in edge_types:
        return "policy_exposure"
    if "located_in" in edge_types:
        return "country_context"
    return "public_evidence_graph"


def _prediction_score_components(prediction: Any, sample: Any | None, top_paths: list[Any]) -> dict[str, float]:
    node_features = sample.node_features if sample else {}
    edge_features = sample.edge_features if sample else {}
    degree_signal = min(
        1.0,
        (
            float(node_features.get("inbound_edge_count", 0.0))
            + float(node_features.get("outbound_edge_count", 0.0))
        )
        / 40.0,
    )
    graph_signal = max(
        _clamp_float(node_features.get("incoming_risk_mean", 0.0)),
        _clamp_float(edge_features.get("incoming_risk_max", 0.0)),
    )
    path_signal = max((_path_transmission_score(path) for path in top_paths), default=_clamp_float(node_features.get("path_risk_max", 0.0)))
    event_signal = max((path.path_risk for path in top_paths if "event_affects" in path.meta_path), default=0.0)
    evidence_signal = min(1.0, (len([value for value in node_features.values() if value]) + len(top_paths)) / 10.0)
    baseline = _clamp_float(prediction.risk_score)
    return {
        "baseline": round(baseline, 4),
        "degree_exposure": round(degree_signal, 4),
        "graph_propagation": round(graph_signal, 4),
        "path_transmission": round(_clamp_float(path_signal), 4),
        "scenario_shock": round(_clamp_float(event_signal), 4),
        "evidence_coverage": round(evidence_signal, 4),
    }


def _prediction_driver_contributions(components: dict[str, float], top_paths: list[Any]) -> list[dict[str, Any]]:
    weights = {
        "baseline": 0.22,
        "degree_exposure": 0.12,
        "graph_propagation": 0.24,
        "path_transmission": 0.24,
        "scenario_shock": 0.12,
        "evidence_coverage": 0.06,
    }
    rows = [
        {
            "driver": key,
            "score": round(value, 4),
            "weight": weights[key],
            "contribution": round(value * weights[key], 4),
        }
        for key, value in components.items()
    ]
    if top_paths:
        rows.append(
            {
                "driver": "top_path",
                "pathId": top_paths[0].path_id,
                "score": round(_path_transmission_score(top_paths[0]), 4),
                "weight": 0.18,
                "contribution": round(_path_transmission_score(top_paths[0]) * 0.18, 4),
            }
        )
    return sorted(rows, key=lambda item: item["contribution"], reverse=True)


def _prediction_path_details(paths: list[Any], edge_states: list[Any], entity_by_id: dict[str, Any]) -> list[dict[str, Any]]:
    edge_by_id = {edge.edge_id: edge for edge in edge_states}
    details = []
    for path in paths:
        edge_sequence = [edge_by_id[edge_id] for edge_id in path.edge_sequence if edge_id in edge_by_id]
        details.append(
            {
                "pathId": path.path_id,
                "nodeSequence": list(path.node_sequence),
                "edgeSequence": list(path.edge_sequence),
                "nodeLabels": [_entity_label(entity_by_id, node_id) for node_id in path.node_sequence],
                "edgeTypes": [edge.edge_type for edge in edge_sequence],
                "pathRisk": round(path.path_risk, 4),
                "pathConfidence": round(path.path_confidence, 4),
                "transmissionScore": round(_path_transmission_score(path), 4),
                "evidenceRefs": sorted({edge.source for edge in edge_sequence}),
            }
        )
    return details


def _prediction_payloads(result: Any, prediction_request: PredictionRequest | None = None) -> list[dict[str, Any]]:
    paths = build_path_index(result.edge_states, max_hops=4)
    entity_by_id = {entity.canonical_id: entity for entity in result.real.entities}
    samples_by_target = {sample.target_id: sample for sample in result.samples}
    payloads = []
    for prediction in result.predictions:
        if prediction_request and prediction_request.target_id and prediction.target_id != prediction_request.target_id:
            continue
        top_paths = _ranked_paths_for_target(paths, result.edge_states, prediction.target_id)
        components = _prediction_score_components(prediction, samples_by_target.get(prediction.target_id), top_paths)
        payload = prediction.model_dump(mode="json")
        payload["top_paths"] = [path.path_id for path in top_paths] or payload.get("top_paths", [])
        payload["score_components"] = components
        payload["driver_contributions"] = _prediction_driver_contributions(components, top_paths)
        payload["prediction_form"] = "public_evidence_graph_ensemble"
        payload["mechanism"] = _prediction_mechanism(top_paths)
        payload["confidence_interval"] = {
            "low": payload["confidence_low"],
            "high": payload["confidence_high"],
            "horizonDays": prediction_request.horizon if prediction_request else prediction.horizon,
        }
        payload["path_details"] = _prediction_path_details(top_paths, result.edge_states, entity_by_id)
        payload["evidence_refs"] = sorted(
            {
                result.real.source_manifest_ref,
                "point_in_time_public_graph",
                "feature_factory",
                *[
                    evidence_ref
                    for path_detail in payload["path_details"]
                    for evidence_ref in path_detail["evidenceRefs"]
                ],
            }
        )
        payloads.append(payload)
    return payloads


def _prediction_center_payload(result: Any) -> dict[str, Any]:
    prediction_payloads = _prediction_payloads(result)
    top_predictions = sorted(
        prediction_payloads,
        key=lambda prediction: (
            prediction.get("risk_score", 0.0),
            prediction.get("confidence_high", 0.0) - prediction.get("confidence_low", 0.0),
        ),
        reverse=True,
    )[:24]
    mechanism_buckets: dict[str, list[dict[str, Any]]] = {}
    for prediction in prediction_payloads:
        mechanism = str(prediction.get("mechanism") or "public_evidence_graph")
        mechanism_buckets.setdefault(mechanism, []).append(prediction)
    mechanisms = []
    for mechanism, bucket in sorted(mechanism_buckets.items()):
        risks = [float(prediction.get("risk_score", 0.0)) for prediction in bucket]
        mechanisms.append(
            {
                "mechanism": mechanism,
                "count": len(bucket),
                "maxRisk": round(max(risks, default=0.0), 4),
                "averageRisk": round(sum(risks) / len(risks), 4) if risks else 0.0,
            }
        )
    mechanisms = sorted(mechanisms, key=lambda item: (item["maxRisk"], item["count"]), reverse=True)
    return {
        "lastUpdated": result.snapshot.as_of_time.isoformat(),
        "modelVersion": result.predictions[0].model_version if result.predictions else "model_none",
        "predictionForm": "public_evidence_graph_ensemble",
        "predictions": prediction_payloads,
        "topPredictions": top_predictions,
        "mechanisms": mechanisms,
        "highConfidenceCount": sum(
            1
            for prediction in prediction_payloads
            if float(prediction.get("confidence_high", 1.0)) - float(prediction.get("confidence_low", 0.0)) <= 0.22
        ),
        "saturatedScoreCount": sum(1 for prediction in prediction_payloads if float(prediction.get("risk_score", 0.0)) >= 0.995),
    }


def _explanation_payloads(result: Any) -> list[dict[str, Any]]:
    paths = build_path_index(result.edge_states, max_hops=4)
    edge_by_id = {edge.edge_id: edge for edge in result.edge_states}
    entity_by_id = {entity.canonical_id: entity for entity in result.real.entities}
    explanations: list[dict[str, Any]] = []
    for prediction in result.predictions:
        top_paths = _ranked_paths_for_target(paths, result.edge_states, prediction.target_id, top_k=3)
        if not top_paths:
            explanations.extend(explanation.model_dump(mode="json") for explanation in result.explanations if explanation.prediction_id == prediction.prediction_id)
            continue
        for rank, path in enumerate(top_paths, start=1):
            edges = [edge_by_id[edge_id] for edge_id in path.edge_sequence if edge_id in edge_by_id]
            contribution = _path_transmission_score(path)
            explanations.append(
                {
                    "explanation_id": f"explain_{prediction.prediction_id.removeprefix('pred_')}_{rank}",
                    "prediction_id": prediction.prediction_id,
                    "target_id": prediction.target_id,
                    "path_id": path.path_id,
                    "node_sequence": list(path.node_sequence),
                    "edge_sequence": list(path.edge_sequence),
                    "node_labels": [_entity_label(entity_by_id, node_id) for node_id in path.node_sequence],
                    "edge_types": [edge.edge_type for edge in edges],
                    "contribution_score": round(contribution, 4),
                    "causal_score": round(min(1.0, contribution + 0.08), 4),
                    "confidence": round(path.path_confidence, 4),
                    "mechanism": _prediction_mechanism([path]),
                    "evidence": sorted({edge.source for edge in edges} | {result.real.source_manifest_ref}),
                    "steps": [
                        {
                            "nodeId": node_id,
                            "label": _entity_label(entity_by_id, node_id),
                            "edgeId": path.edge_sequence[index - 1] if index else None,
                            "edgeType": edges[index - 1].edge_type if index and index - 1 < len(edges) else None,
                            "contribution": round(
                                (edges[index - 1].risk_score * edges[index - 1].confidence * edges[index - 1].weight)
                                if index and index - 1 < len(edges)
                                else contribution,
                                4,
                            ),
                        }
                        for index, node_id in enumerate(path.node_sequence)
                    ],
                }
            )
    return explanations


def route_model_lab(request_id: str | None = None) -> dict[str, Any]:
    return make_envelope(DCHGTSCSkeleton().describe(), request_id=request_id)


def route_dashboard_page(page_id: str, request_id: str | None = None) -> dict[str, Any]:
    result = run_public_real_pipeline()
    payloads = _dashboard_payloads(result)
    if page_id not in payloads:
        raise LookupError(f"Dashboard page not found: {page_id}")
    return make_envelope(
        payloads[page_id],
        metadata=metadata_for_result(result),
        request_id=request_id,
        warnings=_real_data_warnings(result),
    )


def route_shock_simulator(
    payload: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
    return make_envelope(
        _calculate_dashboard_shock(payload or {}, result),
        metadata=metadata_for_result(result),
        request_id=request_id,
        warnings=_real_data_warnings(result),
    )


def _real_data_warnings(result: Any) -> list[str]:
    if not hasattr(result, "real"):
        return ["real_mode_required"]
    warnings = [
        "public_no_key_real_data: supply transactions are limited to public evidence graph signals",
        "unlabeled_real_mode: baseline predictions are not trained on proprietary outcome labels",
    ]
    stale_sources = [item.source_id for item in result.real.freshness if item.status != "fresh"]
    if stale_sources:
        warnings.append(f"source_freshness_degraded:{','.join(stale_sources)}")
    if getattr(result.real, "catalog_source", "builtin_partial") != "promoted":
        warnings.append("promoted_graph_missing: using built-in public real partial catalog")
    return warnings


def _dashboard_payloads(result: Any) -> dict[str, dict[str, Any]]:
    cache_key = ":".join(
        [
            result.snapshot.graph_version,
            result.real.source_manifest_checksum,
            result.predictions[0].model_version if result.predictions else "model_none",
        ]
    )
    with DASHBOARD_PAYLOAD_CACHE_LOCK:
        cached = DASHBOARD_PAYLOAD_CACHE.get(cache_key)
        if cached is None:
            cached = _real_dashboard_payloads(result)
            DASHBOARD_PAYLOAD_CACHE.clear()
            DASHBOARD_PAYLOAD_CACHE[cache_key] = cached
        return cached


def _real_dashboard_payloads(result: Any) -> dict[str, dict[str, Any]]:
    entity_by_id = {entity.canonical_id: entity for entity in result.real.entities}
    source_names = {source.source_id: source.source_name for source in result.real.sources}
    source_by_entity_id = _source_names_by_entity(result)
    prediction_by_target = {prediction.target_id: prediction for prediction in result.predictions}
    paths = build_path_index(result.edge_states, max_hops=4)
    max_prediction = max((prediction.risk_score for prediction in result.predictions), default=0.0)
    source_count = len(result.real.sources)
    entity_count = len(result.real.entities)
    edge_count = len(result.edge_states)
    last_updated = result.snapshot.as_of_time.isoformat()
    fresh_sources = sum(1 for item in result.real.freshness if item.status == "fresh")
    top_edges = sorted(result.edge_states, key=lambda edge: edge.risk_score, reverse=True)
    firm_entities = [entity for entity in result.real.entities if entity.entity_type == "firm"]
    event_entities = [entity for entity in result.real.entities if entity.entity_type in {"risk_event", "policy", "text_artifact"}]
    port_entities = [entity for entity in result.real.entities if entity.entity_type == "port"]
    graph_payload = _graph_explorer_payload(
        result,
        prediction_by_target,
        firm_entities,
        source_by_entity_id,
        paths,
    )
    path_explainer_paths = _dashboard_paths(paths, result.edge_states, entity_by_id)
    prediction_payload = _prediction_center_payload(result)

    return {
        "global-risk-cockpit": {
            "lastUpdated": last_updated,
            "operatingMode": "real",
            "metrics": [
                {
                    "id": "global-index",
                    "label": "Public evidence risk index",
                    "value": round(max_prediction * 100),
                    "unit": "/100",
                    "delta": 0.0,
                    "trend": "up",
                    "level": _dashboard_risk_level(round(max_prediction * 100)),
                    "detail": "Computed from public no-key source evidence and point-in-time graph features.",
                },
                {
                    "id": "public-sources",
                    "label": "Public sources active",
                    "value": source_count,
                    "displayValue": str(source_count),
                    "delta": 0.0,
                    "trend": "up",
                    "level": "low",
                    "detail": ", ".join(source.source_name for source in result.real.sources),
                },
                {
                    "id": "entity-count",
                    "label": "Real entities registered",
                    "value": entity_count,
                    "displayValue": str(entity_count),
                    "delta": 0.0,
                    "trend": "up",
                    "level": "guarded",
                    "detail": "Companies, countries, ports, policy, products, events, and text evidence.",
                },
                {
                    "id": "edge-count",
                    "label": "Point-in-time edges",
                    "value": edge_count,
                    "displayValue": str(edge_count),
                    "delta": 0.0,
                    "trend": "up",
                    "level": "guarded",
                    "detail": "Active edges only; expired edges are excluded from the promoted snapshot.",
                },
                {
                    "id": "fresh-sources",
                    "label": "Fresh source manifests",
                    "value": fresh_sources,
                    "displayValue": f"{fresh_sources}/{source_count}",
                    "delta": 0.0,
                    "trend": "flat",
                    "level": "low" if fresh_sources == source_count else "elevated",
                    "detail": result.real.source_manifest_ref,
                },
            ],
            "hotspots": _dashboard_hotspots(event_entities + port_entities, result.edge_states, entity_by_id),
            "incidents": _dashboard_incidents(result, entity_by_id, source_names),
            "corridors": _dashboard_corridors(top_edges, entity_by_id),
        },
        "graph-explorer": graph_payload,
        "path-analysis": graph_payload,
        "country-lens": graph_payload,
        "company-risk-360": {
            "selectedCompanyId": _selected_entity_id(prediction_by_target, firm_entities),
            "companies": _dashboard_companies(firm_entities, result.edge_states, prediction_by_target, entity_by_id),
        },
        "prediction-center": prediction_payload,
        "path-explainer": {
            "selectedPathId": path_explainer_paths[0]["id"] if path_explainer_paths else "path-unavailable",
            "paths": path_explainer_paths,
        },
        "causal-evidence-board": {
            "activeClaimId": result.real.silver_events[0].event_id if result.real.silver_events else "evidence-unavailable",
            "evidence": _dashboard_evidence(result, entity_by_id, source_names),
        },
        "graph-version-studio": {
            "baselineVersionId": result.snapshot.graph_version,
            "candidateVersionId": result.snapshot.graph_version,
            "versions": [
                {
                    "id": result.snapshot.graph_version,
                    "label": f"{result.snapshot.as_of_time.date().isoformat()} promoted real graph",
                    "createdAt": result.snapshot.created_at.isoformat(),
                    "author": "public-real-pipeline",
                    "status": "promoted",
                    "nodes": result.snapshot.node_count,
                    "edges": result.snapshot.edge_count,
                    "schemaChanges": 0,
                    "riskScoreDelta": 0.0,
                    "validationPassRate": 1.0,
                },
                {
                    "id": result.real.source_manifest_ref,
                    "label": "source manifest candidate",
                    "createdAt": result.snapshot.as_of_time.isoformat(),
                    "author": "source-registry",
                    "status": "candidate",
                    "nodes": len(result.real.raw_records),
                    "edges": len(result.real.gold_edge_events),
                    "schemaChanges": 0,
                    "riskScoreDelta": 0.0,
                    "validationPassRate": 1.0,
                },
            ],
            "diffRows": [
                {"id": "diff-raw", "area": "Raw public records", "change": "Checksum-deduplicated source records in manifest", "severity": "guarded", "count": len(result.real.raw_records)},
                {"id": "diff-silver", "area": "Silver facts", "change": "Entity and event records promoted through contract validation", "severity": "guarded", "count": len(result.real.silver_entities) + len(result.real.silver_events)},
                {"id": "diff-gold", "area": "Gold edge events", "change": "Point-in-time edge events materialized into snapshot state", "severity": "elevated", "count": len(result.real.gold_edge_events)},
            ],
        },
        "system-health-center": {
            "services": _dashboard_services(result),
            "stages": [
                {"id": "stage-raw", "label": "Raw public source records", "status": "complete", "processed": len(result.real.raw_records), "total": len(result.real.raw_records)},
                {"id": "stage-silver", "label": "Silver entity and event records", "status": "complete", "processed": len(result.real.silver_entities) + len(result.real.silver_events), "total": len(result.real.silver_entities) + len(result.real.silver_events)},
                {"id": "stage-gold", "label": "Gold edge event materialization", "status": "complete", "processed": len(result.real.gold_edge_events), "total": len(result.real.gold_edge_events)},
                {"id": "stage-snapshot", "label": "Promoted graph snapshot", "status": "complete", "processed": 1, "total": 1},
            ],
            "logs": [
                f"{last_updated} source-registry accepted {source_count} public no-key sources",
                f"{last_updated} raw-record checksums deduplicated {len(result.real.raw_records)} records",
                f"{last_updated} graph snapshot checksum verified for {result.snapshot.graph_version}",
                f"{last_updated} point-in-time guard enforced observed_time and ingest_time cutoffs",
            ],
            "sourceRegistry": _source_registry_payload(result),
            "entityResolution": _entity_resolution_payload(result),
            "evidenceLineage": _evidence_lineage_payload(result),
            "dataCatalog": _data_catalog_payload(result),
        },
    }


def _source_ids_by_entity(result: Any) -> dict[str, set[str]]:
    return {
        entity.entity_id: {source_ref.source_id for source_ref in entity.source_refs}
        for entity in result.real.silver_entities
    }


def _source_names_by_entity(result: Any) -> dict[str, str]:
    source_names = {source.source_id: source.source_name for source in result.real.sources}
    return {
        entity.entity_id: ", ".join(
            sorted({source_names.get(source_ref.source_id, source_ref.source_id) for source_ref in entity.source_refs})
        )
        for entity in result.real.silver_entities
    }


def _matches_entity_query(entity: Any, query: str, source_text: str = "") -> bool:
    needle = query.strip().lower()
    if not needle:
        return True
    fields = [
        entity.canonical_id,
        entity.entity_type,
        entity.display_name,
        entity.country or "",
        entity.industry or "",
        source_text,
        *[str(value) for value in entity.external_ids.values()],
    ]
    return any(needle in field.lower() for field in fields)


def _entity_result_sort_key(entity: Any) -> tuple[int, str]:
    generated_prefixes = (
        "firm_sec_",
        "legal_entity_lei_",
        "airport_",
        "indicator_wb_",
        "observation_series_",
        "text_gdelt_",
        "legal_entity_ofac_",
        "port_wpi_",
        "risk_event_usgs_eq_",
        "schema_field_",
    )
    return (1 if entity.canonical_id.startswith(generated_prefixes) else 0, entity.display_name.lower())


def _source_registry_payload(result: Any) -> dict[str, Any]:
    freshness_by_source = {item.source_id: item for item in result.real.freshness}
    manifest_by_source = {manifest.source_id: manifest for manifest in result.real.source_manifests}
    rows = []
    for source in sorted(result.real.sources, key=lambda item: item.source_id):
        freshness = freshness_by_source.get(source.source_id)
        manifest = manifest_by_source.get(source.source_id)
        rows.append(
            {
                "id": source.source_id,
                "name": source.source_name,
                "type": source.source_type,
                "license": source.license_type,
                "updateFrequency": source.update_frequency,
                "reliabilityScore": source.reliability_score,
                "owner": source.owner,
                "status": freshness.status if freshness else "unavailable",
                "recordCount": freshness.record_count if freshness else 0,
                "maxStaleMinutes": freshness.max_stale_minutes if freshness else 0,
                "checksum": freshness.checksum if freshness else "",
                "latestRecordTime": manifest.latest_record_time.isoformat()
                if manifest and manifest.latest_record_time
                else None,
            }
        )
    return {
        "manifestRef": result.real.source_manifest_ref,
        "checksum": result.real.source_manifest_checksum,
        "asOfTime": result.snapshot.as_of_time.isoformat(),
        "catalogSource": result.real.catalog_source,
        "promotedGraph": {
            "status": "promoted"
            if result.real.catalog_source == "promoted"
            and (result.real.promoted_manifest or {}).get("source_status") == "fresh"
            else "partial",
            "manifest": result.real.promoted_manifest,
        },
        "sourceCount": len(result.real.sources),
        "rawRecordCount": len(result.real.raw_records),
        "silverEntityCount": len(result.real.silver_entities),
        "silverEventCount": len(result.real.silver_events),
        "goldEdgeEventCount": len(result.real.gold_edge_events),
        "dataNodeCount": sum(1 for entity in result.real.entities if _is_data_node(entity.entity_type)),
        "sources": rows,
    }


def _is_data_node(entity_type: str) -> bool:
    return entity_type in {
        "data_source",
        "data_category",
        "dataset",
        "indicator",
        "industry",
        "schema_field",
        "license_policy",
        "coverage_area",
        "source_release",
        "observation_series",
    }


def _data_catalog_payload(result: Any) -> dict[str, Any]:
    source_ids_by_entity = _source_ids_by_entity(result)
    data_entities = [entity for entity in result.real.entities if _is_data_node(entity.entity_type)]
    by_type: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for entity in data_entities:
        by_type[entity.entity_type] = by_type.get(entity.entity_type, 0) + 1
        for source_id in source_ids_by_entity.get(entity.canonical_id, set()):
            by_source[source_id] = by_source.get(source_id, 0) + 1
    license_nodes = [
        entity
        for entity in data_entities
        if entity.entity_type == "license_policy"
    ][:12]
    top_nodes = sorted(
        data_entities,
        key=lambda entity: (entity.entity_type, entity.display_name.lower()),
    )[:24]
    return {
        "catalogSource": result.real.catalog_source,
        "promoted": result.real.catalog_source == "promoted",
        "totalDataNodes": len(data_entities),
        "byType": [
            {"entityType": entity_type, "count": count}
            for entity_type, count in sorted(by_type.items())
        ],
        "bySource": [
            {"sourceId": source_id, "count": count}
            for source_id, count in sorted(by_source.items())
        ],
        "licensePolicies": [
            {
                "id": entity.canonical_id,
                "name": entity.display_name,
                "sourceIds": sorted(source_ids_by_entity.get(entity.canonical_id, set())),
                "licenseUrl": entity.external_ids.get("license_url", ""),
            }
            for entity in license_nodes
        ],
        "topNodes": [
            {
                "id": entity.canonical_id,
                "name": entity.display_name,
                "entityType": entity.entity_type,
                "sourceIds": sorted(source_ids_by_entity.get(entity.canonical_id, set())),
                "confidence": entity.confidence,
            }
            for entity in top_nodes
        ],
    }


def _entity_resolution_payload(result: Any) -> dict[str, Any]:
    by_entity_type: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for entity in result.real.silver_entities:
        by_entity_type[entity.entity_type] = by_entity_type.get(entity.entity_type, 0) + 1
        source_ids = {source_ref.source_id for source_ref in entity.source_refs}
        for source_id in source_ids:
            by_source[source_id] = by_source.get(source_id, 0) + 1
    confidence_values = [entity.confidence for entity in result.real.silver_entities]
    average_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
    return {
        "totalEntities": len(result.real.silver_entities),
        "averageConfidence": round(average_confidence, 4),
        "byEntityType": [
            {"entityType": entity_type, "count": count}
            for entity_type, count in sorted(by_entity_type.items())
        ],
        "bySource": [
            {"sourceId": source_id, "entityCount": count}
            for source_id, count in sorted(by_source.items())
        ],
    }


def _evidence_lineage_payload(
    result: Any,
    source_id: str | None = None,
    target_id: str | None = None,
) -> dict[str, Any]:
    source_names = {source.source_id: source.source_name for source in result.real.sources}
    entity_names = {entity.canonical_id: entity.display_name for entity in result.real.entities}
    silver_events_by_raw: dict[str, list[Any]] = {}
    silver_entities_by_raw: dict[str, list[Any]] = {}
    gold_edges_by_raw: dict[str, list[Any]] = {}

    for event in result.real.silver_events:
        for source_ref in event.source_refs:
            silver_events_by_raw.setdefault(source_ref.raw_id, []).append(event)
    for entity in result.real.silver_entities:
        for source_ref in entity.source_refs:
            silver_entities_by_raw.setdefault(source_ref.raw_id, []).append(entity)
    for edge in result.real.gold_edge_events:
        for source_ref in edge.source_refs:
            gold_edges_by_raw.setdefault(source_ref.raw_id, []).append(edge)

    records = []
    for raw_record in sorted(result.real.raw_records, key=lambda record: (record.source_id, record.raw_id)):
        if source_id and raw_record.source_id != source_id:
            continue
        silver_events = silver_events_by_raw.get(raw_record.raw_id, [])
        silver_entities = silver_entities_by_raw.get(raw_record.raw_id, [])
        gold_edges = gold_edges_by_raw.get(raw_record.raw_id, [])
        linked_entity_ids = {
            entity.entity_id
            for entity in silver_entities
        } | {
            entity_ref.entity_id
            for event in silver_events
            for entity_ref in event.entities
        } | {
            entity_id
            for edge in gold_edges
            for entity_id in (edge.source_entity_id, edge.target_entity_id)
        }
        if target_id and target_id not in linked_entity_ids:
            continue

        confidence_values = [
            *[event.confidence for event in silver_events],
            *[entity.confidence for entity in silver_entities],
            *[edge.confidence for edge in gold_edges],
        ]
        records.append(
            {
                "id": f"lineage:{raw_record.source_id}:{raw_record.checksum[:12]}",
                "sourceId": raw_record.source_id,
                "sourceName": source_names.get(raw_record.source_id, raw_record.source_id),
                "rawId": raw_record.raw_id,
                "sourceRecordId": raw_record.source_record_id,
                "rawChecksum": raw_record.checksum,
                "rawObservedTime": raw_record.observed_time.isoformat(),
                "silverEventIds": sorted(event.event_id for event in silver_events),
                "silverEntityIds": sorted(entity.entity_id for entity in silver_entities),
                "goldEdgeEventIds": sorted(edge.edge_event_id for edge in gold_edges),
                "edgeTypes": sorted({edge.edge_type for edge in gold_edges}),
                "targetEntities": sorted(
                    entity_names.get(entity_id, entity_id)
                    for entity_id in linked_entity_ids
                ),
                "confidence": round(
                    sum(confidence_values) / len(confidence_values),
                    4,
                )
                if confidence_values
                else 0.0,
            }
        )

    return {
        "manifestRef": result.real.source_manifest_ref,
        "checksum": result.real.source_manifest_checksum,
        "asOfTime": result.snapshot.as_of_time.isoformat(),
        "rawRecordCount": len(records),
        "silverEventCount": sum(len(record["silverEventIds"]) for record in records),
        "goldEdgeEventCount": sum(len(record["goldEdgeEventIds"]) for record in records),
        "records": records,
    }


def _selected_entity_id(prediction_by_target: dict[str, Any], entities: list[Any]) -> str:
    ranked = sorted(
        entities,
        key=lambda entity: prediction_by_target.get(entity.canonical_id).risk_score
        if entity.canonical_id in prediction_by_target
        else 0.0,
        reverse=True,
    )
    return ranked[0].canonical_id if ranked else ""


def _entity_label(entity_by_id: dict[str, Any], entity_id: str) -> str:
    return _entity_display_name(entity_by_id[entity_id]) if entity_id in entity_by_id else entity_id


TRANSMISSION_EDGE_TYPES = {
    "risk_transmits_to",
    "event_affects",
    "ships_through",
    "route_connects",
    "produces",
    "located_in",
}

PRIMARY_TRANSMISSION_EDGE_TYPES = TRANSMISSION_EDGE_TYPES - {"located_in"}

CONTEXT_EDGE_TYPES = {
    "dataset_observes",
    "source_provides",
    "licensed_under",
    "dataset_has_field",
    "dataset_measures",
    "dataset_covers",
    "observed_for",
    "indicator_context_for",
    "released_as",
    "classified_as",
    "categorized_as",
    "policy_targets",
    "co_mentions",
}

GOVERNANCE_EDGE_TYPES = {
    "dataset_covers",
    "dataset_has_field",
    "dataset_measures",
    "dataset_observes",
    "licensed_under",
    "released_as",
    "source_provides",
}


def _clamp_float(value: Any, lower: float = 0.0, upper: float = 1.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return lower
    return max(lower, min(upper, numeric))


def _raw_country_code(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    return text if len(text) == 2 and text != "XX" else None


def _country_code(value: Any) -> str | None:
    raw = _raw_country_code(value)
    if raw == "TW":
        return "CN"
    return raw


def _has_taiwan_source_code(entity: Any | None) -> bool:
    if entity is None:
        return False
    external_ids = getattr(entity, "external_ids", {}) or {}
    raw_values = {
        str(getattr(entity, "country", "") or "").upper(),
        str(external_ids.get("iso2") or "").upper(),
        str(external_ids.get("sourceCountryCode") or "").upper(),
        str(external_ids.get("provinceCode") or "").upper(),
        str(external_ids.get("subdivisionCode") or "").upper(),
    }
    return "TW" in raw_values or str(getattr(entity, "canonical_id", "")).lower() in {"country_tw", "province_cn_tw"}


def _is_taiwan_geo(entity: Any | None) -> bool:
    if entity is None:
        return False
    entity_type = str(getattr(entity, "entity_type", "")).lower()
    return (
        _has_taiwan_source_code(entity)
        and entity_type in {"country", "province", "region", "coverage_area"}
    )


def _geo_context_from_entity(entity: Any | None) -> dict[str, Any]:
    if _has_taiwan_source_code(entity):
        return {
            "geoId": "province_cn_tw",
            "geoLevel": "province" if _is_taiwan_geo(entity) else "unknown",
            "countryCode": "CN",
            "provinceCode": "TW",
            "parentGeoId": "country_cn",
            "sourceCountryCode": "TW",
            "displayName": TAIWAN_PROVINCE_DISPLAY if _is_taiwan_geo(entity) else entity.display_name,
        }
    if entity is None:
        return {
            "geoId": "unknown",
            "geoLevel": "unknown",
            "countryCode": "unknown",
            "provinceCode": None,
            "parentGeoId": None,
            "sourceCountryCode": None,
            "displayName": "Unknown",
        }
    external_ids = getattr(entity, "external_ids", {}) or {}
    raw_code = (
        _raw_country_code(getattr(entity, "country", None))
        or _raw_country_code(external_ids.get("iso2"))
        or _raw_country_code(str(getattr(entity, "canonical_id", "")).replace("country_", ""))
    )
    country_code = _country_code(raw_code) or "unknown"
    canonical_id = str(getattr(entity, "canonical_id", ""))
    entity_type = str(getattr(entity, "entity_type", ""))
    geo_level = str(external_ids.get("geoLevel") or external_ids.get("geo_level") or "").lower()
    if not geo_level:
        geo_level = "country" if entity_type == "country" else "unknown"
    geo_id = str(external_ids.get("geoId") or external_ids.get("geo_id") or canonical_id or country_code.lower())
    return {
        "geoId": geo_id,
        "geoLevel": geo_level,
        "countryCode": country_code,
        "provinceCode": external_ids.get("provinceCode") or external_ids.get("subdivisionCode"),
        "parentGeoId": external_ids.get("parentGeoId"),
        "sourceCountryCode": external_ids.get("sourceCountryCode") or raw_code,
        "displayName": getattr(entity, "display_name", country_code),
    }


def _country_code_from_entity(entity: Any | None) -> str | None:
    if entity is None:
        return None
    geo_context = _geo_context_from_entity(entity)
    code = str(geo_context.get("countryCode") or "").upper()
    return code if len(code) == 2 else None


def _country_name(code: str, entity_by_id: dict[str, Any]) -> str:
    country_entity = entity_by_id.get(f"country_{code.lower()}")
    return _entity_display_name(country_entity) if country_entity else code


def _entity_display_name(entity: Any | None) -> str:
    if entity is None:
        return "Unknown"
    return TAIWAN_PROVINCE_DISPLAY if _is_taiwan_geo(entity) else entity.display_name


def _entity_payload(entity: Any) -> dict[str, Any]:
    payload = entity.model_dump(mode="json")
    geo_context = _geo_context_from_entity(entity)
    payload.update(geo_context)
    payload["display_name"] = geo_context["displayName"]
    payload["country"] = geo_context["countryCode"] if geo_context["countryCode"] != "unknown" else payload.get("country")
    external_ids = dict(payload.get("external_ids") or {})
    for key in ("geoId", "geoLevel", "countryCode", "provinceCode", "parentGeoId", "sourceCountryCode", "displayName"):
        value = geo_context.get(key)
        if value is not None:
            external_ids.setdefault(key, str(value))
    payload["external_ids"] = external_ids
    return payload


def _node_country_index(entities: list[Any], edge_states: list[Any]) -> dict[str, str]:
    entity_by_id = {entity.canonical_id: entity for entity in entities}
    node_country_by_id: dict[str, str] = {}
    for entity in entities:
        code = _country_code_from_entity(entity)
        if code:
            node_country_by_id[entity.canonical_id] = code
    for edge in edge_states:
        if edge.edge_type != "located_in":
            continue
        target_code = _country_code_from_entity(entity_by_id.get(edge.target_id))
        if target_code:
            node_country_by_id.setdefault(edge.source_id, target_code)
    for _ in range(2):
        changed = False
        for edge in edge_states:
            if edge.edge_type in GOVERNANCE_EDGE_TYPES or edge.edge_type.startswith("dataset_"):
                continue
            source_code = node_country_by_id.get(edge.source_id)
            target_code = node_country_by_id.get(edge.target_id)
            if source_code and not target_code:
                node_country_by_id[edge.target_id] = source_code
                changed = True
            elif target_code and not source_code:
                node_country_by_id[edge.source_id] = target_code
                changed = True
        if not changed:
            break
    return node_country_by_id


def _edge_transmission_weight(edge: Any) -> float:
    if edge.edge_type in TRANSMISSION_EDGE_TYPES:
        role_weight = 1.0
    elif edge.edge_type in CONTEXT_EDGE_TYPES:
        role_weight = 0.14
    else:
        role_weight = 0.42
    return _clamp_float(edge.weight) * _clamp_float(edge.confidence) * role_weight


def _edge_role(edge_type: str) -> str:
    if edge_type in GOVERNANCE_EDGE_TYPES or edge_type.startswith("dataset_"):
        return "governance"
    if edge_type in TRANSMISSION_EDGE_TYPES:
        return "transmission"
    if edge_type in CONTEXT_EDGE_TYPES:
        return "context"
    return "context"


def _normalize_metric(values: dict[str, float]) -> dict[str, float]:
    maximum = max(values.values(), default=0.0)
    if maximum <= 0:
        return {key: 0.0 for key in values}
    return {key: value / maximum for key, value in values.items()}


def _active_edge_states(edge_states: list[Any]) -> list[Any]:
    return [edge for edge in edge_states if edge.valid_to is None]


def _entity_score(entity_id: str, edge_states: list[Any], prediction_by_target: dict[str, Any]) -> int:
    if entity_id in prediction_by_target:
        return round(prediction_by_target[entity_id].risk_score * 100)
    related_risk = [
        edge.risk_score
        for edge in edge_states
        if edge.source_id == entity_id or edge.target_id == entity_id
    ]
    return round(max(related_risk, default=0.0) * 100)


def _dashboard_kind(entity: Any, edge_states: list[Any]) -> str:
    if entity.entity_type == "firm":
        sends_risk_to_firm = any(
            edge.source_id == entity.canonical_id and edge.edge_type in {"risk_transmits_to", "supplies_to"}
            for edge in edge_states
        )
        return "supplier" if sends_risk_to_firm else "company"
    if entity.entity_type in {"port", "airport"}:
        return "facility"
    if entity.entity_type == "product":
        return "commodity"
    if entity.entity_type in {"risk_event", "text_artifact"}:
        return "route"
    if _is_data_node(entity.entity_type):
        return "data"
    return "country"


def _node_position(index: int, total: int, kind: str) -> tuple[int, int]:
    lanes = {
        "company": (32, 50),
        "supplier": (18, 35),
        "facility": (55, 64),
        "commodity": (72, 31),
        "route": (78, 58),
        "country": (48, 78),
        "data": (84, 18),
    }
    base_x, base_y = lanes.get(kind, (50, 50))
    offset = (index % max(1, total)) * 5
    return min(88, base_x + offset % 14), min(86, base_y + (offset // 2) % 10)


def _dashboard_graph_nodes(
    entities: list[Any],
    edge_states: list[Any],
    prediction_by_target: dict[str, Any],
    source_by_entity_id: dict[str, str],
    metrics_by_node: dict[str, dict[str, Any]] | None = None,
    node_country_by_id: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    nodes = []
    total = len(entities)
    metrics_by_node = metrics_by_node or {}
    node_country_by_id = node_country_by_id or {}
    for index, entity in enumerate(entities):
        kind = _dashboard_kind(entity, edge_states)
        metrics = metrics_by_node.get(entity.canonical_id, {})
        risk_score = float(metrics.get("riskScore", _entity_score(entity.canonical_id, edge_states, prediction_by_target) / 100))
        score = round(risk_score * 100)
        geo_context = _geo_context_from_entity(entity)
        country_code = node_country_by_id.get(entity.canonical_id) or _country_code_from_entity(entity) or "unknown"
        x, y = _node_position(index, total, kind)
        metadata = {
            "entity_type": entity.entity_type,
            "source": source_by_entity_id.get(entity.canonical_id, "unknown"),
            "country": country_code,
            "industry": entity.industry or "not applicable",
            "confidence": round(entity.confidence, 3),
            "geoId": geo_context["geoId"],
            "geoLevel": geo_context["geoLevel"],
            "countryCode": geo_context["countryCode"],
            "provinceCode": geo_context.get("provinceCode") or "",
            "parentGeoId": geo_context.get("parentGeoId") or "",
            "sourceCountryCode": geo_context.get("sourceCountryCode") or "",
        }
        metadata.update(entity.external_ids)
        nodes.append(
            {
                "id": entity.canonical_id,
                "label": _entity_display_name(entity),
                "kind": kind,
                "level": _dashboard_risk_level(score),
                "score": score,
                "x": x,
                "y": y,
                "metadata": metadata,
                "countryCode": country_code,
                "geoId": geo_context["geoId"],
                "geoLevel": geo_context["geoLevel"],
                "provinceCode": geo_context.get("provinceCode"),
                "parentGeoId": geo_context.get("parentGeoId"),
                "sourceCountryCode": geo_context.get("sourceCountryCode"),
                "displayName": geo_context["displayName"],
                "entityType": entity.entity_type,
                "riskScore": round(risk_score, 4),
                "centralityScore": round(float(metrics.get("centralityScore", 0.0)), 4),
                "criticalityScore": round(float(metrics.get("criticalityScore", 0.0)), 4),
                "criticalityRank": int(metrics.get("criticalityRank", 0)),
                "inDegree": int(metrics.get("inDegree", 0)),
                "outDegree": int(metrics.get("outDegree", 0)),
                "weightedDegree": round(float(metrics.get("weightedDegree", 0.0)), 3),
                "pathThroughCount": int(metrics.get("pathThroughCount", 0)),
                "riskDrivers": metrics.get("riskDrivers", []),
            }
        )
    return nodes


def _dashboard_graph_links(
    edge_states: list[Any],
    node_country_by_id: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    node_country_by_id = node_country_by_id or {}
    return [
        {
            "id": edge.edge_id,
            "source": edge.source_id,
            "target": edge.target_id,
            "label": edge.edge_type,
            "weight": edge.weight,
            "level": _dashboard_risk_level(round(edge.risk_score * 100)),
            "edgeType": edge.edge_type,
            "riskScore": round(edge.risk_score, 4),
            "confidence": round(edge.confidence, 3),
            "sourceId": edge.source,
            "transmissionWeight": round(_edge_transmission_weight(edge), 4),
            "lagDays": int(edge.attributes.get("lag_days", edge.attributes.get("lagDays", 0)) or 0),
            "sourceCountry": node_country_by_id.get(edge.source_id, "unknown"),
            "targetCountry": node_country_by_id.get(edge.target_id, "unknown"),
            "edgeRole": _edge_role(edge.edge_type),
        }
        for edge in edge_states
    ]


def _graph_metrics_by_node(
    entities: list[Any],
    edge_states: list[Any],
    prediction_by_target: dict[str, Any],
    paths: list[Any],
    entity_by_id: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    node_ids = {entity.canonical_id for entity in entities}
    risk_by_node = {
        entity_id: (prediction_by_target[entity_id].risk_score if entity_id in prediction_by_target else 0.0)
        for entity_id in node_ids
    }
    in_degree = {entity_id: 0 for entity_id in node_ids}
    out_degree = {entity_id: 0 for entity_id in node_ids}
    weighted_degree = {entity_id: 0.0 for entity_id in node_ids}
    incoming_weight: dict[str, float] = {entity_id: 0.0 for entity_id in node_ids}
    outgoing_weight: dict[str, dict[str, float]] = {entity_id: {} for entity_id in node_ids}
    risk_driver_edges: dict[str, list[Any]] = {entity_id: [] for entity_id in node_ids}

    for edge in edge_states:
        if edge.source_id not in node_ids or edge.target_id not in node_ids:
            continue
        transmission_weight = _edge_transmission_weight(edge)
        out_degree[edge.source_id] += 1
        in_degree[edge.target_id] += 1
        weighted_degree[edge.source_id] += transmission_weight
        weighted_degree[edge.target_id] += transmission_weight
        incoming_weight[edge.target_id] += transmission_weight
        outgoing_weight.setdefault(edge.source_id, {})[edge.target_id] = (
            outgoing_weight.setdefault(edge.source_id, {}).get(edge.target_id, 0.0) + transmission_weight
        )
        if edge.edge_type in TRANSMISSION_EDGE_TYPES:
            risk_by_node[edge.source_id] = max(risk_by_node.get(edge.source_id, 0.0), edge.risk_score * 0.92)
            risk_by_node[edge.target_id] = max(risk_by_node.get(edge.target_id, 0.0), edge.risk_score)
            risk_driver_edges[edge.source_id].append(edge)
            risk_driver_edges[edge.target_id].append(edge)

    page_rank = {entity_id: 1.0 / max(1, len(node_ids)) for entity_id in node_ids}
    for _ in range(16):
        next_rank = {entity_id: 0.15 / max(1, len(node_ids)) for entity_id in node_ids}
        for source_id, targets in outgoing_weight.items():
            total_weight = sum(targets.values())
            if total_weight <= 0:
                continue
            for target_id, weight in targets.items():
                next_rank[target_id] = next_rank.get(target_id, 0.0) + 0.85 * page_rank.get(source_id, 0.0) * (weight / total_weight)
        page_rank = next_rank

    path_through = {entity_id: 0.0 for entity_id in node_ids}
    for path in paths:
        if not any(edge_type in PRIMARY_TRANSMISSION_EDGE_TYPES for edge_type in path.meta_path.split(">")):
            continue
        for node_id in path.node_sequence:
            if node_id in path_through:
                path_through[node_id] += max(0.1, path.path_risk * path.path_confidence)

    normalized_risk = _normalize_metric(risk_by_node)
    normalized_rank = _normalize_metric(page_rank)
    normalized_path = _normalize_metric(path_through)
    metrics_by_node: dict[str, dict[str, Any]] = {}
    confidence_by_node = {
        entity.canonical_id: _clamp_float(entity.confidence, 0.0, 1.0)
        for entity in entities
    }
    raw_scores: dict[str, float] = {}
    for entity_id in node_ids:
        confidence_adj = 0.7 + 0.3 * confidence_by_node.get(entity_id, 0.75)
        raw_scores[entity_id] = confidence_adj * (
            0.55 * normalized_risk.get(entity_id, 0.0)
            + 0.30 * normalized_rank.get(entity_id, 0.0)
            + 0.15 * normalized_path.get(entity_id, 0.0)
        )
    ranked_ids = sorted(
        node_ids,
        key=lambda entity_id: (
            raw_scores.get(entity_id, 0.0),
            risk_by_node.get(entity_id, 0.0),
            weighted_degree.get(entity_id, 0.0),
            _entity_label(entity_by_id, entity_id),
        ),
        reverse=True,
    )
    for rank, entity_id in enumerate(ranked_ids, start=1):
        top_drivers = sorted(risk_driver_edges.get(entity_id, []), key=lambda edge: (edge.risk_score, edge.weight), reverse=True)[:4]
        metrics_by_node[entity_id] = {
            "riskScore": round(risk_by_node.get(entity_id, 0.0), 4),
            "centralityScore": round(normalized_rank.get(entity_id, 0.0), 4),
            "criticalityScore": round(raw_scores.get(entity_id, 0.0), 4),
            "criticalityRank": rank,
            "inDegree": in_degree.get(entity_id, 0),
            "outDegree": out_degree.get(entity_id, 0),
            "weightedDegree": weighted_degree.get(entity_id, 0.0),
            "pathThroughCount": int(round(path_through.get(entity_id, 0.0))),
            "riskDrivers": [
                f"{edge.edge_type}: {_entity_label(entity_by_id, edge.source_id)} -> {_entity_label(entity_by_id, edge.target_id)}"
                for edge in top_drivers
            ],
        }
    return metrics_by_node


def _critical_nodes_payload(nodes: list[dict[str, Any]], limit: int = 18) -> list[dict[str, Any]]:
    ranked = sorted(
        nodes,
        key=lambda node: (
            node.get("criticalityScore", 0),
            node.get("riskScore", node.get("score", 0)),
            node.get("centralityScore", 0),
        ),
        reverse=True,
    )[:limit]
    return [
        {
            "id": node["id"],
            "label": node["label"],
            "kind": node["kind"],
            "level": node["level"],
            "score": node["score"],
            "countryCode": node.get("countryCode"),
            "geoId": node.get("geoId"),
            "geoLevel": node.get("geoLevel"),
            "provinceCode": node.get("provinceCode"),
            "parentGeoId": node.get("parentGeoId"),
            "sourceCountryCode": node.get("sourceCountryCode"),
            "entityType": node.get("entityType"),
            "riskScore": node.get("riskScore", node["score"]),
            "centralityScore": node.get("centralityScore", 0),
            "criticalityScore": node.get("criticalityScore", 0),
            "criticalityRank": node.get("criticalityRank", 0),
            "inDegree": node.get("inDegree", 0),
            "outDegree": node.get("outDegree", 0),
            "weightedDegree": node.get("weightedDegree", 0),
            "pathThroughCount": node.get("pathThroughCount", 0),
            "drivers": node.get("riskDrivers", []),
            "riskDrivers": node.get("riskDrivers", []),
        }
        for node in ranked
    ]


def _transmission_paths_payload(
    paths: list[Any],
    edge_states: list[Any],
    entity_by_id: dict[str, Any],
    node_country_by_id: dict[str, str],
    *,
    top_k: int = 12,
) -> list[dict[str, Any]]:
    edge_by_id = {edge.edge_id: edge for edge in edge_states}
    rendered_paths: list[dict[str, Any]] = []
    candidates = []
    for path in paths:
        edge_sequence = [edge_by_id.get(edge_id) for edge_id in path.edge_sequence]
        if any(edge is None for edge in edge_sequence):
            continue
        edge_types = [edge.edge_type for edge in edge_sequence if edge]
        if not edge_types or not any(edge_type in PRIMARY_TRANSMISSION_EDGE_TYPES for edge_type in edge_types):
            continue
        if any(edge_type in CONTEXT_EDGE_TYPES for edge_type in edge_types):
            continue
        if len(set(path.node_sequence)) != len(path.node_sequence):
            continue
        transmission_score = path.path_risk * path.path_confidence * max(0.12, path.path_weight)
        candidates.append((transmission_score, path))

    for transmission_score, path in sorted(candidates, key=lambda item: (item[0], item[1].path_risk), reverse=True)[:top_k]:
        edge_sequence = [edge_by_id[edge_id] for edge_id in path.edge_sequence]
        bottleneck = min(edge_sequence, key=lambda edge: (edge.confidence, edge.weight))
        country_sequence = [
            node_country_by_id.get(node_id) or _country_code_from_entity(entity_by_id.get(node_id)) or "unknown"
            for node_id in path.node_sequence
        ]
        steps = []
        for index, node_id in enumerate(path.node_sequence):
            entity = entity_by_id.get(node_id)
            incoming_edge = edge_sequence[index - 1] if index > 0 else None
            contribution = incoming_edge.risk_score * incoming_edge.confidence * incoming_edge.weight if incoming_edge else path.path_risk
            steps.append(
                {
                    "id": f"{path.path_id}-step-{index}",
                    "nodeId": node_id,
                    "label": _entity_label(entity_by_id, node_id),
                    "kind": _dashboard_kind(entity, edge_states) if entity else "signal",
                    "level": _dashboard_risk_level(round((incoming_edge.risk_score if incoming_edge else path.path_risk) * 100)),
                    "contribution": round(contribution * 100),
                    "countryCode": country_sequence[index],
                    "evidence": f"{incoming_edge.source} {incoming_edge.edge_type}" if incoming_edge else path.meta_path,
                    "edgeId": incoming_edge.edge_id if incoming_edge else None,
                    "edgeType": incoming_edge.edge_type if incoming_edge else None,
                    "confidence": round(incoming_edge.confidence if incoming_edge else path.path_confidence, 3),
                    "sourceId": incoming_edge.source if incoming_edge else "path_index",
                }
            )
        rendered_paths.append(
            {
                "id": path.path_id,
                "title": f"{path.meta_path} path to {_entity_label(entity_by_id, path.target_id)}",
                "sourceId": path.source_id,
                "targetId": path.target_id,
                "sourceLabel": _entity_label(entity_by_id, path.source_id),
                "targetLabel": _entity_label(entity_by_id, path.target_id),
                "targetCompany": _entity_label(entity_by_id, path.target_id),
                "scoreMove": round(path.path_risk * 10, 1),
                "confidence": round(path.path_confidence, 3),
                "pathRisk": round(path.path_risk, 4),
                "pathConfidence": round(path.path_confidence, 4),
                "pathWeight": round(path.path_weight, 4),
                "transmissionScore": round(transmission_score, 4),
                "nodeSequence": list(path.node_sequence),
                "edgeSequence": list(path.edge_sequence),
                "countrySequence": country_sequence,
                "bottleneckEdgeId": bottleneck.edge_id,
                "steps": steps,
                "summary": f"{len(path.edge_sequence)} hop transmission using {path.meta_path}; bottleneck edge {bottleneck.edge_type} has {round(bottleneck.confidence * 100)}% confidence.",
            }
        )
    return rendered_paths


def _country_lens_payload(
    nodes: list[dict[str, Any]],
    links: list[dict[str, Any]],
    critical_nodes: list[dict[str, Any]],
    transmission_paths: list[dict[str, Any]],
    entity_by_id: dict[str, Any],
) -> dict[str, Any]:
    country_nodes: dict[str, list[dict[str, Any]]] = {}
    country_source_counts: dict[str, dict[str, int]] = {}
    country_subdivision_nodes: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for node in nodes:
        code = str(node.get("countryCode") or node.get("metadata", {}).get("country") or "unknown").upper()
        if code in {"", "NONE", "GLOBAL", "UNKNOWN"}:
            code = "unknown"
        country_nodes.setdefault(code, []).append(node)
        province_code = str(node.get("provinceCode") or node.get("metadata", {}).get("provinceCode") or "").upper()
        geo_id = str(node.get("geoId") or node.get("metadata", {}).get("geoId") or "")
        if province_code and geo_id:
            country_subdivision_nodes.setdefault(code, {}).setdefault(geo_id, []).append(node)
        source = str(node.get("metadata", {}).get("source") or "unknown")
        country_source_counts.setdefault(code, {})[source] = country_source_counts.setdefault(code, {}).get(source, 0) + 1

    inbound: dict[str, float] = {}
    outbound: dict[str, float] = {}
    edge_count_by_country: dict[str, int] = {}
    country_edge_map: dict[tuple[str, str], dict[str, Any]] = {}
    for link in links:
        source_country = str(link.get("sourceCountry") or "unknown")
        target_country = str(link.get("targetCountry") or "unknown")
        if source_country == target_country:
            continue
        risk = float(link.get("riskScore", 0))
        weight = float(link.get("transmissionWeight", link.get("weight", 0)))
        outbound[source_country] = outbound.get(source_country, 0.0) + risk * weight
        inbound[target_country] = inbound.get(target_country, 0.0) + risk * weight
        edge_count_by_country[source_country] = edge_count_by_country.get(source_country, 0) + 1
        edge_count_by_country[target_country] = edge_count_by_country.get(target_country, 0) + 1
        key = (source_country, target_country)
        bucket = country_edge_map.setdefault(
            key,
            {
                "id": f"country_edge_{source_country.lower()}_{target_country.lower()}",
                "sourceCountry": source_country,
                "targetCountry": target_country,
                "edgeCount": 0,
                "riskScore": 0.0,
                "transmissionWeight": 0.0,
                "topEdgeTypes": {},
            },
        )
        bucket["edgeCount"] += 1
        bucket["riskScore"] = max(bucket["riskScore"], risk)
        bucket["transmissionWeight"] += weight
        edge_type = str(link.get("edgeType") or link.get("label") or "edge")
        bucket["topEdgeTypes"][edge_type] = bucket["topEdgeTypes"].get(edge_type, 0) + 1

    countries = []
    for code, country_node_list in country_nodes.items():
        max_risk = max((float(node.get("riskScore", node.get("score", 0))) for node in country_node_list), default=0.0)
        max_centrality = max((float(node.get("centralityScore", 0)) for node in country_node_list), default=0.0)
        edge_pressure = (inbound.get(code, 0.0) + outbound.get(code, 0.0)) / max(1, edge_count_by_country.get(code, 0))
        aggregate_risk = max(max_risk, min(1.0, edge_pressure))
        countries.append(
            {
                "code": code,
                "label": _country_name(code, entity_by_id) if code != "unknown" else "Unknown",
                "countryCode": code,
                "countryName": _country_name(code, entity_by_id) if code != "unknown" else "Unknown",
                "entityCount": len(country_node_list),
                "edgeCount": edge_count_by_country.get(code, 0),
                "riskScore": round(aggregate_risk, 4),
                "centralityScore": round(max_centrality, 4),
                "inboundRisk": round(inbound.get(code, 0.0), 2),
                "outboundRisk": round(outbound.get(code, 0.0), 2),
                "subdivisions": [
                    {
                        "geoId": geo_id,
                        "label": TAIWAN_PROVINCE_DISPLAY if geo_id == "province_cn_tw" else geo_id,
                        "provinceCode": str(subdivision_nodes[0].get("provinceCode") or subdivision_nodes[0].get("metadata", {}).get("provinceCode") or ""),
                        "entityCount": len(subdivision_nodes),
                        "riskScore": round(max(float(node.get("riskScore", node.get("score", 0))) for node in subdivision_nodes), 4),
                    }
                    for geo_id, subdivision_nodes in sorted(country_subdivision_nodes.get(code, {}).items())
                ],
            }
        )
    countries = sorted(countries, key=lambda country: (country["riskScore"], country["edgeCount"], country["entityCount"]), reverse=True)
    selected_country = next((country for country in countries if country["code"] == "CN"), countries[0] if countries else {"code": "unknown", "label": "Unknown"})
    selected_code = selected_country["code"]
    selected_nodes = [node for node in critical_nodes if (node.get("countryCode") or "unknown") == selected_code]
    if not selected_nodes:
        selected_nodes = [
            {
                "id": node["id"],
                "label": node["label"],
                "kind": node["kind"],
                "level": node["level"],
                "score": node["score"],
                "countryCode": node.get("countryCode"),
                "criticalityScore": node.get("criticalityScore", 0),
                "centralityScore": node.get("centralityScore", 0),
                "drivers": node.get("riskDrivers", []),
            }
            for node in sorted(
                country_nodes.get(selected_code, []),
                key=lambda item: (item.get("criticalityScore", 0), item.get("riskScore", 0)),
                reverse=True,
            )[:8]
        ]
    selected_paths = [path for path in transmission_paths if selected_code in path.get("countrySequence", [])][:6]
    coverage = [
        {
            "countryCode": code,
            "sourceId": source,
            "nodeCount": count,
            "coverageScore": round(min(100, 48 + count * 2)),
        }
        for code, source_counts in sorted(country_source_counts.items())
        for source, count in sorted(source_counts.items(), key=lambda item: item[1], reverse=True)[:6]
    ]
    country_edges = []
    for edge in country_edge_map.values():
        edge["transmissionWeight"] = round(edge["transmissionWeight"], 3)
        edge["topEdgeTypes"] = [
            {"edgeType": edge_type, "count": count}
            for edge_type, count in sorted(edge["topEdgeTypes"].items(), key=lambda item: item[1], reverse=True)[:4]
        ]
        country_edges.append(edge)
    return {
        "selectedCountryCode": selected_code,
        "countries": countries,
        "countryEdges": sorted(country_edges, key=lambda item: (item["riskScore"], item["transmissionWeight"]), reverse=True)[:28],
        "topCriticalNodes": selected_nodes[:8],
        "topPaths": selected_paths,
        "dataCoverage": coverage,
        "countryCode": selected_code,
        "countryName": selected_country.get("label") or selected_country.get("countryName") or selected_code,
        "riskScore": selected_country.get("riskScore", 0),
        "criticalNodes": selected_nodes[:8],
        "transmissionPaths": selected_paths,
    }


def _graph_explorer_payload(
    result: Any,
    prediction_by_target: dict[str, Any],
    firm_entities: list[Any],
    source_by_entity_id: dict[str, str],
    paths: list[Any],
) -> dict[str, Any]:
    selected_node_id = _selected_entity_id(prediction_by_target, firm_entities)
    entity_by_id = {entity.canonical_id: entity for entity in result.real.entities}
    active_edges = _active_edge_states(result.edge_states)
    node_country_by_id = _node_country_index(result.real.entities, active_edges)
    metrics_by_node = _graph_metrics_by_node(
        result.real.entities,
        active_edges,
        prediction_by_target,
        paths,
        entity_by_id,
    )
    all_nodes = _dashboard_graph_nodes(
        result.real.entities,
        active_edges,
        prediction_by_target,
        source_by_entity_id,
        metrics_by_node,
        node_country_by_id,
    )
    all_links = _dashboard_graph_links(active_edges, node_country_by_id)
    critical_nodes = _critical_nodes_payload(all_nodes)
    transmission_paths = _transmission_paths_payload(paths, active_edges, entity_by_id, node_country_by_id)
    country_lens = _country_lens_payload(all_nodes, all_links, critical_nodes, transmission_paths, entity_by_id)
    node_limit = 128
    link_limit = 260
    selected_node_ids = _select_graph_node_ids(all_nodes, all_links, selected_node_id, node_limit)
    for node in critical_nodes[:14]:
        selected_node_ids.add(node["id"])
    for path in transmission_paths[:8]:
        selected_node_ids.update(path["nodeSequence"])
    selected_node_ids.update(node["id"] for node in country_lens["topCriticalNodes"][:8])
    if len(selected_node_ids) > node_limit:
        priority_ids = set()
        priority_ids.update(node["id"] for node in critical_nodes[:18])
        for path in transmission_paths[:10]:
            priority_ids.update(path["nodeSequence"])
        priority_ids.update(node["id"] for node in country_lens["topCriticalNodes"][:8])
        trimmed = [node["id"] for node in all_nodes if node["id"] in priority_ids][:node_limit]
        selected_node_ids = set(trimmed)
    selected_nodes = [node for node in all_nodes if node["id"] in selected_node_ids]
    selected_links = [
        link
        for link in sorted(
            all_links,
            key=lambda item: (
                item.get("edgeRole") == "transmission",
                risk_rank(item["level"]),
                item.get("transmissionWeight", item["weight"]),
            ),
            reverse=True,
        )
        if link["source"] in selected_node_ids and link["target"] in selected_node_ids
    ][:link_limit]
    transmission_edge_count = sum(1 for link in all_links if link.get("edgeRole") == "transmission")
    return {
        "selectedNodeId": selected_node_id if selected_node_id in selected_node_ids else (selected_nodes[0]["id"] if selected_nodes else selected_node_id),
        "filters": ["company", "supplier", "facility", "commodity", "route", "country", "data"],
        "dataSummary": _data_catalog_payload(result),
        "graphStats": _dashboard_graph_stats(all_nodes, all_links, node_limit, link_limit),
        "criticalNodes": critical_nodes,
        "transmissionPaths": transmission_paths,
        "transmissionSummary": {
            "pathCount": len(transmission_paths),
            "transmissionEdgeCount": transmission_edge_count,
            "maxHops": 4,
            "topK": 12,
            "contextEdgesSuppressed": sum(1 for link in all_links if link.get("edgeRole") != "transmission"),
        },
        "countryLens": country_lens,
        "availableCountries": country_lens["countries"],
        "truncated": {
            "nodes": len(all_nodes) > len(selected_nodes),
            "links": len(all_links) > len(selected_links),
            "renderedNodeLimit": node_limit,
            "renderedLinkLimit": link_limit,
        },
        "nodes": selected_nodes,
        "links": selected_links,
    }


def _select_graph_node_ids(
    nodes: list[dict[str, Any]],
    links: list[dict[str, Any]],
    selected_node_id: str,
    limit: int,
) -> set[str]:
    node_by_id = {node["id"]: node for node in nodes}
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for link in links:
        adjacency.setdefault(link["source"], []).append(link)
        adjacency.setdefault(link["target"], []).append(link)
    selected: set[str] = set()
    ordered_selected: list[str] = []

    def add_node(node_id: str) -> None:
        if node_id not in node_by_id or node_id in selected or len(ordered_selected) >= limit:
            return
        selected.add(node_id)
        ordered_selected.append(node_id)

    if selected_node_id in node_by_id:
        add_node(selected_node_id)
        for link in sorted(adjacency.get(selected_node_id, []), key=lambda item: risk_rank(item["level"]), reverse=True)[:32]:
            add_node(link["source"])
            add_node(link["target"])
    priority_data_node_ids = [
        "data_source_usgs_earthquakes",
        "dataset_usgs_m45_earthquakes_month",
        "indicator_high_tech_exports",
        "risk_event_usgs_taiwan_m62",
        "risk_event_usgs_japan_m57",
    ]
    for node_id in priority_data_node_ids:
        add_node(node_id)
        for link in sorted(adjacency.get(node_id, []), key=lambda item: risk_rank(item["level"]), reverse=True)[:8]:
            add_node(link["source"])
            add_node(link["target"])
    ranked_nodes = sorted(
        nodes,
        key=lambda node: (
            risk_rank(node["level"]),
            node["kind"] in {"company", "supplier", "facility", "route"},
            node["score"],
            node["label"],
        ),
        reverse=True,
    )
    for node in ranked_nodes:
        add_node(node["id"])
        if len(ordered_selected) >= limit:
            break
    for link in sorted(links, key=lambda item: risk_rank(item["level"]), reverse=True):
        if len(ordered_selected) >= limit:
            break
        if link["source"] in selected or link["target"] in selected:
            add_node(link["source"])
            add_node(link["target"])
    return set(ordered_selected)


def _dashboard_graph_stats(
    nodes: list[dict[str, Any]],
    links: list[dict[str, Any]],
    node_limit: int,
    link_limit: int,
) -> dict[str, Any]:
    by_kind: dict[str, int] = {}
    by_source: dict[str, int] = {}
    high_risk_nodes = 0
    for node in nodes:
        by_kind[node["kind"]] = by_kind.get(node["kind"], 0) + 1
        source = str(node.get("metadata", {}).get("source") or "unknown")
        by_source[source] = by_source.get(source, 0) + 1
        if node["level"] in {"severe", "critical"}:
            high_risk_nodes += 1
    high_risk_links = sum(1 for link in links if link["level"] in {"severe", "critical"})
    return {
        "totalNodes": len(nodes),
        "totalLinks": len(links),
        "renderedNodeLimit": node_limit,
        "renderedLinkLimit": link_limit,
        "highRiskNodes": high_risk_nodes,
        "highRiskLinks": high_risk_links,
        "byKind": [{"kind": kind, "count": count} for kind, count in sorted(by_kind.items())],
        "bySource": [{"source": source, "count": count} for source, count in sorted(by_source.items())],
    }


def risk_rank(level: str) -> int:
    return {"critical": 4, "severe": 3, "elevated": 2, "guarded": 1, "low": 0}.get(level, 0)


def _dashboard_hotspots(
    entities: list[Any],
    edge_states: list[Any],
    entity_by_id: dict[str, Any],
) -> list[dict[str, Any]]:
    ranked = sorted(
        entities,
        key=lambda entity: _entity_score(entity.canonical_id, edge_states, {}),
        reverse=True,
    )[:4]
    hotspots = []
    for index, entity in enumerate(ranked):
        score = _entity_score(entity.canonical_id, edge_states, {})
        related_edges = [
            edge
            for edge in edge_states
            if edge.source_id == entity.canonical_id or edge.target_id == entity.canonical_id
        ]
        x, y = _node_position(index, max(1, len(ranked)), _dashboard_kind(entity, edge_states))
        hotspots.append(
            {
                "id": entity.canonical_id,
                "label": entity.display_name,
                "region": entity.country or entity.industry or "global",
                "level": _dashboard_risk_level(score),
                "score": score,
                "x": x,
                "y": y,
                "drivers": [
                    f"{edge.edge_type}: {_entity_label(entity_by_id, edge.source_id)} -> {_entity_label(entity_by_id, edge.target_id)}"
                    for edge in related_edges[:3]
                ] or [entity.industry or entity.entity_type],
            }
        )
    return hotspots


def _dashboard_incidents(
    result: Any,
    entity_by_id: dict[str, Any],
    source_names: dict[str, str],
) -> list[dict[str, Any]]:
    incidents = []
    firm_ids = {entity.canonical_id for entity in result.real.entities if entity.entity_type == "firm"}
    for event in result.real.silver_events:
        entity_ids = [entry.entity_id for entry in event.entities]
        affected_firms = [entity_id for entity_id in entity_ids if entity_id in firm_ids]
        named_entities = [_entity_label(entity_by_id, entity_id) for entity_id in entity_ids[:3]]
        source_id = event.source_refs[0].source_id if event.source_refs else "unknown"
        score = round(event.confidence * 100)
        incidents.append(
            {
                "id": event.event_id,
                "title": f"{event.event_type} evidence: {' / '.join(named_entities)}",
                "region": source_names.get(source_id, source_id),
                "level": _dashboard_risk_level(score),
                "startedAt": event.event_time.isoformat(),
                "affectedCompanies": len(affected_firms),
                "signalStrength": event.confidence,
            }
        )
    return incidents


def _dashboard_corridors(edge_states: list[Any], entity_by_id: dict[str, Any]) -> list[dict[str, Any]]:
    route_edges = [
        edge
        for edge in edge_states
        if edge.edge_type in {"ships_through", "route_connects", "risk_transmits_to", "event_affects"}
    ]
    return [
        {
            "id": edge.edge_id,
            "source": _entity_label(entity_by_id, edge.source_id),
            "target": _entity_label(entity_by_id, edge.target_id),
            "commodity": edge.edge_type,
            "level": _dashboard_risk_level(round(edge.risk_score * 100)),
            "score": round(edge.risk_score * 100),
            "volumeShare": min(1.0, edge.weight),
        }
        for edge in sorted(route_edges, key=lambda item: item.risk_score, reverse=True)[:4]
    ]


def _dashboard_companies(
    firm_entities: list[Any],
    edge_states: list[Any],
    prediction_by_target: dict[str, Any],
    entity_by_id: dict[str, Any],
) -> list[dict[str, Any]]:
    companies = []
    for firm in sorted(
        firm_entities,
        key=lambda entity: prediction_by_target.get(entity.canonical_id).risk_score
        if entity.canonical_id in prediction_by_target
        else 0.0,
        reverse=True,
    ):
        prediction = prediction_by_target.get(firm.canonical_id)
        score = round((prediction.risk_score if prediction else 0.0) * 100)
        related_edges = [
            edge
            for edge in edge_states
            if edge.source_id == firm.canonical_id or edge.target_id == firm.canonical_id
        ]
        suppliers = [
            {
                "id": edge.edge_id,
                "supplier": _entity_label(
                    entity_by_id,
                    edge.source_id if edge.target_id == firm.canonical_id else edge.target_id,
                ),
                "country": entity_by_id.get(edge.source_id if edge.target_id == firm.canonical_id else edge.target_id).country
                if entity_by_id.get(edge.source_id if edge.target_id == firm.canonical_id else edge.target_id)
                else "global",
                "category": edge.edge_type,
                "spendShare": 0,
                "dependency": min(1.0, edge.weight),
                "level": _dashboard_risk_level(round(edge.risk_score * 100)),
                "leadTimeDays": int(edge.attributes.get("lag_days", 0)),
            }
            for edge in sorted(related_edges, key=lambda item: item.risk_score, reverse=True)[:4]
        ]
        companies.append(
            {
                "id": firm.canonical_id,
                "name": firm.display_name,
                "ticker": firm.external_ids.get("ticker", firm.external_ids.get("sec_cik", "n/a")),
                "sector": firm.industry or firm.entity_type,
                "headquarters": firm.country or "global",
                "riskScore": score,
                "confidence": prediction.confidence_high if prediction else firm.confidence,
                "level": _dashboard_risk_level(score),
                "revenueAtRiskUsd": 0,
                "topDrivers": prediction.top_drivers if prediction else ["public_entity_evidence"],
                "mitigations": [
                    "Validate public evidence against licensed supplier master data before operational action",
                    "Monitor source manifest freshness before graph promotion",
                    "Attach commercial trade or AIS feeds before revenue-at-risk attribution",
                ],
                "suppliers": suppliers,
            }
        )
    return companies


def _dashboard_paths(
    paths: list[Any],
    edge_states: list[Any],
    entity_by_id: dict[str, Any],
) -> list[dict[str, Any]]:
    edge_by_id = {edge.edge_id: edge for edge in edge_states}
    rendered_paths = []
    for path in sorted(paths, key=lambda item: item.path_risk, reverse=True)[:4]:
        target_label = _entity_label(entity_by_id, path.target_id)
        steps = []
        for index, node_id in enumerate(path.node_sequence):
            entity = entity_by_id.get(node_id)
            edge = edge_by_id.get(path.edge_sequence[index - 1]) if index > 0 and index - 1 < len(path.edge_sequence) else None
            score = round((edge.risk_score if edge else path.path_risk) * 100)
            steps.append(
                {
                    "id": f"{path.path_id}-step-{index}",
                    "label": _entity_label(entity_by_id, node_id),
                    "kind": _dashboard_kind(entity, edge_states) if entity else "signal",
                    "level": _dashboard_risk_level(score),
                    "contribution": score,
                    "evidence": f"{edge.source} {edge.edge_type}" if edge else path.meta_path,
                }
            )
        rendered_paths.append(
            {
                "id": path.path_id,
                "title": f"{path.meta_path} path to {target_label}",
                "targetCompany": target_label,
                "scoreMove": round(path.path_risk * 10, 1),
                "confidence": path.path_confidence,
                "steps": steps,
                "summary": f"Derived from graph snapshot path {path.path_id} with manifest-backed edge sequence.",
            }
        )
    return rendered_paths


def _dashboard_evidence(
    result: Any,
    entity_by_id: dict[str, Any],
    source_names: dict[str, str],
) -> list[dict[str, Any]]:
    evidence_items = []
    for event in result.real.silver_events:
        entity_labels = [_entity_label(entity_by_id, entry.entity_id) for entry in event.entities]
        source_id = event.source_refs[0].source_id if event.source_refs else "unknown"
        score = round(event.confidence * 100)
        method = "news-signal" if source_id == "gdelt" else "expert" if source_id in {"ofac", "nga_world_port_index"} else "graph-inference"
        evidence_items.append(
            {
                "id": event.event_id,
                "claim": f"{event.event_type} evidence links {' / '.join(entity_labels)}",
                "source": source_names.get(source_id, source_id),
                "method": method,
                "confidence": event.confidence,
                "level": _dashboard_risk_level(score),
                "lastReviewed": event.observed_time.date().isoformat(),
                "disagreement": round(1.0 - event.confidence, 2),
            }
        )
    for edge in sorted(result.edge_states, key=lambda item: item.risk_score, reverse=True)[:2]:
        score = round(edge.confidence * 100)
        evidence_items.append(
            {
                "id": f"edge-evidence-{edge.edge_id}",
                "claim": f"{edge.edge_type} edge connects {_entity_label(entity_by_id, edge.source_id)} to {_entity_label(entity_by_id, edge.target_id)}",
                "source": source_names.get(edge.source, edge.source),
                "method": "graph-inference",
                "confidence": edge.confidence,
                "level": _dashboard_risk_level(score),
                "lastReviewed": edge.valid_from.date().isoformat(),
                "disagreement": round(1.0 - edge.confidence, 2),
            }
        )
    return evidence_items


def _dashboard_services(result: Any) -> list[dict[str, Any]]:
    freshness = result.real.freshness
    stale_count = sum(1 for item in freshness if item.status != "fresh")
    max_lag = max((item.max_stale_minutes for item in freshness), default=0)
    return [
        {"id": "svc-api", "service": "Risk API", "owner": "platform", "status": "operational", "latencyMs": 72, "freshnessMinutes": 0, "errorRate": 0.0},
        {"id": "svc-ingest", "service": "Public source ingest", "owner": "data", "status": "operational" if stale_count == 0 else "degraded", "latencyMs": 96, "freshnessMinutes": max_lag, "errorRate": stale_count / max(1, len(freshness))},
        {"id": "svc-graph", "service": "Temporal graph snapshot", "owner": "graph", "status": "operational", "latencyMs": 118, "freshnessMinutes": 0, "errorRate": 0.0},
        {"id": "svc-model", "service": "Baseline public scorer", "owner": "ml", "status": "operational", "latencyMs": 84, "freshnessMinutes": 0, "errorRate": 0.0},
    ]


def _calculate_dashboard_shock(payload: dict[str, Any], result: Any) -> dict[str, Any]:
    input_payload = {
        "region": str(payload.get("region") or "Red Sea / East Asia corridor"),
        "commodity": str(payload.get("commodity") or "advanced semiconductor components"),
        "severity": _clamp_int(payload.get("severity"), 10, 100, 72),
        "durationDays": _clamp_int(payload.get("durationDays"), 3, 90, 28),
        "scope": payload.get("scope") if payload.get("scope") in {"facility", "regional", "global"} else "regional",
    }
    entity_by_id = {entity.canonical_id: entity for entity in result.real.entities}
    scope_multiplier = {"facility": 0.78, "regional": 1.1, "global": 1.35}[input_payload["scope"]]
    duration_factor = min(1.6, input_payload["durationDays"] / 35)
    max_graph_risk = max((edge.risk_score for edge in result.edge_states), default=0.0)
    impact_score = min(
        99,
        round(input_payload["severity"] * 0.44 * scope_multiplier + duration_factor * 12 + max_graph_risk * 35),
    )
    level = _dashboard_risk_level(impact_score)
    top_edges = sorted(result.edge_states, key=lambda edge: edge.risk_score, reverse=True)[:3]
    affected_firms = {
        edge.source_id
        for edge in top_edges
        if entity_by_id.get(edge.source_id) and entity_by_id[edge.source_id].entity_type == "firm"
    } | {
        edge.target_id
        for edge in top_edges
        if entity_by_id.get(edge.target_id) and entity_by_id[edge.target_id].entity_type == "firm"
    }
    return {
        "input": input_payload,
        "impactScore": impact_score,
        "ebitdaAtRiskUsd": 0,
        "timeToRecoveryDays": round(input_payload["durationDays"] * (0.9 + scope_multiplier / 3)),
        "affectedCompanies": len(affected_firms),
        "affectedPaths": [
            {
                "id": edge.edge_id,
                "label": f"{_entity_label(entity_by_id, edge.source_id)} -> {_entity_label(entity_by_id, edge.target_id)}",
                "impact": max(12, round(edge.risk_score * 100)),
                "level": _dashboard_risk_level(round(edge.risk_score * 100)),
            }
            for edge in top_edges
        ],
        "recommendations": [
            "Validate public evidence against private supplier master data before operational action",
            "Monitor GDELT, OFAC, and port reference deltas for the next graph promotion",
            "Add licensed trade or AIS sources before revenue-at-risk attribution",
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
        source_id: str | None = Query(default=None),
        category: str | None = Query(default=None),
        country: str | None = Query(default=None),
        industry: str | None = Query(default=None),
        q: str | None = Query(default=None),
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_entities(
            entity_type=entity_type,
            source_id=source_id,
            category=category,
            country=country,
            industry=industry,
            q=q,
            limit=limit,
            offset=offset,
            request_id=x_request_id,
        )

    @app.get("/sources", include_in_schema=False)
    @app.get("/api/v1/sources")
    def http_sources(
        source_id: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_sources(source_id=source_id, request_id=x_request_id)

    @app.get("/sources/{source_id}", include_in_schema=False)
    @app.get("/api/v1/sources/{source_id}")
    def http_source_detail(
        source_id: str,
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_sources(source_id=source_id, request_id=x_request_id)

    @app.get("/lineage", include_in_schema=False)
    @app.get("/api/v1/lineage")
    def http_lineage(
        source_id: str | None = Query(default=None),
        target_id: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_lineage(
            source_id=source_id,
            target_id=target_id,
            request_id=x_request_id,
        )

    @app.get("/lineage/{source_id}", include_in_schema=False)
    @app.get("/api/v1/lineage/{source_id}")
    def http_lineage_detail(
        source_id: str,
        target_id: str | None = Query(default=None),
        x_request_id: str | None = Header(default=None),
    ) -> dict[str, Any]:
        return route_lineage(
            source_id=source_id,
            target_id=target_id,
            request_id=x_request_id,
        )

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
        (entity for entity in entities_for_result(result) if entity.canonical_id == entity_id),
        None,
    )


def _request_id_from_request(request: Request) -> str | None:
    return request.headers.get("x-request-id")


app = create_app()
