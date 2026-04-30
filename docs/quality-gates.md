# Quality Gates

Quality gates define what must be true before changes are merged. Gates should be automated in CI where possible and documented when manual review is still required.

## Gate Matrix

| Gate | Applies to | Required evidence |
| --- | --- | --- |
| Governance and docs | `AGENTS.md`, `README.md`, `docs/`, `.github/workflows/`, `tests/e2e/` | Required docs exist, local Markdown links resolve, no conflict markers |
| E2E acceptance | `tests/e2e/` and user-visible workflows | Feature files or acceptance docs include traceable scenarios and tags |
| Contract compatibility | `data_contracts/`, `packages/shared-types/`, `packages/api-client/` | Schema validation and backwards-compatibility checks |
| Unit and API behavior | `services/api/`, `packages/` | Unit tests, API tests, error path coverage |
| Graph invariants | `graph_kernel/`, `packages/sra_core/`, `tests/graph_invariants/` | Node and edge validation, traversal invariants, temporal validity checks |
| Leakage and model quality | `ml/`, `configs/features/`, `configs/labels/`, `tests/leakage/` | Leakage tests, evaluation reports, model promotion criteria |
| Frontend runtime | `apps/web/`, `packages/shared-types/`, `packages/api-client/`, `packages/design-system/` | `npm install`, typecheck, build, and browser smoke evidence |
| Infrastructure | `infra/`, environment configs | Build validation, secret hygiene, deployment dry run where available |

## Current CI Coverage

The initial workflow in `.github/workflows/quality-gates.yml` runs:

- Required governance, architecture, data-flow, quality, and E2E doc checks.
- Local Markdown link validation for repository-relative links.
- Conflict marker detection in governance, docs, workflow, and E2E files.
- E2E acceptance scenario count and tag validation.
- Node dependency installation plus `lint`, `typecheck`, and `test` scripts when `package.json` exists.
- Python compile checks when Python files exist.
- Python project dependency installation plus `pytest` when pytest-style tests exist.
- Main CI browser smoke starts the zero-dependency API server and Next.js dev server, then runs `npm run smoke:web` in both real API mode and mock mode.

Language checks skip only when the corresponding implementation files or test files are absent. Once a manifest or test suite exists, the workflow must either run it or document the concrete blocker.

## Merge Policy

- A failing required CI gate blocks merge.
- A skipped optional gate is acceptable only when the repository lacks the corresponding implementation files.
- A new public behavior must add or update E2E acceptance coverage.
- A new data shape must add or update the relevant data contract.
- A new model signal must add or update leakage and evaluation criteria.
- A new graph behavior must add or update graph invariant coverage.

## Local Validation Checklist

Before handoff, run the closest available checks:

- Documentation-only change: required file existence, Markdown links, conflict marker scan.
- E2E acceptance change: scenario count, tags, and traceability to architecture or data-flow docs.
- API or package change: unit tests and contract tests.
- Graph change: graph invariant tests.
- ML change: leakage tests and evaluation checks.
- Frontend change: install dependencies, run `npm --workspace apps/web run typecheck`, run `npm --workspace apps/web run build`, and smoke-test core pages with `npm run smoke:web` while the web dev server is running.
- Infrastructure change: build or deployment validation for the touched environment.

## Current Runtime Smoke Targets

- API health: `http://127.0.0.1:8000/api/v1/health`
- Web app: `http://127.0.0.1:3000`
- Required frontend pages: Global Risk Cockpit, Graph Explorer, Company Risk 360, Path Explainer, Shock Simulator, Causal Evidence Board, Graph Version Studio, System Health Center.
- Browser smoke report: `artifacts/browser-smoke/report.json`
- Required API metadata: every visible prediction, simulation, explanation, and report must carry graph, feature, label, model, and `as_of_time` metadata.

Related docs: [multi-agent operating model](governance/multi-agent.md), [E2E acceptance suite](../tests/e2e/README.md).
