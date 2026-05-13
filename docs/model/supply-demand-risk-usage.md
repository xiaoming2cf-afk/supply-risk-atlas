# Supply-Demand Risk Usage

This note describes how supply, demand, production dependency, and evidence
context relationships are used by model-facing workflows. It does not introduce
new model formulas or production-readiness claims.

## Relationship Classes In Model Workflows

- Supply disruption views use `SUPPLY_RELATIONSHIP` edges and their supplied
  item, lead-time, substitutability, and concentration metadata.
- Demand spike views use `DEMAND_RELATIONSHIP` edges and demand-pressure proxy
  metadata.
- Production dependency propagation uses `PRODUCTION_DEPENDENCY` edges with
  criticality, substitutability, bottleneck, and propagation-mode metadata.
- Evidence inspection uses `EVIDENCE_CONTEXT` links only for traceability.

`EVIDENCE_CONTEXT` links must never be used as physical propagation edges.

## Supply Disruption

A supply disruption starts from a supplier, supplied item, service, capability,
route, or capacity proxy. The modeled effect follows supply relationships and
production dependencies that depend on the supplied item. HHI concentration can
increase severity when supplier diversity is limited.

## Demand Spike

A demand spike starts from a downstream sector, market indicator, or scenario
input. It follows demand relationships to product grades and then compares
demand pressure against supply/dependency proxies. It does not imply a supplier
failure.

## Production Dependency Propagation

A production dependency event starts from a required input or condition such as
equipment, material, chemical, IP, logistics context, policy context, utility
condition, hazard exposure, or process stage. Propagation uses bottleneck and
substitutability metadata to identify constrained downstream nodes.

## Optimizer Usage

Intervention categories should remain aligned with relationship classes:

- supplier diversification for supply relationships
- demand smoothing for demand relationships
- critical input backup for production dependencies
- logistics redundancy for route dependencies
- compliance monitoring for policy context

The optimizer must not treat evidence context links as intervention targets.

## Geography And Output Safety

All model-facing outputs use `region:china_taiwan` with display label `中国台湾`
and parent context `country:CN` / `中国`. Reports, exports, charts, and tables
must keep `graph_version`, `source_manifest_id`, `data_mode`, `graph_mode`,
warnings, source refs, and calibration status.

## Limits

The relationship model is fixture/proxy/promoted-public-evidence infrastructure.
It is not a financial-loss engine, not a production decision system, and not a
live operational connector.
