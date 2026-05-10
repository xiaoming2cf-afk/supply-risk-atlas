# Risk Score v0

Risk Score v0 is an explainable, deterministic baseline for the fixture-based SemiRisk-KG v0.1 graph. It is not a production model and does not use neural networks, random forests, private exposure data, or fabricated business metrics.

## Scope

- Graph source: SemiRisk-KG v0.1 fixture/promoted test graph.
- Default entity: `company:tsmc`.
- Feature version: `semirisk_risk_score_v0.1`.
- Required lineage: every score carries `graph_version`, `source_manifest_id`, `as_of_time`, component evidence refs, and `fixture_graph:not_production_ready`.
- Raw source payloads are not exposed through model output or API payloads.

## Components

All component values are normalized to 0-100 and computed from graph edge weights and confidence.

| Component | Meaning |
| --- | --- |
| `exposure_score` | Dependency, supply, process, production, and route pressure near the entity. |
| `criticality_score` | Direct weighted graph degree normalized by the highest weighted degree in the snapshot. |
| `substitution_gap` | Dependency pressure not covered by explicit `substitutable_with` evidence. |
| `policy_risk` | `restricted_by` policy evidence directly or through graph context. |
| `event_pressure` | `impacted_by` risk-event evidence directly or through graph context. |
| `market_pressure` | WSTS-style `market_indicator` evidence connected through graph context. |

Overall score is a weighted average over evidence-backed available components:

```text
score =
  0.25 * exposure_score +
  0.25 * criticality_score +
  0.15 * substitution_gap +
  0.15 * policy_risk +
  0.10 * event_pressure +
  0.10 * market_pressure
```

If a component has no evidence for an entity, it is reported as unavailable and its weight is excluded from the denominator. If no evidence-backed components remain, no score is returned.

## Levels

| Score range | Level |
| --- | --- |
| `< 25` | `low` |
| `25-49.99` | `guarded` |
| `50-69.99` | `elevated` |
| `70-84.99` | `severe` |
| `>= 85` | `critical` |

## API Payload

`GET /api/v1/risk/entities/{entity_id}` returns the standardized API envelope. `data` includes:

- `node_id`
- `score`
- `level`
- `components`
- `evidence_refs`
- `feature_version`
- `graph_version`
- `source_manifest_id`
- `as_of_time`
- `fixture_graph`
- `warnings`

`GET /api/v1/risk/portfolio` returns a lightweight ranked list of fixture graph entities. It is intended for Entity Risk 360 entity selection, not portfolio optimization.

## Limitations

Risk Score v0 is a fixture graph readiness slice. It is useful for validating contracts, lineage, API wiring, and frontend workflow behavior. It must not be interpreted as a production semiconductor supply-chain risk score until public-source ingestion, source review, evidence graph expansion, and external validation are complete.
