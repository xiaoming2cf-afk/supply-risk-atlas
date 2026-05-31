from __future__ import annotations

from collections import Counter
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from services.api.services.common import semiconductor_fixture_warnings, semiconductor_metadata
from services.api.services.semiconductor_snapshot_cache import fixture_snapshot_for_services
from sra_core.api.envelope import make_envelope, make_error_envelope
from sra_core.geo.normalize import sanitize_chart_table_payload


ROOT = Path(__file__).resolve().parents[3]
CONTENT_PATH = ROOT / "configs" / "sources" / "semiconductor_supply_chain_content.yaml"
CONTENT_FEATURE_VERSION = "semiconductor_content_coverage_v0.1"
DEFAULT_LIMIT = 100
MAX_LIMIT = 500


@lru_cache(maxsize=1)
def _content_fixture() -> dict[str, Any]:
    return yaml.safe_load(CONTENT_PATH.read_text(encoding="utf-8"))


def semiconductor_content_summary_payload() -> dict[str, Any]:
    fixture = _content_fixture()
    counts = _coverage_counts(fixture)
    return sanitize_chart_table_payload(
        {
            "content_version": fixture["content_version"],
            "source_manifest_id": fixture["source_manifest_id"],
            "data_mode": fixture["data_mode"],
            "graph_mode": fixture["graph_mode"],
            "source_status": "fixture_or_promoted_public_evidence",
            "calibration_status": "fixture_proxy_not_calibrated",
            "coverage_level": fixture["coverage_level"],
            "last_updated": fixture["generated_at"],
            "fixture_required": fixture["fixture_required"],
            "live_fetch_default": fixture["live_fetch_default"],
            "counts": counts,
            "coverage_counts": counts,
            "source_family_counts": _source_family_counts(fixture),
            "source_summaries": fixture["source_summaries"],
            "coverage_gaps": fixture.get("coverage_gaps", []),
            "representative_country_region_exposures": fixture["country_region_exposures"][:10],
            "representative_value_chain_layers": fixture["value_chain_layers"][:12],
            "representative_entities": fixture["entity_profiles"][:12],
            "representative_chokepoints": fixture["chokepoints"][:8],
            "warnings": fixture.get("warnings", []),
        }
    )


