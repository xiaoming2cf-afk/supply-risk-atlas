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
    assert "shouldShowDiagnostics(status)" in source
    assert "<span>data_mode:" not in source
    assert "<span>source_status:" not in source
    assert "<span>graph_mode:" not in source
    assert "<span>graph_version:" not in source
    assert "<span>source_manifest_id:" not in source
    assert "<span>calibration_status:" not in source
    assert "<span>last_checked_at:" not in source
    assert "<span>not_production_ready: true" not in source
    assert "<span>failed_endpoint:" not in source
    assert "<span>transport_attempts:" not in source


def test_metadata_summary_filters_internal_audit_tokens_from_primary_badges() -> None:
    source = read("apps/web/src/features/common/AuditDetails.tsx")

    assert "INTERNAL_METADATA_SUMMARY_LABELS" in source
    for token in [
        '"data_mode"',
        '"source_status"',
        '"graph_mode"',
        '"graph_version"',
        '"source_manifest_id"',
        '"calibration_status"',
        '"last_checked_at"',
        '"transport_attempts"',
        '"failed_endpoint"',
        '"not_production_ready"',
    ]:
        assert token in source
    assert "isUserFacingSummaryLabel(item.label)" in source


def test_common_chart_and_table_metadata_is_collapsed_by_default() -> None:
    table_source = read("apps/web/src/features/common/tables/DataTable.tsx")
    chart_source = read("apps/web/src/features/common/charts/ChartPrimitives.tsx")
    display_source = read("apps/web/src/features/common/displayLabels.ts")
    component_source = read("apps/web/src/app/components.tsx")
    source_catalog_source = read("apps/web/src/features/common/tables/SourceCatalogTable.tsx")
    connector_status_source = read("apps/web/src/features/common/tables/ConnectorStatusTable.tsx")

    for source in (table_source, chart_source):
        assert "AuditDetails" in source
        assert "MetadataSummary" in source
        assert "hasAuditSignal" in source
        assert "graph_version=" not in source
        assert "source_manifest_id=" not in source
        assert "metadata-line" not in source
    assert "formatDisplayLabel(column)" in table_source
    assert "formatDisplayLabel(title)" in table_source
    assert "Structured metadata" in table_source
    assert "JSON.stringify(value)" not in table_source
    assert "renderArrayCell(value)" in table_source
    assert ".map(formatDisplayValue).map(String)" not in table_source
    assert "formatNodeDisplayRef" in table_source
    assert "formatSourceDisplayRef" in table_source
    assert "formatChartLabel(item.label)" in chart_source
    assert '["sec_edgar_lite", "SEC EDGAR public filings"]' in display_source
    assert '["region:china_taiwan", "中国台湾"]' in display_source
    assert "formatDisplayLabel(metric.label)" in component_source
    assert "formatDisplayLabel(label)" in component_source
    assert "formatDisplayValue(value)" in component_source
    assert '"SourceCatalog"' not in source_catalog_source
    assert '"ConnectorStatus"' not in connector_status_source
    assert '"Source catalog"' in source_catalog_source
    assert '"Connector status"' in connector_status_source


