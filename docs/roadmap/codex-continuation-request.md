# Codex Continuation Request

## Current Status

- Latest pushed commit: `9841a37f228015c808f8fada715fad698b95de55`.
- Branch: `main`.
- Preserve user-owned local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
  - `data/runtime/` remains ignored runtime state.

## Completed In This Recovery Loop

- Added `/api/build-info` for Web build identity with `Cache-Control: no-store`.
- Extended `scripts/check-deployed-version.py` to verify four public signals:
  - direct API `/api/v1/version`
  - Web same-origin `/api/v1/version` proxy
  - Web root HTML commit marker
  - Web `/api/build-info`
- Added `.github/workflows/render-manual-deploy.yml`.
  - The workflow is `workflow_dispatch` only.
  - It requires GitHub Actions secrets instead of committing credentials.
  - It triggers API and Web Render deploys for a requested commit.
  - It can request Render cache clearing.
  - It runs bounded public convergence checks after deploy.
- Added `docs/roadmap/render-deploy-secret-requirements.md` with the exact safe setup requirements.
- Fixed the initial workflow YAML validation problem and pushed the corrected workflow.

## Validation Evidence

- `python -m pytest tests/quality/test_render_manual_deploy_workflow.py tests/quality/test_deployed_version_checker.py tests/quality/test_web_commit_marker.py -q` - passed.
- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/quality/test_no_forbidden_geography_labels.py -q` - passed.
- `python -m pytest tests/api/test_version_endpoint.py tests/api/test_system_health_semiconductor_graph.py tests/api/test_system_health_storage_sources.py tests/quality/test_deployed_version_checker.py -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- GitHub `ci` passed for `9841a37f228015c808f8fada715fad698b95de55`.
- GitHub `Quality Gates` passed for `9841a37f228015c808f8fada715fad698b95de55`.

## Deployment Status

- Current status: `deployed_stale_or_unverified`.
- Latest public probe for expected commit `9841a37f228015c808f8fada715fad698b95de55` reported:
  - API commit: `c3f245d47f678053fc4aca44024a31498ea58d86`
  - Web same-origin proxy commit: `c3f245d47f678053fc4aca44024a31498ea58d86`
  - Web root HTML commit marker: not visible for latest commit
  - Web `/api/build-info`: unavailable because the deployed Web build predates that route
- Local shell did not have `RENDER_API_KEY`, `RENDER_API_SERVICE_ID`, `RENDER_WEB_SERVICE_ID`, `GITHUB_TOKEN`, or `GH_TOKEN` present.
- GitHub UI showed the manual workflow as active, but the `Run workflow` panel returned a page loading error in Browser automation. The failed tab was closed before continuing.

## Required Next Action

Run the manual workflow after a reliable GitHub UI/API path is available:

1. Open GitHub Actions for `Render Manual Deploy`.
2. Select `Run workflow`.
3. Use `main`.
4. Set `commit_sha` to `9841a37f228015c808f8fada715fad698b95de55`.
5. Set `clear_cache` to `clear`.
6. Run the workflow.
7. If the workflow fails because secrets are missing, configure only the secrets listed in `docs/roadmap/render-deploy-secret-requirements.md`.
8. Re-run:

```powershell
python scripts/check-deployed-version.py --expected-commit 9841a37f228015c808f8fada715fad698b95de55 --timeout 25 --attempts 3
```

The acceptable final statuses are:

- `deployed_verified`, or
- `render_deploy_blocked_missing_safe_deploy_path` with missing secret evidence.

Do not claim deployment completion while the public probes remain stale.

## Constraints For The Next Run

- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
