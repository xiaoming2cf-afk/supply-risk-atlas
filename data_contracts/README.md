# Data Contracts

Contracts are defined in three layers:

1. Ontology YAML under `configs/ontology`.
2. Pydantic models under `packages/sra_core/sra_core/contracts`.
3. Runtime contract tests under `tests/contract`.

Schema evolution policy:

- Update ontology/config first.
- Update Pydantic contracts second.
- Update API/shared TypeScript types third.
- Add compatibility or migration notes for any breaking change.
- Existing graph snapshots and reports must retain their original version metadata.
