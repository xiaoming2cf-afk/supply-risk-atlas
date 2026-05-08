from __future__ import annotations

from typing import Any

from graph_kernel.path_index import build_path_index


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
    "located_in",
}

PRIMARY_TRANSMISSION_EDGE_TYPES = TRANSMISSION_EDGE_TYPES - {"located_in"}

GOVERNANCE_EDGE_TYPES = {
    "dataset_covers",
    "dataset_has_field",
    "dataset_measures",
    "dataset_observes",
    "licensed_under",
    "released_as",
    "source_provides",
}

COMPONENT_WEIGHTS = {
    "baseline": 0.22,
    "degree_exposure": 0.12,
    "graph_propagation": 0.24,
    "path_transmission": 0.24,
    "scenario_shock": 0.12,
    "evidence_coverage": 0.06,
}

PREDICTION_FORM = "public_evidence_graph_ensemble"


def clamp_float(value: Any, lower: float = 0.0, upper: float = 1.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return lower
    return max(lower, min(upper, numeric))


def path_transmission_score(path: Any) -> float:
    return (
        clamp_float(path.path_risk)
        * clamp_float(path.path_confidence)
        * max(0.12, float(path.path_weight or 0.0))
    )


def ranked_paths_for_target(
    paths: list[Any],
    edge_states: list[Any],
    target_id: str,
    *,
    top_k: int = 5,
) -> list[Any]:
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
    return sorted(
        candidates,
        key=lambda path: (path_transmission_score(path), path.path_risk),
        reverse=True,
    )[:top_k]


def classify_prediction_mechanism(top_paths: list[Any]) -> str:
    edge_types = {edge_type for path in top_paths for edge_type in path.meta_path.split(">")}
    if "event_affects" in edge_types:
        return "event_shock"
    if {"ships_through", "route_connects", "ships_to", "route_leg", "handled_at"} & edge_types:
        return "logistics_corridor"
    if {
        "supplies_to",
        "component_of",
        "input_to",
        "material_processed_into",
        "manufactured_at",
        "stored_at",
        "used_by",
    } & edge_types:
        return "supply_chain_dependency"
    if {"substitutes", "qualified_alternative_to"} & edge_types:
        return "resilience_alternative"
    if "risk_transmits_to" in edge_types:
        return "supplier_dependency"
    if "policy_targets" in edge_types:
        return "policy_exposure"
    if "located_in" in edge_types:
        return "country_context"
    return "public_evidence_graph"


def prediction_score_components(prediction: Any, sample: Any | None, top_paths: list[Any]) -> dict[str, float]:
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
        clamp_float(node_features.get("incoming_risk_mean", 0.0)),
        clamp_float(edge_features.get("incoming_risk_max", 0.0)),
    )
    path_signal = max(
        (path_transmission_score(path) for path in top_paths),
        default=clamp_float(node_features.get("path_risk_max", 0.0)),
    )
    event_signal = max(
        (path.path_risk for path in top_paths if "event_affects" in path.meta_path),
        default=0.0,
    )
    evidence_signal = min(
        1.0,
        (len([value for value in node_features.values() if value]) + len(top_paths)) / 10.0,
    )
    baseline = clamp_float(prediction.risk_score)
    return {
        "baseline": round(baseline, 4),
        "degree_exposure": round(degree_signal, 4),
        "graph_propagation": round(graph_signal, 4),
        "path_transmission": round(clamp_float(path_signal), 4),
        "scenario_shock": round(clamp_float(event_signal), 4),
        "evidence_coverage": round(evidence_signal, 4),
    }


def prediction_driver_contributions(
    components: dict[str, float],
    top_paths: list[Any],
) -> list[dict[str, Any]]:
    rows = [
        {
            "driver": key,
            "score": round(value, 4),
            "weight": COMPONENT_WEIGHTS[key],
            "contribution": round(value * COMPONENT_WEIGHTS[key], 4),
        }
        for key, value in components.items()
    ]
    if top_paths:
        top_path_score = path_transmission_score(top_paths[0])
        rows.append(
            {
                "driver": "top_path",
                "pathId": top_paths[0].path_id,
                "score": round(top_path_score, 4),
                "weight": 0.18,
                "contribution": round(top_path_score * 0.18, 4),
            }
        )
    return sorted(rows, key=lambda item: item["contribution"], reverse=True)


