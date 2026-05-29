# Codex Continuation Request

## Current Status

- Latest pushed commit: `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- Branch: `main`.
- GitHub `ci`: passed for `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- GitHub `Quality Gates`: passed for `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- Preserve user-owned local files:
  - `apps/web/AGENTS.md`
  - `apps/web/CLAUDE.md`
  - `data/runtime/` remains ignored runtime state.

## Completed In Latest Loop

- Decluttered the frontend display layer so ordinary pages show concise public-evidence / research-fixture summaries instead of raw engineering metadata.
- Added `AuditDetails`, `MetadataSummary`, and `DiagnosticDetails` display components.
- Moved `data_mode`, `graph_mode`, `graph_version`, `source_manifest_id`, calibration details, endpoint diagnostics, and warning details behind collapsed audit sections.
- Preserved API fields, report/export metadata, no-raw-payload behavior, and canonical geography terminology.
- Pushed the local commit to GitHub after a network retry with approved elevated `git push`.

## Validation Evidence

- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `npm.cmd run smoke:web` - passed with 63 checks.
- Targeted post-push checks:
  - `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` - passed.
  - `npm.cmd --workspace apps/web run typecheck` - passed.

## Deployment Status

- Current status: `deployed_stale_or_unverified`.
- Public deployed version probe for expected commit `c78f32c62c85f965d71e35d6e72dfc8daec72cc0` reported:
  - API commit: `06c50120449525fac149be9a4de6536b7371cc16`
  - Web `/api/build-info` commit: `06c50120449525fac149be9a4de6536b7371cc16`
  - Web same-origin proxy commit: `06c50120449525fac149be9a4de6536b7371cc16`
  - Web root HTML commit marker: latest commit not visible
- GitHub Actions run `26643255838` attempted the `Render Manual Deploy` workflow for `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- The workflow failed in the preflight step before triggering Render deploys because required GitHub Actions secrets are missing:
  - `RENDER_API_KEY`
  - `RENDER_API_SERVICE_ID`
  - `RENDER_WEB_SERVICE_ID`
- No Render credentials, token values, cookies, private diagnostics, or raw payloads were exposed or stored.

## Required Next Action

Configure the required GitHub Actions secrets using the guidance in `docs/roadmap/render-deploy-secret-requirements.md`, then re-run the manual workflow:

1. Open GitHub Actions for `Render Manual Deploy`.
2. Select `Run workflow`.
3. Use `main`.
4. Set `commit_sha` to `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
5. Set `clear_cache` to `clear`.
6. Run the workflow.
7. Re-run:

```powershell
python scripts/check-deployed-version.py --expected-commit c78f32c62c85f965d71e35d6e72dfc8daec72cc0 --timeout 25 --attempts 3
```

The acceptable final statuses are:

- `deployed_verified`, or
- `render_deploy_blocked_missing_safe_deploy_path` with the missing-secret evidence above.

After deployment is verified or safely blocked, retry the project-scoped GPT Pro handoff with sanitized evidence only. Do not paste secrets, raw logs, account screenshots, cookies, tokens, private diagnostics, or raw payloads.

## Constraints For The Next Run

- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