def test_i18n_preserves_canonical_geography_display_labels() -> None:
    source = read("apps/web/src/app/i18n.tsx")

    assert '中国台湾: { zh: "中国台湾", fr: "中国台湾" }' in source
    assert '"中国台湾海峡": { zh: "中国台湾海峡", fr: "中国台湾海峡" }' in source
    assert '中国台湾: { zh: "中国台湾", fr: "Chine" }' not in source
    assert '"中国台湾海峡": { zh: "中国台湾海峡", fr: "Détroit lié à la Chine" }' not in source


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
    display_source = read("apps/web/src/features/common/displayLabels.ts")

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
    assert '["noisy_or", "Independent exposure spread"]' in display_source
    assert '["leontief_bottleneck", "Bottleneck-limited spread"]' in display_source
    assert '["additive_cap", "Capped cumulative spread"]' in display_source
    assert "ACRONYMS.get(lower)" in display_source
    assert "capitalize(lower)" in display_source
    assert "${result.run_id}; ${result.simulation_version}" not in source
    assert "${result.run_id}; ${result.optimization_version}" not in source
    assert "simulation run IDs, and recommended controls" not in source
    assert "path_id: path.path_id" not in source
    assert "label: shockSet.shock_set_id" not in source
    assert "shock_set_id: shockSet.shock_set_id" not in source
    assert '<span className="row-title">{path.path_id}</span>' not in source
    assert '<span className="row-title">{shockSet.shock_set_id}</span>' not in source
    assert "formatInlineDisplayText(path.explanation)" in source
    assert "formatInlineDisplayText(shockSet.explanation)" in source
    assert "formatInlineDisplayText(topShockSet?.explanation ?? result.explanation)" in source
    assert "label: action.action_id" not in source
    assert "action_id: action.action_id" not in source
    assert "target_id: action.target_id" not in source
    assert "{entity.node_id} / {entity.node_type}" not in source
    assert '<Field label="Selected entity" value={risk.node_id}' not in source
    assert 'columns={["node_id", "label", "node_type", "loss_score", "evidence_refs"]}' not in source
    assert 'columns={["run_id", "created_at", "status"]}' not in source
    assert 'columns={["run_id", "scenario_type", "loss_mode", "propagation_mode"]}' not in source
    assert '<Field label="context_run_id"' not in source
    assert '<Field label="forward_context_run_id"' not in source
    assert '<Field label="reverse_context_run_id"' not in source
    assert '<Field label="selected_run_refs"' not in source
    assert '<Field label="report_version"' not in source
    assert '<Field label="latest_run_id"' not in source
    assert '<Field label="previous_run_id"' not in source
    assert '<Field label="run_id"' not in source
    assert 'title="Before/after simulation run IDs"' not in source
    assert 'title="Simulation run counts"' in source
    assert "formatNodeDisplayRef(action.target_id)" in source
    assert "formatSourceDisplayRef(row.sourceId)" in source
    assert "formatSourceDisplayList(license.sourceIds)" in source
    assert "formatRunDisplayName(run, index)" in source
    assert "formatNodeDisplayRef(prediction.target_id)" in source
    assert '"semirisk_reverse_stress_v0.1"' not in read("scripts/browser-smoke.mjs")
    assert '"semirisk_intervention_optimizer_v0.1"' not in read("scripts/browser-smoke.mjs")
    assert '"semirisk_investigation_report_v0.1"' not in read("scripts/browser-smoke.mjs")

    overlay_source = read("apps/web/src/features/graph-explorer/GraphScenarioOverlay.tsx")
    assert "<span>run_id:" not in overlay_source
    assert 'label: "run_id", value: overlay?.run_id' in overlay_source


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
        assert "formatNodeDisplayRef" in source
        assert "formatSourceDisplayRef" in source


def test_browser_smoke_checks_unavailable_preview_as_dom_state_not_user_text() -> None:
    source = read("scripts/browser-smoke.mjs")

    assert "previewStates: Array.from(document.querySelectorAll('[data-preview-state]'))" in source
    assert 'state.previewStates.includes("unavailable_preview")' in source
    assert 'relationshipState.previewStates.includes("unavailable_preview")' in source
    assert "hasControlledUnavailableCopy" in source
    assert "Backend relationship data unavailable; authoritative rows are hidden." in source
    assert 'relationshipState.text.includes("Local graph")' in source
    assert 'relationshipState.text.includes("excluded from")' in source
    assert "(!hasUnavailablePreview || hasControlledUnavailableCopy)" in source
    assert 'state.text.includes("unavailable_preview")' not in source
    assert 'relationshipState.text.includes("unavailable_preview")' not in source


