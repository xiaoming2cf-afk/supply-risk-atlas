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
from sra_core.real_pipeline import real_metadata, run_public_real_pipeline


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
        entities = [entity for entity in entities if (entity.country or "").lower() == country.lower()]
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
        [entity.model_dump(mode="json") for entity in entities[offset : offset + limit]],
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
        entity.model_dump(mode="json"),
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
        metadata=metadata_for_result(result),
        request_id=request_id,
    )


def route_explanations(
    explanation_request: ExplanationRequest | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    result = run_public_real_pipeline()
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
    return _real_dashboard_payloads(result)


def _real_dashboard_payloads(result: Any) -> dict[str, dict[str, Any]]:
    entity_by_id = {entity.canonical_id: entity for entity in result.real.entities}
    source_names = {source.source_id: source.source_name for source in result.real.sources}
    source_by_entity_id = _source_names_by_entity(result)
    prediction_by_target = {prediction.target_id: prediction for prediction in result.predictions}
    paths = build_path_index(result.edge_states)
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
        "graph-explorer": {
            "selectedNodeId": _selected_entity_id(prediction_by_target, firm_entities),
            "filters": ["company", "supplier", "facility", "commodity", "route", "country", "data"],
            "dataSummary": _data_catalog_payload(result),
            "nodes": _dashboard_graph_nodes(
                result.real.entities,
                result.edge_states,
                prediction_by_target,
                source_by_entity_id,
            ),
            "links": _dashboard_graph_links(result.edge_states),
        },
        "company-risk-360": {
            "selectedCompanyId": _selected_entity_id(prediction_by_target, firm_entities),
            "companies": _dashboard_companies(firm_entities, result.edge_states, prediction_by_target, entity_by_id),
        },
        "path-explainer": {
            "selectedPathId": paths[0].path_id if paths else "path-unavailable",
            "paths": _dashboard_paths(paths, result.edge_states, entity_by_id),
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
    return entity_by_id[entity_id].display_name if entity_id in entity_by_id else entity_id


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
    if entity.entity_type in {"data_source", "data_category", "dataset", "indicator", "industry"}:
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
) -> list[dict[str, Any]]:
    nodes = []
    total = len(entities)
    for index, entity in enumerate(entities):
        kind = _dashboard_kind(entity, edge_states)
        score = _entity_score(entity.canonical_id, edge_states, prediction_by_target)
        x, y = _node_position(index, total, kind)
        metadata = {
            "entity_type": entity.entity_type,
            "source": source_by_entity_id.get(entity.canonical_id, "unknown"),
            "country": entity.country or "global",
            "industry": entity.industry or "not applicable",
            "confidence": round(entity.confidence, 3),
        }
        metadata.update(entity.external_ids)
        nodes.append(
            {
                "id": entity.canonical_id,
                "label": entity.display_name,
                "kind": kind,
                "level": _dashboard_risk_level(score),
                "score": score,
                "x": x,
                "y": y,
                "metadata": metadata,
            }
        )
    return nodes


def _dashboard_graph_links(edge_states: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": edge.edge_id,
            "source": edge.source_id,
            "target": edge.target_id,
            "label": edge.edge_type,
            "weight": edge.weight,
            "level": _dashboard_risk_level(round(edge.risk_score * 100)),
        }
        for edge in edge_states
    ]


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
