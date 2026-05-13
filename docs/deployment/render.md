# Render Deployment

SupplyRiskAtlas deploys to Render as two Git-backed web services managed by the root `render.yaml` Blueprint.

## Services

| Service | Runtime | Purpose |
| --- | --- | --- |
| `supply-risk-atlas-api` | Python | FastAPI-compatible API envelope routes under `/api/v1/*` |
| `supply-risk-atlas-web` | Node.js | Next.js web app and same-origin API proxy |

The frontend uses `NEXT_PUBLIC_SUPPLY_RISK_API_URL=https://supply-risk-atlas-api.onrender.com/api/v1` on Render so browser requests can call the API directly through CORS. The Next.js `/api/v1/*` proxy remains available for same-origin deployments and uses `SUPPLY_RISK_API_ORIGIN=https://supply-risk-atlas-api.onrender.com`, with `SUPPLY_RISK_API_HOSTPORT` retained as a private-network fallback.
The Blueprint pins `PYTHON_VERSION=3.11.9` and `NODE_VERSION=22` for reproducible builds. Render deployment is lightweight by default: the API build installs the service only and does not run online ingestion. The API can serve the SemiRisk fixture graph and any pre-promoted public graph that already exists; large or online ingestion jobs must be run as explicit offline maintenance tasks, not during Render build or startup.

## Environment

| Variable | Service | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_SUPPLY_RISK_API_URL` | web | Browser-visible API base URL, normally `https://supply-risk-atlas-api.onrender.com/api/v1` on Render. |
| `SUPPLY_RISK_API_ORIGIN` | web | Same-origin proxy upstream, normally `https://supply-risk-atlas-api.onrender.com`. |
| `SUPPLY_RISK_API_HOSTPORT` | web | Optional Render private-network fallback for the same-origin proxy. |
| `SUPPLY_RISK_CORS_ORIGINS` | API | Comma-separated allowed web origins. Production must not use wildcard CORS. |
| `SUPPLY_RISK_ENV` | API | Use `production` on Render so CORS defaults stay strict. |
| `SUPPLY_RISK_DATA_MODE` | both | Current value is `fixture`; no production data mode is enabled. |
| `SUPPLY_RISK_GRAPH_MODE` | API | `fixture` by default; `promoted` may serve prebuilt public-evidence promoted graph artifacts when present. |
| `SUPPLY_RISK_STORAGE_MODE` | API | `memory` or `sqlite`; SQLite stores sanitized manifests, runs, reports, and graph metadata only. |
| `SUPPLY_RISK_SQLITE_PATH` | API | SQLite database location. The API health payload must report only `redacted`, never the raw path. |
| `SUPPLY_RISK_FIXTURE_GRAPH_MODE` | both | Documents the active fixture graph mode, currently `semirisk_fixture_v0.1`. |
| `SUPPLY_RISK_MAX_REQUEST_BYTES` | API | Request body cap; default and Render value are `262144`. |
| `SUPPLY_RISK_RUN_STORE_SIZE` | API | Bounded in-memory run summary count; default and Render value are `32`. |
| `SUPPLY_RISK_GIT_COMMIT` | API | Optional explicit deployed API commit. Render may also provide `RENDER_GIT_COMMIT`; `/api/v1/version` reports this without paths. |
| `SUPPLY_RISK_BUILD_TIME` | API | Optional build timestamp for `/api/v1/version`; use an ISO-8601 timestamp when configured. |
| `NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT` | web | Optional web build commit shown in System Health; set to the deployed Git SHA when Render exposes it. |
| `NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME` | web | Optional web build timestamp shown in System Health. |

Current limits are `forward iterations <= 5000`, `reverse beam_width <= 20`, `reverse max_combination_size <= 4`, `reverse iterations_per_candidate <= 1000`, and `optimizer max_actions <= 10`.

## Deploy From GitHub

1. Push the repository to GitHub.
2. In Render, create a new Blueprint and select this GitHub repository.
3. Use the root `render.yaml`.
4. Apply the Blueprint.
5. After both services are live, open the `supply-risk-atlas-web` Render URL.

Expected GitHub remote form:

```powershell
git remote add origin https://github.com/<owner>/supply-risk-atlas.git
git branch -M main
git push -u origin main
```

