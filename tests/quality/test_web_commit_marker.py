from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAYOUT_PATH = ROOT / "apps" / "web" / "src" / "app" / "layout.tsx"
NEXT_CONFIG_PATH = ROOT / "apps" / "web" / "next.config.mjs"


def test_web_layout_exposes_static_commit_metadata() -> None:
    source = LAYOUT_PATH.read_text(encoding="utf-8")

    assert "NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT" in source
    assert "NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME" in source
    assert '"supply-risk-web-commit"' in source
    assert '"supply-risk-web-build-time"' in source


def test_render_git_commit_takes_priority_over_stale_public_env_override() -> None:
    source = NEXT_CONFIG_PATH.read_text(encoding="utf-8")

    render_index = source.index("process.env.RENDER_GIT_COMMIT")
    public_index = source.index("process.env.NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT")

    assert render_index < public_index
