# SemiRisk Fixture Validation Experiments

This directory contains deterministic validation experiments for the fixture-based SemiRisk model. The outputs are paper-support tables for internal consistency, sensitivity, and ablation analysis. They are not calibrated production results and are not financial loss estimates.

## Run

```powershell
python experiments/semirisk_validation/run_validation.py
```

Optional arguments:

- `--config`: path to a JSON-compatible YAML config. Default: `experiments/semirisk_validation/configs/base.yaml`.
- `--output-dir`: output directory. Default: `experiments/semirisk_validation/outputs`.
- `--seed`: override the config seed.

The runner writes paired `.json` and `.csv` files for each experiment plus a manifest containing git commit, graph/source versions, model/simulation/optimization versions, seed, and config hash.

## Outputs

- `risk_method_comparison`
- `hhi_sensitivity`
- `loss_mode_comparison`
- `propagation_mode_comparison`
- `optimizer_context_consistency`
- `ablation_study`
- `manifest`

All outputs are fixture-labeled and include no raw source payloads or private diagnostics.
