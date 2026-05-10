from __future__ import annotations

import json

from sra_core.reports.investigation import REPORT_VERSION, generate_investigation_report


def _assert_safe(payload: object) -> None:
    text = json.dumps(payload, sort_keys=True).lower()
    assert '"raw_payload":' not in text
    assert '"private_diagnostics":' not in text
    assert "secret" not in text


def test_investigation_report_json_includes_versions_and_exclusions() -> None:
    report = generate_investigation_report({"entity_id": "company:tsmc", "include_entity_risk": True, "format": "json"})

    assert report["report_id"].startswith("report_")
    assert report["report_version"] == REPORT_VERSION
    assert report["risk_score"]["node_id"] == "company:tsmc"
    assert report["versions"]["graph_version"].startswith("semirisk_kg_v0_1_")
    assert report["versions"]["source_manifest_id"].startswith("semirisk_fixture_manifest_")
    assert report["raw_payload_excluded"] is True
    assert report["private_diagnostics_excluded"] is True
    assert "fixture_graph:not_production_ready" in report["warnings"]
    _assert_safe(report)


def test_investigation_report_markdown_is_generated() -> None:
    report = generate_investigation_report({"entity_id": "company:tsmc", "include_entity_risk": True, "format": "markdown"})

    assert report["format"] == "markdown"
    assert "# Investigation Report" in report["markdown"]
    assert "raw_payload_excluded: true" in report["markdown"]
    _assert_safe(report)
