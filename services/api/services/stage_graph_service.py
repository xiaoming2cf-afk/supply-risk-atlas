from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from graph_kernel.relationship_builder import classify_edge
from services.api.services.common import (
    semiconductor_fixture_warnings,
    semiconductor_metadata,
    source_ref_ids,
)
from services.api.services.graph_service import (
    GRAPH_VIEW_VERSION,
    _base_view_metadata,
    _bounded_limit,
    _build_active_semiconductor_snapshot,
    _chart_payloads,
    _edge_view,
    _node_view,
    _table_payloads,
)
from sra_core.api.envelope import make_envelope, make_error_envelope
from sra_core.geo.normalize import sanitize_chart_table_payload


ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = ROOT / "configs" / "sources" / "stage_source_coverage_matrix.yaml"
CATALOG_PATH = ROOT / "configs" / "ontology" / "semiconductor_node_catalog.yaml"
STAGE_OVERVIEW_NODE_CAP = 18
STAGE_OVERVIEW_EDGE_CAP = 30
STAGE_FOCUS_NODE_CAP = 25
STAGE_FOCUS_EDGE_CAP = 40


RUNTIME_NODE_TYPE_ALIASES: dict[str, set[str]] = {
    "L0_policy_macro": {"country", "region", "policy_event", "sanction_event", "compliance_risk"},
    "L1_raw_minerals": {"country", "region", "critical_mineral", "commodity", "raw_material"},
    "L2_materials_chemicals": {"chemical", "material", "commodity", "raw_material", "critical_mineral"},
    "L3_design_eda_ip": {"company", "component", "product_grade"},
    "L4_equipment": {"company", "equipment", "process_stage", "policy_event"},
    "L5_fabrication": {"company", "facility", "process_stage", "technology_node", "hazard_event", "risk_event"},
    "L6_products": {"product_grade", "component", "demand_indicator", "company"},
    "L7_packaging_testing": {"company", "process_stage", "product_grade", "component", "material"},
    "L8_logistics": {"logistics_facility", "route", "port", "airport", "country", "region", "hazard_event"},
    "L9_downstream_demand": {"downstream_sector", "demand_indicator", "product_grade", "component"},
    "L10_risk_events": {"risk_event", "hazard_event", "policy_event", "facility", "logistics_facility", "region"},
    "L11_compliance": {"policy_event", "sanction_event", "compliance_risk", "restricted_item", "restricted_entity", "company", "equipment", "product_grade"},
}


