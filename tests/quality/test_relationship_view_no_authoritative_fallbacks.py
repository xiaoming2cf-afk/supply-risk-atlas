from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RELATIONSHIP_VIEW_FILES = {
    "apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx": "SUPPLY_RELATIONSHIP",
    "apps/web/src/features/graph-explorer/DemandRelationshipView.tsx": "DEMAND_RELATIONSHIP",
    "apps/web/src/features/graph-explorer/ProductionDependencyView.tsx": "PRODUCTION_DEPENDENCY",
    "apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx": "SUPPLY_DEMAND_BALANCE",
}


def test_relationship_views_do_not_render_graph_derived_authoritative_rows() -> None:
    forbidden_snippets = [
        "visibleLinks.slice",
        "visibleNodes.slice",
        "showing controlled local graph rows",
    ]
    for relative_path, expected_class in RELATIONSHIP_VIEW_FILES.items():
        source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in forbidden_snippets:
            assert snippet not in source, f"{relative_path} still contains {snippet!r}"
        assert "unavailable-preview" in source
        assert 'data-preview-state="unavailable_preview"' in source
        assert "data is temporarily unavailable" in source
        assert "coverage review" in source
        assert "public evidence support" in source
        assert "Backend" not in source
        assert "authoritative" not in source.lower()
        assert "non-authoritative" not in source.lower()
        assert "local preview" not in source.lower()
        assert expected_class in source
        assert "relationship_class" in source
        assert "data={!isEndpointUnavailable" in source or "data={!isEndpointUnavailable ?" in source


def test_graph_explorer_keeps_diagnostics_separate_from_relationship_rows() -> None:
    source = (REPO_ROOT / "apps/web/src/features/graph-explorer/GraphExplorer.tsx").read_text(encoding="utf-8")

    assert "diagnosticsForEndpointResult" in source
    assert "failed_endpoint" in source
    assert "transport_attempts" in source
    assert "relationshipEndpointLoadingExpired" in source
    assert "displayedEndpointDetails" in source
    assert "const endpointDataForMode =" in source
    assert 'displayedEndpointDetails.source === "backend"' in source
    assert 'displayedEndpointDetails.status === "active"' in source
    assert "endpointData={endpointDataForMode}" in source
    assert "mode: options.mode" in source
    assert 'status: "loading"' in source
    assert "visibleLinks.slice" not in source
    assert "buildRelationshipExportSummary(mode, endpointDataForMode, displayedEndpointDetails, metadata)" in source
    assert "data_scope: \"relationship_data_temporarily_unavailable\"" in source
    assert "data_scope: \"reviewed_public_relationship_rows\"" in source
    assert "data_scope: \"reviewed_public_aggregate_rows\"" in source
    assert "unavailable_preview_no_authoritative_relationship_rows" not in source
    assert "authoritative_backend_relationship_rows_only" not in source
    assert "authoritative_backend_aggregate_rows_only" not in source
    assert "Loading authoritative relationship data." not in source
    assert "GRAPH_ENDPOINT_LOADING_TIMEOUT_MS" in source
    assert "Graph data is taking longer than expected; review source coverage before using this view." in source
    assert "Stage graph data is taking longer than expected; review source coverage before using this stage." in source
    assert "transportAttempts: 0" in source
    assert source.index("buildRelationshipExportSummary") < source.index("links: view.visibleLinks.map")


def test_supply_demand_balance_ui_requires_aggregate_markers() -> None:
    source = (REPO_ROOT / "apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx").read_text(encoding="utf-8")

    assert "row.relationship_class === SUPPLY_DEMAND_BALANCE_CLASS" in source
    assert 'row.row_type === "aggregate"' in source
    assert "row.not_supply_chain_dependency === true" in source