def prediction_path_details(
    paths: list[Any],
    edge_states: list[Any],
    entity_by_id: dict[str, Any],
) -> list[dict[str, Any]]:
    edge_by_id = {edge.edge_id: edge for edge in edge_states}
    total_score = sum(path_transmission_score(path) for path in paths) or 1.0
    details = []
    for path in paths:
        edge_sequence = [edge_by_id[edge_id] for edge_id in path.edge_sequence if edge_id in edge_by_id]
        bottleneck = min(edge_sequence, key=lambda edge: (edge.confidence * edge.weight, edge.confidence), default=None)
        transmission_score = path_transmission_score(path)
        details.append(
            {
                "pathId": path.path_id,
                "nodeSequence": list(path.node_sequence),
                "edgeSequence": list(path.edge_sequence),
                "nodeLabels": [entity_label(entity_by_id, node_id) for node_id in path.node_sequence],
                "edgeTypes": [edge.edge_type for edge in edge_sequence],
                "pathRisk": round(path.path_risk, 4),
                "pathConfidence": round(path.path_confidence, 4),
                "transmissionScore": round(transmission_score, 4),
                "pathContribution": round(transmission_score / total_score, 4),
                "bottleneckEdgeId": bottleneck.edge_id if bottleneck else None,
                "bottleneckEdgeType": bottleneck.edge_type if bottleneck else None,
                "bottleneckScore": round((bottleneck.confidence * bottleneck.weight), 4) if bottleneck else None,
                "evidenceRefs": sorted({edge.source for edge in edge_sequence}),
            }
        )
    return details


def prediction_source_coverage(path_details: list[dict[str, Any]], result: Any) -> dict[str, Any]:
    covered = sorted(
        {
            ref
            for path_detail in path_details
            for ref in path_detail.get("evidenceRefs", [])
            if ref
        }
    )
    source_ids = sorted(getattr(source, "source_id", "") for source in getattr(result.real, "sources", []))
    source_count = len([source_id for source_id in source_ids if source_id])
    coverage_score = min(1.0, len(covered) / max(1, source_count))
    return {
        "sourceCount": source_count,
        "coveredSourceCount": len(covered),
        "coverageScore": round(coverage_score, 4),
        "coveredSources": covered,
        "manifestRef": result.real.source_manifest_ref,
    }


def prediction_confidence_interval(prediction: Any, horizon_days: int) -> dict[str, Any]:
    low = clamp_float(prediction.confidence_low)
    high = clamp_float(prediction.confidence_high)
    return {
        "low": low,
        "high": high,
        "horizonDays": horizon_days,
        "width": round(high - low, 4),
        "method": "baseline_score_band_with_public_evidence_diagnostics",
    }


def prediction_sensitivity_diagnostics(
    components: dict[str, float],
    top_paths: list[Any],
    edge_states: list[Any],
) -> list[dict[str, Any]]:
    diagnostics: list[dict[str, Any]] = []
    for component, value in components.items():
        weight = COMPONENT_WEIGHTS.get(component, 0.0)
        diagnostics.append(
            {
                "factor": component,
                "baselineValue": round(value, 4),
                "direction": "up" if value * weight >= 0 else "flat",
                "deltaIfReduced10Pct": round(-value * weight * 0.10, 4),
                "deltaIfIncreased10Pct": round((1.0 - value) * weight * 0.10, 4),
            }
        )
    edge_by_id = {edge.edge_id: edge for edge in edge_states}
    for path in top_paths[:3]:
        edges = [edge_by_id.get(edge_id) for edge_id in path.edge_sequence]
        edges = [edge for edge in edges if edge is not None]
        bottleneck = min(edges, key=lambda edge: (edge.confidence * edge.weight, edge.confidence), default=None)
        if bottleneck is None:
            continue
        diagnostics.append(
            {
                "factor": "bottleneck_edge",
                "pathId": path.path_id,
                "edgeId": bottleneck.edge_id,
                "edgeType": bottleneck.edge_type,
                "baselineValue": round(bottleneck.confidence * bottleneck.weight, 4),
                "direction": "up",
                "deltaIfReduced10Pct": round(-path_transmission_score(path) * 0.10, 4),
                "deltaIfIncreased10Pct": round(path_transmission_score(path) * 0.10, 4),
            }
        )
    return sorted(
        diagnostics,
        key=lambda item: max(
            abs(float(item.get("deltaIfReduced10Pct", 0.0))),
            abs(float(item.get("deltaIfIncreased10Pct", 0.0))),
        ),
        reverse=True,
    )


