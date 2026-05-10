# Semiconductor Ontology

`configs/ontology/semiconductor.yaml` defines the foundation node and edge vocabulary for semiconductor supply-chain resilience. It does not create production graph data by itself; it defines the contract that future promoted semiconductor graph snapshots must satisfy.

## Rules

- Nodes and edges require source refs or provenance refs, confidence, and temporal validity fields.
- Graph snapshots must be deterministic for a fixed source manifest, ontology version, config, and `as_of_time`.
- Missing, stale, partial, or unavailable data must render as a degraded state instead of fabricated graph counts or scores.
- API and frontend payloads must not expose raw source payloads, secrets, private diagnostics, or hidden internal fields.
- Export-control and sanctions evidence may be modeled as policy events and risk relationships, but the platform must not recommend evasion or circumvention.

## Node Types

The foundation node types are `company`, `country`, `region`, `facility`, `process_stage`, `equipment`, `material`, `chemical`, `component`, `product_grade`, `technology_node`, `policy_event`, `risk_event`, `market_indicator`, `trade_flow`, and `route`.

Each node type defines `description`, `required_fields`, `allowed_edge_directions`, `example`, and `version`. Required fields include `source_refs`, `confidence`, `valid_from`, and nullable `valid_to`.

## Edge Types

The foundation edge types are `participates_in`, `located_in`, `requires`, `produces`, `supplies`, `depends_on`, `substitutable_with`, `restricted_by`, `impacted_by`, `exports_to`, `imports_from`, `routes_through`, `correlated_with`, and `evidence_for`.

Each edge type defines `description`, `required_fields`, allowed source node types, allowed target node types, `allowed_edge_directions`, `example`, and `version`. Required fields include `provenance_refs`, `confidence`, `valid_from`, nullable `valid_to`, and `evidence_text_summary`.

## Promotion Checklist

- Source registry entry exists and has terms, license, owner, freshness SLA, and review status.
- Raw, silver, and graph contracts are declared before data is promoted.
- Every visible graph node or edge can be traced back to a source manifest and source refs without exposing raw payloads.
- Invalid node type, invalid edge type, invalid edge direction, missing provenance, and missing temporal validity fail tests.
