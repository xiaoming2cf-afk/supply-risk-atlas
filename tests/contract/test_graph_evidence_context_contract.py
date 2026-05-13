from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "data_contracts" / "graph_schema" / "evidence_context_link.schema.json"


def test_evidence_context_link_cannot_be_confused_with_supply_chain_dependency() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    properties = schema["properties"]
    required = set(schema["required"])

    assert schema["title"] == "evidence_context_link"
    assert properties["derived_context"]["const"] is True
    assert properties["not_supply_chain_dependency"]["const"] is True
    assert properties["user_facing_label"]["const"] == "evidence-context link"
    assert required >= {
        "derived_context",
        "not_supply_chain_dependency",
        "user_facing_label",
        "provenance_refs",
        "evidence_text_summary",
    }