def build_prediction_payloads(
    result: Any,
    prediction_request: Any | None = None,
) -> list[dict[str, Any]]:
    paths = build_path_index(result.edge_states, max_hops=4)
    entity_by_id = {entity.canonical_id: entity for entity in result.real.entities}
    samples_by_target = {sample.target_id: sample for sample in result.samples}
    payloads = []
    for prediction in result.predictions:
        if (
            prediction_request
            and prediction_request.target_id
            and prediction.target_id != prediction_request.target_id
        ):
            continue
        top_paths = ranked_paths_for_target(paths, result.edge_states, prediction.target_id)
        components = prediction_score_components(
            prediction,
            samples_by_target.get(prediction.target_id),
            top_paths,
        )
        path_details = prediction_path_details(top_paths, result.edge_states, entity_by_id)
        source_coverage = prediction_source_coverage(path_details, result)
        payload = prediction.model_dump(mode="json")
        payload["top_paths"] = [path.path_id for path in top_paths] or payload.get("top_paths", [])
        payload["score_components"] = components
        payload["driver_contributions"] = prediction_driver_contributions(components, top_paths)
        payload["prediction_form"] = PREDICTION_FORM
        payload["mechanism"] = classify_prediction_mechanism(top_paths)
        payload["confidence_interval"] = prediction_confidence_interval(
            prediction,
            prediction_request.horizon if prediction_request else prediction.horizon,
        )
        payload["path_details"] = path_details
        payload["source_coverage"] = source_coverage
        payload["sensitivity_diagnostics"] = prediction_sensitivity_diagnostics(
            components,
            top_paths,
            result.edge_states,
        )
        payload["evidence_refs"] = sorted(
            {
                result.real.source_manifest_ref,
                "point_in_time_public_graph",
                "feature_factory",
                *[
                    evidence_ref
                    for path_detail in path_details
                    for evidence_ref in path_detail["evidenceRefs"]
                ],
            }
        )
        payloads.append(payload)
    return payloads


def build_prediction_center_payload(result: Any) -> dict[str, Any]:
    prediction_payloads = build_prediction_payloads(result)
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
        coverage = [
            float(prediction.get("source_coverage", {}).get("coverageScore", 0.0))
            for prediction in bucket
        ]
        mechanisms.append(
            {
                "mechanism": mechanism,
                "count": len(bucket),
                "maxRisk": round(max(risks, default=0.0), 4),
                "averageRisk": round(sum(risks) / len(risks), 4) if risks else 0.0,
                "averageSourceCoverage": round(sum(coverage) / len(coverage), 4) if coverage else 0.0,
            }
        )
    mechanisms = sorted(mechanisms, key=lambda item: (item["maxRisk"], item["count"]), reverse=True)
    return {
        "lastUpdated": result.snapshot.as_of_time.isoformat(),
        "modelVersion": result.predictions[0].model_version if result.predictions else "model_none",
        "predictionForm": PREDICTION_FORM,
        "predictions": prediction_payloads,
        "topPredictions": top_predictions,
        "mechanisms": mechanisms,
        "highConfidenceCount": sum(
            1
            for prediction in prediction_payloads
            if float(prediction.get("confidence_high", 1.0))
            - float(prediction.get("confidence_low", 0.0))
            <= 0.22
        ),
        "saturatedScoreCount": sum(
            1 for prediction in prediction_payloads if float(prediction.get("risk_score", 0.0)) >= 0.995
        ),
    }


def entity_label(entity_by_id: dict[str, Any], entity_id: str) -> str:
    entity = entity_by_id.get(entity_id)
    return entity.display_name if entity is not None else entity_id
