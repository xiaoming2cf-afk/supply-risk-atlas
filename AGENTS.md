# SupplyRiskAtlas Agent Governance

This repository is a shared multi-agent workspace. Agents are expected to preserve each other's work, stay inside their assigned ownership lane, and leave changes traceable through docs, tests, or CI gates.

## Ground Rules

- Work only inside `supply-risk-atlas`.
- Read the files you will edit before changing them.
- Do not revert, rename, delete, or reformat files outside your ownership lane unless the current owner explicitly asks.
- Treat generated datasets, model weights, local caches, and build outputs as derived artifacts unless a repository policy says otherwise.
- Keep changes small enough to review and connect each change to a documented requirement, contract, test, or gate.
- Prefer structured contracts and schemas over ad hoc conventions.
- Record unresolved assumptions in the nearest relevant doc instead of burying them in implementation comments.

## Ownership Lanes

| Lane | Primary paths | Typical deliverables |
| --- | --- | --- |
| Product and frontend | `apps/web/`, `packages/design-system/`, `packages/api-client/` | User workflows, UI states, design system components, client integration |
| API and contracts | `services/api/`, `packages/shared-types/`, `packages/sra_core/api/`, `data_contracts/` | API endpoints, shared types, schema compatibility, contract tests |
| Graph and core model | `graph_kernel/`, `packages/sra_core/`, `configs/ontology/` | Entity graph, graph invariants, traversal logic, ontology updates |
| Data and ML | `ml/`, `configs/features/`, `configs/labels/`, `configs/models/` | Feature pipelines, labels, leakage checks, model training and evaluation |
| Infrastructure | `infra/`, deployment configs, runtime environment files | Runtime topology, containers, deployment and environment configuration |
| QA and docs supervisor | `AGENTS.md`, `README.md`, `docs/`, `.github/workflows/`, `tests/e2e/` | Governance, architecture docs, data-flow docs, quality gates, E2E acceptance descriptions |

When a change crosses lanes, the initiating agent must document why the cross-lane change is required and keep the edit limited to the contract between lanes.

## Coordination Protocol

1. Inspect existing files and current ownership before editing.
2. Announce the path scope and intended outcome in the task thread.
3. Make the smallest coherent change that satisfies the request.
4. Run the most relevant local checks available in the current repository state.
5. Summarize changed paths, checks run, and any skipped gates with a concrete reason.

## Conflict Protocol

- If another agent has changed a file in your lane, read the new version and build on it.
- If another agent has changed a file outside your lane, leave it alone unless the task cannot be completed without that change.
- If two agents need the same file, prefer adding a narrow section rather than restructuring the whole file.
- If a conflict cannot be resolved locally, stop and ask for direction instead of overwriting work.

## Quality Expectations

Every meaningful change should satisfy at least one of these checks:

- Documentation is updated for behavior, architecture, data flow, or ownership changes.
- Contracts or schemas are updated when data shape changes.
- Unit, contract, graph invariant, leakage, model evaluation, or E2E acceptance coverage is added or updated for user-visible behavior.
- CI reflects the gate that should prevent regression.

The repository quality gates are described in [docs/quality-gates.md](docs/quality-gates.md).