def test_graph_explorer_tables_format_source_and_node_ids_for_primary_ui() -> None:
    source_coverage = read("apps/web/src/features/graph-explorer/GraphSourceCoverageView.tsx")
    evidence_view = read("apps/web/src/features/graph-explorer/GraphEvidenceView.tsx")
    node_catalog = read("apps/web/src/features/graph-explorer/GraphNodeCatalogView.tsx")
    matrix = read("apps/web/src/features/graph-explorer/GraphMatrixView.tsx")
    inspector = read("apps/web/src/features/graph-explorer/GraphInspector.tsx")

    assert "formatSourceCell(row.source_id" in source_coverage
    assert '{String(row.source_id ?? "source_ref")}' not in source_coverage
    assert "fallbackRows" not in source_coverage
    assert "view.visibleLinks" not in source_coverage
    assert "source_coverage_endpoint_unavailable" in source_coverage
    assert "formatEvidenceRef" in evidence_view
    assert "formatNodeCell" in node_catalog
    assert "formatSourceCandidate" in node_catalog
    assert "view.visibleNodes" not in node_catalog
    assert "node_catalog_endpoint_unavailable" in node_catalog
    assert "view.visibleLinks" not in matrix
    assert "graph.nodes.find" not in matrix
    assert "matrix_endpoint_unavailable" in matrix
    assert "formatEvidenceRef(ref)" in inspector
    assert "<li key={ref}>{ref}</li>" not in inspector
    assert "formatCountryRef(node.countryCode" in inspector
    assert "formatNodeRef(edge.source)" in inspector


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


def test_semiconductor_content_coverage_is_summarized_on_primary_pages() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")
    shared_types = read("packages/shared-types/src/semiconductor-content.ts")
    api_client = read("packages/api-client/src/dashboard.ts")

    assert "semiconductorContentCoverage" in source
    assert 'title="Chip supply chain coverage"' in source
    assert '<Field label="Countries / regions"' in source
    assert '<Field label="Value-chain layers"' in source
    assert '<Field label="Entity profiles"' in source
    assert '<Field label="Relationship summaries"' in source
    assert '<Field label="Chokepoints"' in source
    assert '<Field label="Source families"' in source
    assert '<Field label="L0-L11 stage coverage"' in source
    assert '<Field label="Implemented stages"' in source
    assert "stage map: L0-L11" in source
    assert 'aria-label="All L0-L11 semiconductor supply-chain stage coverage"' in source
    assert "visible stages: {chainStageCoverageRows.length}" in source
    assert "chainStageCoverageRows.map((stage)" in source
    assert "chainStageCoverageRows.slice(0, 6)" not in source
    assert "{stage.stage_name}" in source
    assert "fixture required | live fetch" in source
    assert "Stage coverage links national/policy, enterprise disclosure, and industry fixture sources" in source
    assert "National and regional coverage" in source
    assert "Industry layer coverage" in source
    assert "Enterprise coverage" in source
    assert 'label="Data audit details"' in source
    assert "stage_source_family_counts" in source
    assert "stage_source_coverage" in source
    assert "Priority coverage gaps" in source
    assert "stage_narrow_patch_plan" in source
    assert "required_narrow_patch_if_failed" in source
    assert "contentCoverage.source_manifest_id" in source
    assert "contentCoverage.graph_version" not in source
    assert "contentCoverage.source_manifest_id" in source
    assert "contentCoverage.data_mode" in source
    assert "contentCoverage.graph_mode" in source
    assert "SemiconductorCoverageOverview" in shared_types
    assert "SemiconductorChainStageCoverageSummary" in shared_types
    assert "SemiconductorEntityProfile" in shared_types
    assert "getSemiconductorCoverageOverview" in api_client
    assert "getSemiconductorCountryExposures" in api_client
    assert "getSemiconductorChokepoints" in api_client


