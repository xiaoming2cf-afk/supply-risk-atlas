---
name: sra-graph-kernel
description: Use when building or reviewing SupplyRiskAtlas graph ontology, graph snapshots, graph lineage, graph quality, or graph-derived metrics.
---

# SRA Graph Kernel

## When To Use

Use for ontology, graph snapshots, graph invariants, lineage lookup, criticality, quality reports, and graph-derived API/UI data.

## Required Files To Read

- `AGENTS.md`
- `configs/ontology/`
- `configs/ontology/semiconductor.yaml`
- `graph_kernel/`
- `docs/domain/semiconductor-ontology.md`
- `tests/contract/`
- `tests/graph_invariants/`

## Forbidden Behaviors

- Do not create graph nodes or edges without provenance refs.
- Do not invent graph counts, entity relationships, or risk paths.
- Do not expose raw source payloads in graph/API-visible contracts.
- Do not encode recommendations for sanctions or export-control circumvention.

## Required Checks

- Snapshot construction must be deterministic for fixed manifest, ontology version, config, and `as_of_time`.
- Nodes and edges must have valid ontology types, valid directions, provenance, confidence, and temporal validity.
- Snapshot output must include graph version, ontology version, source manifest ID, counts, quality report, and degraded-state counts.

## Expected Summary Format

- Ontology/snapshot changes:
- Determinism guarantees:
- Lineage behavior:
- Quality checks:
- Tests run:
- Limitations:
