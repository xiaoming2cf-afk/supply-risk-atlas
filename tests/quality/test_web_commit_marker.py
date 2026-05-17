from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAYOUT_PATH = ROOT / "apps" / "web" / "src" / "app" / "layout.tsx"


def test_web_layout_exposes_static_commit_metadata() -> None:
    source = LAYOUT_PATH.read_text(encoding="utf-8")

    assert "NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT" in source
    assert "NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME" in source
    assert '"supply-risk-web-commit"' in source
    assert '"supply-risk-web-build-time"' in source
