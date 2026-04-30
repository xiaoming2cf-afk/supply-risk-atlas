# Render Deployment

SupplyRiskAtlas deploys to Render as two Git-backed web services managed by the root `render.yaml` Blueprint.

## Services

| Service | Runtime | Purpose |
| --- | --- | --- |
| `supply-risk-atlas-api` | Python | FastAPI-compatible API envelope routes under `/api/v1/*` |
| `supply-risk-atlas-web` | Node.js | Next.js web app and same-origin API proxy |

The frontend uses `NEXT_PUBLIC_SUPPLY_RISK_API_URL=/api/v1` on Render. Requests from the browser go to the web service first, then the Next.js route handler proxies them to the API over Render's private network using `SUPPLY_RISK_API_HOSTPORT`.
The Blueprint pins `PYTHON_VERSION=3.11.9` and `NODE_VERSION=22` for reproducible builds.

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

No secrets are required for the current synthetic MVP. The web service receives
`NEXT_PUBLIC_SUPPLY_RISK_API_URL=/api/v1` and proxies same-origin API requests to
the API service through `SUPPLY_RISK_API_HOSTPORT`.

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
