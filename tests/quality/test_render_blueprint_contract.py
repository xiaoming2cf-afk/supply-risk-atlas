from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
RENDER_PATH = ROOT / "render.yaml"
API_SERVICE = "supply-risk-atlas-api"
WEB_SERVICE = "supply-risk-atlas-web"
FIXTURE_GRAPH_MODE = "semirisk_fixture_v0.1"
SECRET_LIKE_ENV_RE = re.compile(
    r"(SECRET|TOKEN|PASSWORD|PRIVATE|CREDENTIAL|API_KEY|ACCESS_KEY|AUTH)",
    re.IGNORECASE,
)
SECRET_LIKE_VALUE_RE = re.compile(
    r"(-----BEGIN|sk-[a-z0-9]{20,}|ghp_[a-z0-9]{20,}|render_api_key)",
    re.IGNORECASE,
)


@pytest.fixture
def render_blueprint() -> dict[str, Any]:
    return yaml.safe_load(RENDER_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def services_by_name(render_blueprint: dict[str, Any]) -> dict[str, dict[str, Any]]:
    services = render_blueprint.get("services")
    assert isinstance(services, list)
    return {service["name"]: service for service in services}


def test_render_blueprint_declares_expected_api_and_web_services(
    services_by_name: dict[str, dict[str, Any]],
) -> None:
    assert set(services_by_name) == {API_SERVICE, WEB_SERVICE}

    api = services_by_name[API_SERVICE]
    web = services_by_name[WEB_SERVICE]
    assert api["type"] == "web"
    assert api["runtime"] == "python"
    assert api["healthCheckPath"] == "/api/v1/health"
    assert api["autoDeploy"] is True

    assert web["type"] == "web"
    assert web["runtime"] == "node"
    assert web["healthCheckPath"] == "/"
    assert web["autoDeploy"] is True


def test_render_blueprint_keeps_fixture_mode_and_no_live_fetch(
    services_by_name: dict[str, dict[str, Any]],
) -> None:
    for service_name in (API_SERVICE, WEB_SERVICE):
        env = _env_by_key(services_by_name[service_name])
        assert env["SUPPLY_RISK_DATA_MODE"]["value"] == "fixture"
        assert env["SUPPLY_RISK_FIXTURE_GRAPH_MODE"]["value"] == FIXTURE_GRAPH_MODE

        env_payload = json.dumps(services_by_name[service_name].get("envVars", []), sort_keys=True)
        assert "live_fetch" not in env_payload.lower()
        assert "live-fetch" not in env_payload.lower()
        for entry in services_by_name[service_name].get("envVars", []):
            value = str(entry.get("value", "")).lower()
            assert value != "live"


def test_render_blueprint_links_api_and_web_urls(
    services_by_name: dict[str, dict[str, Any]],
) -> None:
    api_env = _env_by_key(services_by_name[API_SERVICE])
    web_env = _env_by_key(services_by_name[WEB_SERVICE])

    web_origin = f"https://{WEB_SERVICE}.onrender.com"
    api_origin = f"https://{API_SERVICE}.onrender.com"
    assert api_env["SUPPLY_RISK_DEPLOY_TARGET"]["value"] == f"{WEB_SERVICE}.onrender.com"
    assert api_env["SUPPLY_RISK_CORS_ORIGINS"]["value"] == web_origin

    assert web_env["SUPPLY_RISK_DEPLOY_TARGET"]["value"] == f"{WEB_SERVICE}.onrender.com"
    assert web_env["SUPPLY_RISK_API_ORIGIN"]["value"] == api_origin
    assert web_env["NEXT_PUBLIC_SUPPLY_RISK_API_URL"]["value"] == f"{api_origin}/api/v1"
    assert urlparse(web_env["NEXT_PUBLIC_SUPPLY_RISK_API_URL"]["value"]).netloc == (
        f"{API_SERVICE}.onrender.com"
    )
    assert web_env["SUPPLY_RISK_API_HOSTPORT"]["fromService"] == {
        "type": "web",
        "name": API_SERVICE,
        "property": "hostport",
    }


def test_render_blueprint_build_filters_exclude_runtime_data(
    services_by_name: dict[str, dict[str, Any]],
) -> None:
    assert "data/runtime" not in RENDER_PATH.read_text(encoding="utf-8").replace("\\", "/")
    for service_name in (API_SERVICE, WEB_SERVICE):
        paths = services_by_name[service_name].get("buildFilter", {}).get("paths")
        assert isinstance(paths, list)
        assert paths
        for path in paths:
            normalized = str(path).replace("\\", "/")
            assert not normalized.startswith("data/runtime")
            assert "/data/runtime" not in normalized


def test_render_blueprint_env_vars_do_not_embed_secret_like_values(
    services_by_name: dict[str, dict[str, Any]],
) -> None:
    for service_name in (API_SERVICE, WEB_SERVICE):
        for entry in services_by_name[service_name].get("envVars", []):
            key = entry["key"]
            assert not SECRET_LIKE_ENV_RE.search(key)
            assert entry.keys() <= {"key", "value", "fromService"}
            assert "sync" not in entry
            if "value" in entry:
                assert not SECRET_LIKE_VALUE_RE.search(str(entry["value"]))


def _env_by_key(service: dict[str, Any]) -> dict[str, dict[str, Any]]:
    env_entries = service.get("envVars")
    assert isinstance(env_entries, list)
    env_by_key = {entry["key"]: entry for entry in env_entries}
    assert len(env_by_key) == len(env_entries)
    return env_by_key