def route_stage_graph(
    stage_id: str,
    limit: int = STAGE_OVERVIEW_NODE_CAP,
    relationship_class: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    return _route_stage_payload(
        stage_id=stage_id,
        limit=limit,
        node_cap=STAGE_OVERVIEW_NODE_CAP,
        edge_cap=STAGE_OVERVIEW_EDGE_CAP,
        mode="stage-overview",
        relationship_class=relationship_class,
        request_id=request_id,
    )


def route_stage_graph_focus(
    stage_id: str,
    node_id: str | None = None,
    limit: int = STAGE_FOCUS_NODE_CAP,
    relationship_class: str | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    return _route_stage_payload(
        stage_id=stage_id,
        limit=limit,
        node_cap=STAGE_FOCUS_NODE_CAP,
        edge_cap=STAGE_FOCUS_EDGE_CAP,
        mode="stage-focus",
        relationship_class=relationship_class,
        focus_node_id=node_id,
        request_id=request_id,
    )


def route_stage_graph_source_coverage(
    stage_id: str,
    request_id: str | None = None,
) -> dict[str, Any]:
    stage = _stage_by_id(stage_id)
    if stage is None:
        return _stage_not_found(stage_id, request_id=request_id)
    snapshot = _build_active_semiconductor_snapshot()
    payload = _stage_base_payload(snapshot, stage=stage, mode="stage-source-coverage")
    payload["source_coverage"] = _stage_source_coverage(stage)
    return make_envelope(
        sanitize_chart_table_payload(payload),
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_stage_graph_evidence(
    stage_id: str,
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    return _route_stage_payload(
        stage_id=stage_id,
        limit=limit,
        node_cap=STAGE_OVERVIEW_NODE_CAP,
        edge_cap=_bounded_limit(limit),
        mode="stage-evidence",
        evidence_only=True,
        request_id=request_id,
    )


def route_stage_graph_tables(
    stage_id: str,
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    stage = _stage_by_id(stage_id)
    if stage is None:
        return _stage_not_found(stage_id, request_id=request_id)
    snapshot = _build_active_semiconductor_snapshot()
    tables = _table_payloads(snapshot)
    selected = {
        table_id: tables.get(_table_id_for_name(table_id), [])[: _bounded_limit(limit)]
        for table_id in stage.get("tables", [])
    }
    payload = {
        **_stage_base_payload(snapshot, stage=stage, mode="stage-tables"),
        "tables": selected,
        "limit": _bounded_limit(limit),
    }
    return make_envelope(
        sanitize_chart_table_payload(payload),
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def route_stage_graph_charts(
    stage_id: str,
    limit: int = 50,
    request_id: str | None = None,
) -> dict[str, Any]:
    stage = _stage_by_id(stage_id)
    if stage is None:
        return _stage_not_found(stage_id, request_id=request_id)
    snapshot = _build_active_semiconductor_snapshot()
    charts = _chart_payloads(snapshot, limit=_bounded_limit(limit))
    selected = {
        chart_id: charts.get(_chart_id_for_name(chart_id), [])[: _bounded_limit(limit)]
        for chart_id in stage.get("charts", [])
    }
    payload = {
        **_stage_base_payload(snapshot, stage=stage, mode="stage-charts"),
        "charts": selected,
        "limit": _bounded_limit(limit),
    }
    return make_envelope(
        sanitize_chart_table_payload(payload),
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def _route_stage_payload(
    *,
    stage_id: str,
    limit: int,
    node_cap: int,
    edge_cap: int,
    mode: str,
    relationship_class: str | None = None,
    focus_node_id: str | None = None,
    evidence_only: bool = False,
    request_id: str | None = None,
) -> dict[str, Any]:
    stage = _stage_by_id(stage_id)
    if stage is None:
        return _stage_not_found(stage_id, request_id=request_id)
    snapshot = _build_active_semiconductor_snapshot()
    selected_nodes = _stage_nodes(snapshot, stage)
    if focus_node_id and focus_node_id in selected_nodes:
        selected_nodes = _focus_nodes(snapshot, selected_nodes, focus_node_id)
    node_cap = min(node_cap, _bounded_limit(limit))
    selected_nodes = selected_nodes[:node_cap]
    selected_edges = _stage_edges(
        snapshot,
        stage,
        selected_node_ids={node["id"] for node in selected_nodes},
        relationship_class=relationship_class,
        evidence_only=evidence_only,
    )[:edge_cap]
    payload = {
        **_stage_base_payload(snapshot, stage=stage, mode=mode),
        "nodes": selected_nodes,
        "edges": selected_edges,
        "clusters": _stage_clusters(selected_nodes),
        "chart_data_refs": stage.get("charts", []),
        "table_data_refs": stage.get("tables", []),
        "source_coverage": _stage_source_coverage(stage),
        "evidence_refs": _evidence_refs(selected_edges, limit=50),
        "relationship_class_counts": dict(Counter(edge["relationship_class"] for edge in selected_edges)),
        "relationship_class_filter": relationship_class,
        "layout_hints": {
            "mode": mode,
            "max_nodes": node_cap,
            "max_edges": edge_cap,
            "rendered_node_count": len(selected_nodes),
            "rendered_edge_count": len(selected_edges),
            "does_not_render_full_graph": True,
            "evidence_context_links_are_non_dependency": True,
        },
    }
    if not selected_nodes:
        payload["warnings"] = [
            *payload["warnings"],
            f"stage_graph_degraded:no_nodes_for:{stage['stage_id']}",
        ]
    return make_envelope(
        sanitize_chart_table_payload(payload),
        metadata=semiconductor_metadata(snapshot, feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        warnings=semiconductor_fixture_warnings(snapshot),
    )


def _stage_base_payload(snapshot: Any, *, stage: dict[str, Any], mode: str) -> dict[str, Any]:
    base = _base_view_metadata(snapshot, mode=mode)
    return {
        **base,
        "stage_id": stage["stage_id"],
        "stage_name": stage["stage_name"],
        "business_question": stage["business_question"],
        "core_node_types": stage["core_node_types"],
        "core_edge_types": stage["core_edge_types"],
        "relationship_classes": stage["relationship_classes"],
        "source_status": stage.get("source_status", "incomplete_fixture_proxy"),
        "evidence_ref_count": int(stage.get("evidence_ref_count") or 0),
        "calibration_status": stage.get("calibration_status", "fixture_proxy_not_calibrated"),
        "failure_reason": stage.get("failure_reason", "not_recorded"),
        "required_narrow_patch_if_failed": stage.get("required_narrow_patch_if_failed", "not_recorded"),
    }


def _stage_nodes(snapshot: Any, stage: dict[str, Any]) -> list[dict[str, Any]]:
    catalog_layers = _catalog_layer_by_node_id()
    allowed_types = set(stage.get("core_node_types", [])) | RUNTIME_NODE_TYPE_ALIASES.get(stage["stage_id"], set())
    stage_id = str(stage["stage_id"])
    rows: list[dict[str, Any]] = []
    for node in sorted(snapshot.nodes, key=lambda item: (-float(item.confidence), item.node_id)):
        node_stage = catalog_layers.get(_canonical_catalog_key(node.node_id))
        if node.node_type not in allowed_types and node_stage != stage_id:
            continue
        row = _node_view(node)
        row["stage_id"] = stage_id
        row["stage_name"] = stage["stage_name"]
        rows.append(row)
    return rows


def _stage_edges(
    snapshot: Any,
    stage: dict[str, Any],
    *,
    selected_node_ids: set[str],
    relationship_class: str | None,
    evidence_only: bool,
) -> list[dict[str, Any]]:
    allowed_edge_types = set(stage.get("core_edge_types", []))
    allowed_classes = set(stage.get("relationship_classes", []))
    if relationship_class:
        requested = relationship_class.strip().upper()
        allowed_classes &= {requested}
    rows: list[dict[str, Any]] = []
    for edge in sorted(snapshot.edges, key=lambda item: (-float(item.confidence), item.edge_id)):
        edge_class = classify_edge(edge.edge_type)
        if evidence_only and edge_class != "EVIDENCE_CONTEXT":
            continue
        if allowed_classes and edge_class not in allowed_classes:
            continue
        connected = edge.source_node_id in selected_node_ids or edge.target_node_id in selected_node_ids
        edge_type_match = edge.edge_type in allowed_edge_types
        if not connected and not edge_type_match:
            continue
        row = _edge_view(edge)
        row["stage_id"] = stage["stage_id"]
        row["stage_name"] = stage["stage_name"]
        rows.append(row)
    return rows


def _focus_nodes(snapshot: Any, stage_nodes: list[dict[str, Any]], focus_node_id: str) -> list[dict[str, Any]]:
    stage_ids = {node["id"] for node in stage_nodes}
    neighbors: set[str] = {focus_node_id}
    for edge in snapshot.edges:
        if edge.source_node_id == focus_node_id and edge.target_node_id in stage_ids:
            neighbors.add(edge.target_node_id)
        if edge.target_node_id == focus_node_id and edge.source_node_id in stage_ids:
            neighbors.add(edge.source_node_id)
    return [node for node in stage_nodes if node["id"] in neighbors][:STAGE_FOCUS_NODE_CAP]


def _stage_clusters(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(str(node["kind"]) for node in nodes)
    return [
        {"id": f"stage-cluster:{node_type}", "node_type": node_type, "node_count": count}
        for node_type, count in sorted(counts.items())
    ]


def _stage_source_coverage(stage: dict[str, Any]) -> list[dict[str, Any]]:
    primary = set(stage.get("primary_sources", []))
    secondary = set(stage.get("secondary_sources", []))
    return [
        {
            "source_id": source_id,
            "stage_id": stage["stage_id"],
            "tier": "primary" if source_id in primary else "secondary",
            "connector_status": "fixture_or_registry",
            "source_status": stage.get("source_status", "incomplete_fixture_proxy"),
            "calibration_status": stage.get("calibration_status", "fixture_proxy_not_calibrated"),
            "failure_reason": stage.get("failure_reason", "not_recorded"),
            "live_fetch_default": "disabled",
            "fixture_required": True,
        }
        for source_id in sorted(primary | secondary)
    ]


def _evidence_refs(edges: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for edge in edges:
        for source_id in edge.get("evidence_refs", []):
            rows.append(
                {
                    "edge_id": edge["id"],
                    "edge_type": edge["edge_type"],
                    "relationship_class": edge["relationship_class"],
                    "source_id": source_id,
                    "not_supply_chain_dependency": edge.get("not_supply_chain_dependency") is True,
                }
            )
    return rows[:limit]


def _stage_by_id(stage_id: str) -> dict[str, Any] | None:
    for stage in _matrix()["stages"]:
        if stage["stage_id"] == stage_id:
            return stage
    return None


def _matrix() -> dict[str, Any]:
    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def _catalog_layer_by_node_id() -> dict[str, str]:
    catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))
    result: dict[str, str] = {}
    for node in catalog.get("nodes", []):
        node_id = str(node.get("node_id", ""))
        if node_id:
            result[_canonical_catalog_key(node_id)] = str(node.get("chain_layer") or node.get("layer") or "")
    return result


def _canonical_catalog_key(node_id: str) -> str:
    return node_id.strip().lower().replace("fab:tsmc_fab_18", "facility:tsmc_fab18")


def _stage_not_found(stage_id: str, *, request_id: str | None) -> dict[str, Any]:
    return make_error_envelope(
        "stage_graph_stage_not_found",
        f"Unknown stage_id: {stage_id}",
        metadata=semiconductor_metadata(feature_version=GRAPH_VIEW_VERSION),
        request_id=request_id,
        field="stage_id",
        warnings=["fixture_graph:not_production_ready"],
    )


def _chart_id_for_name(component_name: str) -> str:
    mapping = {
        "PolicyTimeline": "policy_event_timeline",
        "HazardTimeline": "hazard_exposure_timeline",
        "HHIConcentrationChart": "hhi_concentration_bar",
        "TradePartnerConcentrationChart": "hhi_concentration_bar",
        "MineralSupplyHHIChart": "hhi_concentration_bar",
        "RiskComponentStackedBar": "risk_component_breakdown",
        "StageRiskContributionChart": "risk_component_breakdown",
        "SourceFreshnessChart": "source_freshness_table",
        "GraphQualityChart": "graph_quality_table",
        "StageSourceCoverageChart": "stage_source_coverage",
        "StageNodeCoverageChart": "stage_node_coverage",
        "StageEvidenceQualityChart": "stage_evidence_quality",
        "MaterialSupplierConcentrationChart": "supplier_concentration_hhi",
        "EquipmentRestrictionTimelineChart": "policy_restriction_impact",
        "FabHazardExposureChart": "hazard_exposure_by_layer",
        "ProductDemandPressureChart": "downstream_demand_pressure",
        "PackagingCapacityProxyChart": "supplier_concentration_hhi",
        "LogisticsRouteExposureChart": "hazard_exposure_by_layer",
        "DownstreamDemandMixChart": "downstream_demand_pressure",
        "ComplianceRestrictionMatrixChart": "policy_restriction_impact",
        "SupplyDemandBalanceChart": "supply_demand_balance",
        "SupplierConcentrationHHIChart": "supplier_concentration_hhi",
        "CriticalInputBottleneckChart": "critical_input_bottleneck",
        "DownstreamDemandPressureChart": "downstream_demand_pressure",
        "ProductToProcessDependencyChart": "product_to_process_dependency",
        "PolicyRestrictionImpactChart": "policy_restriction_impact",
        "HazardExposureByLayerChart": "hazard_exposure_by_layer",
        "SupplierCountryConcentrationChart": "supplier_country_concentration",
    }
    return mapping.get(component_name, "risk_component_breakdown")


def _table_id_for_name(component_name: str) -> str:
    mapping = {
        "ConnectorStatusTable": "connector_status",
        "CriticalInputTable": "production_dependencies",
        "DemandRelationshipTable": "demand_relationships",
        "EvidenceRefsTable": "evidence_refs",
        "HazardEventTable": "hazard_events",
        "LogisticsFacilityTable": "logistics_facilities",
        "PolicyEventTable": "policy_events",
        "ProductDemandTable": "product_demand",
        "ProductionDependencyTable": "production_dependencies",
        "SupplyRelationshipTable": "supply_relationships",
        "TradeFlowTable": "trade_flows",
    }
    return mapping.get(component_name, "graph_nodes")
