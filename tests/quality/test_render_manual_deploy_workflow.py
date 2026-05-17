from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "render-manual-deploy.yml"
SECRET_DOC_PATH = ROOT / "docs" / "roadmap" / "render-deploy-secret-requirements.md"


def test_render_deploy_workflow_is_manual_only() -> None:
    source = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in source
    assert "push:" not in source
    assert "pull_request:" not in source
    assert "schedule:" not in source
    assert "ref: ${{ env.EXPECTED_COMMIT }}" not in source


def test_render_deploy_workflow_uses_secret_gated_api_path() -> None:
    source = WORKFLOW_PATH.read_text(encoding="utf-8")

    for secret_name in ["RENDER_API_KEY", "RENDER_API_SERVICE_ID", "RENDER_WEB_SERVICE_ID"]:
        assert f"secrets.{secret_name}" in source

    assert "POST" in source
    assert "https://api.render.com/v1/services/${service_id}/deploys" in source
    assert '"commitId": os.environ["EXPECTED_COMMIT"]' in source
    assert '"clearCache": os.environ["CLEAR_CACHE"]' in source
    assert "scripts/check-deployed-version.py" in source
    assert "cat ${response_file}" not in source
    assert "cat \"${response_file}\"" not in source
    assert "upload-artifact" not in source


def test_render_secret_requirements_doc_is_actionable_without_values() -> None:
    source = SECRET_DOC_PATH.read_text(encoding="utf-8")

    for secret_name in ["RENDER_API_KEY", "RENDER_API_SERVICE_ID", "RENDER_WEB_SERVICE_ID"]:
        assert secret_name in source

    assert "render_deploy_blocked_missing_safe_deploy_path" in source
    assert "Do not paste this value" in source
    assert "rnd_" not in source
