from __future__ import annotations

import json
from pathlib import Path

from experiments.semirisk_validation.run_validation import DEFAULT_CONFIG, main


def test_validation_runner_writes_all_outputs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_validation.py",
            "--config",
            str(DEFAULT_CONFIG),
            "--output-dir",
            str(tmp_path),
            "--seed",
            "123",
        ],
    )

    assert main() == 0

    expected = {
        "risk_method_comparison",
        "hhi_sensitivity",
        "loss_mode_comparison",
        "propagation_mode_comparison",
        "optimizer_context_consistency",
        "ablation_study",
        "manifest",
    }
    for name in expected:
        assert (tmp_path / f"{name}.json").exists()
        assert (tmp_path / f"{name}.csv").exists()

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["seed"] == 123
    assert manifest["graph_version"].startswith("semirisk_kg_v0_1_")
    assert manifest["source_manifest_id"].startswith("semirisk_fixture_manifest_")
    assert manifest["feature_version"] == "semirisk_risk_score_likelihood_impact_v0.1"
    assert manifest["simulation_version"] == "semirisk_forward_mc_v0.1"
    assert manifest["optimization_version"] == "semirisk_intervention_optimizer_v0.1"
    assert "raw_payload" not in (tmp_path / "risk_method_comparison.json").read_text(encoding="utf-8")
