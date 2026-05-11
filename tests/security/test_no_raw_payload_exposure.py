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


def test_report_and_run_history_do_not_echo_raw_payload_markers() -> None:
    client = _client()
    marker = "RAW-SOURCE-PAYLOAD-SHOULD-NOT-ECHO"

    response = client.post(
        "/api/v1/reports/investigation",
        json={
            "entity_id": "company:tsmc",
            "format": "json",
            "raw_payload": {"source_record": marker},
            "source_payload": {"record": marker},
        },
    )
    payload = response.json()
    rendered = json.dumps(payload, sort_keys=True)

    assert payload["status"] == "success"
    assert payload["data"]["raw_payload_excluded"] is True
    assert marker not in rendered
    assert '"raw_payload":' not in rendered
    assert '"source_payload":' not in rendered

    runs = client.get("/api/v1/runs").json()
    rendered_runs = json.dumps(runs, sort_keys=True)
    assert marker not in rendered_runs
    assert '"raw_payload":' not in rendered_runs
    assert '"source_payload":' not in rendered_runs
