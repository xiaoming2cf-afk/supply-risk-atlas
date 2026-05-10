# Overnight Implementation Log

This log tracks the gated implementation sequence for the semiconductor platform workflow. Fixture graph data is test/promoted data only and remains labeled with `fixture_graph:not_production_ready`.

## Gate 0 - Audit And Failure Reproduction

- Files changed: `docs/roadmap/overnight-implementation-log.md`
- Commands run:
  - `git status --short --branch`
  - `git rev-parse HEAD`
  - `git rev-parse origin/main`
  - file inspection of runtime routing, smoke, CI, Render, and quality-gate docs
- Result: Pass for audit. The actual checkout starts at `4fd9c83a631218ff348edbd5e4b776706681a4d7`, matching `origin/main`. Untracked `apps/web/AGENTS.md` and `apps/web/CLAUDE.md` are present and intentionally untouched.
- Findings:
  - CI real-mode smoke is configured with `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1` and `SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8000`.
  - `scripts/browser-smoke.mjs` already probes System Health, graph snapshot, graph neighborhood, Entity Risk, and risk portfolio before deciding whether degraded UI states are acceptable.
  - `apps/web/src/env.d.ts` lacked declarations for server-side proxy env vars.
  - `docs/quality-gates.md` still described CI mock-mode smoke even though `.github/workflows/ci.yml` runs real-mode smoke only.
  - `render.yaml` still ran online bulk ingestion during API build, which conflicts with the lightweight fixture-first deployment gate.
- Known limitations: Render deployment history cannot be inspected from this environment without Render credentials.
- Next gate decision: Proceed to Gate 1 runtime stabilization after aligning env typings, docs, and Render build behavior.

## Gate 1 - Runtime Stabilization

- Files changed:
  - `apps/web/src/env.d.ts`
  - `README.md`
  - `render.yaml`
  - `docs/quality-gates.md`
  - `docs/deployment/render.md`
  - `docs/roadmap/overnight-implementation-log.md`
- Commands run: pending.
- Commands run:
  - `python -m pytest tests/model tests/api tests/graph_invariants -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run typecheck:packages`
  - `npm.cmd --workspace apps/web run build`
  - local direct smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
  - local proxy smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
- Result: Pass. Python targeted tests passed `75 passed`; typecheck, package typecheck, build, direct smoke, and proxy smoke passed. Browser smoke reported `19 checks`.
- Evidence:
  - System Health smoke excerpt includes `SemiRisk-KG v0.1 fixture graph`, `registryReady: true`, `ontologyReady: true`, `fixtureGraph: true`, `graphVersion: semirisk_kg_v0_1_20260501T000000Z_6ed40afa3b7a`, `sourceManifestId: semirisk_fixture_manifest_f8fa1615a0a7`, `nodeCount: 30`, and `edgeCount: 45`.
  - Entity Risk 360 smoke excerpt includes `company:tsmc`, `58.33`, `elevated`, `semirisk_risk_score_v0.1`, `graph_version`, `source_manifest_id`, and `fixture_graph:not_production_ready`.
- Known limitations: Existing unrelated local processes occupied ports 8000 and 3000 during validation. Gate 1 smoke used API port 8010 and restarted the local Next dev server on port 3000 with explicit API env.
- Next gate decision: Proceed to Gate 2.

## Gate 2 - Forward Monte Carlo Stress Slice

- Files changed:
  - `ml/simulation/scenario_schema.py`
  - `ml/simulation/metrics.py`
  - `ml/simulation/propagation.py`
  - `ml/simulation/monte_carlo.py`
  - `services/api/main.py`
  - `services/api/dev_server.py`
  - `tests/simulation/test_propagation.py`
  - `tests/simulation/test_monte_carlo.py`
  - `tests/api/test_scenario_forward.py`
  - `docs/model/forward-stress-testing.md`
- Commands run:
  - `python -m pytest tests/simulation tests/api/test_scenario_forward.py -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run typecheck:packages`
  - `npm.cmd --workspace apps/web run build`
- Result: Pass. Simulation and forward scenario API tests passed `10 passed`. Web typecheck, package typecheck, and build passed.
- Evidence: `POST /api/v1/scenarios/forward` returns a success envelope with `run_id`, `seed`, `graph_version`, `source_manifest_id`, `simulation_version: semirisk_forward_mc_v0.1`, percentile losses, `cvar_95`, affected nodes, transmission paths, warnings, assumptions, and evidence refs.
- Known limitations: The engine uses the SemiRisk fixture graph only and reports normalized loss scores, not dollar losses.
- Next gate decision: Proceed to Gate 3.

## Gate 3 - Shock Simulator v2 Frontend

- Files changed:
  - `apps/web/src/app/pages.tsx`
  - `packages/shared-types/src/index.ts`
  - `packages/api-client/src/dashboard.ts`
  - `scripts/browser-smoke.mjs`
- Commands run:
  - local direct smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
  - local proxy smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
