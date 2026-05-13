from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from sra_core.geo.terminology import CANONICAL_DISPLAY, CANONICAL_REGION_ID
from services.api.main import create_app


TEXT_EXTENSIONS = {
    ".csv",
    ".json",
    ".js",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

ALLOWLISTED_INTERNAL_ALIAS_FILES = {
    Path("packages/sra_core/sra_core/geo/terminology.py"),
    Path("packages/sra_core/sra_core/entity_resolution/country_codes.py"),
    Path("packages/sra_core/sra_core/entity_resolution/company_aliases.py"),
    Path("packages/sra_core/sra_core/ingestion/bulk_public.py"),
    Path("tests/geo/test_geography_terminology.py"),
    Path("tests/quality/test_no_forbidden_geography_labels.py"),
}


def _legacy_latin() -> str:
    return "Tai" + "wan"


def _legacy_chinese() -> str:
    return "".join(chr(code) for code in (0x53F0, 0x6E7E))


def _forbidden_patterns() -> list[re.Pattern[str]]:
    latin = _legacy_latin()
    return [
        re.compile(r"\bcountry:(?:tw|" + latin + r")\b", re.IGNORECASE),
        re.compile(r"\bregion:(?:tw|" + latin + r")\b", re.IGNORECASE),
        re.compile(r"\bcountry_tw\b", re.IGNORECASE),
        re.compile(r"\bregion_tw\b", re.IGNORECASE),
        re.compile(r"\bprovince_cn_tw\b", re.IGNORECASE),
        re.compile(r"(?<!china_)\b" + latin + r"\b", re.IGNORECASE),
        re.compile(r"(?<!中国)" + _legacy_chinese()),
        re.compile("中国台湾省"),
    ]


def _tracked_text_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], text=True)
    files: list[Path] = []
    for line in output.splitlines():
        path = Path(line)
        if path in ALLOWLISTED_INTERNAL_ALIAS_FILES:
            continue
        if any(part in {"__pycache__", "node_modules", ".next", "dist", "build"} for part in path.parts):
            continue
        if path.suffix in TEXT_EXTENSIONS and path.exists():
            files.append(path)
    return files


def _assert_no_forbidden(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    offenders = [pattern.pattern for pattern in _forbidden_patterns() if pattern.search(text)]
    assert offenders == []


def test_tracked_user_visible_files_do_not_contain_forbidden_geo_labels() -> None:
    offenders: list[str] = []
    for path in _tracked_text_files():
        text = path.read_text(encoding="utf-8")
        for pattern in _forbidden_patterns():
            if pattern.search(text):
                offenders.append(f"{path}: {pattern.pattern}")
                break

    assert offenders == []


def test_core_api_outputs_normalize_geography_labels() -> None:
    client = TestClient(create_app())
    paths = [
        "/api/v1/graph/snapshot",
        "/api/v1/graph/view",
        "/api/v1/analytics/charts",
        "/api/v1/analytics/tables/evidence-refs",
    ]

    for path in paths:
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        _assert_no_forbidden(payload)

    graph_payload = client.get("/api/v1/graph/snapshot").json()
    rendered = json.dumps(graph_payload, ensure_ascii=False)
    assert CANONICAL_REGION_ID in rendered
    assert CANONICAL_DISPLAY in rendered


def test_report_exports_normalize_geography_labels() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/reports/investigation",
        json={"entity_id": "company:tsmc", "format": "json"},
    )

    assert response.status_code == 200
    payload = response.json()
    _assert_no_forbidden(payload)


def test_region_node_is_not_exposed_as_independent_country() -> None:
    client = TestClient(create_app())
    payload = client.get("/api/v1/graph/snapshot").json()
    nodes = payload["data"]["nodes"]
    region_nodes = [node for node in nodes if node["node_id"] == CANONICAL_REGION_ID]

    assert region_nodes
    assert all(node["node_type"] == "region" for node in region_nodes)
    for node in region_nodes:
        attributes = node.get("attributes", {})
        assert attributes.get("country_id") == "country:CN"
        assert attributes.get("country_display") == "中国"
