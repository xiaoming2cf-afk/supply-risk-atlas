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
