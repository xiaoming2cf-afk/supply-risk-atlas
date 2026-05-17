# Codex Continuation Request

## Current Status

- Latest pushed commit before this continuation note: `0d440fefa0872d55ecbe3619ef8e4e3754ce2ccb`.
- Branch: `main`.
- Preserved local files that must not be staged unless the user asks:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
  - `data/runtime/` remains ignored runtime state.

## Local And CI Validation

- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed after synchronizing the `api_commit_reported` version-readiness state.
- `python -m pytest tests/api/test_version_endpoint.py tests/api/test_system_health_semiconductor_graph.py tests/api/test_system_health_storage_sources.py tests/quality/test_deployed_version_checker.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- GitHub `ci` passed for `0d440fe`.
- GitHub `Quality Gates` passed for `0d440fe`.

## What Changed

- `/api/v1/version` readiness semantics now report `api_commit_reported` when the API commit is known but the API process does not receive a Web build commit value.
- Cross-service deployment consistency remains enforced by `scripts/check-deployed-version.py`, which verifies API commit, Web proxy commit, and Web HTML commit marker externally.
- The stage graph API exposes source-family coverage, source gaps, and proxy limitations for national, enterprise, and industry semiconductor evidence coverage.
- Graph Explorer stage views display source-family coverage and limitations instead of hiding them in docs.
- Supply-demand balance rows include graph/source/data-mode metadata, source refs, evidence refs, validity fields, warnings, and calibration status.
- A follow-up local patch increases idempotent read retry budgets for deployed transient 5xx/timeout windows. POST/write calls remain single-attempt.
- A second local patch makes `/api/v1/version` and System Health reuse the service-level fixture snapshot cache and adds bounded retry attempts to `scripts/check-deployed-version.py`.

## Deployment Status

- Current deployed status: `deployed_stale_or_unverified`.
- Render API and Web were manually redeployed to `fa26bb0b468ae058a3ce3e346a56536303463e36`.
- Latest pushed HEAD `0d440fefa0872d55ecbe3619ef8e4e3754ce2ccb` has not been verified on Render.
- Public probes still showed deployed API/Web proxy at `fa26bb0` when checking against `0d440fe`.
- Web HTML did not expose the `0d440fe` commit marker.
- Deployed smoke ran in best-effort mode and exited 0, but captured transient 502s for relationship/stage graph reads during page load.
- Direct probes later showed `/api/v1/version`, `/api/v1/graph/supply-relationships?limit=5`, and `/api/v1/stage-graph/L5_fabrication?limit=18` returning HTTP 200 against deployed `fa26bb0`.

## Computer Use And GPT Pro Handoff

- Project-scoped Chrome Browser control was used for Render Dashboard and the GPT Pro project conversation.
- Render actions completed:
  - triggered latest-commit deploy for `supply-risk-atlas-api` to `fa26bb0`;
  - triggered latest-commit deploy for `supply-risk-atlas-web` to `fa26bb0`;
  - later attempts to trigger `0d440fe` redeploy timed out in the Render UI and were not confirmed.
- GPT Pro received a sanitized status packet and returned the next review priorities:
  - deployed `/version` must match latest HEAD before deployment completion is claimed;
  - supply/demand/production/balance views must show zero authoritative rows when endpoints are unavailable;
  - source coverage must keep fixture, promoted, unavailable, and official support distinct;
  - exports and reports must not use local graph-derived fallback rows as relationship facts.
- No credentials, cookies, tokens, OTPs, raw payloads, private diagnostics, or PII were copied into repository files.

## Required Next Decision

Continue with a narrow release-hardening gate:

1. Re-run local checks after the version/cache/probe patch.
2. Commit and push the version/cache/probe patch.
3. Wait for GitHub `ci` and `Quality Gates`.
4. Use Render Dashboard or a safe non-chat Render automation path to redeploy API and Web from the latest HEAD.
5. Verify `python scripts/check-deployed-version.py --expected-commit <latest-head> --timeout 30` returns `deployed_verified`.
6. Run `npm.cmd run smoke:web -- --mode=deployed`.
7. If deployed smoke still captures relationship/stage 502s, patch the read-path retry or page-level refresh behavior without presenting fallback rows as authoritative data.

## Constraints For The Next Run

- Preserve existing public pages and API endpoints.
- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