def test_entity_risk_profile_enrichment_is_evidence_bound_and_folded() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")
    risk_types = read("packages/shared-types/src/risk.ts")

    assert "semiconductor_profile" in risk_types
    assert "semiconductorProfile" in source
    assert 'title="Supply-chain role"' in source
    assert '<Field label="Value-chain roles"' in source
    assert '<Field label="Primary layers"' in source
    assert '<Field label="Country exposure"' in source
    assert '<Field label="Risk tags"' in source
    assert '<Field label="Dependencies"' in source
    assert "semiconductorProfile.evidence_summary" in source
    assert "semiconductorProfile.substitution_notes" in source
    assert '{ label: "provenance", value: semiconductorProfile.provenance.map(formatSourceDisplayRef) }' in source
    assert '<Field label="entity_id"' not in source


def test_entity_risk_primary_fields_use_user_facing_metric_labels() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")
    entity_risk_source = source.split("export function CompanyRisk360", 1)[1].split("export function PredictionCenter", 1)[0]

    forbidden_primary_labels = [
        '<Field label="score"',
        '<Field label="level"',
        '<Field label="likelihood"',
        '<Field label="impact"',
        '<Field label="confidence"',
        '<Field label="vulnerability_modifier"',
        '<Field label="source_concentration_hhi"',
        '<Field label="source_concentration_level"',
        '<Field label="country_concentration_hhi"',
        '<Field label="country_concentration_level"',
        '<Field label="weighting_method"',
        '<Field label="Selected entity" value={selectedNodeId}',
    ]

    for needle in forbidden_primary_labels:
        assert needle not in entity_risk_source
    assert '<Field label="Risk score"' in entity_risk_source
    assert '<Field label="Risk level"' in entity_risk_source
    assert '<Field label="Likelihood"' in entity_risk_source
    assert '<Field label="Impact"' in entity_risk_source
    assert '<Field label="Vulnerability adjustment"' in entity_risk_source
    assert '<Field label="Confidence"' in entity_risk_source
    assert '<Field label="Evidence records"' in entity_risk_source
    assert '<Field label="Source concentration HHI"' in entity_risk_source
    assert '<Field label="Country concentration HHI"' in entity_risk_source
    assert '<Field label="Weighting method"' in entity_risk_source
    assert '<Field label="Selected entity" value={formatNodeDisplayRef(selectedNodeId)}' in entity_risk_source


def test_entity_risk_evidence_tables_hide_raw_edge_and_source_record_ids() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")
    entity_risk_source = source.split("export function CompanyRisk360", 1)[1].split("export function PredictionCenter", 1)[0]

    assert 'columns={["edge_id", "edge_type", "source_ref", "summary"]}' not in entity_risk_source
    assert "source_record_id" not in entity_risk_source
    assert "<td>{evidence.edge_id}</td>" not in entity_risk_source
    assert "<td>{evidence.edge_type}</td>" not in entity_risk_source
    assert 'relationship: formatDisplayLabel(evidence.edge_type)' in entity_risk_source
    assert 'source: formatSourceDisplayRef(evidence.source_refs[0]?.source_id ?? "unavailable")' in entity_risk_source
    assert 'columns={["relationship", "source", "summary"]}' in entity_risk_source
    assert "<th>{t(\"Relationship\")}</th>" in entity_risk_source
    assert "<td>{formatDisplayLabel(evidence.edge_type)}</td>" in entity_risk_source
    assert "<td>{sourceRef ? formatSourceDisplayRef(sourceRef.source_id) : \"unavailable\"}</td>" in entity_risk_source


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
    assert "formatNodeDisplayRef(raw)" in source
    assert "formatSourceDisplayRef(value)" in source
    assert "formatDisplayValue(String(family.source_status" in source
    assert 'label: "known source gaps"' in source
    assert 'label: "proxy limitations"' in source
    assert 'label: "next narrow patch"' in source
    assert 'label: "source_gaps"' not in source
    assert 'label: "proxy_limitations"' not in source
    assert "Evidence support by source" in source
    assert "formatSourceList(family.source_ids)" in source
    assert "formatCoverageText(source.coverage_summary, stage.id)" in source
    assert "source.source_id)}</strong>" not in source
    assert "SUPPLY_RELATIONSHIP\", \"supply relationships\"" in source
    assert "view.visibleNodes" not in source
    assert "view.visibleLinks" not in source
    assert "fallbackNodes" not in source
    assert "fallbackEdges" not in source
    assert "Stage graph data unavailable; backend stage rows are hidden." in source
    assert "Loading authoritative stage graph data." in source
    assert "isStageEndpointUnavailable" in source
    assert "Source coverage fallback" not in source
    assert 'source coverage: {sourceCoverage.length || "fallback"}' not in source
    assert 'source families: {sourceFamilyCoverage.length || "not recorded"}' not in source
    assert 'evidence refs: {evidenceRefs.length || "fallback"}' not in source
    assert "source coverage unavailable" in source
    assert "source families unavailable" in source
    assert "evidence refs unavailable" in source


