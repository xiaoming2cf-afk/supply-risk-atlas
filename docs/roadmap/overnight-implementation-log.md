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
