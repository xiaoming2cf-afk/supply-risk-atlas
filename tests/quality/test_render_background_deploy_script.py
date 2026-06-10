from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "trigger-render-deploy.py"


def _load_deploy_module():
    spec = importlib.util.spec_from_file_location("trigger_render_deploy", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_background_render_deploy_reports_missing_env_without_network(monkeypatch) -> None:
    deploy = _load_deploy_module()

    def forbidden_urlopen(*_args, **_kwargs):
        raise AssertionError("missing env preflight must not call Render")

    monkeypatch.setattr(deploy, "urlopen", forbidden_urlopen)

    report = deploy.trigger_render_deploys(
        commit="b253acf418837b775c7b8310c21e403a33854329",
        clear_cache="clear",
        timeout=1,
        dry_run=False,
        env={},
    )

    assert report["status"] == "render_deploy_blocked_missing_safe_deploy_path"
    assert report["missing_env"] == [
        "RENDER_API_KEY",
        "RENDER_API_SERVICE_ID",
        "RENDER_WEB_SERVICE_ID",
    ]
    assert report["render_api_call_attempted"] is False
    assert report["safe_deploy_path"] is False
    assert report["next_action"] == "set_render_api_key_and_service_ids_outside_chat_then_retry"
    assert report["services"] == []
    assert "retry_hint" in report


def test_background_render_deploy_dry_run_does_not_call_render(monkeypatch) -> None:
    deploy = _load_deploy_module()

    def forbidden_urlopen(*_args, **_kwargs):
        raise AssertionError("dry run must not call Render")

    monkeypatch.setattr(deploy, "urlopen", forbidden_urlopen)

    report = deploy.trigger_render_deploys(
        commit="b253acf418837b775c7b8310c21e403a33854329",
        clear_cache="clear",
        timeout=1,
        dry_run=True,
        env={
            "RENDER_API_KEY": "secret-value-not-output",
            "RENDER_API_SERVICE_ID": "srv-api123",
            "RENDER_WEB_SERVICE_ID": "srv-web123",
        },
    )

    rendered = str(report)
    assert report["status"] == "render_deploy_dry_run"
    assert report["render_api_call_attempted"] is False
    assert report["safe_deploy_path"] is True
    assert report["next_action"] == "rerun_without_dry_run_when_ready"
    assert [row["service"] for row in report["services"]] == [
        "supply-risk-atlas-api",
        "supply-risk-atlas-web",
    ]
    assert "secret-value-not-output" not in rendered
    assert "srv-api123" not in rendered
    assert "srv-web123" not in rendered


def test_background_render_deploy_rejects_invalid_commit_without_network(monkeypatch) -> None:
    deploy = _load_deploy_module()

    def forbidden_urlopen(*_args, **_kwargs):
        raise AssertionError("invalid commit preflight must not call Render")

    monkeypatch.setattr(deploy, "urlopen", forbidden_urlopen)

    report = deploy.trigger_render_deploys(
        commit=deploy.clean_commit("not-a-sha"),
        clear_cache="clear",
        timeout=1,
        dry_run=True,
        env={
            "RENDER_API_KEY": "secret-value-not-output",
            "RENDER_API_SERVICE_ID": "srv-api123",
            "RENDER_WEB_SERVICE_ID": "srv-web123",
        },
    )

    assert report["status"] == "render_deploy_blocked_invalid_commit"
    assert report["render_api_call_attempted"] is False
    assert report["safe_deploy_path"] is False
    assert report["next_action"] == "provide_7_to_40_character_git_sha"
    assert report["services"] == []


def test_background_render_deploy_rejects_invalid_service_id_without_leaking_value(monkeypatch) -> None:
    deploy = _load_deploy_module()

    def forbidden_urlopen(*_args, **_kwargs):
        raise AssertionError("invalid service id preflight must not call Render")

    monkeypatch.setattr(deploy, "urlopen", forbidden_urlopen)

    report = deploy.trigger_render_deploys(
        commit="b253acf418837b775c7b8310c21e403a33854329",
        clear_cache="clear",
        timeout=1,
        dry_run=True,
        env={
            "RENDER_API_KEY": "secret-value-not-output",
            "RENDER_API_SERVICE_ID": "https://private.example/srv-api123",
            "RENDER_WEB_SERVICE_ID": "srv-web123",
        },
    )

    rendered = str(report)
    assert report["status"] == "render_deploy_blocked_invalid_service_id"
    assert report["render_api_call_attempted"] is False
    assert report["safe_deploy_path"] is False
    assert report["next_action"] == "set_valid_render_service_ids_outside_chat_then_retry"
    assert report["services"] == [{"service": "supply-risk-atlas-api", "status": "invalid_service_id"}]
    assert "secret-value-not-output" not in rendered
    assert "https://private.example/srv-api123" not in rendered
    assert "srv-web123" not in rendered


def test_background_render_deploy_sanitizes_http_error(monkeypatch) -> None:
    deploy = _load_deploy_module()

    def failing_urlopen(*_args, **_kwargs):
        raise deploy.HTTPError(
            "https://api.render.com/v1/services/srv-api123/deploys",
            401,
            "Unauthorized private response",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr(deploy, "urlopen", failing_urlopen)

    report = deploy.trigger_render_deploys(
        commit="b253acf418837b775c7b8310c21e403a33854329",
        clear_cache="clear",
        timeout=1,
        dry_run=False,
        env={
            "RENDER_API_KEY": "secret-value-not-output",
            "RENDER_API_SERVICE_ID": "srv-api123",
            "RENDER_WEB_SERVICE_ID": "srv-web123",
        },
    )

    rendered = str(report)
    assert report["status"] == "render_deploy_trigger_failed"
    assert report["render_api_call_attempted"] is True
    assert report["safe_deploy_path"] is True
    assert report["next_action"] == "run_check_deployed_version_after_render_builds_finish"
    assert {row["http_status"] for row in report["services"]} == {401}
    assert "secret-value-not-output" not in rendered
    assert "srv-api123" not in rendered
    assert "srv-web123" not in rendered
    assert "Unauthorized private response" not in rendered