def test_graph_explorer_endpoint_status_uses_user_facing_unavailable_copy() -> None:
    source = read("apps/web/src/features/graph-explorer/GraphExplorer.tsx")

    assert "GRAPH_ENDPOINT_UNAVAILABLE_MESSAGE" in source
    assert "STAGE_ENDPOINT_UNAVAILABLE_MESSAGE" in source
    assert "GRAPH_DATA_LOADING_MESSAGE" in source
    assert "GRAPH_DATA_TIMEOUT_MESSAGE" in source
    assert "GRAPH_DATA_LOADED_MESSAGE" in source
    assert "STAGE_DATA_LOADING_MESSAGE" in source
    assert "STAGE_DATA_TIMEOUT_MESSAGE" in source
    assert "STAGE_DATA_LOADED_MESSAGE" in source
    assert "Backend graph data unavailable; authoritative rows are hidden." in source
    assert "Backend stage graph data unavailable; authoritative rows are hidden." in source
    assert "Loading authoritative graph data." in source
    assert "Authoritative graph data loaded." in source
    assert "Loading authoritative stage graph data." in source
    assert "Authoritative stage graph data loaded." in source
    assert "Authoritative data connected" in source
    assert "Backend data unavailable" in source
    assert "Fallback graph payload" not in source
    assert "Fallback stage graph payload" not in source
    assert "Backend graph view endpoint loading." not in source
    assert "Backend graph view endpoint active." not in source
    assert "Backend stage graph endpoint loading." not in source
    assert "Backend stage graph endpoint active." not in source


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


def test_deployed_smoke_accepts_only_controlled_forward_diagnostics() -> None:
    source = read("scripts/browser-smoke.mjs")

    assert "const canAcceptForwardDegradedState = deployedBestEffort || !forwardScenarioReady;" in source
    assert "const canAcceptReverseDegradedState = deployedBestEffort || !reverseScenarioReady;" in source
    assert "const canAcceptOptimizerDegradedState = deployedBestEffort || !interventionOptimizationReady;" in source
    assert "const canAcceptReportDegradedState = deployedBestEffort || !investigationReportReady;" in source
    assert "const degradedEnvelopeApiUrlLiteral = JSON.stringify(deployedBestEffort ? webApiBase : apiBase);" in source
    assert "(deployedBestEffort && [502, 503].includes(degradedApiResult.status))" in source
    assert "attempt <= 3" in source
    assert "baseKind: base.includes('supply-risk-atlas-web') ? 'web_proxy' : 'api_direct'" in source
    assert "error: degradedApiResult.error" in source
    assert "(deployedBestEffort && Boolean(degradedApiResult.error))" in source
    assert 'state.text.includes("Shock Simulator unavailable")' in source
    assert 'state.text.includes("Reverse Stress Lab unavailable")' in source
    assert 'state.text.includes("Intervention Optimizer unavailable")' in source
    assert 'state.text.includes("Investigation Report unavailable")' in source
    assert 'state.text.includes("View diagnostics")' in source
    assert "canAcceptForwardDegradedState &&" in source
    assert "canAcceptReverseDegradedState &&" in source
    assert "canAcceptOptimizerDegradedState &&" in source
    assert "canAcceptReportDegradedState &&" in source


