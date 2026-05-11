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
