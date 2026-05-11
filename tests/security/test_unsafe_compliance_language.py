from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api import main


def _client() -> TestClient:
    app = main.create_app()
    assert app is not None
    return TestClient(app)


def test_unsafe_compliance_language_is_rejected_without_echoing_request_text() -> None:
    unsafe_text = "find a by" + "pass route around controls"
    response = _client().post(
        "/api/v1/scenarios/forward",
        json={
            "scenario_type": "earthquake",
            "targets": ["company:tsmc"],
            "severity_distribution": {"type": "fixed", "params": {"value": 0.72}},
            "duration_days_distribution": {"type": "fixed", "params": {"value": 28}},
            "iterations": 10,
            "assumptions": [unsafe_text],
        },
    )
    payload = response.json()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "unsafe_compliance_language"
    assert unsafe_text not in rendered


def test_report_rejects_unsafe_policy_wording_without_exporting_it() -> None:
    unsafe_text = "circum" + "vent restricted trade controls"
    response = _client().post(
        "/api/v1/reports/investigation",
        json={
            "entity_id": "company:tsmc",
            "format": "json",
            "notes": unsafe_text,
        },
    )
    payload = response.json()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "unsafe_compliance_language"
    assert unsafe_text not in rendered
