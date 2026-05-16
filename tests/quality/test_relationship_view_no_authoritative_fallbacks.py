from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RELATIONSHIP_VIEW_FILES = [
    "apps/web/src/features/graph-explorer/SupplyRelationshipView.tsx",
    "apps/web/src/features/graph-explorer/DemandRelationshipView.tsx",
    "apps/web/src/features/graph-explorer/ProductionDependencyView.tsx",
    "apps/web/src/features/graph-explorer/SupplyDemandBalanceView.tsx",
]


def test_relationship_views_do_not_render_graph_derived_authoritative_rows() -> None:
    forbidden_snippets = [
        "visibleLinks.slice",
        "visibleNodes.slice",
        "showing controlled local graph rows",
    ]
    for relative_path in RELATIONSHIP_VIEW_FILES:
        source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for snippet in forbidden_snippets:
            assert snippet not in source, f"{relative_path} still contains {snippet!r}"
        assert "unavailable-preview" in source
        assert "no authoritative" in source.lower()
        assert "data={!isEndpointUnavailable" in source or "data={!isEndpointUnavailable ?" in source


def test_graph_explorer_keeps_diagnostics_separate_from_relationship_rows() -> None:
    source = (REPO_ROOT / "apps/web/src/features/graph-explorer/GraphExplorer.tsx").read_text(encoding="utf-8")

    assert "diagnosticsForEndpointResult" in source
    assert "failed_endpoint" in source
    assert "transport_attempts" in source
    assert "endpointData={endpointDetails.data}" in source
    assert "visibleLinks.slice" not in source
