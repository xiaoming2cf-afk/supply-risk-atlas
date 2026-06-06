from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / ".github" / "workflows"


def _workflow_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(WORKFLOW_DIR.glob("*.yml"))
    )


def test_github_owned_actions_use_node24_ready_major_versions() -> None:
    source = _workflow_text()

    assert "actions/checkout@v5" in source
    assert "actions/setup-node@v5" in source
    assert "actions/setup-python@v5" in source
    assert "actions/upload-artifact@v6" in source

    assert "actions/checkout@v4" not in source
    assert "actions/setup-node@v4" not in source
    assert "actions/upload-artifact@v4" not in source

