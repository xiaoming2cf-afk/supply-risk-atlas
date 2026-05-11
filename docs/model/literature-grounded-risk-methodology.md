# Literature-Grounded SemiRisk Methodology

This document separates source principles from implemented fixture proxy formulas. The current platform is not calibrated and is not production-ready.

## Source Principles

- NIST SP 800-30 Rev. 1 states that risk assessment considers threat likelihood and adverse impact. SemiRisk implements this as `score = 100 * likelihood * impact * vulnerability_modifier`. Source: [NIST CSRC](https://csrc.nist.gov/pubs/sp/800/30/r1/final).
- OECD supply-chain resilience work frames critical dependencies around importance, disruption risk, and diversification or substitution limits. SemiRisk maps this to critical dependency and vulnerability proxy fields. Source: [OECD Supply Chain Resilience Review](https://www.oecd.org/content/dam/oecd/en/publications/reports/2025/06/oecd-supply-chain-resilience-review_9930d256/94e3a8ea-en.pdf).
- OECD trade dependency work uses concentration-style indicators, including HHI-style concentration, for import dependency analysis. SemiRisk uses HHI on a `0_to_1` scale with low `<0.20`, moderate `0.20-<0.40`, and high `>=0.40` operational bands for supply-chain/trade-dependency analysis. These bands are OECD-derived platform thresholds, not universal official OECD low/moderate/high labels and not DOJ/FTC antitrust bands. Sources: [OECD economic security chapter](https://www.oecd.org/en/publications/economic-security-in-a-changing-world_4eac89c7-en/full-report/economic-security-and-vulnerabilities-in-international-supply-chains_dc88aefa.html), [OECD trade dependencies paper](https://www.oecd.org/en/publications/towards-demystifying-trade-dependencies_2a1a2bb9-en.html).
- The resilience triangle represents loss of functionality over time. SemiRisk implements a normalized resilience integral loss over fixture functionality curves.
- Supply-chain resilience literature distinguishes hazard-induced cumulative functionality loss, opportunity-induced gains, and non-hazard losses. SemiRisk currently implements only hazard/disruption-style losses and documents opportunity gains as deferred. Source: [U.S. DOT ROSA record](https://rosap.ntl.bts.gov/view/dot/68155).
- Production-network literature shows that input-output linkages create direct and indirect cascade effects. SemiRisk uses graph propagation over dependency edges. Source: [AEA JEP production networks](https://www.aeaweb.org/articles?id=10.1257%2Fjep.28.4.23).
- Inoperability and dynamic input-output methods model functionality loss and recovery. SemiRisk uses a bounded fixture proxy for functionality loss and recovery. Source: [MDPI IIM paper](https://www.mdpi.com/2227-7099/8/4/109).
- DEA common weights require calibration or data-derived estimation. SemiRisk does not treat hard-coded weights as authoritative common weights.

## Implemented Proxy Status

All current formulas are deterministic fixture proxies with `calibration_status = fixture_proxy_not_calibrated`. They are suitable for testing contracts, lineage, and workflow behavior, not production decisions.
