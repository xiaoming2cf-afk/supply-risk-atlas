# Codex Continuation Request

## Current Status

- Latest pushed commit before the Render Web env-priority patch: `c3f245d47f678053fc4aca44024a31498ea58d86`.
- Branch: `main`.
- Preserve user-owned local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
  - `data/runtime/` remains ignored runtime state.

## Local And CI Validation

- `python -m pytest tests/api/test_version_endpoint.py tests/api/test_system_health_semiconductor_graph.py tests/api/test_system_health_storage_sources.py tests/quality/test_deployed_version_checker.py -q` - passed, 27 tests.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- GitHub `ci` passed for `f2854ea`.
- GitHub `Quality Gates` passed for `f2854ea`.

## What Changed

- `/api/v1/version` and System Health now reuse the service-level fixture snapshot cache instead of rebuilding the semiconductor fixture graph directly.
- `scripts/check-deployed-version.py` uses bounded per-probe attempts and records attempt counts for API, Web HTML, and Web proxy probes.
- The deployed checker treats public-probe exceptions as sanitized failed attempts instead of surfacing private transport details.
- Cross-service deployment consistency remains enforced by checking API commit, Web proxy commit, and Web HTML commit marker.
- The Web layout now emits static HTML metadata for `supply-risk-web-commit` and `supply-risk-web-build-time`; this patch still needs commit/push/deploy verification.
- `next.config.mjs` now prioritizes `RENDER_GIT_COMMIT` over a stale `NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT` override for Web build identity.
- Relationship and stage graph endpoints remain bounded, metadata-complete, and separated by relationship class.

## Deployment Status

- Current deployment status: `deployed_stale_or_unverified`.
- Latest deployed API version observed by public probes: `c3f245d47f678053fc4aca44024a31498ea58d86`.
- Remaining blocker: Web static HTML still rendered an old `data-web-build-commit` value because a stale public Web commit env var overrode Render's Git commit during build.
- Public deployment probes after Render redeploy showed:
  - API `/api/v1/version` reported `c3f245d`.
  - Web same-origin version proxy reported `c3f245d`.
  - Web HTML still rendered `fa26bb0` before the env-priority patch.
- Relationship and stage endpoint reachability was confirmed during the stale-deployment recovery checks, and public version probes now show the API/Web runtime proxy aligned at `f2854ea`:
  - `/api/v1/graph/supply-relationships?limit=5`
  - `/api/v1/graph/demand-relationships?limit=5`
  - `/api/v1/graph/production-dependencies?limit=5`
  - `/api/v1/graph/supply-demand-balance?limit=5`
  - `/api/v1/stage-graph/L5_fabrication?limit=18`

## Computer Use And GPT Pro Handoff

- Project-scoped Browser/Chrome automation was used for Render Dashboard and the GPT Pro project conversation.
- Render API redeploy was triggered from the Dashboard and public probes now show API/Web runtime proxy commit `f2854ea`.
- Render Web Dashboard interaction became unstable while verifying the click flow, but public Web proxy probes show the Web runtime is also serving `f2854ea`.
- No credentials, cookies, tokens, OTPs, private diagnostics, raw payloads, private operational URLs, or PII were copied into repository files.
- GPT Pro's current review priorities remain:
  - do not claim deployment completion until `/api/v1/version`, Web proxy, and Web HTML match latest HEAD;
  - relationship views must show zero authoritative rows when backend endpoints are unavailable;
  - source coverage must distinguish fixture, promoted, unavailable, and official support;
  - exports and reports must not use local graph-derived fallback rows as authoritative relationship facts.

## Required Next Decision

Use a safe Render deployment path to redeploy API and Web from latest `main`:

1. Commit and push the Render Web env-priority patch.
2. Wait for GitHub `ci` and `Quality Gates`.
3. Trigger Web redeploy for `supply-risk-atlas-web` from the marker patch commit.
4. Trigger API redeploy for `supply-risk-atlas-api` if the API commit is no longer aligned with latest `main`.
5. Verify `python scripts/check-deployed-version.py --expected-commit <latest-head> --timeout 30 --attempts 3` returns `deployed_verified`.
6. Run `npm.cmd run smoke:web -- --mode=deployed`.
7. If deployed smoke captures transient relationship or stage endpoint failures, keep the degraded state explicit and do not render local graph-derived relationship rows as authoritative facts.
8. Send GPT Pro a sanitized status packet with commit SHA, CI status, deployed verification result, controlled failures, and screenshots only when they do not expose account data.

## Constraints For The Next Run

- Preserve existing public pages and API endpoints.
- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