Render Blueprint URL form after the repository exists:

```text
https://dashboard.render.com/blueprint/new?repo=https://github.com/<owner>/supply-risk-atlas
```

No secrets are required for the current MVP. V1 real-data work may use only
public no-key sources, with source license, freshness, schema validation, and
input-manifest evidence recorded before deployment. Production secrets, private
source credentials, and paid data feeds are deferred until a separate
secrets-management gate is approved.

The web service must receive both:

```text
NEXT_PUBLIC_SUPPLY_RISK_API_URL=https://supply-risk-atlas-api.onrender.com/api/v1
SUPPLY_RISK_API_ORIGIN=https://supply-risk-atlas-api.onrender.com
SUPPLY_RISK_DATA_MODE=fixture
SUPPLY_RISK_GRAPH_MODE=fixture
SUPPLY_RISK_FIXTURE_GRAPH_MODE=semirisk_fixture_v0.1
NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT=<deployed-git-sha-if-available>
NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME=<iso-build-time-if-available>
```

The API service must receive:

```text
SUPPLY_RISK_ENV=production
SUPPLY_RISK_CORS_ORIGINS=https://supply-risk-atlas-web.onrender.com
SUPPLY_RISK_DATA_MODE=fixture
SUPPLY_RISK_GRAPH_MODE=fixture
SUPPLY_RISK_STORAGE_MODE=sqlite
SUPPLY_RISK_SQLITE_PATH=data/runtime/supply_risk_atlas.db
SUPPLY_RISK_FIXTURE_GRAPH_MODE=semirisk_fixture_v0.1
SUPPLY_RISK_MAX_REQUEST_BYTES=262144
SUPPLY_RISK_RUN_STORE_SIZE=32
SUPPLY_RISK_GIT_COMMIT=<deployed-git-sha-if-available>
SUPPLY_RISK_BUILD_TIME=<iso-build-time-if-available>
```

`SUPPLY_RISK_API_HOSTPORT` is optional and is used only as a private-network fallback for the same-origin proxy. Keep the direct public API URL configured so browser smoke diagnostics and runtime pages do not depend on the proxy path. `SUPPLY_RISK_DATA_MODE=fixture` and `SUPPLY_RISK_GRAPH_MODE=fixture` document that the deployed first platform slices use the SemiRisk fixture graph and must carry the `fixture_graph:not_production_ready` warning. System Health must display storage/source/connector/deployment readiness with the SQLite path redacted.

## Deployment Version Checks

The API exposes sanitized deployment metadata at:

```text
https://supply-risk-atlas-api.onrender.com/api/v1/version
```

The response reports `git_commit`, `build_time`, `app_version`, `data_mode`,
`graph_mode`, `storage_mode`, `source_manifest_id`, `graph_version`,
`environment`, and warnings. It must not expose filesystem paths, environment
variable dumps, secrets, private diagnostics, or raw source payloads.

Run the local/deployed comparison script after a Render deploy:

```powershell
python scripts/check-deployed-version.py --expected-commit <latest-main-sha>
```

If the script reports `stale_or_unverified`, use the manual repair flow:

1. Redeploy the API service from the latest `main` commit.
2. Redeploy the Web service from the latest `main` commit.
3. Clear the Web build cache if Graph Explorer v2/v3 or System Health version fields remain stale.
4. Verify `SUPPLY_RISK_CORS_ORIGINS`, `NEXT_PUBLIC_SUPPLY_RISK_API_URL`, `SUPPLY_RISK_API_ORIGIN`, `SUPPLY_RISK_DATA_MODE`, `SUPPLY_RISK_GRAPH_MODE`, and storage env vars.
5. Rerun `python scripts/check-deployed-version.py --expected-commit <latest-main-sha>`.
6. Rerun `npm.cmd run smoke:web -- --mode=deployed`.

## Data Hygiene

- Do not store raw source data in Render environment variables, build logs, or
  service logs.
- Do not print raw records, source payloads, credentials, signed URLs, or
  personal data in startup diagnostics or request logs.
- Log source IDs, manifest IDs, contract versions, aggregate counts, stale/fresh
  status, and digests instead of raw values.
