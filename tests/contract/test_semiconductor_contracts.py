from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from sra_core.contracts.semiconductor import SemiriskEdge, SemiriskNode, parse_semirisk_time


ROOT = Path(__file__).resolve().parents[2]

RAW_SCHEMAS = [
    "eto_supply_chain_raw.schema.json",
    "wsts_billings_raw.schema.json",
    "gta_export_controls_raw.schema.json",
    "gdelt_semiconductor_event_raw.schema.json",
]
SILVER_SCHEMAS = [
    "semiconductor_entity.schema.json",
    "semiconductor_event.schema.json",
    "semiconductor_market_indicator.schema.json",
]
GRAPH_SCHEMAS = [
    "semirisk_node.schema.json",
    "semirisk_edge.schema.json",
    "semirisk_graph_snapshot.schema.json",
]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_requested_semiconductor_contract_schemas_exist() -> None:
    for name in RAW_SCHEMAS:
        assert (ROOT / "data_contracts" / "raw_schema" / name).exists()
    for name in SILVER_SCHEMAS:
        assert (ROOT / "data_contracts" / "silver_schema" / name).exists()
    for name in GRAPH_SCHEMAS:
        assert (ROOT / "data_contracts" / "graph_schema" / name).exists()


def test_raw_schemas_require_lineage_and_payload_summary_fields() -> None:
    required = {
        "source_id",
        "source_record_id",
        "retrieved_at",
        "source_published_at",
        "as_of_time",
        "payload_hash",
        "provenance_url",
        "raw_payload_summary",
        "license_or_terms_ref",
    }
    for name in RAW_SCHEMAS:
        schema = _load(ROOT / "data_contracts" / "raw_schema" / name)
        assert set(schema["required"]) == required


def test_graph_schemas_have_enums_and_do_not_expose_raw_payload() -> None:
    node_schema = _load(ROOT / "data_contracts" / "graph_schema" / "semirisk_node.schema.json")
    edge_schema = _load(ROOT / "data_contracts" / "graph_schema" / "semirisk_edge.schema.json")
    snapshot_schema = _load(ROOT / "data_contracts" / "graph_schema" / "semirisk_graph_snapshot.schema.json")

    assert "invalid_node_type" not in node_schema["properties"]["node_type"]["enum"]
    assert "invalid_edge_type" not in edge_schema["properties"]["edge_type"]["enum"]
    assert "raw_payload" not in json.dumps(node_schema)
    assert "raw_payload" not in json.dumps(edge_schema)
    assert "raw_payload" not in json.dumps(snapshot_schema)
    assert {"valid_from", "valid_to"}.issubset(node_schema["required"])
    assert {"valid_from", "valid_to", "provenance_refs"}.issubset(edge_schema["required"])


def test_pydantic_contracts_reject_invalid_types() -> None:
    source_ref = {
        "source_id": "eto_cset_advanced_semiconductor_supply_chain",
        "source_record_id": "record-1",
        "raw_id": "raw:record-1",
        "payload_hash": "a" * 64,
        "provenance_url": "https://example.test/source",
        "retrieved_at": "2026-05-01T00:00:00Z",
        "as_of_time": "2026-05-01T00:00:00Z",
    }
    with pytest.raises(ValidationError):
        SemiriskNode(
            node_id="node:bad",
            node_type="invalid_node_type",
            canonical_name="Bad",
            attributes={},
            source_refs=[source_ref],
            confidence=0.5,
            valid_from=parse_semirisk_time("2026-05-01T00:00:00Z"),
            valid_to=None,
        )
    with pytest.raises(ValidationError):
        SemiriskEdge(
            edge_id="edge:bad",
            source_node_id="company:tsmc",
            target_node_id="company:asml",
            edge_type="invalid_edge_type",
            weight=1.0,
            confidence=0.5,
            valid_from=parse_semirisk_time("2026-05-01T00:00:00Z"),
            valid_to=None,
            provenance_refs=[source_ref],
            evidence_text_summary="bad",
        )
