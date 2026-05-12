from __future__ import annotations

from pathlib import Path


ROOT = Path("apps/web/src/features/graph-explorer")


def test_derived_search_context_is_named_as_link_not_real_edge() -> None:
    view_model = (ROOT / "graphViewModel.ts").read_text(encoding="utf-8")

    assert "evidence-context link" in view_model
    assert "search-context-link:" in view_model
    assert "search-context-edge" not in view_model
    assert "source evidence" not in view_model
    assert "derived_context: true" in view_model
    assert "not_supply_chain_dependency: true" in view_model
    assert 'source: "search_result_metadata"' in view_model
    assert 'edgeType: "evidence_context"' in view_model


def test_inspector_and_canvas_make_context_link_semantics_explicit() -> None:
    inspector = (ROOT / "GraphInspector.tsx").read_text(encoding="utf-8")
    canvas = (ROOT / "GraphCanvas.tsx").read_text(encoding="utf-8")
    styles = Path("packages/design-system/src/styles.css").read_text(encoding="utf-8")

    assert "This is not a supply-chain dependency edge." in inspector
    assert "evidence-context link / not supply-chain dependency" in canvas
    assert "risk-flow-evidence-context-link" in canvas
    assert "risk-flow-evidence-context-link" in styles