- Keep raw source artifacts outside GitHub and Render build artifacts unless a
  future private storage policy explicitly allows them.
- Public deployment configuration may reference only public no-key sources in
  v1.

## Local Parity

Local checks before pushing:

```powershell
python -m pytest -q
npm test
$env:SUPPLY_RISK_API_URL='http://127.0.0.1:8000/api/v1'
$env:SUPPLY_RISK_EXPECT_MODE='real'
npm run smoke:web
```

Smoke modes:

```powershell
npm.cmd run smoke:web -- --mode=proxy
npm.cmd run smoke:web -- --mode=local
npm.cmd run smoke:web -- --mode=deployed
```

- `proxy` uses `SUPPLY_RISK_WEB_URL` or `http://127.0.0.1:3000` and the same-origin `/api/v1` proxy.
- `local` defaults to `http://127.0.0.1:3000` plus `http://127.0.0.1:8000/api/v1`.
- `deployed` defaults to the Render web/API URLs and is best-effort so transient deployed-service failures do not mask local regression status.

The local web app can still connect directly to the local API with:

```powershell
$env:NEXT_PUBLIC_SUPPLY_RISK_API_URL='http://127.0.0.1:8000/api/v1'
$env:SUPPLY_RISK_API_ORIGIN='http://127.0.0.1:8000'
npm --workspace apps/web run dev -- --hostname 127.0.0.1 --port 3000
```

Post-deploy SemiRisk fixture graph checks:

```powershell
Invoke-RestMethod https://supply-risk-atlas-api.onrender.com/api/v1/graph/snapshot
Invoke-RestMethod https://supply-risk-atlas-api.onrender.com/api/v1/risk/entities/company:tsmc
Invoke-RestMethod https://supply-risk-atlas-api.onrender.com/api/v1/scenarios/forward -Method Post -ContentType 'application/json' -Body '{"scenario_type":"earthquake","targets":["company:tsmc"],"severity_distribution":{"type":"fixed","params":{"value":0.72}},"duration_days_distribution":{"type":"fixed","params":{"value":28}},"iterations":80,"seed":42,"as_of_time":"2026-05-01T00:00:00Z"}'
Invoke-RestMethod https://supply-risk-atlas-api.onrender.com/api/v1/scenarios/reverse -Method Post -ContentType 'application/json' -Body '{"target_metric":"cvar95_loss","failure_threshold":35,"candidate_scope":{"node_types":["company","equipment","material","chemical","process_stage","product_grade"],"edge_types":[]},"max_combination_size":2,"beam_width":4,"iterations_per_candidate":30,"seed":42,"as_of_time":"2026-05-01T00:00:00Z"}'
Invoke-RestMethod https://supply-risk-atlas-api.onrender.com/api/v1/optimization/interventions -Method Post -ContentType 'application/json' -Body '{"budget":70,"allowed_intervention_types":["add_alternative_supplier","increase_inventory_buffer","add_policy_monitoring"],"max_actions":3,"risk_aversion_beta":0.7,"compliance_constraints":{"no_export_control_evasion":true,"no_sanctions_circumvention":true},"seed":42,"as_of_time":"2026-05-01T00:00:00Z"}'
Invoke-RestMethod https://supply-risk-atlas-api.onrender.com/api/v1/reports/investigation -Method Post -ContentType 'application/json' -Body '{"entity_id":"company:tsmc","include_entity_risk":true,"format":"json"}'
$env:SUPPLY_RISK_WEB_URL='https://supply-risk-atlas-web.onrender.com'
$env:SUPPLY_RISK_API_URL='https://supply-risk-atlas-api.onrender.com/api/v1'
$env:SUPPLY_RISK_EXPECT_MODE='real'
npm run smoke:web
```

Deployed smoke checklist:

- `#system-health-center`
- `#graph-explorer`
- `#company-risk-360` or `#entity-risk-360`
- `#shock-simulator`
- `#reverse-stress-lab`
- `#intervention-optimizer`
- `#investigation-report`

If Render web stays stale after a pushed commit, redeploy the web service from
the latest Git commit and clear the web build cache before rerunning the remote
smoke command. Do not claim deployed completion unless the web route shows
either fixture graph readiness or an explicit API unavailable state.
