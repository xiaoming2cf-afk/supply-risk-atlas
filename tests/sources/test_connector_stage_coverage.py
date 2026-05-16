from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "configs" / "sources" / "stage_source_coverage_matrix.yaml"
AUDIT_PATH = ROOT / "docs" / "data" / "connector-stage-coverage-audit.md"
CONNECTOR_ROOT = ROOT / "packages" / "sra_core" / "sra_core" / "ingestion" / "connectors"

REQUIRED_CONNECTORS = {
    "sec_edgar_lite.py",
    "gdelt_semiconductor_lite.py",
    "un_comtrade_semiconductor_trade_lite.py",
    "wits_trade_tariff_lite.py",
    "usgs_minerals_lite.py",
    "usgs_earthquake_lite.py",
    "nga_world_port_index_lite.py",
    "ofac_sanctions_list_lite.py",
    "consolidated_screening_list_lite.py",
    "bis_export_controls_lite.py",
    "federal_register_export_controls_lite.py",
    "eto_supply_chain.py",
    "wsts_billings.py",
}

SOURCE_FAMILY_LABELS = {
    "National/policy/macro public",
    "Enterprise public disclosure",
    "Industry public fixture",
}


def _matrix() -> dict:
    return yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))


def test_required_connectors_are_mapped_to_at_least_one_stage() -> None:
    connector_stages: dict[str, set[str]] = {}
    for stage in _matrix()["stages"]:
        for connector in stage["connector_files"]:
            connector_stages.setdefault(connector, set()).add(stage["stage_id"])

    assert REQUIRED_CONNECTORS <= set(connector_stages)
    for connector in REQUIRED_CONNECTORS:
        assert connector_stages[connector], connector
        assert (CONNECTOR_ROOT / connector).exists(), connector


def test_every_stage_has_two_source_candidates_in_connector_audit() -> None:
    for stage in _matrix()["stages"]:
        sources = set(stage["primary_sources"]) | set(stage["secondary_sources"])
        assert len(sources) >= 2, stage["stage_id"]
        assert stage["connector_files"], stage["stage_id"]


def test_connector_stage_audit_does_not_claim_production_readiness() -> None:
    text = AUDIT_PATH.read_text(encoding="utf-8").lower()

    assert "production readiness" not in text
    assert "production-ready" not in text
    assert "production ready" not in text
    assert "production_verified" not in text
    assert "official" not in text
    assert "disabled by default" in text


def test_connector_stage_audit_records_source_families_and_live_disabled() -> None:
    text = AUDIT_PATH.read_text(encoding="utf-8")

    for label in SOURCE_FAMILY_LABELS:
        assert label in text
    for connector in REQUIRED_CONNECTORS:
        row = next(line for line in text.splitlines() if f"`{connector}`" in line)
        assert "disabled by default" in row
        assert any(label in row for label in SOURCE_FAMILY_LABELS), connector
