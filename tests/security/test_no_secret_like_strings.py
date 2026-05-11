from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from services.api import main


def _client() -> TestClient:
    app = main.create_app()
    assert app is not None
    main.RUN_STORE.clear()
    return TestClient(app)


def test_secret_like_user_text_is_redacted_from_scenario_and_run_history() -> None:
    client = _client()
    fake_secret = "sk-test-secret-123456789"

    response = client.post(
        "/api/v1/scenarios/forward",
        json={
            "scenario_type": "earthquake",
            "targets": ["company:tsmc"],
            "severity_distribution": {"type": "fixed", "params": {"value": 0.72}},
            "duration_days_distribution": {"type": "fixed", "params": {"value": 28}},
            "iterations": 10,
            "assumptions": [f"api_key={fake_secret}"],
        },
    )
    payload = response.json()
    rendered = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "success"
    assert fake_secret not in rendered
    assert "api_key=" not in rendered
    assert "[redacted]" in rendered

    runs = client.get("/api/v1/runs").json()
    rendered_runs = json.dumps(runs, sort_keys=True)
    assert fake_secret not in rendered_runs
    assert "api_key=" not in rendered_runs