- Result: Pass. Browser smoke passed `20 checks` after making literal run-manifest field names visible in the Shock Simulator result panel.
- Evidence: Smoke covers `#shock-simulator`, clicks `Run forward stress`, and verifies `expected_loss`, `p50_loss`, `p90_loss`, `p95_loss`, `cvar_95`, `time_to_recover_days`, `time_to_survive_days`, `run_id`, `seed`, `graph_version`, `source_manifest_id`, `simulation_version`, and `semirisk_forward_mc_v0.1`.
- Known limitations: The page does not auto-run Monte Carlo on load by design.
- Next gate decision: Proceed to Gate 4.

## Gate 4 - Reverse Stress Testing v1

- Files changed:
  - `ml/simulation/shock_candidates.py`
  - `ml/simulation/plausibility.py`
  - `ml/simulation/reverse_stress.py`
  - `ml/simulation/scenario_schema.py`
  - `services/api/main.py`
  - `services/api/dev_server.py`
  - `tests/simulation/test_reverse_stress.py`
  - `tests/api/test_scenario_reverse.py`
  - `docs/model/reverse-stress-testing.md`
- Commands run:
  - `python -m pytest tests/simulation/test_reverse_stress.py tests/api/test_scenario_reverse.py -q`
- Result: Pass. Reverse stress unit and API tests passed `8 passed`.
- Evidence: `POST /api/v1/scenarios/reverse` returns `run_id`, `seed`, `graph_version`, `source_manifest_id`, `simulation_version: semirisk_reverse_stress_v0.1`, `ranked_shock_sets`, `baseline_comparison`, `plausibility_cost`, affected paths, warnings, assumptions, and evidence refs.
- Known limitations: Candidate shocks are fixture graph candidates only.
- Next gate decision: Proceed to Gate 5.

## Gate 5 - Reverse Stress Lab Frontend

- Files changed:
  - `packages/shared-types/src/index.ts`
  - `packages/api-client/src/dashboard.ts`
  - `apps/web/src/app/App.tsx`
  - `apps/web/src/app/pages.tsx`
  - `scripts/browser-smoke.mjs`
- Commands run: pending.
- Commands run:
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run typecheck:packages`
  - `npm.cmd --workspace apps/web run build`
  - local direct smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
  - local proxy smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
- Result: Pass. Typecheck, package typecheck, build, direct smoke, and proxy smoke passed. Browser smoke reported `22 checks`.
- Evidence: Smoke covers `#reverse-stress-lab`, clicks `Run reverse stress`, and verifies `ranked_shock_sets`, `threshold_met`, `expected_loss`, `cvar95`, `plausibility_cost`, `baseline_comparison`, `run_id`, `graph_version`, `source_manifest_id`, and `semirisk_reverse_stress_v0.1`.
- Known limitations: Reverse Stress Lab evaluates fixture graph candidates only and runs synchronously within bounded iteration limits.
- Next gate decision: Proceed to Gate 6.

## Gate 6 - Intervention Optimizer v1

- Files changed:
  - `ml/optimization/__init__.py`
  - `ml/optimization/interventions.py`
  - `ml/optimization/objectives.py`
  - `ml/optimization/baselines.py`
  - `ml/optimization/constraints.py`
  - `services/api/main.py`
  - `services/api/dev_server.py`
  - `tests/optimization/test_interventions.py`
  - `tests/optimization/test_optimization_baselines.py`
  - `tests/api/test_optimization_routes.py`
  - `docs/model/intervention-optimization.md`
- Commands run:
  - `python -m pytest tests/optimization tests/api/test_optimization_routes.py -q`
- Result: Pass. Optimizer unit and API tests passed `7 passed`.
- Evidence: `POST /api/v1/optimization/interventions` returns budget-feasible `recommended_actions`, before/after expected loss and CVaR95, cost, ROI, baselines, assumptions, constraints, evidence refs, warnings, and run manifest.
- Known limitations: Effects are deterministic normalized fixture estimates, not financial savings.
- Next gate decision: Proceed to Gate 7.

## Gate 7 - Intervention Optimizer Frontend

- Files changed:
  - `packages/shared-types/src/index.ts`
  - `packages/api-client/src/dashboard.ts`
  - `apps/web/src/app/App.tsx`
  - `apps/web/src/app/i18n.tsx`
  - `apps/web/src/app/pages.tsx`
  - `scripts/browser-smoke.mjs`
- Commands run: pending.
- Commands run:
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run typecheck:packages`
  - `npm.cmd --workspace apps/web run build`
  - local direct smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
  - local proxy smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `NEXT_PUBLIC_SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
- Result: Pass. Typecheck, package typecheck, build, direct smoke, and proxy smoke passed. Browser smoke reported `24 checks`.
- Evidence: Smoke covers `#intervention-optimizer`, clicks `Run optimizer`, and verifies `recommended_actions`, before/after expected loss and CVaR95, cost, ROI, baselines, run ID, graph version, source manifest, and optimizer version.
- Known limitations: Optimizer is a deterministic greedy fixture baseline; action effects are normalized planning estimates.
- Next gate decision: Proceed to Gate 8.

## Gate 8 - Investigation Report Export v1

