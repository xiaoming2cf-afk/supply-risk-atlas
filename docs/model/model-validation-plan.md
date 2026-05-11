# SemiRisk Fixture Model Validation Plan

This plan defines deterministic validation experiments for the fixture-based SemiRisk model. The outputs support internal consistency review and later paper writing. They are not calibrated production results, not production decisions, and not financial loss estimates.

## Validation Questions

1. Do the heuristic baseline and likelihood-impact-vulnerability proxy rank fixture nodes differently?
2. How sensitive are concentration labels and significant-dependency flags to OECD-derived operational HHI thresholds and global reference HHI proxies?
3. How do normalized loss outputs change across affected-mean, graph-weighted, demand-fulfillment, capacity-functionality, and resilience-integral loss modes?
4. How do downstream effects change across max, additive-cap, noisy-or, Leontief bottleneck, PSI-recursive, and auto-semiconductor propagation modes?
5. Does the optimizer respond to scenario context rather than returning one fixed default result?
6. Which proxy families drive risk scores under ablation?

## Experiment Runner

Run:

```powershell
python experiments/semirisk_validation/run_validation.py
```

The default config is `experiments/semirisk_validation/configs/base.yaml`. The file is JSON-compatible YAML to avoid adding a runtime YAML dependency. The runner writes paired JSON and CSV tables under `experiments/semirisk_validation/outputs`.

Each run writes a manifest with:

- `git_commit`
- `graph_version`
- `source_manifest_id`
- `feature_version`
- `simulation_version`
- `optimization_version`
- `seed`
- `config_hash`

## Interpretation Limits

- All inputs come from the promoted fixture graph; no live data is fetched.
- HHI bands are OECD-derived operational supply-chain/trade-dependency thresholds, not universal official OECD low/moderate/high labels and not DOJ/FTC antitrust bands.
- Current calibration status is fixture/proxy based.
- Validation outputs must not be used as production decisions, financial loss estimates, or export-control evasion guidance.
