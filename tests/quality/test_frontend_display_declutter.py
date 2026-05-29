from pathlib import Path


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

    for source in (table_source, chart_source):
        assert "AuditDetails" in source
        assert "MetadataSummary" in source
        assert "graph_version=" not in source
        assert "source_manifest_id=" not in source
        assert "metadata-line" not in source
    assert "formatDisplayLabel(column)" in table_source
    assert "formatDisplayLabel(metric.label)" in component_source
    assert "formatDisplayLabel(label)" in component_source


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


def test_page_relevance_policy_declares_display_tiers() -> None:
    source = read("apps/web/src/features/common/pageRelevance.ts")

    assert "displayTiers" in source
    assert "audit_details" in source
    assert "developer_diagnostics" in source
