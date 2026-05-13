from __future__ import annotations

import json

from graph_kernel.promoted_pipeline import build_promoted_artifacts


def test_promoted_graph_artifacts_do_not_contain_raw_payloads_or_bodies() -> None:
    rendered = json.dumps(build_promoted_artifacts(), sort_keys=True).lower()

    assert "raw_payload" not in rendered
    assert "article_body" not in rendered
    assert "filing_body" not in rendered
    assert "authorization" not in rendered
    assert "api_key" not in rendered

