# Formula Source Registry

| Formula ref | Source principle | Implemented proxy |
| --- | --- | --- |
| `nist_sp_800_30_r1_likelihood_impact` | Risk combines likelihood and impact. | `score = 100 * likelihood * impact * vulnerability_modifier`. |
| `oecd_supply_chain_resilience_critical_dependency` | Critical dependencies combine importance, disruption risk, and substitution/diversification limits. | Critical dependency proxy from graph importance, supply/demand risk, and strategic node type. |
| `oecd_trade_dependency_hhi_concentration` | Concentration and significant dependency can be represented with HHI-style indicators. | HHI on `0_to_1` scale; low `<0.20`, moderate `0.20-<0.40`, high `>=0.40` as OECD-derived operational supply-chain thresholds, not official generic OECD labels and not DOJ/FTC antitrust bands. |
| `resilience_triangle_functionality_loss` | Resilience loss can be represented as area between baseline and degraded functionality over time. | Normalized integral over fixture functionality curve. |
| `multi_component_supply_chain_resilience_functionality_loss` | Supply-chain resilience may separate hazard-induced loss, opportunity gains, and non-hazard losses. | Current implementation handles hazard/disruption loss only; opportunity gains deferred. |
| `production_network_input_output_propagation` | Production-network input-output linkages create direct and indirect cascade effects. | Multi-hop graph propagation over dependency, route, policy, and event edges. |
| `production_shortage_interdependency_perfect_complements` | Short-term critical inputs can create bottleneck propagation. | `leontief_bottleneck` mode for `requires` and `depends_on` edges. |
| `recursive_production_shortage_interdependency` | Higher-order shortage propagation can recurse through production networks. | `psi_recursive` proxy mode for multi-hop stress testing. |
| `legacy_max_overwrite_baseline` | Legacy implementation retained for comparison only. | `max` propagation mode; not default. |
| `heuristic_baseline_unvalidated_component_weights` | No authoritative source. | Prior weighted component score; baseline only. |