def test_graph_legend_does_not_render_raw_warning_metadata_in_primary_list() -> None:
    source = read("apps/web/src/features/graph-explorer/GraphLegend.tsx")
    audit_source = read("apps/web/src/features/common/AuditDetails.tsx")

    assert "visibleWarningLabels(metadata.warnings)" in source
    assert "metadata.warnings.map((warning)" not in source
    assert 'return warning' not in source
    assert "formatPublicWarning" in source
    assert 'return "Public evidence warning"' not in source
    assert 'return String(formatDisplayValue(warning))' in audit_source
    assert "semirisk_fixture_metadata" in audit_source
    assert "Fixture graph metadata available" in audit_source


def test_audit_details_formats_internal_tokens_before_rendering() -> None:
    source = read("apps/web/src/features/common/AuditDetails.tsx")

    assert "formatPublicWarning(warning)" in source
    assert 'return "Research fixture mode"' in source
    assert 'return "Research fixture calibration"' in source
    assert 'return value ? "yes" : "no"' in source
    assert "{warning}</li>" not in source
    assert "fixture_proxy_not_calibrated; not_financial_loss" not in source


def test_graph_evidence_view_does_not_use_edge_id_as_visible_source_fallback() -> None:
    source = read("apps/web/src/features/graph-explorer/GraphEvidenceView.tsx")

    assert "formatEvidenceRef((row as Record<string, unknown>).source_id)" in source
    assert "formatEvidenceRef((row as Record<string, unknown>).source_id ?? (row as Record<string, unknown>).edge_id)" not in source
    assert 'return "Evidence source"' in source


def test_relationship_chart_labels_use_user_facing_node_labels() -> None:
    supply = read("apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx")
    demand = read("apps/web/src/features/graph-explorer/DemandRelationshipView.tsx")
    dependency = read("apps/web/src/features/graph-explorer/ProductionDependencyView.tsx")
    balance = read("apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx")

    assert "label: formatCell(row.supplier_id ?? \"supplier\")" in supply
    assert "label: String(row.supplier_id ?? \"supplier\")" not in supply
    assert "const key = formatCell(row.product_grade_id ?? \"product_grade\")" in demand
    assert "const key = String(row.product_grade_id ?? \"product_grade\")" not in demand
    assert "label: formatCell(row.dependency_target_id ?? row.dependency_type ?? \"dependency\")" in dependency
    assert "label: String(row.dependency_target_id ?? row.dependency_type ?? \"dependency\")" not in dependency
    assert "label: formatCell((row as Record<string, unknown>).product_grade_id ?? \"product\")" in balance
    assert "label: String((row as Record<string, unknown>).product_grade_id ?? \"product\")" not in balance


def test_relationship_views_do_not_use_internal_class_names_as_summary_badges() -> None:
    relationship_files = [
        "apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx",
        "apps/web/src/features/graph-explorer/DemandRelationshipView.tsx",
        "apps/web/src/features/graph-explorer/ProductionDependencyView.tsx",
        "apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx",
    ]

    for relative_path in relationship_files:
        source = read(relative_path)
        assert "{ label: data.relationship_class }" not in source
        assert " Relationship view" not in source
        assert " Dependency view" not in source
        assert " Balance view" not in source

    stage_source = read("apps/web/src/features/graph-explorer/stage-views/StageGraphView.tsx")
    assert "relationship class:" not in stage_source
    assert "Can this edge propagate risk?" not in stage_source
    assert "fixture/promoted public-evidence view" not in stage_source
    assert "Risk propagation:" in stage_source
    assert "Focused view: up to 18 nodes / 30 edges" in stage_source


