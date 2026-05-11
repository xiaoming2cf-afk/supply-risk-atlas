# Long-Run Architecture Hardening Log

This log records gate-by-gate evidence for the architecture hardening sequence. It is source-bound and must not claim production readiness.

## Preflight and Reconciliation

- Gate name: Preflight and reconciliation
- Current reconciled HEAD: `4374ff0072ca3cc320c7e395e627cb4e9baa465a`
- Previous local HEAD before reconciliation: `fcd1389f4088b616e0eeb96765228e945331cc4f`
- Safety branch: `safety/pre-hardening-20260511-140440`
- Preserved stash: `stash@{0}` (`pre-hardening dirty workspace 20260511-140440`)
- Files changed: this log only
- Commands run:
  - `git branch safety/pre-hardening-20260511-140440 HEAD`
  - `git stash push --include-untracked -m "pre-hardening dirty workspace 20260511-140440"`
  - `git fetch origin`
  - `git merge --ff-only origin/main`
  - `git rev-parse HEAD`
  - `git status --short`
- Pass/fail: pass
- Evidence:
  - Local `main` fast-forwarded from `fcd1389f4088b616e0eeb96765228e945331cc4f` to `4374ff0072ca3cc320c7e395e627cb4e9baa465a`.
  - Working tree was clean immediately after reconciliation.
- Unresolved limitations:
  - The preserved stash has not been reapplied; it is available only for targeted recovery if a later gate needs unique local work.
  - Platform remains fixture/proxy based and not production ready.
- Next gate decision: run required baseline commands before Gate 1 refactoring.

## Baseline

- Gate name: Baseline verification before refactors
- Current HEAD: `4374ff0072ca3cc320c7e395e627cb4e9baa465a`
- Files changed: `docs/roadmap/long-run-architecture-hardening-log.md`
- Commands run:
  - `python -m pytest -q`
  - `npm --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run build`
  - `npm.cmd run smoke:web`
  - `python -c "from services.api.dev_server import run; run(port=8010)"`
  - `set SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8010&& npm.cmd --workspace apps/web run dev -- --hostname 127.0.0.1 --port 3000`
  - `SUPPLY_RISK_WEB_URL=http://127.0.0.1:3000 SUPPLY_RISK_API_URL=http://127.0.0.1:3000/api/v1 npm.cmd run smoke:web`
- Pass/fail: pass with documented environment caveats
- Evidence:
  - `python -m pytest -q`: passed, 213 tests.
  - `npm --workspace apps/web run typecheck`: failed before running TypeScript because PowerShell execution policy blocks `npm.ps1`.
  - `npm.cmd --workspace apps/web run typecheck`: passed.
  - `npm.cmd --workspace apps/web run build`: passed; Next.js build completed successfully.
  - Initial `npm.cmd run smoke:web`: failed with `ECONNREFUSED 127.0.0.1:3000` because no local web server was running.
  - Local API dev server was started on `127.0.0.1:8010`.
  - Local Next dev server was started on `127.0.0.1:3000` with `SUPPLY_RISK_API_ORIGIN=http://127.0.0.1:8010`.
  - Rerun smoke passed: `Browser smoke passed: 22 checks. Report: D:\系统\supply-risk-atlas\artifacts\browser-smoke\report.json`.
- Unresolved limitations:
  - Browser smoke depends on a running local web server; the script does not start one by itself.
  - Platform remains fixture/proxy based and not production ready.
  - `apps/web/AGENTS.md` and `apps/web/CLAUDE.md` remain pre-existing untracked files and are not part of this gate.
- Next gate decision: proceed to Gate 1 backend route architecture split.

## Gate 1 - Backend Route Architecture Split

