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


def test_report_drops_private_diagnostics_and_internal_paths() -> None:
    response = _client().post(
        "/api/v1/reports/investigation",
        json={
            "entity_id": "company:tsmc",
            "format": "json",
            "private_diagnostics": {
                "stack": "Traceback: internal failure",
                "internal_path": "D:/private/source/file.py",
            },
        },
    )
    rendered = json.dumps(response.json(), sort_keys=True).lower()

    assert response.json()["status"] == "success"
    assert '"private_diagnostics":' not in rendered
    assert "traceback" not in rendered
    assert "d:/private" not in rendered


def test_not_found_diagnostics_are_controlled_and_non_private() -> None:
    payload = _client().get("/api/v1/entities/missing").json()
    rendered = json.dumps(payload, sort_keys=True).lower()

    assert payload["status"] == "error"
    assert "traceback" not in rendered
    assert "internal_path" not in rendered
    assert "d:\\" not in rendered
    assert "site-packages" not in rendered
