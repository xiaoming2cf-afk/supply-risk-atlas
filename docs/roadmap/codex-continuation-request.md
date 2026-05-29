# Codex Continuation Request

## Current Status

- Latest implementation commit: `1e506a8da2e110d214d5b37ead43988d34de9481`.
- Branch: `main`.
- GitHub `ci`: passed for `1e506a8da2e110d214d5b37ead43988d34de9481`.
- GitHub `Quality Gates`: passed for `1e506a8da2e110d214d5b37ead43988d34de9481`.
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
- Added docs-only deployment handoff commit `fa4ba1ed05ea9d0ac33fc98eccc30268c97bdbf1`; GitHub `ci` and `Quality Gates` passed.
- Added implementation commit `1e506a8da2e110d214d5b37ead43988d34de9481` to fix the CI browser-smoke display declutter regression:
  - `AuditDetails` is now an explicit client component.
  - Closed audit details no longer render technical field rows into the DOM until the user expands the section.
  - Next dev server allows local smoke origins `127.0.0.1` and `localhost`.

## Validation Evidence

- `python -m pytest tests/quality -q` - passed.
- `python -m pytest tests/api tests/security tests/graph_invariants -q` - passed.
- `npm.cmd --workspace apps/web run typecheck` - passed.
- `npm.cmd --workspace apps/web run build` - passed.
- `npm.cmd run smoke:web` - passed with 63 checks.
- `python -m pytest tests/api -q` - passed.
- `python -m pytest tests/security tests/graph_invariants -q` - passed.
- Targeted post-push checks:
  - `python -m pytest tests/quality/test_frontend_display_declutter.py tests/quality/test_deployed_api_transport_fallback.py tests/quality/test_relationship_view_no_authoritative_fallbacks.py -q` - passed.
  - `npm.cmd --workspace apps/web run typecheck` - passed.

## Deployment Status

- Current status: `deployed_stale_or_unverified`.
- Public deployed version probe for expected commit `1e506a8da2e110d214d5b37ead43988d34de9481` reported:
  - API commit: `06c50120449525fac149be9a4de6536b7371cc16`
  - Web `/api/build-info` commit: `06c50120449525fac149be9a4de6536b7371cc16`
  - Web same-origin proxy commit: `06c50120449525fac149be9a4de6536b7371cc16`
  - Web root HTML commit marker: latest commit not visible
- GitHub Actions run `26643255838` attempted the `Render Manual Deploy` workflow for `c78f32c62c85f965d71e35d6e72dfc8daec72cc0`.
- GitHub Actions run `26646684760` attempted the `Render Manual Deploy` workflow for `1e506a8da2e110d214d5b37ead43988d34de9481`.
- The workflow failed in the preflight step before triggering Render deploys because required GitHub Actions secrets are missing:
  - `RENDER_API_KEY`
  - `RENDER_API_SERVICE_ID`
  - `RENDER_WEB_SERVICE_ID`
- No Render credentials, token values, cookies, private diagnostics, or raw payloads were exposed or stored.
- Chrome/Computer Use status:
  - Render Dashboard opened successfully in the authenticated Chrome profile.
  - Browser control then timed out when inspecting the Render page.
  - A fresh Chrome window was opened with user authorization and retried.
  - The fresh Render Dashboard page also timed out through the extension, so UI redeploy remains blocked by Chrome extension communication stability.
  - A stale Render tab close was attempted after the first failure, but claiming that tab also timed out; no additional Render UI loop was attempted.

## Required Next Action

Configure the required GitHub Actions secrets using the guidance in `docs/roadmap/render-deploy-secret-requirements.md`, then re-run the manual workflow:

1. Open GitHub Actions for `Render Manual Deploy`.
2. Select `Run workflow`.
3. Use `main`.
4. Set `commit_sha` to `1e506a8da2e110d214d5b37ead43988d34de9481`.
5. Set `clear_cache` to `clear`.
6. Run the workflow.
7. Re-run:

```powershell
python scripts/check-deployed-version.py --expected-commit 1e506a8da2e110d214d5b37ead43988d34de9481 --timeout 25 --attempts 3
```

The acceptable final statuses are:

- `deployed_verified`, or
- `render_deploy_blocked_missing_safe_deploy_path` with the missing-secret evidence above.

After deployment is verified or safely blocked, retry the project-scoped GPT Pro handoff with sanitized evidence only. Do not paste secrets, raw logs, account screenshots, cookies, tokens, private diagnostics, or raw payloads.

## GPT Pro Handoff Status

- Attempted after `8124f03a38ae68851e873d82b44bb81bdaf69439` passed GitHub `ci` and `Quality Gates`.
- The project-scoped ChatGPT project URL timed out through the Codex Chrome Extension before a sanitized status could be pasted.
- A failed-tab cleanup attempt also timed out, so no further browser loop was attempted.
- Safe next action: manually paste the sanitized handoff summary from `docs/roadmap/stage-centered-visualization-and-source-expansion-log.md` into the GPT Pro project, or retry when Chrome extension control is stable.

## Constraints For The Next Run

- Do not enable live connector fetch during import, tests, CI, app startup, or Render startup.
- Do not expose raw payloads, secrets, cookies, tokens, private diagnostics, local filesystem paths, private operational URLs, or PII.
- Keep canonical geography terminology: `region:china_taiwan` / `中国台湾`, parent `country:CN` / `中国`.
- Evidence-context links remain non-dependency inspection links.
- Keep supply, demand, production dependency, and evidence-context relationship classes separated.
- The platform remains fixture/proxy/promoted-public-evidence research infrastructure, not production-ready.
