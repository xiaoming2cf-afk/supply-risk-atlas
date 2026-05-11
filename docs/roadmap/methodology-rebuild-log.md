# Methodology Rebuild Log

## Baseline Preflight

- Baseline source: `origin/main` at `d67942267efb8a6f3d6e33251f7546f8cd62e18c`.
- Baseline worktree: `D:\系统\sra-baseline-d679422` detached at `origin/main`.
- Existing MVP workflows verified before methodology changes:
  - System Health Center
  - Entity Risk 360
  - Shock Simulator
  - Reverse Stress Lab
  - Intervention Optimizer
  - Investigation Report
  - graph snapshot and risk APIs through browser smoke

### Baseline commands

- `python -m pytest -q`: passed.
- `npm.cmd --workspace apps/web run typecheck`: initially failed because the clean baseline worktree had no installed Node binaries (`tsc` not found); after `npm.cmd ci`, passed.
- `npm.cmd --workspace apps/web run build`: initially failed for the same missing dependency reason; after `npm.cmd ci`, passed.
- Local direct API browser smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3020`, `SUPPLY_RISK_API_URL=http://127.0.0.1:8020/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`: passed, 26 checks.

## Methodology Rebuild

- Demoted the old weighted risk score to `semirisk_risk_score_heuristic_v0.1` and `heuristic_weighted_sum_baseline`.
- Added default `semirisk_risk_score_likelihood_impact_v0.1` using likelihood x impact x vulnerability.
- Added OECD-derived operational HHI concentration thresholds on a `0_to_1` scale.
- Added resilience-integral loss as the default forward-stress loss mode while keeping `affected_mean` as a legacy baseline.
- Added multi-source propagation modes and made `auto_semiconductor` the default.
- Added reverse stress threshold normalization and scenario-aware, simulation-based intervention optimization.
- Added report methodology disclosures and formula source documentation.
- Added `tests/quality/test_python_source_readability.py` to reject large minified one-line Python modules.

## Post-change Validation

- `python -m pytest tests/model tests/simulation tests/optimization tests/api tests/reports -q`: passed.
- `python -m pytest -q`: passed.
- `npm.cmd --workspace apps/web run typecheck`: passed.
- `npm.cmd --workspace apps/web run build`: passed.
- Local direct API browser smoke: passed, 26 checks.
- Local proxy browser smoke: passed, 26 checks.
- Plain `npm --workspace ...` is blocked in this PowerShell environment by the local `npm.ps1` execution policy; `npm.cmd` is the equivalent command used for validation.

## Known Limitations

- Current formulas remain fixture/proxy based and report `fixture_proxy_not_calibrated`.
- Outputs are not production decisions and not financial loss estimates.
- No live connectors, new pages, neural/GNN/LSTM/random-forest models, DOJ/FTC HHI bands, or export-control evasion advice were added.
