from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SEMANTICS_PATH = ROOT / "configs" / "ontology" / "semiconductor_relationship_semantics.yaml"


def _load_semantics() -> dict:
    return yaml.safe_load(SEMANTICS_PATH.read_text(encoding="utf-8"))


def test_relationship_classes_are_distinct_and_complete() -> None:
    data = _load_semantics()
    classes = data["relationship_classes"]

    assert set(classes) == {
        "SUPPLY_RELATIONSHIP",
        "DEMAND_RELATIONSHIP",
        "PRODUCTION_DEPENDENCY",
        "EVIDENCE_CONTEXT",
    }
    assert not (
        set(classes["SUPPLY_RELATIONSHIP"]["allowed_edge_types"])
        & set(classes["DEMAND_RELATIONSHIP"]["allowed_edge_types"])
    )
    assert not (
        set(classes["EVIDENCE_CONTEXT"]["allowed_edge_types"])
        & set(classes["PRODUCTION_DEPENDENCY"]["allowed_edge_types"])
    )


def test_required_fields_for_supply_demand_and_dependency_edges() -> None:
    classes = _load_semantics()["relationship_classes"]

    assert "supplied_item_id" in classes["SUPPLY_RELATIONSHIP"]["required_fields"]
    assert "demand_proxy_type" in classes["DEMAND_RELATIONSHIP"]["required_fields"]
    assert "criticality" in classes["PRODUCTION_DEPENDENCY"]["required_fields"]
    assert "substitutability" in classes["PRODUCTION_DEPENDENCY"]["required_fields"]
    assert "bottleneck_flag" in classes["PRODUCTION_DEPENDENCY"]["required_fields"]


def test_evidence_context_link_cannot_be_used_for_propagation() -> None:
    evidence = _load_semantics()["relationship_classes"]["EVIDENCE_CONTEXT"]

    assert evidence["propagation_use"] == "never"
    assert evidence["allowed_edge_types"] == ["evidence_context_link"]
    assert evidence["required_metadata"]["derived_context"] is True
    assert evidence["required_metadata"]["not_supply_chain_dependency"] is True
    assert evidence["required_metadata"]["user_facing_label"] == "evidence-context link"
    assert evidence["required_metadata"]["warning"] == "This is not a supply-chain dependency edge."


def test_relationship_semantics_use_canonical_geography_policy() -> None:
    policy = _load_semantics()["geography_terminology_policy"]

    assert policy["canonical_region_id"] == "region:china_taiwan"
    assert policy["canonical_display"] == "中国台湾"
    assert policy["parent_country_id"] == "country:CN"
    assert policy["parent_country_display"] == "中国"
