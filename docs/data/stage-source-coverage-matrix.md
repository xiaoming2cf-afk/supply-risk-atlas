# Stage Source Coverage Matrix

This matrix organizes the fixture/proxy/promoted public-evidence layer around semiconductor supply-chain stages L0-L11. It is a planning and runtime-routing artifact, not a production data claim.

The canonical machine-readable file is `configs/sources/stage_source_coverage_matrix.yaml`.

## Coverage Rules

- Every stage has at least two public source candidates.
- Every stage has at least one graph view, chart, and table.
- Live connector fetches remain disabled by default.
- Evidence-context links are inspection links only and must not be used as supply, demand, or production-dependency edges.
- Geography labels use `region:china_taiwan` with display `中国台湾` and parent `country:CN` / `中国` where that region appears.

## Stage Summary

| Stage | Focus | Primary evidence families | Main views |
| --- | --- | --- | --- |
| L0 | Policy and macro | OECD, BIS, Federal Register, OFAC/CSL, World Bank | PolicyMacroGraphView |
| L1 | Critical minerals and raw materials | USGS, UN Comtrade, WITS, GDELT | MineralDependencyGraphView |
| L2 | Materials and chemicals | ETO/CSET, UN Comtrade, WITS, SEC, GDELT | MaterialChemicalDependencyGraphView |
| L3 | Design, EDA, and IP | SEC, company reports, OECD, OpenAlex/Crossref | DesignIPDependencyGraphView |
| L4 | Equipment | ETO/CSET, BIS, Federal Register, SEC, GDELT | EquipmentProcessDependencyGraphView |
| L5 | Fabrication and front-end process | ETO/CSET, company reports, USGS earthquake, WSTS | FabProcessGraphView |
| L6 | Products and chip types | WSTS, SEC, company reports, GDELT | ProductDemandGraphView |
| L7 | Packaging and testing | ETO/CSET, company reports, GDELT, UN Comtrade | PackagingTestingGraphView |
| L8 | Logistics, ports, and routes | NGA World Port Index, GDELT, USGS earthquake, UN Comtrade | LogisticsRouteGraphView |
| L9 | Downstream demand | WSTS, SEC, GDELT, company reports | DownstreamDemandGraphView |
| L10 | Risk events | GDELT, USGS earthquake, SEC, company reports | EventTimelineGraphView |
| L11 | Compliance | BIS, Federal Register, OFAC, CSL | ComplianceRiskGraphView |

## Limitations

The matrix intentionally records source gaps and fixture limitations. Supplier shares, capacity values, qualification times, and product demand values are proxy summaries unless a source explicitly supports them. No row should be interpreted as operational certification.