def route_semiconductor_coverage_overview(request_id: str | None = None) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    payload = {
        **_base_payload(fixture, snapshot, content_scope="coverage_overview"),
        "coverage_counts": _coverage_counts(fixture),
        "source_family_counts": _source_family_counts(fixture),
        "source_summaries": fixture["source_summaries"],
        "coverage_gaps": fixture.get("coverage_gaps", []),
        "representative_country_region_exposures": fixture["country_region_exposures"][:10],
        "representative_value_chain_layers": fixture["value_chain_layers"][:12],
        "representative_entities": fixture["entity_profiles"][:12],
        "representative_chokepoints": fixture["chokepoints"][:8],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_value_chain_layers(
    stage: str | None = None,
    layer_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    rows = list(fixture["value_chain_layers"])
    if stage:
        rows = [row for row in rows if str(row.get("stage")) == stage]
    if layer_id:
        rows = [row for row in rows if str(row.get("layer_id")) == layer_id]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="value_chain_layers"),
        "filters": {"stage": stage, "layer_id": layer_id},
        "total": len(rows),
        "layers": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_country_exposures(
    geo_id: str | None = None,
    stage: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    rows = list(fixture["country_region_exposures"])
    if geo_id:
        rows = [row for row in rows if str(row.get("geo_id")) == geo_id]
    if stage:
        stage_key = stage.strip().lower()
        rows = [
            row
            for row in rows
            if any(stage_key in str(value).lower() for value in _country_stage_values(row))
        ]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="country_region_exposures"),
        "filters": {"geo_id": geo_id, "stage": stage},
        "total": len(rows),
        "country_region_exposures": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_entity_profiles(
    entity_id: str | None = None,
    stage: str | None = None,
    layer_id: str | None = None,
    geo_id: str | None = None,
    source_id: str | None = None,
    risk_tag: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    rows = list(fixture["entity_profiles"])
    if entity_id:
        rows = [row for row in rows if str(row.get("entity_id")).lower() == entity_id.lower()]
    if layer_id:
        rows = [row for row in rows if layer_id in (row.get("primary_layers") or [])]
    if stage:
        layer_stage = {row["layer_id"]: row["stage"] for row in fixture["value_chain_layers"]}
        rows = [
            row
            for row in rows
            if any(layer_stage.get(layer) == stage for layer in row.get("primary_layers", []))
        ]
    if geo_id:
        rows = [row for row in rows if str(row.get("headquarters_country")) == geo_id]
    if source_id:
        rows = [row for row in rows if source_id in (row.get("provenance") or [])]
    if risk_tag:
        rows = [row for row in rows if risk_tag in (row.get("risk_tags") or [])]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="entity_profiles"),
        "filters": {
            "entity_id": entity_id,
            "stage": stage,
            "layer_id": layer_id,
            "geo_id": geo_id,
            "source_id": source_id,
            "risk_tag": risk_tag,
        },
        "total": len(rows),
        "entity_profiles": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_relationships(
    relationship_class: str | None = None,
    relationship_type: str | None = None,
    edge_type: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
    layer_id: str | None = None,
    stage: str | None = None,
    source_family: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    layer_stage = {row["layer_id"]: row["stage"] for row in fixture["value_chain_layers"]}
    chokepoint_layers = {row["layer_id"] for row in fixture["chokepoints"]}
    rows = [
        _relationship_row(edge, fixture=fixture, layer_stage=layer_stage, chokepoint_layers=chokepoint_layers)
        for edge in fixture["relationship_edges"]
    ]
    if relationship_class:
        normalized_class = relationship_class.upper()
        rows = [row for row in rows if row["relationship_class"] == normalized_class]
    if relationship_type:
        rows = [row for row in rows if row["relationship_type"] == relationship_type]
    if edge_type:
        rows = [row for row in rows if row["edge_type"] == edge_type]
    if source_id:
        rows = [row for row in rows if row["source_node_id"] == source_id or row["source_id"] == source_id]
    if target_id:
        rows = [row for row in rows if row["target_node_id"] == target_id or row["target_id"] == target_id]
    if layer_id:
        rows = [
            row
            for row in rows
            if layer_id in {row.get("source_node_id"), row.get("target_node_id"), row.get("source_id"), row.get("target_id")}
        ]
    if stage:
        rows = [row for row in rows if stage in (row.get("stage_context") or [])]
    if source_family:
        rows = [row for row in rows if source_family in (row.get("source_families") or [])]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="relationship_edges"),
        "filters": {
            "relationship_class": relationship_class,
            "relationship_type": relationship_type,
            "edge_type": edge_type,
            "source_id": source_id,
            "target_id": target_id,
            "layer_id": layer_id,
            "stage": stage,
            "source_family": source_family,
        },
        "total": len(rows),
        "relationship_class_counts": dict(Counter(row["relationship_class"] for row in rows)),
        "relationships": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_source_coverage(
    stage: str | None = None,
    source_family: str | None = None,
    relationship_class: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    rows = _source_coverage_rows(fixture)
    if stage:
        rows = [row for row in rows if row["stage"] == stage]
    if source_family:
        rows = [row for row in rows if source_family in row["source_families"]]
    if relationship_class:
        normalized_class = relationship_class.upper()
        rows = [row for row in rows if normalized_class in row["relationship_classes"]]
    source_family_counts: Counter[str] = Counter()
    relationship_counts: Counter[str] = Counter()
    for row in rows:
        source_family_counts.update(row["source_families"])
        relationship_counts.update(row["relationship_classes"])
    payload = {
        **_base_payload(fixture, snapshot, content_scope="source_coverage_matrix"),
        "filters": {
            "stage": stage,
            "source_family": source_family,
            "relationship_class": relationship_class,
        },
        "total": len(rows),
        "source_family_counts": dict(sorted(source_family_counts.items())),
        "relationship_class_counts": dict(sorted(relationship_counts.items())),
        "source_families": fixture["source_summaries"],
        "coverage_gaps": fixture.get("coverage_gaps", []),
        "stage_source_coverage": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def route_semiconductor_chokepoints(
    layer_id: str | None = None,
    stage: str | None = None,
    limit: int = DEFAULT_LIMIT,
    request_id: str | None = None,
) -> dict[str, Any]:
    try:
        snapshot = fixture_snapshot_for_services()
        fixture = _content_fixture()
    except Exception as exc:
        return _content_error(exc, request_id=request_id)
    layer_stage = {row["layer_id"]: row["stage"] for row in fixture["value_chain_layers"]}
    rows = list(fixture["chokepoints"])
    if layer_id:
        rows = [row for row in rows if str(row.get("layer_id")) == layer_id]
    if stage:
        rows = [row for row in rows if layer_stage.get(str(row.get("layer_id"))) == stage]
    payload = {
        **_base_payload(fixture, snapshot, content_scope="chokepoints"),
        "filters": {"layer_id": layer_id, "stage": stage},
        "total": len(rows),
        "chokepoints": rows[: _bounded_limit(limit)],
    }
    return _content_envelope(payload, snapshot=snapshot, request_id=request_id)


def profile_for_entity(entity_id: str) -> dict[str, Any] | None:
    normalized = entity_id.lower()
    for row in _content_fixture()["entity_profiles"]:
        if str(row.get("entity_id", "")).lower() == normalized:
            return sanitize_chart_table_payload(deepcopy(row))
    return None


def _content_envelope(
    payload: dict[str, Any],
    *,
    snapshot: Any,
    request_id: str | None,
) -> dict[str, Any]:
    return make_envelope(
        sanitize_chart_table_payload(payload),
        metadata=semiconductor_metadata(snapshot, feature_version=CONTENT_FEATURE_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def _content_error(exc: Exception, *, request_id: str | None) -> dict[str, Any]:
    return make_error_envelope(
        "semiconductor_content_unavailable",
        "Semiconductor content fixture could not be loaded.",
        metadata=semiconductor_metadata(feature_version=CONTENT_FEATURE_VERSION),
        request_id=request_id,
        warnings=[f"semiconductor_content_fixture_failed:{type(exc).__name__}"],
    )


def _base_payload(fixture: dict[str, Any], snapshot: Any, *, content_scope: str) -> dict[str, Any]:
    return {
        "content_scope": content_scope,
        "content_version": fixture["content_version"],
        "graph_version": snapshot.graph_version,
        "source_manifest_id": snapshot.source_manifest_id,
        "data_mode": getattr(snapshot, "data_mode", fixture["data_mode"]),
        "graph_mode": getattr(snapshot, "graph_mode", fixture["graph_mode"]),
        "source_status": "fixture_or_promoted_public_evidence",
        "calibration_status": "fixture_proxy_not_calibrated",
        "last_updated": fixture["generated_at"],
        "fixture_required": fixture["fixture_required"],
        "live_fetch_default": fixture["live_fetch_default"],
        "warnings": fixture.get("warnings", []),
        "audit": {
            "source_manifest_id": fixture["source_manifest_id"],
            "api_visibility_policy": fixture["api_visibility_policy"],
            "source_payload_policy": fixture["source_payload_policy"],
            "coverage_level": fixture["coverage_level"],
            "production_status": fixture["production_status"],
        },
    }


def _coverage_counts(fixture: dict[str, Any]) -> dict[str, int]:
    return {
        "country_region_count": len(fixture["country_region_exposures"]),
        "value_chain_layer_count": len(fixture["value_chain_layers"]),
        "entity_profile_count": len(fixture["entity_profiles"]),
        "relationship_edge_count": len(fixture["relationship_edges"]),
        "chokepoint_count": len(fixture["chokepoints"]),
        "source_family_count": len(fixture["source_summaries"]),
    }


def _source_family_counts(fixture: dict[str, Any]) -> dict[str, int]:
    families: Counter[str] = Counter()
    for section_name in ("country_region_exposures", "value_chain_layers", "entity_profiles", "relationship_edges", "chokepoints"):
        for row in fixture.get(section_name, []):
            for source_id in row.get("provenance", []):
                families[_source_family_for_source(source_id)] += 1
    return dict(sorted(families.items()))


def _relationship_row(
    edge: dict[str, Any],
    *,
    fixture: dict[str, Any],
    layer_stage: dict[str, str],
    chokepoint_layers: set[str],
) -> dict[str, Any]:
    row = deepcopy(edge)
    row["source_refs"] = list(edge.get("provenance", []))
    row["evidence_refs"] = list(edge.get("provenance", []))
    row["valid_from"] = fixture["generated_at"]
    row["valid_to"] = None
    row["calibration_status"] = "fixture_proxy_not_calibrated"
    row["source_families"] = sorted(
        {_source_family_for_source(source_id) for source_id in row["source_refs"]}
    )
    row["stage_context"] = _relationship_stage_context(edge, layer_stage)
    row["can_propagate_risk"] = row["relationship_class"] in {
        "SUPPLY_RELATIONSHIP",
        "PRODUCTION_DEPENDENCY",
    }
    if row["relationship_class"] == "SUPPLY_RELATIONSHIP":
        row.update(
            {
                "supplier_id": row["source_node_id"],
                "buyer_or_stage_id": row["target_node_id"],
                "supplied_item_id": row["target_node_id"],
                "supplied_item_type": _node_kind(row["target_node_id"]),
                "relationship_scope": "public_evidence_stage_summary",
                "share_or_capacity_proxy": None,
                "lead_time_days": None,
                "qualification_time_days": None,
                "substitution_available": None,
            }
        )
    elif row["relationship_class"] == "DEMAND_RELATIONSHIP":
        row.update(
            {
                "demand_source_id": row["source_node_id"],
                "product_grade_id": row["target_node_id"],
                "region": None,
                "period": None,
                "demand_proxy_type": "public_evidence_summary",
                "demand_value": None,
                "demand_growth_proxy": None,
                "can_propagate_risk": False,
            }
        )
    elif row["relationship_class"] == "PRODUCTION_DEPENDENCY":
        row.update(
            {
                "dependency_source_id": row["source_node_id"],
                "dependency_target_id": row["target_node_id"],
                "dependency_type": row["edge_type"],
                "criticality": "high_proxy"
                if row["source_node_id"] in chokepoint_layers or row["target_node_id"] in chokepoint_layers
                else "public_evidence_proxy",
                "substitutability": "low_or_uncertain_proxy",
                "bottleneck_flag": row["source_node_id"] in chokepoint_layers or row["target_node_id"] in chokepoint_layers,
                "propagation_mode_hint": "physical_or_policy_constraint",
            }
        )
    elif row["relationship_class"] == "EVIDENCE_CONTEXT":
        row.update(
            {
                "derived_context": True,
                "not_supply_chain_dependency": True,
                "can_propagate_risk": False,
                "user_facing_label": "evidence-context link",
                "warning": "This is not a supply-chain dependency edge.",
            }
        )
    return row


def _source_coverage_rows(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    layer_stage = {row["layer_id"]: row["stage"] for row in fixture["value_chain_layers"]}
    relationship_rows = [
        _relationship_row(
            edge,
            fixture=fixture,
            layer_stage=layer_stage,
            chokepoint_layers={row["layer_id"] for row in fixture["chokepoints"]},
        )
        for edge in fixture["relationship_edges"]
    ]
    relationships_by_layer: dict[str, list[dict[str, Any]]] = {}
    for relationship in relationship_rows:
        for node_id in (
            relationship.get("source_node_id"),
            relationship.get("target_node_id"),
            relationship.get("source_id"),
            relationship.get("target_id"),
        ):
            if node_id in layer_stage:
                relationships_by_layer.setdefault(str(node_id), []).append(relationship)
    entities_by_layer: dict[str, list[dict[str, Any]]] = {}
    for entity in fixture["entity_profiles"]:
        for layer_id in entity.get("primary_layers", []):
            entities_by_layer.setdefault(str(layer_id), []).append(entity)
    chokepoints_by_layer: dict[str, list[dict[str, Any]]] = {}
    for chokepoint in fixture["chokepoints"]:
        chokepoints_by_layer.setdefault(str(chokepoint.get("layer_id")), []).append(chokepoint)

    rows: list[dict[str, Any]] = []
    for layer in fixture["value_chain_layers"]:
        layer_id = layer["layer_id"]
        related_relationships = relationships_by_layer.get(layer_id, [])
        related_entities = entities_by_layer.get(layer_id, [])
        related_chokepoints = chokepoints_by_layer.get(layer_id, [])
        source_refs = set(layer.get("provenance", []))
        source_refs.update(source for row in related_relationships for source in row.get("source_refs", []))
        source_refs.update(source for row in related_entities for source in row.get("provenance", []))
        source_refs.update(source for row in related_chokepoints for source in row.get("provenance", []))
        relationship_classes = sorted({row["relationship_class"] for row in related_relationships})
        rows.append(
            {
                "layer_id": layer_id,
                "layer_name": layer["layer_name"],
                "stage": layer["stage"],
                "coverage_level": layer["coverage_level"],
                "source_refs": sorted(source_refs),
                "source_families": sorted({_source_family_for_source(source_id) for source_id in source_refs}),
                "relationship_classes": relationship_classes,
                "relationship_count": len(related_relationships),
                "entity_count": len(related_entities),
                "chokepoint_count": len(related_chokepoints),
                "relationship_coverage": {
                    "supply": "SUPPLY_RELATIONSHIP" in relationship_classes,
                    "demand": "DEMAND_RELATIONSHIP" in relationship_classes,
                    "production_dependency": "PRODUCTION_DEPENDENCY" in relationship_classes,
                    "evidence_context": "EVIDENCE_CONTEXT" in relationship_classes,
                },
                "source_gaps": _layer_source_gaps(relationship_classes, source_refs),
                "connector_status": "fixture_required_live_disabled",
                "live_fetch_default": fixture["live_fetch_default"],
                "fixture_required": fixture["fixture_required"],
            }
        )
    return rows


def _relationship_stage_context(edge: dict[str, Any], layer_stage: dict[str, str]) -> list[str]:
    stages = {
        layer_stage[node_id]
        for node_id in (
            edge.get("source_node_id"),
            edge.get("target_node_id"),
            edge.get("source_id"),
            edge.get("target_id"),
        )
        if node_id in layer_stage
    }
    return sorted(stages)


def _node_kind(node_id: str) -> str:
    if ":" in node_id:
        return node_id.split(":", 1)[0]
    if node_id.startswith("vc_"):
        return "value_chain_layer"
    return "node"


def _layer_source_gaps(relationship_classes: list[str], source_refs: set[str]) -> list[str]:
    gaps: list[str] = []
    if not relationship_classes:
        gaps.append("no_direct_relationship_edge_in_fixture")
    if not any(source.startswith(("sec_edgar", "company_annual_report")) for source in source_refs):
        gaps.append("enterprise_disclosure_not_mapped")
    if not any(source.startswith(("un_comtrade", "wits", "usgs", "nga", "bis", "federal_register", "ofac", "consolidated")) for source in source_refs):
        gaps.append("national_policy_macro_source_not_mapped")
    return gaps


def _source_family_for_source(source_id: str) -> str:
    if source_id.startswith(("sec_edgar", "company_annual_report")):
        return "enterprise_public_disclosure"
    if source_id.startswith(("eto_", "wsts_", "gdelt_", "openalex_")):
        return "industry_public_fixture"
    return "national_policy_macro_public"


def _country_stage_values(row: dict[str, Any]) -> list[Any]:
    return [
        *(row.get("upstream_strengths") or []),
        *(row.get("midstream_strengths") or []),
        *(row.get("downstream_strengths") or []),
        row.get("semiconductor_role_summary"),
        row.get("chokepoint_exposure"),
    ]


def _bounded_limit(value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))
