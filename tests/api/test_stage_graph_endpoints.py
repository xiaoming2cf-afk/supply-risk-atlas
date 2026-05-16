from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api.main import create_app


STAGE_IDS = [
    "L0_policy_macro",
    "L1_raw_minerals",
    "L2_materials_chemicals",
    "L3_design_eda_ip",
    "L4_equipment",
    "L5_fabrication",
    "L6_products",
    "L7_packaging_testing",
    "L8_logistics",
    "L9_downstream_demand",
    "L10_risk_events",
    "L11_compliance",
]


def _client() -> TestClient:
    app = create_app()
    assert app is not None
    return TestClient(app)


def _assert_stage_payload(payload: dict[str, object], stage_id: str) -> dict[str, object]:
    assert payload["status"] == "success"
    data = payload["data"]
    assert isinstance(data, dict)
    assert data["stage_id"] == stage_id
    for key in (
        "stage_name",
        "business_question",
        "nodes",
        "edges",
        "clusters",
        "chart_data_refs",
        "table_data_refs",
        "source_coverage",
        "evidence_refs",
        "graph_version",
        "source_manifest_id",
        "data_mode",
        "graph_mode",
        "warnings",
        "relationship_class_counts",
        "required_data_fields",
        "primary_sources",
        "secondary_sources",
        "source_families",
        "source_family_coverage",
        "source_gaps",
        "proxy_limitations",
        "source_status",
        "evidence_ref_count",
        "calibration_status",
        "failure_reason",
        "required_narrow_patch_if_failed",
    ):
        assert key in data
    rendered = json.dumps(payload, ensure_ascii=False, sort_keys=True).lower()
    assert "raw_payload" not in rendered
    assert "article_body" not in rendered
    assert "filing_body" not in rendered
    assert "authorization" not in rendered
    assert "api_key" not in rendered
    assert "official" not in rendered
    assert "production_verified" not in rendered
    assert "source_status: official" not in rendered
    assert "production_status: production" not in rendered
    assert "country:" + "tw" not in rendered
    assert "region:" + "tw" not in rendered
    return data


@pytest.mark.parametrize("stage_id", STAGE_IDS)
def test_stage_graph_endpoint_returns_bounded_stage_data(
    monkeypatch: pytest.MonkeyPatch,
    stage_id: str,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get(f"/api/v1/stage-graph/{stage_id}?limit=18")
    data = _assert_stage_payload(response.json(), stage_id)

    assert response.status_code == 200
    assert len(data["nodes"]) <= 18
    assert len(data["edges"]) <= 30
    assert data["layout_hints"]["does_not_render_full_graph"] is True
    assert data["source_coverage"]
    assert data["source_status"] in {
        "fixture_promoted_public_evidence",
        "incomplete_fixture_proxy",
        "unavailable_controlled",
        "deferred_registry_only",
    }
    assert data["calibration_status"] == "fixture_proxy_not_calibrated"
    assert isinstance(data["evidence_ref_count"], int)
    assert data["source_families"]
    assert data["source_family_coverage"]
    assert data["source_gaps"]
    assert data["proxy_limitations"]
    for row in data["source_coverage"]:
        assert row["source_status"] == data["source_status"]
        assert row["calibration_status"] == data["calibration_status"]
    for row in data["source_family_coverage"]:
        assert row["source_family"] in data["source_families"]
        assert row["live_fetch_default"] == "disabled"
        assert row["fixture_required"] is True
        assert row["api_visibility_policy"] == "sanitized_summary_and_lineage_only"


def test_stage_graph_focus_endpoint_caps_expansion(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get("/api/v1/stage-graph/L5_fabrication/focus?node_id=facility:tsmc_fab18&limit=25")
    data = _assert_stage_payload(response.json(), "L5_fabrication")

    assert response.status_code == 200
    assert len(data["nodes"]) <= 25
    assert len(data["edges"]) <= 40


def test_stage_graph_relationship_filter_keeps_relationship_classes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get(
        "/api/v1/stage-graph/L4_equipment?relationship_class=SUPPLY_RELATIONSHIP",
    )
    data = _assert_stage_payload(response.json(), "L4_equipment")

    assert response.status_code == 200
    assert data["relationship_class_filter"] == "SUPPLY_RELATIONSHIP"
    assert all(edge["relationship_class"] == "SUPPLY_RELATIONSHIP" for edge in data["edges"])


@pytest.mark.parametrize("suffix", ["source-coverage", "evidence", "tables", "charts"])
def test_stage_graph_support_endpoints_return_sanitized_metadata(
    monkeypatch: pytest.MonkeyPatch,
    suffix: str,
) -> None:
    monkeypatch.setenv("SUPPLY_RISK_GRAPH_MODE", "promoted")

    response = _client().get(f"/api/v1/stage-graph/L8_logistics/{suffix}")
    data = response.json()["data"]

    assert response.status_code == 200
    assert data["stage_id"] == "L8_logistics"
    assert "graph_version" in data
    assert "source_manifest_id" in data
    rendered = json.dumps(data, ensure_ascii=False, sort_keys=True).lower()
    assert "raw_payload" not in rendered
    assert "country:" + "tw" not in rendered
    assert "region:" + "tw" not in rendered