- Files changed:
  - `packages/sra_core/sra_core/reports/__init__.py`
  - `packages/sra_core/sra_core/reports/investigation.py`
  - `services/api/main.py`
  - `services/api/dev_server.py`
  - `packages/shared-types/src/index.ts`
  - `packages/api-client/src/index.ts`
  - `packages/api-client/src/dashboard.ts`
  - `apps/web/src/app/App.tsx`
  - `apps/web/src/app/i18n.tsx`
  - `apps/web/src/app/pages.tsx`
  - `scripts/browser-smoke.mjs`
  - `tests/reports/test_investigation_report.py`
  - `tests/api/test_report_export.py`
  - `docs/model/investigation-report-export.md`
- Commands run:
  - `python -m pytest tests/reports tests/api/test_report_export.py -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run typecheck:packages`
  - `npm.cmd --workspace apps/web run build`
  - local direct smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
  - local proxy smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
- Result: Pass. Report API and model tests passed `5 passed`; typecheck, package typecheck, build, direct smoke, and proxy smoke passed. Browser smoke reported `26 checks`.
- Evidence: `POST /api/v1/reports/investigation` returns `report_id`, `report_version: semirisk_investigation_report_v0.1`, version metadata, evidence summary, graph context, warnings, limitations, `raw_payload_excluded: true`, and `private_diagnostics_excluded: true`. Smoke covers `#investigation-report`, clicks `Generate JSON report`, and verifies the report metadata plus exclusion flags.
- Known limitations: Reports are generated synchronously and returned directly; persistent report storage is deferred.
- Next gate decision: Defer Gate 9 prediction cleanup unless final stability checks reveal a narrow required fix; proceed to Gate 10 documentation and final acceptance checks.

## Gate 9 - Prediction Center v1 Baseline Cleanup

- Files changed: none.
- Commands run: `Get-ChildItem tests -Directory`
- Result: Deferred. Earlier gates are stable and the checkout does not contain `tests/prediction`; no prediction cleanup was required to pass the runtime or workflow gates.
- Known limitations: The existing Prediction Center remains the pre-existing public workflow and is not upgraded to a new market/event pressure baseline in this overnight pass.
- Next gate decision: Proceed to Gate 10 final CI, smoke, docs, and acceptance.

## Gate 10 - Final CI, Smoke, Docs, Acceptance

- Files changed:
  - `README.md`
  - `docs/deployment/render.md`
  - `docs/quality-gates.md`
  - `tests/e2e/supply-risk-atlas.feature`
  - `docs/roadmap/overnight-implementation-log.md`
- Commands run:
  - `python -m pytest tests/contract tests/ingestion tests/graph_invariants tests/model tests/simulation tests/optimization tests/api tests/reports -q`
  - `python -m pytest -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run typecheck:packages`
  - `npm.cmd --workspace apps/web run build`
  - local direct smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_API_URL=http://127.0.0.1:8010/api/v1`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
  - local proxy smoke with `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000`, `SUPPLY_RISK_EXPECT_MODE=real`, `npm.cmd run smoke:web`
- Result: Pass. Targeted Python suite passed; full pytest passed; typecheck, package typecheck, build, direct smoke, and proxy smoke passed. Browser smoke reported `26 checks`.
- Final acceptance evidence:
  - System Health local smoke shows `SemiRisk-KG v0.1 fixture graph`, `graphVersion: semirisk_kg_v0_1_20260501T000000Z_6ed40afa3b7a`, `sourceManifestId: semirisk_fixture_manifest_f8fa1615a0a7`, `nodeCount: 30`, `edgeCount: 45`, `registryReady: true`, `ontologyReady: true`, and `fixture_graph:not_production_ready`.
  - Entity Risk 360 local smoke shows `company:tsmc`, `58.33`, `elevated`, all six Risk Score v0 components, `semirisk_risk_score_v0.1`, `graph_version`, `source_manifest_id`, and the fixture warning.
  - Forward Monte Carlo example: `scenario_type=earthquake`, `run_id=fwd_9eb2aaddecd930db`, `seed=42`, `expected_loss=30.6632`, `cvar95=30.6632`, `graph_version=semirisk_kg_v0_1_20260501T000000Z_6ed40afa3b7a`, `source_manifest_id=semirisk_fixture_manifest_f8fa1615a0a7`.
  - Reverse Stress example: `run_id=rev_d927b00a66219239`, `ranked_shock_sets_count=4`, `top_shock_set=shockset_ec587a094897623a`, `cvar95=35.9867`, `plausibility_cost=0.5342`.
  - Intervention Optimizer example: `run_id=opt_29d024a91a47dfa0`, `budget=70`, `recommended_actions_count=3`, `before_cvar95=29.5275`, `after_cvar95=17.3625`, `resilience_roi=0.2253`.
  - Investigation Report example: `report_id=report_fa346c5952fa1fab`, JSON generation available, Markdown generation available, `raw_payload_excluded=true`.
- Skipped tests: `tests/prediction` is absent in this checkout, so prediction-specific pytest selection was skipped.
- Known limitations: Render deploy verification is best-effort without Render credentials; remote web may remain stale until these commits are pushed and the Render web service redeploys.
- Next gate decision: Stop. The requested priority gates through report export and final smoke/docs are stable locally.