def test_timeline_and_geo_views_avoid_raw_id_visible_fallbacks() -> None:
    timeline = read("apps/web/src/features/graph-explorer/GraphTimelineView.tsx")
    geo = read("apps/web/src/features/graph-explorer/GraphGeoView.tsx")

    assert "formatTimelineEventLabel(event, index)" in timeline
    assert "event.id ?? \"event\"" not in timeline
    assert "formatDisplayValue(String(value))" in timeline
    assert "formatGeoLabel(country as Record<string, unknown>)" in geo
    assert "countryName ?? (country as Record<string, unknown>).code" not in geo
    assert "formatNodeDisplayRef(value) || String(formatDisplayValue(value))" in geo


def test_data_table_hides_raw_evidence_record_ids_without_source_context() -> None:
    source = read("apps/web/src/features/common/tables/DataTable.tsx")

    assert "const evidenceId = record.source_record_id ?? record.evidence_id ?? record.ref_id ?? record.edge_id ?? record.id" in source
    assert 'if (evidenceId) return "Evidence record";' in source
    assert "if (id) return formatPrimaryValue(String(id));" not in source
    assert "record.source_record_id ??\n      record.evidence_id ??" not in source


def test_graph_canvas_tooltips_do_not_fallback_to_raw_edge_ids() -> None:
    graph_canvas = read("apps/web/src/features/graph-explorer/GraphCanvas.tsx")
    legacy_dashboard = read("apps/web/src/features/common/legacyDashboard.tsx")

    for source in (graph_canvas, legacy_dashboard):
        assert "title: formatEdgeTooltipTitle(edge.label, link)" in source
        assert "title: edge.label ? String(edge.label) : link?.label ?? edge.id" not in source
        assert 'return "Graph edge";' in source
        assert "link?.edgeRole || link?.edgeType" in source


def test_graph_node_country_labels_use_canonical_geography_formatter() -> None:
    display_labels = read("apps/web/src/features/common/displayLabels.ts")
    controls = read("apps/web/src/features/graph-explorer/GraphControls.tsx")
    focus = read("apps/web/src/features/graph-explorer/GraphFocusView.tsx")
    canvas = read("apps/web/src/features/graph-explorer/GraphCanvas.tsx")
    legacy_dashboard = read("apps/web/src/features/common/legacyDashboard.tsx")

    assert "export function formatGeographyDisplayRef" in display_labels
    assert 'return "\\u4e2d\\u56fd\\u53f0\\u6e7e";' in display_labels.encode("unicode_escape").decode("ascii")
    assert 'return "Global";' in display_labels
    for source in (controls, focus, canvas, legacy_dashboard):
        assert "formatGeographyDisplayRef" in source
    for source in (controls, focus):
        assert 'node.countryCode ?? "global"' in source
        assert "{node.countryCode ?? \"global\"}" not in source
    assert "${data.graphNode.countryCode ?? String(data.graphNode.metadata.country ?? \"global\")}" not in canvas
    assert "{node.countryCode ?? String(node.metadata.country ?? \"global\")}" not in canvas
    assert "${data.graphNode.countryCode ?? String(data.graphNode.metadata.country ?? \"global\")}" not in legacy_dashboard
    assert "{node.countryCode ?? String(node.metadata.country ?? \"global\")}" not in legacy_dashboard


def test_system_health_manifest_and_checksum_are_audit_details_not_primary_subtitles() -> None:
    source = read("apps/web/src/features/common/legacyDashboard.tsx")

    assert 'subtitle="Public source registry summary; manifest and checksum details are available in audit details."' in source
    assert 'subtitle="Public evidence lineage summary from source records to graph edges."' in source
    assert "subtitle={`${health.sourceRegistry.manifestRef}; checksum" not in source
    assert "subtitle={`${health.evidenceLineage.manifestRef}; raw to silver to gold audit chain.`}" not in source
    assert '<Field label="Checksum"' not in source
    assert '{ label: "manifest_ref", value: health.sourceRegistry.manifestRef }' in source
    assert '{ label: "checksum", value: manifestChecksum }' in source
    assert '{ label: "manifest_ref", value: health.evidenceLineage.manifestRef }' in source
    assert '{ label: "checksum", value: health.evidenceLineage.checksum.slice(0, 12) }' in source
