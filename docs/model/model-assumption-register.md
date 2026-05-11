# Model Assumption Register

| Area | Assumption | Status | Warning |
| --- | --- | --- | --- |
| Risk score | Default score uses likelihood x impact x vulnerability over fixture evidence. | Fixture proxy, not calibrated | `fixture_proxy_not_calibrated` |
| Heuristic baseline | Prior component weights are retained only for comparison. | Not calibrated | `heuristic_weights:not_literature_calibrated` |
| Concentration | Supplier/country shares are inferred from fixture graph edge weights and confidence. | Fixture proxy | `fixture_proxy_supplier_shares` |
| HHI thresholds | Low/moderate/high HHI bands are OECD-derived operational supply-chain thresholds, not universal official OECD labels and not DOJ/FTC antitrust bands. | Platform threshold policy | `oecd_derived_supply_chain` |
| Loss | Functionality curves use normalized fixture capacity/demand proxies. | Fixture proxy | `not_financial_loss` |
| Propagation | Critical input chains use bottleneck logic; event/policy exposure uses noisy-or. | Deterministic proxy | `fixture_graph:not_production_ready` |
| Optimization | Before/after metrics rerun bounded forward Monte Carlo. | Fixture proxy | `not_production_decision` |
| Reports | Reports disclose methodology and formula refs, but refs are source principles, not validated coefficients. | Required disclosure | `not_production_decision` |
