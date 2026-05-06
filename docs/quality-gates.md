# Quality Gates

Quality gates define what must be true before changes are merged. Gates should be automated in CI where possible and documented when manual review is still required.

## Gate Matrix

| Gate | Applies to | Required evidence |
| --- | --- | --- |
| Governance and docs | `AGENTS.md`, `README.md`, `docs/`, `.github/workflows/`, `tests/e2e/` | Required docs exist, local Markdown links resolve, no conflict markers |
| E2E acceptance | `tests/e2e/` and user-visible workflows | Feature files or acceptance docs include traceable scenarios and tags |
| Real-data source license | Raw-source manifests, ingest config, source adapters, deployment config | Source is public, no-key for v1, redistribution and derivative-use terms are recorded before ingest |
| Real-data schema validation | `data_contracts/`, raw/silver/source manifests, source adapters | Every ingested source maps to a contract version and fails closed on incompatible required fields |
| Source freshness | Raw-source manifests, ingest jobs, health checks, stale-state UI/API behavior | Source `as_of_time`, retrieval time, freshness SLA, and stale behavior are documented and tested |
| Evidence lineage | Source registry, raw/silver/gold transforms, API, System Health UI | `/api/v1/lineage` links raw checksums to silver events/entities and gold edge events without exposing raw payloads |
| Snapshot determinism | Graph/materialization inputs, input manifests, model/feature snapshots | Snapshot output can be reproduced from an immutable input manifest without network fetches |
| PII and secret hygiene | Source adapters, logs, CI workflows, deployment docs, environment configs | No private credentials, PII, raw source rows, or raw data extracts appear in CI logs, artifacts, docs, or public config |
| Contract compatibility | `data_contracts/`, `packages/shared-types/`, `packages/api-client/` | Schema validation and backwards-compatibility checks |
| Unit and API behavior | `services/api/`, `packages/` | Unit tests, API tests, error path coverage |
| Graph invariants | `graph_kernel/`, `packages/sra_core/`, `tests/graph_invariants/` | Node and edge validation, traversal invariants, temporal validity checks |
| Leakage and model quality | `ml/`, `configs/features/`, `configs/labels/`, `tests/leakage/` | Leakage tests, evaluation reports, model promotion criteria |
| Frontend runtime | `apps/web/`, `packages/shared-types/`, `packages/api-client/`, `packages/design-system/` | `npm install`, typecheck, build, and browser smoke evidence |
| Infrastructure | `infra/`, environment configs | Build validation, secret hygiene, deployment dry run where available |

## Real-Data-First Gates

Real-data work must be governed before it is automated. Synthetic fixtures may support tests, but production-facing behavior cannot silently fall back to fabricated source semantics when a real public source is expected.

| Gate | Required before merge | Blocks |
| --- | --- | --- |
| License policy | A source manifest records source URL, publisher, license or terms URL, allowed use, redistribution limits, attribution text, and reviewer. V1 sources must be public and require no API key. | New source ingest, source-derived docs, source-derived screenshots, and deployments that expose source-derived values |
| Schema validation | Raw records validate against `data_contracts/raw_schema/` or a named source-specific contract before transformation. Silver, graph, feature, label, and API outputs validate against their existing contracts. | Promotion from raw to silver, graph builds, API exposure, and model training |
| Source freshness | Each source records `source_published_at` when available, `retrieved_at`, `as_of_time`, freshness SLA, stale threshold, and degraded behavior. Stale source handling must be visible to API/UI consumers. | Scheduled ingest promotion, production deploys, and analyst-facing freshness claims |
| Bulk promoted graph | Public-real bulk graph promotion writes a manifest with cache paths, checksums, source status, node/edge counts, and `raw_data_in_git=false`. API reads promoted data when present and reports partial state when absent. | API exposure of large real nodes, Graph Explorer data-node layer, System Health source directory |
| Contract compatibility | Contract changes include backwards-compatibility notes, migration behavior, and owner review. Breaking changes must update consumers and tests in the same change set. | API/client changes, graph schema changes, source contract changes, and model input changes |
| PII/secret hygiene | No private credentials, personal data, raw rows, proprietary identifiers, or raw extracts are committed, uploaded as artifacts, or printed in CI logs. Use aggregate counts, hashed IDs, schema names, and manifest references in diagnostics. | CI artifact upload, deployment config, source adapter logging, and public docs |
| Input-manifest determinism | Real snapshots are built from an immutable input manifest listing source identifiers, retrieval timestamps, content digests, contract versions, transform versions, and runtime config. Rebuilds must not fetch floating latest data unless creating a new manifest. | Graph snapshots, feature snapshots, labels, model evaluations, and release candidates |

