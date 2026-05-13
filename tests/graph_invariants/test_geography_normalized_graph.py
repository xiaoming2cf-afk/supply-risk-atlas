from __future__ import annotations

import json

from graph_kernel.promoted_pipeline import build_promoted_graph_snapshot
from sra_core.geo.terminology import CANONICAL_DISPLAY, CANONICAL_REGION_ID


def test_promoted_graph_uses_canonical_region_node_and_display_label() -> None:
    payload = build_promoted_graph_snapshot().model_dump(mode="json")
    nodes = {node["node_id"]: node for node in payload["nodes"]}

    assert CANONICAL_REGION_ID in nodes
    assert nodes[CANONICAL_REGION_ID]["node_type"] == "region"
    assert nodes[CANONICAL_REGION_ID]["canonical_name"] == CANONICAL_DISPLAY
    assert nodes[CANONICAL_REGION_ID]["attributes"]["country_id"] == "country:CN"


def test_promoted_graph_has_no_old_region_country_node() -> None:
    payload = build_promoted_graph_snapshot().model_dump(mode="json")
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    forbidden_tokens = [
        "country:" + "tw",
        "country:" + "TW",
        "country:" + "Tai" + "wan",
        "region:" + "tw",
        "region:" + "TW",
        "region:" + "Tai" + "wan",
    ]
    assert all(token not in rendered for token in forbidden_tokens)


def test_relationship_edges_normalize_geography_ids_and_text() -> None:
    payload = build_promoted_graph_snapshot().model_dump(mode="json")

    for edge in payload["edges"]:
        legacy_country_id = "country:" + "tw"
        legacy_region_id = "region:" + "tw"
        assert edge["source_node_id"] not in {legacy_country_id, legacy_region_id}
        assert edge["target_node_id"] not in {legacy_country_id, legacy_region_id}
        assert "Tai" + "wan" not in edge["evidence_text_summary"]

    region_edges = [
        edge
        for edge in payload["edges"]
        if CANONICAL_REGION_ID in {edge["source_node_id"], edge["target_node_id"]}
    ]
    assert region_edges
    for edge in region_edges:
        if edge["relationship_class"] == "EVIDENCE_CONTEXT":
            assert edge["attributes"]["not_supply_chain_dependency"] is True
            assert edge["attributes"]["warning"] == "This is not a supply-chain dependency edge."
