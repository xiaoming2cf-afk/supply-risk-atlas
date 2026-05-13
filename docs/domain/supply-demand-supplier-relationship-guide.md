# Supply, Demand, And Supplier Relationship Guide

This guide explains how the graph separates supply, demand, production
dependency, and evidence context relationships. Keeping these classes separate is
required for auditability and for preventing evidence links from becoming model
edges.

## Supply Relationships

A supply relationship describes a supplier providing an item or capability. The
direction is from supplier to supplied item, buyer, stage, product, or fab.

Required fields include `supplier_id`, `supplied_item_id`,
`supplied_item_type`, `relationship_scope`, `source_refs`, `confidence`,
`valid_from`, and optional lead-time or substitution proxies when evidence is
available.

Supply relationships support supplier concentration and HHI analysis. They do
not imply audited production capacity or private contract data.

## Demand Relationships

A demand relationship describes demand pressure from a downstream sector, market
indicator, region market, or scenario input to a product grade. The direction is
from demand source to product grade.

Required fields include `demand_source_id`, `product_grade_id`,
`demand_proxy_type`, `source_refs`, `confidence`, and validity dates. Demand
edges must not be treated as supplier edges because they describe pull signals,
not provision of a supplied item.

## Production Dependencies

A production dependency describes a requirement for a process, product, package,
fab, or capacity node to function. Examples include equipment, chemicals,
materials, IP, logistics context, policy context, and hazard exposure.

Required fields include `dependency_source_id`, `dependency_target_id`,
`dependency_type`, `criticality`, `substitutability`, `bottleneck_flag`,
`propagation_mode_hint`, `source_refs`, and validity dates.

Production dependencies are the primary graph class for bottleneck propagation.
Supply disruptions and production dependency failures propagate differently:
supply disruptions begin at supplier/item provision edges, while production
dependencies describe required conditions or inputs within the production chain.

## Demand Shocks

Demand shocks begin with downstream demand sources and product grades. They
should use demand relationships and demand-pressure proxies. They must not be
modeled as supplier outages or as physical input failures.

## Evidence Context Links

An evidence context link is a non-causal inspection aid. It connects an evidence
record to a node or edge for traceability only.

Required metadata:

- `derived_context: true`
- `not_supply_chain_dependency: true`
- `user_facing_label: evidence-context link`
- `warning: This is not a supply-chain dependency edge.`

Evidence context links must never be used for propagation, supplier
concentration, demand pressure, production dependency scoring, optimization, or
shortage proxy calculations.

## Geography Policy

The canonical region node for the relevant region is `region:china_taiwan` with
display label `中国台湾` and parent context `country:CN` / `中国`. API responses,
reports, charts, tables, source summaries, and user-facing docs must use this
canonical form.

## Research Limits

All relationship outputs are fixture/proxy/promoted-public-evidence summaries.
They are not production data, not financial-loss estimates, and not calibrated
capacity or demand forecasts.
