# Connector Stage Coverage Audit

This audit ties existing fixture-first connectors to the L0-L11 semiconductor supply-chain stages. It documents coverage quality, not operational certification.

| Connector | Stages | Relationship support | Primary chart/table usage | Live status | Limitations |
| --- | --- | --- | --- | --- | --- |
| `sec_edgar_lite.py` | L2, L3, L4, L5, L6, L9, L10 | evidence context, disclosed dependencies, demand context | Evidence refs, product demand, risk components | disabled by default | Only sanitized disclosure summaries are API-visible. |
| `gdelt_semiconductor_lite.py` | L0, L1, L2, L4, L5, L6, L7, L8, L9, L10, L11 | event evidence, policy/hazard context, demand evidence | Event timelines, hazard exposure, evidence tables | disabled by default | News-derived confidence remains proxy-only. |
| `un_comtrade_semiconductor_trade_lite.py` | L1, L2, L7, L8 | trade dependency evidence | Trade flows, HHI, critical input tables | disabled by default | HS-code mappings are documented proxies. |
| `wits_trade_tariff_lite.py` | L1, L2 | tariff and trade-policy context | Trade concentration, material inputs | disabled by default | Tariff data is not a direct supply relationship. |
| `usgs_minerals_lite.py` | L1 | mineral supply and reserves proxy | Mineral HHI, critical inputs | disabled by default | Mineral-to-semiconductor dependency is proxy-only. |
| `usgs_earthquake_lite.py` | L5, L8, L10 | hazard exposure | Hazard exposure and event tables | disabled by default | Affected regions are normalized before API visibility. |
| `nga_world_port_index_lite.py` | L8 | logistics facility and route context | Logistics route exposure and facility table | disabled by default | Facility attributes are route context, not shipment volumes. |
| `ofac_sanctions_list_lite.py` | L0, L11 | restricted entity evidence | Compliance restriction tables | disabled by default | No circumvention or screening bypass advice is provided. |
| `consolidated_screening_list_lite.py` | L0, L11 | restricted entity evidence | Connector status and compliance tables | disabled by default | Registry/list evidence only. |
| `bis_export_controls_lite.py` | L0, L4, L11 | policy restriction evidence | Policy restriction impact and policy events | disabled by default | Legal interpretation is out of scope. |
| `federal_register_export_controls_lite.py` | L0, L4, L11 | export-control policy evidence | Policy timelines and restriction matrix | disabled by default | Rule summaries are sanitized. |
| `eto_supply_chain.py` | L1, L2, L4, L5, L7 | supply and production-dependency seed evidence | Dependency views, critical inputs, supplier concentration | disabled by default | Research fixture only. |
| `wsts_billings.py` | L5, L6, L9 | demand relationship and market pressure proxy | Demand pressure, supply-demand balance | disabled by default | Demand values are proxy summaries. |

## Source Gaps

- Stage L3 depends heavily on company disclosures and literature references; many non-US disclosures require manual upload.
- Stage L7 packaging capacity is represented as proxy service/capacity relationships rather than calibrated capacity.
- Stage L8 logistics has facility and route context but not production-grade route volume.
- Stage L1 mineral-to-semiconductor mapping remains a documented proxy.

All connector live modes remain disabled by default, fixture mode is required, and raw source payloads are excluded from API, frontend, reports, and exported summaries.
