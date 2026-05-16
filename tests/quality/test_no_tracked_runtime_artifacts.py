from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "check-no-raw-payloads.py"


def _load_scan_module():
    spec = importlib.util.spec_from_file_location("check_no_raw_payloads", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_tracked_runtime_artifacts_are_blocked() -> None:
    scanner = _load_scan_module()

    failures = scanner._tracked_raw_artifact_failures(
        [
            Path("data/runtime/supply_risk_atlas.db"),
            Path("data/runtime/tmp-debug/gdelt.raw"),
        ],
    )

    assert failures == [
        "data/runtime/supply_risk_atlas.db is a tracked raw/runtime artifact",
        "data/runtime/tmp-debug/gdelt.raw is a tracked raw/runtime artifact",
    ]


def test_tracked_raw_artifact_suffixes_are_blocked_outside_runtime() -> None:
    scanner = _load_scan_module()

    failures = scanner._tracked_raw_artifact_failures(
        [
            Path("reports/debug.sqlite"),
            Path("exports/evidence.parquet"),
            Path("docs/data/public-source-catalog.md"),
        ],
    )

    assert failures == [
        "reports/debug.sqlite is a tracked raw/runtime artifact",
        "exports/evidence.parquet is a tracked raw/runtime artifact",
    ]
