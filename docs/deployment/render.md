# Render Deployment

SupplyRiskAtlas deploys to Render as two Git-backed web services managed by the root `render.yaml` Blueprint.

## Services

| Service | Runtime | Purpose |
| --- | --- | --- |
| `supply-risk-atlas-api` | Python | FastAPI-compatible API envelope routes under `/api/v1/*` |
| `supply-risk-atlas-web` | Node.js | Next.js web app and same-origin API proxy |

The frontend uses `NEXT_PUBLIC_SUPPLY_RISK_API_URL=https://supply-risk-atlas-api.onrender.com/api/v1` on Render so browser requests can call the API directly through CORS. The Next.js `/api/v1/*` proxy remains available for same-origin deployments and uses `SUPPLY_RISK_API_ORIGIN`, with `SUPPLY_RISK_API_HOSTPORT` retained as a private-network fallback.
The Blueprint pins `PYTHON_VERSION=3.11.9` and `NODE_VERSION=22` for reproducible builds. The API build also runs `python -m sra_core.ingestion.bulk_public --mode online ...` so Render creates `data/promoted/public_real/latest/catalog.json` during deployment without committing raw source downloads to Git.

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

The web service receives `NEXT_PUBLIC_SUPPLY_RISK_API_URL=/api/v1` and proxies
same-origin API requests to the API service through `SUPPLY_RISK_API_HOSTPORT`.

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
$env:SUPPLY_RISK_EXPECT_MODE='real'; npm run smoke:web
```

The local web app can still connect directly to the local API with:

```powershell
$env:NEXT_PUBLIC_SUPPLY_RISK_API_URL='http://127.0.0.1:8000/api/v1'
npm --workspace apps/web run dev -- --hostname 127.0.0.1 --port 3000
```
