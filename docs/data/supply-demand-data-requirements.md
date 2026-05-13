# Supply-Demand Data Requirements

This document defines minimum data requirements for relationship-aware public
evidence records. The goal is to keep graph, chart, table, and report outputs
traceable without exposing raw payloads.

## Common Requirements

Every API-visible record must include:

- `graph_version`
- `source_manifest_id`
- `data_mode`
- `graph_mode`
- `source_refs`
- `warnings`
- `confidence`
- `valid_from`
- `valid_to` when available

Raw payload bodies, private diagnostics, internal local paths, secrets, cookies,
authorization headers, and personal data are not API-visible. External text must
be summarized and sanitized before it reaches graph, table, chart, report, or
export output.

## Supply Relationship Records

Required fields:

- `relationship_class: SUPPLY_RELATIONSHIP`
- `edge_type`
- `supplier_id`
- `buyer_or_stage_id` when available
- `supplied_item_id`
- `supplied_item_type`
- `relationship_scope`
- `share_or_capacity_proxy` when evidence supports it
- `lead_time_days` when evidence supports it
- `qualification_time_days` when evidence supports it
- `substitution_available` when evidence supports it
- `source_refs`
- `confidence`

Supply relationship table and chart outputs may include supplier concentration,
HHI proxy, supplied-item counts, source coverage, and warnings. They must not
claim private contracts, audited production capacity, or production readiness.

## Demand Relationship Records

Required fields:

- `relationship_class: DEMAND_RELATIONSHIP`
- `edge_type`
- `demand_source_id`
- `product_grade_id`
- `region` when evidence supports it
- `period` when evidence supports it
- `demand_proxy_type`
- `demand_value` when evidence supports it
- `demand_growth_proxy` when evidence supports it
- `source_refs`
- `confidence`

Demand records support demand pressure, product demand, and supply-demand
balance views. They must not be used as supplier edges because they do not
represent provision of a supplied item.

## Production Dependency Records

Required fields:

- `relationship_class: PRODUCTION_DEPENDENCY`
- `edge_type`
- `dependency_source_id`
- `dependency_target_id`
- `dependency_type`
- `criticality`
- `substitutability`
- `bottleneck_flag`
- `propagation_mode_hint`
- `source_refs`
- `confidence`

Production dependency records support critical-input, bottleneck, and
propagation views. They must remain separate from evidence context links.

## Evidence Context Records

Required fields:

- `relationship_class: EVIDENCE_CONTEXT`
- `edge_type: evidence_context_link`
- `derived_context: true`
- `not_supply_chain_dependency: true`
- `user_facing_label: evidence-context link`
- `warning: This is not a supply-chain dependency edge.`
- `source_refs`
- `confidence`

Evidence context records may appear in inspectors and evidence tables only.
They must not drive propagation, optimization, HHI, demand pressure, shortage
proxy, or production dependency scoring.

## Geography Normalization

Records with geography must normalize the relevant region to
`region:china_taiwan` and display it as `中国台湾`. Country context is
`country:CN` / `中国`. Source text that uses other wording is normalized before
API-visible summaries are stored or emitted.

## Retention And Storage

Persistent storage keeps hashes, summaries, source refs, provenance URLs,
license or terms references, sanitized run summaries, and sanitized reports.
It does not store full raw payloads by default.
