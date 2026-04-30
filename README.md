# SupplyRiskAtlas

SupplyRiskAtlas is a supply-chain risk mapping workspace. The target system combines data contracts, graph modeling, ML risk signals, API services, and a web experience for exploring suppliers, dependencies, exposures, and evidence.

This repository currently contains the project skeleton plus governance, architecture, data-flow, CI, and E2E acceptance documentation. Implementation agents should use these docs as the operating contract while adding source code.

## Repository Map

| Path | Purpose |
| --- | --- |
| `apps/web/` | Web application and frontend components |
| `services/api/` | API service layer |
| `packages/api-client/` | Client SDK or generated API bindings |
| `packages/design-system/` | Shared UI primitives |
| `packages/shared-types/` | Cross-runtime types |
| `packages/sra_core/` | Core domain logic and reusable risk primitives |
| `graph_kernel/` | Supply-chain graph construction and traversal logic |
| `ml/` | Feature engineering, training, simulation, evaluation, and causal analysis |
| `data_contracts/` | Raw, silver, feature, label, and graph schema contracts |
| `configs/` | Environment, feature, label, model, and ontology configuration |
| `infra/` | Local and deployment infrastructure |
| `tests/` | Unit, API, contract, graph invariant, leakage, and E2E tests |
| `docs/` | Governance, architecture, data-flow, quality, and domain documentation |

## Core Docs

- [Agent governance](AGENTS.md)
- [Multi-agent operating model](docs/governance/multi-agent.md)
- [Architecture overview](docs/architecture/overview.md)
- [Data flow](docs/data/data-flow.md)
- [Quality gates](docs/quality-gates.md)
- [Render deployment](docs/deployment/render.md)
- [E2E acceptance suite](tests/e2e/README.md)

## Development Workflow

1. Read [AGENTS.md](AGENTS.md) before making changes.
2. Identify the ownership lane for the paths you need to edit.
3. Update contracts, docs, and tests in the same change when behavior or data shape changes.
4. Run the relevant local checks for the touched lane.
5. Confirm the GitHub Actions workflow in `.github/workflows/quality-gates.yml` passes before merging.

## Local Commands

Run all commands from `D:\系统\supply-risk-atlas`.

Python/API checks:

```powershell
python -m pytest -q
python -m services.api.dev_server
```

The zero-dependency API dev server serves the same synthetic API envelope routes as the FastAPI app. The default health URL is:

```text
http://127.0.0.1:8000/api/v1/health
```

If `uvicorn` is installed, the FastAPI app can also be started with:

```powershell
python -m uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend setup and checks:

```powershell
npm install
npm --workspace apps/web run typecheck
npm --workspace apps/web run build
npm --workspace apps/web run dev -- --hostname 127.0.0.1 --port 3000
npm run smoke:web
```

The web app defaults to mock data. To point it at the local API, set:

```powershell
$env:NEXT_PUBLIC_SUPPLY_RISK_API_URL='http://127.0.0.1:8000/api/v1'
```

When the API URL is configured, the dashboard client calls versioned envelope routes under
`/api/v1/dashboard/*`. If those routes are unavailable, the UI shows `API fallback` and keeps
the deterministic mock view models visible for analysis work.

## Acceptance Baseline

The initial E2E acceptance baseline is documented in [tests/e2e/supply-risk-atlas.feature](tests/e2e/supply-risk-atlas.feature). These scenarios define the user-facing behaviors that implementation work should make executable over time.
