from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_data_lineage_banner_uses_user_facing_summary_and_collapsed_audit_details() -> None:
    source = read("apps/web/src/app/App.tsx")

    assert "DataAuditDetails" in source
    assert "MetadataSummary" in source
    assert "publicDataModeLabel" in source
    assert "<span>data_mode:" not in source
    assert "<span>graph_version:" not in source
    assert "<span>source_manifest_id:" not in source
    assert "<span>not_production_ready: true" not in source
    assert "<span>failed_endpoint:" not in source
    assert "<span>transport_attempts:" not in source


def test_common_chart_and_table_metadata_is_collapsed_by_default() -> None:
    table_source = read("apps/web/src/features/common/tables/DataTable.tsx")
    chart_source = read("apps/web/src/features/common/charts/ChartPrimitives.tsx")
    component_source = read("apps/web/src/app/components.tsx")
    source_catalog_source = read("apps/web/src/features/common/tables/SourceCatalogTable.tsx")
    connector_status_source = read("apps/web/src/features/common/tables/ConnectorStatusTable.tsx")

    for source in (table_source, chart_source):
        assert "AuditDetails" in source
        assert "MetadataSummary" in source
        assert "graph_version=" not in source
        assert "source_manifest_id=" not in source
        assert "metadata-line" not in source
    assert "formatDisplayLabel(column)" in table_source
    assert "formatDisplayLabel(title)" in table_source
    assert "Structured metadata" in table_source
    assert "JSON.stringify(value)" not in table_source
    assert "renderArrayCell(value)" in table_source
    assert ".map(formatDisplayValue).map(String)" not in table_source
    assert "formatDisplayLabel(metric.label)" in component_source
    assert "formatDisplayLabel(label)" in component_source
    assert "formatDisplayValue(value)" in component_source
    assert '"SourceCatalog"' not in source_catalog_source
    assert '"ConnectorStatus"' not in connector_status_source
    assert '"Source catalog"' in source_catalog_source
    assert '"Connector status"' in connector_status_source


def test_default_table_titles_are_user_facing_not_component_names() -> None:
    table_dir = REPO_ROOT / "apps/web/src/features/common/tables"
    component_name_title = re.compile(r'title=\{props\.title \?\? "[A-Z][A-Za-z0-9]+(?:Table|Relationship|Dependency|Demand|Input|Event|Facility|Action|Result|Ranking|Run|Flow|Artifact|Node|Edge|Concentration|Balance)?"')

    offenders = []
    for path in sorted(table_dir.glob("*.tsx")):
        source = path.read_text(encoding="utf-8")
        if component_name_title.search(source):
            offenders.append(path.name)

    assert offenders == []


def test_primary_run_page_copy_uses_user_facing_labels_for_common_metrics() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")

    forbidden_primary_titles = [
        'title="top_transmission_paths"',
        'title="ranked_shock_sets"',
        'title="recommended_actions"',
        'title="baseline_comparison"',
        'title="evidence_refs"',
    ]
    forbidden_primary_copy = [
        ">resilience_integral_loss<",
        ">graph_weighted_loss<",
        ">demand_fulfillment_loss<",
        ">capacity_functionality_loss<",
        ">auto_semiconductor<",
        ">leontief_bottleneck<",
        "not_weighted_sum",
        "run_history_unavailable:",
        "fixture_graph:metadata_unavailable",
        "expected_effect {",
        "evidence_refs {",
        "plausibility_cost {",
        "expected_loss {",
        ">Affected mean legacy<",
        ">Max legacy<",
        ">Noisy OR<",
        ">Leontief bottleneck<",
        ">Additive cap<",
    ]

    for needle in forbidden_primary_titles + forbidden_primary_copy:
        assert needle not in source
    assert "Transmission paths" in source
    assert "Ranked shock sets" in source
    assert "Recommended actions" in source
    assert "Baseline comparison" in source
    assert "Evidence refs" in source
    assert "Run history unavailable" in source
    assert "Fixture graph metadata unavailable" in source
    assert "Template 中国台湾 earthquake" in source
    assert ">Affected mean<" in source
    assert ">Maximum propagation<" in source
    assert ">Independent exposure spread<" in source
    assert ">Bottleneck-limited spread<" in source
    assert ">Capped cumulative spread<" in source


def test_relationship_views_do_not_show_unavailable_preview_as_user_copy() -> None:
    files = [
        "apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx",
        "apps/web/src/features/graph-explorer/DemandRelationshipView.tsx",
        "apps/web/src/features/graph-explorer/ProductionDependencyView.tsx",
        "apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx",
    ]

    for relative_path in files:
        source = read(relative_path)
        assert 'data-preview-state="unavailable_preview"' in source
        assert "unavailable_preview:" not in source
        assert "Backend relationship data unavailable; authoritative rows are hidden." in source


def test_run_page_unavailable_states_keep_endpoint_diagnostics_collapsed() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")

    assert '<Field label="failed_endpoint"' not in source
    assert '<Field label="source_status"' not in source
    assert "Shock Simulator unavailable" in source
    assert "Reverse Stress Lab unavailable" in source
    assert "Intervention Optimizer unavailable" in source
    assert "Investigation Report unavailable" in source
    assert source.count('label="View diagnostics"') >= 4


def test_system_health_heavy_inventory_sections_are_collapsed() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")

    expected_disclosures = [
        'label="Source registry details"',
        'label="Node, edge, and warning details"',
        'label="Data catalog details"',
        'label="Entity resolution details"',
        'label="Evidence lineage details"',
        'label="Runtime event details"',
    ]

    for needle in expected_disclosures:
        assert needle in source
    assert 'title="Source catalog"' in source
    assert 'title="Connector status"' in source


def test_page_relevance_policy_declares_display_tiers() -> None:
    source = read("apps/web/src/features/common/pageRelevance.ts")

    assert "displayTiers" in source
    assert "audit_details" in source
    assert "developer_diagnostics" in source


def test_stage_graph_view_keeps_audit_metadata_out_of_primary_metrics() -> None:
    source = read("apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx")

    assert "MetadataSummary" in source
    assert "AuditDetails" in source
    assert '<Metric label="graph_version"' not in source
    assert '<Metric label="source_manifest_id"' not in source
    assert '<Metric label="data_mode"' not in source
    assert '<Metric label="graph_mode"' not in source
    assert "<h3>{stage.viewName}</h3>" not in source
    assert "<h3>{stage.label}</h3>" in source
    assert "relationshipClassLabel(relationshipClassFilter)" in source
    assert "formatDisplayValue(String(family.source_status" in source


def test_browser_smoke_uses_stage_labels_not_component_names() -> None:
    source = read("scripts/browser-smoke.mjs")

    forbidden_component_names = [
        "PolicyMacroGraphView",
        "MineralDependencyGraphView",
        "EquipmentProcessDependencyGraphView",
        "FabProcessGraphView",
        "LogisticsRouteGraphView",
        "ComplianceRiskGraphView",
    ]
    for needle in forbidden_component_names:
        assert needle not in source
    assert "L0 Policy / macro" in source
    assert "L11 Compliance" in source


def test_graph_legend_does_not_render_raw_warning_metadata_in_primary_list() -> None:
    source = read("apps/web/src/features/graph-explorer/GraphLegend.tsx")

    assert "visibleWarningLabels(metadata.warnings)" in source
    assert "metadata.warnings.map((warning)" not in source
    assert 'return warning' not in source
    assert 'return "Public evidence warning"' in source
    assert "semirisk_fixture_metadata" in source
    assert "Fixture graph metadata available" in source
