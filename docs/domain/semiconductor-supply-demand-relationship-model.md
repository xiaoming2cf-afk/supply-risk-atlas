# Semiconductor Supply, Demand, Dependency, And Evidence Relationships

The graph keeps four relationship classes separate:

- `SUPPLY_RELATIONSHIP`: supplier or service provider to supplied item, buyer, process stage, product grade, or fab.
- `DEMAND_RELATIONSHIP`: demand source to product grade or required capacity.
- `PRODUCTION_DEPENDENCY`: product, process, fab, package, or capacity node to required inputs or operating conditions.
- `EVIDENCE_CONTEXT`: inspection context only.

Supply edges can drive physical supply propagation. Demand edges are used only by demand-shock modeling. Production dependency edges carry criticality, substitutability, bottleneck, and propagation-mode hints. Evidence-context links must never be used as supply, demand, or production dependency edges.

`evidence_context_link` must carry:

- `derived_context: true`
- `not_supply_chain_dependency: true`
- `user_facing_label: evidence-context link`
- `warning: This is not a supply-chain dependency edge.`

Geography labels in relationship payloads must use `region:china_taiwan` / 中国台湾 with parent country context `country:CN` / 中国.

This model is research infrastructure for fixture/proxy and promoted-public-evidence analysis. It is not a production supplier database, not a live compliance engine, and not a financial-loss model.
