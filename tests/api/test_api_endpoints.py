from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic")
from fastapi.testclient import TestClient

from services.api.main import create_app


def _client() -> TestClient:
    app = create_app()
    assert app is not None
    return TestClient(app)


def test_health_aliases_return_envelope_with_request_id() -> None:
    client = _client()

    for path in ("/health", "/api/v1/health"):
        response = client.get(path, headers={"x-request-id": "req_health"})
        payload = response.json()

        assert response.status_code == 200
        assert payload["request_id"] == "req_health"
        assert payload["status"] == "success"
        assert payload["data"]["service"] == "supply-risk-atlas-api"
        assert payload["errors"] == []


@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("get", "/api/v1/entities", None),
        ("get", "/api/v1/entities?q=Apple&limit=2", None),
        ("get", "/api/v1/entities/firm_apple", None),
        ("get", "/api/v1/sources", None),
        ("get", "/api/v1/sources/sec_edgar", None),
        ("get", "/api/v1/lineage", None),
        ("get", "/api/v1/lineage/gdelt", None),
        ("get", "/api/v1/graph", None),
        ("get", "/api/v1/graph/snapshots", None),
        ("get", "/api/v1/features?entity_id=firm_apple", None),
        ("get", "/api/v1/labels", None),
        ("get", "/api/v1/predictions", None),
        ("get", "/api/v1/explanations", None),
        ("get", "/api/v1/simulations", None),
        ("get", "/api/v1/reports", None),
        ("get", "/api/v1/dashboard/global-risk-cockpit", None),
        ("get", "/api/v1/dashboard/graph-explorer", None),
        ("post", "/api/v1/predictions", {"target_id": "firm_apple"}),
        ("post", "/api/v1/explanations", {"target_id": "firm_apple"}),
        (
            "post",
            "/api/v1/simulations",
            {"intervention_type": "close_port", "target_id": "port_kaohsiung"},
        ),
        (
            "post",
            "/api/v1/dashboard/shock-simulator",
            {
                "region": "Taiwan Strait",
                "commodity": "advanced semiconductor components",
                "severity": 95,
                "durationDays": 28,
                "scope": "regional",
            },
        ),
        ("post", "/api/v1/reports", {"report_type": "entity", "target_id": "firm_apple"}),
    ],
)
def test_primary_api_endpoints_return_success_envelopes(
    method: str,
    path: str,
    json_body: dict[str, object] | None,
) -> None:
    client = _client()

    response = client.request(
        method,
        path,
        json=json_body,
        headers={"x-request-id": "req_endpoint"},
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["request_id"] == "req_endpoint"
    assert payload["status"] == "success"
    assert payload["metadata"]["graph_version"]
    assert payload["metadata"]["data_mode"] == "real"
    assert payload["errors"] == []
    assert payload["data"] is not None


def test_not_found_returns_error_envelope() -> None:
    client = _client()

    response = client.get("/api/v1/entities/missing", headers={"x-request-id": "req_missing"})
    payload = response.json()

    assert response.status_code == 404
    assert payload["request_id"] == "req_missing"
    assert payload["status"] == "error"
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "not_found"


def test_dashboard_routes_return_envelope_and_view_model() -> None:
    client = _client()

    cockpit = client.get("/api/v1/dashboard/global-risk-cockpit", headers={"x-request-id": "req_dash"})
    cockpit_payload = cockpit.json()

    assert cockpit.status_code == 200
    assert cockpit_payload["request_id"] == "req_dash"
    assert cockpit_payload["status"] == "success"
    assert cockpit_payload["data"]["operatingMode"] == "real"
    assert cockpit_payload["metadata"]["graph_version"]

    shock = client.post(
        "/api/v1/dashboard/shock-simulator",
        json={
            "region": "Taiwan Strait",
            "commodity": "advanced semiconductor components",
            "severity": 95,
            "durationDays": 28,
            "scope": "regional",
        },
        headers={"x-request-id": "req_shock"},
    )
    shock_payload = shock.json()

    assert shock.status_code == 200
    assert shock_payload["request_id"] == "req_shock"
    assert shock_payload["status"] == "success"
    assert shock_payload["data"]["input"]["severity"] == 95
    assert shock_payload["data"]["impactScore"] > 70


def test_sources_route_exposes_manifest_and_freshness() -> None:
    client = _client()

    response = client.get("/api/v1/sources", headers={"x-request-id": "req_sources"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["request_id"] == "req_sources"
    assert payload["status"] == "success"
    assert payload["mode"] == "real"
    assert payload["data"]["manifestRef"].startswith("manifest_public_real_")
    assert payload["data"]["sourceCount"] >= 7
    assert payload["data"]["dataNodeCount"] >= 30
    assert payload["data"]["promotedGraph"]["status"] in {"promoted", "partial"}
    assert {source["id"] for source in payload["data"]["sources"]} >= {"sec_edgar", "gleif", "gdelt"}
    assert all(source["status"] == "fresh" for source in payload["data"]["sources"])


def test_entity_search_filters_real_registry() -> None:
    client = _client()

    response = client.get("/api/v1/entities?q=Apple&limit=5", headers={"x-request-id": "req_entity_search"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["request_id"] == "req_entity_search"
    assert payload["status"] == "success"
    assert [entity["canonical_id"] for entity in payload["data"]] == ["firm_apple"]

    source_response = client.get("/api/v1/entities?q=SEC%20EDGAR&limit=100")
    source_payload = source_response.json()
    assert source_response.status_code == 200
    source_ids = {entity["canonical_id"] for entity in source_payload["data"]}
    assert {"firm_apple", "firm_tesla", "firm_nvidia"} <= source_ids

    cik_response = client.get("/api/v1/entities?q=0000320193&limit=5")
    cik_payload = cik_response.json()
    assert cik_response.status_code == 200
    assert [entity["canonical_id"] for entity in cik_payload["data"]] == ["firm_apple"]

    data_response = client.get("/api/v1/entities?entity_type=data_source&q=World%20Bank&limit=10")
    data_payload = data_response.json()
    assert data_response.status_code == 200
    assert [entity["canonical_id"] for entity in data_payload["data"]] == ["data_source_world_bank"]

    indicator_response = client.get("/api/v1/entities?q=TX.VAL.TECH.MF.ZS&limit=10")
    indicator_payload = indicator_response.json()
    assert indicator_response.status_code == 200
    assert [entity["canonical_id"] for entity in indicator_payload["data"]] == [
        "indicator_high_tech_exports"
    ]

    filtered_indicator_response = client.get(
        "/api/v1/entities?entity_type=indicator&source_id=world_bank&limit=10"
    )
    filtered_indicator_payload = filtered_indicator_response.json()
    assert filtered_indicator_response.status_code == 200
    assert filtered_indicator_payload["data"]
    assert all(entity["entity_type"] == "indicator" for entity in filtered_indicator_payload["data"])


def test_lineage_route_links_raw_silver_and_gold_records() -> None:
    client = _client()

    response = client.get("/api/v1/lineage", headers={"x-request-id": "req_lineage"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["request_id"] == "req_lineage"
    assert payload["status"] == "success"
    assert payload["mode"] == "real"
    assert payload["data"]["manifestRef"].startswith("manifest_public_real_")
    assert payload["data"]["rawRecordCount"] >= 7
    assert payload["data"]["goldEdgeEventCount"] >= 1
    assert all(len(record["rawChecksum"]) == 64 for record in payload["data"]["records"])

    gdelt_records = [
        record
        for record in payload["data"]["records"]
        if record["sourceId"] == "gdelt"
    ]
    assert gdelt_records
    assert gdelt_records[0]["silverEventIds"]
    assert gdelt_records[0]["goldEdgeEventIds"]
    assert "Apple Inc." in gdelt_records[0]["targetEntities"]

    filtered_response = client.get("/api/v1/lineage?target_id=firm_apple")
    filtered_payload = filtered_response.json()
    assert filtered_response.status_code == 200
    assert filtered_payload["data"]["records"]
    assert all(
        "Apple Inc." in record["targetEntities"]
        for record in filtered_payload["data"]["records"]
    )


def test_cors_preflight_is_available_for_frontend() -> None:
    client = _client()

    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"]
