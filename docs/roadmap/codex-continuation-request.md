# Codex Continuation Request

## Current Status

- Latest pushed implementation commit before this handoff: `623adacf823a417a4b0558010e444430d978f08b`.
- Branch: `main`.
- Preserved local files that must not be staged unless the user asks:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
  - `data/runtime/` remains ignored runtime state.
- GitHub Actions for the latest pushed implementation commit passed:
  - `ci`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25968271852`
  - `Quality Gates`: `https://github.com/xiaoming2cf-afk/supply-risk-atlas/actions/runs/25968271843`
- Local validation for the latest implementation commit passed:
  - `python -m pytest tests/quality -q` - 30 passed.
  - `python -m pytest tests/geo tests/contract tests/sources tests/graph_invariants tests/api tests/security tests/model tests/simulation tests/optimization tests/reports -q` - passed.
  - `python -m pytest -q` - passed.
  - `npm.cmd --workspace apps/web run typecheck` - passed.
  - `npm.cmd --workspace apps/web run typecheck:packages` - passed.
  - `npm.cmd --workspace apps/web run build` - passed.
  - `SUPPLY_RISK_API_URL=http://127.0.0.1:8000/api/v1 SUPPLY_RISK_EXPECT_MODE=real npm.cmd run smoke:web` - passed, 65 checks.
- Deployment status remains `deployed_stale_or_unverified`.
  - `python scripts/check-deployed-version.py --expected-commit 623adac --timeout 20` returned sanitized `stale_or_unverified`.
  - The deployed API and Web probes failed in the latest check, so deployed success is not claimed.
  - No deployed-complete claim is made.

## Computer Use / GPT Pro Handoff Status

- Project-scoped Computer Use was used for GitHub/Chrome/GPT Pro review and limited Render inspection.
- A sanitized GPT Pro review packet was submitted after commit `5147d4f`.
- GPT Pro accepted the CI/browser-smoke stabilization step and identified deployment consistency as the next priority.
- The latest implementation commit `623adac` hardens deployed API read fallback, relationship-view backend authority, relationship evidence metadata, stage source coverage, and browser-smoke page relevance checks.
- Render redeploy is blocked because automation reached an interactive Render sign-in page.
- No credentials, cookies, tokens, screenshots with secrets, raw payloads, private diagnostics, account details, private operational URLs, or unrelated personal content were copied into the repo log or GPT Pro handoff.

## Required Next Decision

Deployment cannot be safely completed by automation until one of these is true:

1. The user manually completes Render sign-in in the browser and leaves the project dashboard open.
2. A safe local Render automation path is configured, such as a Render API key stored outside chat and exposed only to the local shell/tooling.
3. The user explicitly defers deployment and asks Codex to continue with local-only data/API hardening.

After Render access is available, the next run should:

- Trigger API and Web redeploy from the latest `main`.
- Verify `/api/v1/version` reports the latest commit.
- Run deployed endpoint probes.
- Run `npm run smoke:web -- --mode=deployed`.
- Record only sanitized service names, commit SHA, build status, smoke result, failures, and limitations.
- Send GPT Pro a concise sanitized review request.

## Request For GPT Pro

请审查当前 Codex 完成结果，并给出下一轮 prompt。

## Constraints For The Next Run

- Preserve existing public pages and API endpoints.
- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
