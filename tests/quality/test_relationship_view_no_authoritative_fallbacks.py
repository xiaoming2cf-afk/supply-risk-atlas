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
        assert "unavailable_preview" in source
        assert "no authoritative" in source.lower()
        assert expected_class in source
        assert "relationship_class" in source
        assert "data={!isEndpointUnavailable" in source or "data={!isEndpointUnavailable ?" in source


def test_graph_explorer_keeps_diagnostics_separate_from_relationship_rows() -> None:
    source = (REPO_ROOT / "apps/web/src/features/graph-explorer/GraphExplorer.tsx").read_text(encoding="utf-8")

    assert "diagnosticsForEndpointResult" in source
    assert "failed_endpoint" in source
    assert "transport_attempts" in source
    assert "const endpointDataForMode =" in source
    assert 'endpointDetails.mode === mode && endpointDetails.source === "backend" && endpointDetails.status === "active"' in source
    assert "endpointData={endpointDataForMode}" in source
    assert "mode: options.mode" in source
    assert 'status: "loading"' in source
    assert "visibleLinks.slice" not in source
    assert "buildRelationshipExportSummary(mode, endpointDataForMode, endpointDetails, metadata)" in source
    assert "data_scope: \"unavailable_preview_no_authoritative_relationship_rows\"" in source
    assert "authoritative_backend_relationship_rows_only" in source
    assert "authoritative_backend_aggregate_rows_only" in source
    assert source.index("buildRelationshipExportSummary") < source.index("links: view.visibleLinks.map")


def test_supply_demand_balance_ui_requires_aggregate_markers() -> None:
    source = (REPO_ROOT / "apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx").read_text(encoding="utf-8")

    assert "row.relationship_class === SUPPLY_DEMAND_BALANCE_CLASS" in source
    assert 'row.row_type === "aggregate"' in source
    assert "row.not_supply_chain_dependency === true" in source