Minimum v1 source policy:

- Use public no-key sources only.
- Keep raw datasets outside GitHub and CI artifacts.
- Commit only manifests, schemas, source metadata, deterministic fixtures, and aggregate validation reports.
- Do not add production secrets until a separate secrets-management gate exists for Render and GitHub.

## Changed-File Gate Routing

CI and reviewers use this routing table to decide which gates are required and who owns the evidence.

| Changed files | Required gates | Responsible agent |
| --- | --- | --- |
| `docs/`, `AGENTS.md`, `README.md`, `.github/workflows/` | Governance and docs; PII/secret hygiene for workflow or deployment changes | QA and docs supervisor |
| `tests/e2e/` | Governance and docs; E2E acceptance; source freshness when stale or degraded data states change | QA and docs supervisor |
| `data_contracts/`, `configs/sources/`, source manifests, source adapters | Real-data source license; schema validation; source freshness; contract compatibility; PII/secret hygiene | API and contracts with Data and ML |
| `configs/features/`, `configs/labels/`, `ml/` | Schema validation; source freshness; snapshot determinism; leakage and model quality; contract compatibility | Data and ML |
| `graph_kernel/`, `packages/sra_core/`, `configs/ontology/` | Schema validation; snapshot determinism; graph invariants; contract compatibility | Graph and core model |
| `services/api/`, `packages/shared-types/`, `packages/api-client/` | Contract compatibility; unit and API behavior; schema validation for exposed data; source freshness metadata checks | API and contracts |
| `apps/web/`, `packages/design-system/` | Frontend runtime; E2E acceptance for user-visible workflows; source freshness display checks | Product and frontend |
| `infra/`, `render.yaml`, deployment docs, environment config | Infrastructure; PII/secret hygiene; source license policy for exposed data; Render/GitHub deployment notes | Infrastructure with QA and docs supervisor |

## Current CI Coverage

The initial workflow in `.github/workflows/quality-gates.yml` runs:

- Required governance, architecture, data-flow, quality, and E2E doc checks.
- Real-data governance doc checks for license policy, schema validation, source freshness, contract compatibility, PII/secret hygiene, and input-manifest determinism.
- Changed-file route reporting for required gates and responsible agents on pull requests.
- Workflow hygiene checks that reject broad artifact uploads and raw-data artifact paths.
- Local Markdown link validation for repository-relative links.
- Conflict marker detection in governance, docs, workflow, and E2E files.
- E2E acceptance scenario count and tag validation.
- Node dependency installation plus `lint`, `typecheck`, and `test` scripts when `package.json` exists.
- Python compile checks when Python files exist.
- Python project dependency installation plus `pytest` when pytest-style tests exist.
- Main CI browser smoke starts the zero-dependency API server and Next.js dev server, then runs `npm run smoke:web` in both real API mode and mock mode.
- Browser smoke in real API mode verifies `/api/v1/sources`, `/api/v1/lineage`, System Health source registry, entity resolution, evidence lineage, and entity search.
- Public-real bulk ingestion tests verify fixture replay, promoted manifest creation, data governance node classes, and data relationship edge classes.

Language checks skip only when the corresponding implementation files or test files are absent. Once a manifest or test suite exists, the workflow must either run it or document the concrete blocker.

## Merge Policy

- A failing required CI gate blocks merge.
- A skipped optional gate is acceptable only when the repository lacks the corresponding implementation files.
- A new public behavior must add or update E2E acceptance coverage.
- A new data shape must add or update the relevant data contract.
- A new real source must add or update its license, freshness, schema, and input-manifest evidence before ingest automation is merged.
- A new model signal must add or update leakage and evaluation criteria.
- A new graph behavior must add or update graph invariant coverage.
- CI logs and artifacts must contain only sanitized diagnostics, reports, and manifests. Raw data and source extracts stay out of GitHub-hosted CI.

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
- API lineage: `http://127.0.0.1:8000/api/v1/lineage`
- Web app: `http://127.0.0.1:3000`
- Required frontend pages: Global Risk Cockpit, Graph Explorer, Company Risk 360, Path Explainer, Shock Simulator, Causal Evidence Board, Graph Version Studio, System Health Center.
- Browser smoke report: `artifacts/browser-smoke/report.json`
- Required API metadata: every visible prediction, simulation, explanation, and report must carry graph, feature, label, model, and `as_of_time` metadata.

Related docs: [multi-agent operating model](governance/multi-agent.md), [real data governance](governance/real-data-governance.md), [GitHub CI data hygiene](deployment/github-ci.md), [E2E acceptance suite](../tests/e2e/README.md).