- Gate name: Gate 1 backend route architecture split
- Current HEAD before commit: `febe25c0bc49412badbbedce9a9b707d397b6f2a`
- Files changed:
  - `services/api/main.py`
  - `services/api/routes/__init__.py`
  - `services/api/routes/system_health.py`
  - `services/api/routes/graph.py`
  - `services/api/routes/risk.py`
  - `services/api/routes/scenarios.py`
  - `services/api/routes/reverse_stress.py`
  - `services/api/routes/optimization.py`
  - `services/api/routes/reports.py`
  - `services/api/runtime/__init__.py`
  - `services/api/runtime/envelope.py`
  - `services/api/runtime/errors.py`
  - `services/api/runtime/cache.py`
  - `services/api/security/__init__.py`
  - `services/api/security/validation.py`
  - `services/api/security/headers.py`
  - `tests/api/test_route_architecture_split.py`
  - `docs/roadmap/long-run-architecture-hardening-log.md`
- Commands run:
  - `python -m pytest tests/api/test_route_architecture_split.py tests/api/test_api_endpoints.py tests/api/test_api_routes.py tests/api/test_scenario_forward.py tests/api/test_scenario_reverse.py tests/api/test_optimization_routes.py tests/api/test_report_export.py tests/api/test_semirisk_risk_score.py tests/api/test_system_health_semiconductor_graph.py -q`
  - `python -m pytest -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run build`
- Pass/fail: pass
- Evidence:
  - Targeted API route suite passed.
  - Full pytest passed, 217 tests.
  - Web typecheck passed.
  - Web build passed.
  - `main.py` remains import-compatible for `route_system_health_center`, graph snapshot/neighborhood, risk, forward, reverse, optimization, and investigation report route functions.
  - Public FastAPI URLs remain registered through route modules.
  - Snapshot cache is keyed by graph version and as-of time.
  - Bounded run cache stores sanitized summaries only; raw payload and secret-like keys are dropped.
- Unresolved limitations:
  - Route handler implementation bodies still live in `services/api/main.py`; this gate moves public HTTP registration and runtime helpers first while keeping the compatibility facade stable.
  - Gate 2 will expand validation/security behavior beyond the initial placeholder security helpers.
  - Platform remains fixture/proxy based and not production ready.
- Next gate decision: proceed to Gate 2 API input validation and security boundary.

## Gate 2 - API Input Validation and Security Boundary

- Gate name: Gate 2 API input validation and security boundary
- Current HEAD before commit: `e746de33fec84fb09024c011687dda9c71028380`
- Files changed:
  - `services/api/main.py`
  - `services/api/security/validation.py`
  - `services/api/security/headers.py`
  - `tests/security/test_input_validation.py`
  - `tests/security/test_response_sanitization.py`
  - `tests/security/test_security_headers.py`
  - `docs/roadmap/long-run-architecture-hardening-log.md`
- Commands run:
  - `python -m pytest tests/security -q`
  - `python -m pytest tests/api/test_scenario_forward.py tests/api/test_scenario_reverse.py tests/api/test_optimization_routes.py tests/api/test_report_export.py tests/api/test_route_architecture_split.py tests/security -q`
  - `python -m pytest -q`
  - `npm.cmd --workspace apps/web run typecheck`
  - `npm.cmd --workspace apps/web run build`
- Pass/fail: pass
- Evidence:
  - New security tests passed.
  - Affected API and security suites passed.
  - Full pytest passed, 227 tests.
  - Web typecheck passed.
  - Web build passed.
  - Request size guard returns controlled `request_too_large` envelopes.
  - Forward, reverse, optimization, and report routes reject bounded unsafe inputs with controlled envelopes.
  - Security headers are present on API responses.
  - Production CORS default is not wildcard; configured origins are read from `SUPPLY_RISK_CORS_ORIGINS`.
  - Report export sanitizer drops raw/private payload fields while preserving safe exclusion evidence flags.
- Unresolved limitations:
  - Request-size middleware uses `content-length`; streaming chunked request hardening is not implemented.
  - Dev-mode CORS remains wildcard by default for local development.
  - Platform remains fixture/proxy based and not production ready.
- Next gate decision: proceed to Gate 3 frontend feature-module split.
