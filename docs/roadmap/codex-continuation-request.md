# Codex Continuation Request

## Current Status

- Latest pushed commit: `2cac0b9742709b1a26d5263b66214c4b3e274e6e`.
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
- GitHub `ci` passed for `2cac0b9`.
- GitHub `Quality Gates` passed for `2cac0b9`.

## What Changed

- `/api/v1/version` and System Health now reuse the service-level fixture snapshot cache instead of rebuilding the semiconductor fixture graph directly.
- `scripts/check-deployed-version.py` uses bounded per-probe attempts and records attempt counts for API, Web HTML, and Web proxy probes.
- The deployed checker treats public-probe exceptions as sanitized failed attempts instead of surfacing private transport details.
- Cross-service deployment consistency remains enforced by checking API commit, Web proxy commit, and Web HTML commit marker.
- Relationship and stage graph endpoints remain bounded, metadata-complete, and separated by relationship class.

## Deployment Status

- Current deployment status: `deployed_stale_or_unverified`.
- Latest deployed API/Web version observed by public probes: `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- Latest pushed HEAD requiring deployment: `2cac0b9742709b1a26d5263b66214c4b3e274e6e`.
- Five consecutive public deployment probes on 2026-05-17 showed:
  - API `/api/v1/version` responded but reported `fa26bb0`.
  - Web same-origin version proxy responded but reported `fa26bb0`.
  - Web HTML did not expose the `2cac0b9` commit marker.
- Direct public probes showed relationship and stage endpoints returning HTTP 200 while still running the stale deployed commit:
  - `/api/v1/graph/supply-relationships?limit=5`
  - `/api/v1/graph/demand-relationships?limit=5`
  - `/api/v1/graph/production-dependencies?limit=5`
  - `/api/v1/graph/supply-demand-balance?limit=5`
  - `/api/v1/stage-graph/L5_fabrication?limit=18`

## Computer Use And GPT Pro Handoff

- Project-scoped Browser/Chrome automation was previously used for Render Dashboard and the GPT Pro project conversation.
- Render redeploy remains blocked by Dashboard automation instability and stale deployed public probes.
- No credentials, cookies, tokens, OTPs, private diagnostics, raw payloads, private operational URLs, or PII were copied into repository files.
- GPT Pro's current review priorities remain:
  - do not claim deployment completion until `/api/v1/version`, Web proxy, and Web HTML match latest HEAD;
  - relationship views must show zero authoritative rows when backend endpoints are unavailable;
  - source coverage must distinguish fixture, promoted, unavailable, and official support;
  - exports and reports must not use local graph-derived fallback rows as authoritative relationship facts.

## Required Next Decision

Use a safe Render deployment path to redeploy API and Web from latest `main`:

1. Trigger API redeploy for `supply-risk-atlas-api` from `2cac0b9` or newer.
2. Trigger Web redeploy for `supply-risk-atlas-web` from `2cac0b9` or newer.
3. Verify `python scripts/check-deployed-version.py --expected-commit <latest-head> --timeout 30 --attempts 3` returns `deployed_verified`.
4. Run `npm.cmd run smoke:web -- --mode=deployed`.
5. If deployed smoke captures transient relationship or stage endpoint failures, keep the degraded state explicit and do not render local graph-derived relationship rows as authoritative facts.
6. Send GPT Pro a sanitized status packet with commit SHA, CI status, deployed verification result, controlled failures, and screenshots only when they do not expose account data.

## Constraints For The Next Run

- Preserve existing public pages and API endpoints.
- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
