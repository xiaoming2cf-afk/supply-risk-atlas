# Render Deployment Secret Requirements

This project now has a manual GitHub Actions workflow for Render deployment:

- `.github/workflows/render-manual-deploy.yml`
- Trigger: `workflow_dispatch` only
- Purpose: deploy the API and Web services for a requested commit, optionally clearing the Render build cache

The workflow does not run on ordinary `push` events and does not print secrets or raw Render API responses.

## Required GitHub Actions Secrets

Configure these as repository or environment secrets in GitHub Actions before running the workflow.

| Secret | Purpose | Minimum scope | Notes |
| --- | --- | --- | --- |
| `RENDER_API_KEY` | Authenticates calls to the Render API | Render API access for the owning workspace | Do not paste this value into issues, logs, docs, reports, or chat. Rotate it if exposed. |
| `RENDER_API_SERVICE_ID` | Identifies the `supply-risk-atlas-api` service | The existing API service only | Use the Render service ID, not a private URL or token. |
| `RENDER_WEB_SERVICE_ID` | Identifies the `supply-risk-atlas-web` service | The existing Web service only | Use the Render service ID, not a private URL or token. |

## Workflow Behavior

The workflow sends a bounded Render API request to `POST /v1/services/{serviceId}/deploys` with:

- `commitId`: the selected Git commit SHA
- `clearCache`: `clear` or `do_not_clear`

Render's public API documentation states that the Trigger Deploy endpoint supports both fields, and Render's deployment documentation describes "Clear build cache & deploy" as the manual cache-refresh path for stale build artifacts.

After triggering both services, the workflow runs `scripts/check-deployed-version.py` until the public deployment either aligns or the bounded wait window expires.

## Completion Criteria

A deployment is considered aligned only when all public probes agree on the same expected commit:

- direct API `/api/v1/version`
- Web same-origin `/api/v1/version` proxy
- Web root HTML commit marker
- Web `/api/build-info` metadata endpoint

If any required secret is missing, the correct status is:

`render_deploy_blocked_missing_safe_deploy_path`

Do not claim deployment completion until the public probes converge.

## Manual Fallback

If GitHub secrets are unavailable, use the Render Dashboard manually:

1. Open the API service.
2. Use `Manual Deploy` with `Clear build cache & deploy` for the latest commit.
3. Open the Web service.
4. Use `Manual Deploy` with `Clear build cache & deploy` for the latest commit.
5. Run:

```powershell
python scripts/check-deployed-version.py --expected-commit <latest_commit_sha> --timeout 25 --attempts 3
```

Record only sanitized evidence: service name, commit SHA, build status, public probe status, and deployed smoke result.
