# Stage Source Coverage Matrix

This matrix organizes the fixture/proxy/promoted public-evidence layer around semiconductor supply-chain stages L0-L11. It is a planning and runtime-routing artifact, not a production data claim.

The canonical machine-readable file is `configs/sources/stage_source_coverage_matrix.yaml`.

## Coverage Rules

- Every stage has at least two public source candidates.
- Every stage has at least one graph view, chart, and table.
- Live connector fetches remain disabled by default.
- Fixture mode is required for every stage; source records are exposed only as sanitized summaries and lineage.
- Source coverage is counted only from authoritative fixture/promoted source records. `unavailable_preview` UI states and unavailable relationship endpoints never count as stage coverage.
- Evidence-context links are inspection links only and must not be used as supply, demand, or production-dependency edges.
- Geography labels use canonical `region:china_taiwan` with the configured display label and parent `country:CN` where that region appears.

## Source Family Legend

| Source family | Meaning | Live status |
| --- | --- | --- |
| `national_policy_macro_public` | National, multilateral, policy, macro, trade, sanctions, hazard, and logistics public records. | Disabled by default; fixture summaries only. |
| `enterprise_public_disclosure` | Public company filings, sanitized disclosure summaries, and reviewed public annual-report uploads. | Disabled by default; fixture/manual-review summaries only. |
| `industry_public_fixture` | Public industry, market, literature, and event-summary sources promoted through fixtures. | Disabled by default; fixture summaries only. |

## Stage Summary

| Stage | Source families | Source status | Node focus | Relationship classes | Primary chart/table usage | Gaps and proxy limits | Live status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L0 | National/policy/macro, industry fixture | `fixture_promoted_public_evidence` | Countries, policy regimes, macro indicators, export controls, sanctions | Production dependency, evidence context | Policy timelines, restriction impact, compliance matrix/tables | Scope and effective dates are fixture summaries; no legal interpretation. | Disabled by default |
| L1 | National/policy/macro, industry fixture | `incomplete_fixture_proxy` | Minerals, raw materials, mining/refining countries | Production dependency, evidence context | HHI, trade concentration, mineral input tables | Mineral-to-semiconductor mappings and shares are documented proxies. | Disabled by default |
| L2 | Industry fixture, national/policy/macro, enterprise disclosure | `fixture_promoted_public_evidence` | Wafers, chemicals, gases, masks, substrates, CMP inputs | Supply relationship, production dependency, evidence context | Bottleneck, supplier concentration, material input tables | Supplier shares and qualification times are proxies unless disclosed. | Disabled by default |
| L3 | Enterprise disclosure, industry fixture | `incomplete_fixture_proxy` | Design firms, EDA tools, IP, fabless firms, IDMs | Supply relationship, production dependency, evidence context | Risk components and evidence-reference tables | Private IP/license scope and non-US disclosures require public sanitized summaries. | Disabled by default |
| L4 | Industry fixture, national/policy/macro, enterprise disclosure | `fixture_promoted_public_evidence` | Equipment, suppliers, categories, components, process stages | Supply relationship, production dependency, evidence context | Policy impact, critical input, equipment supplier tables | Equipment capacity shares are not calibrated. | Disabled by default |
| L5 | Industry fixture, enterprise disclosure, national/policy/macro | `fixture_promoted_public_evidence` | Fabs, foundries, process stages, nodes, capacity, hazards | Production dependency, supply relationship, evidence context | Hazard exposure, functionality curve, fab process tables | Capacity, utilization, and impact severity are fixture proxies. | Disabled by default |
| L6 | Industry fixture, enterprise disclosure | `fixture_promoted_public_evidence` | Product grades, chip types, downstream products, demand indicators | Demand relationship, production dependency, evidence context | Demand pressure, supply-demand balance, product demand tables | Product-level demand values are aggregated public proxies. | Disabled by default |
| L7 | Industry fixture, enterprise disclosure, national/policy/macro | `incomplete_fixture_proxy` | OSATs, packaging stages, substrates, testing stages | Supply relationship, production dependency, evidence context | Supplier concentration, packaging capacity proxy, service tables | Service evidence is separate from capacity proxy charts. | Disabled by default |
| L8 | National/policy/macro, industry fixture | `incomplete_fixture_proxy` | Ports, airports, logistics routes, shipping lanes, customs regions, hazards | Production dependency, evidence context | Hazard exposure, route exposure, logistics facility tables | Route volumes, lane shares, and routing probabilities are absent. | Disabled by default |
| L9 | Industry fixture, enterprise disclosure | `fixture_promoted_public_evidence` | Downstream sectors, customer industries, demand indicators, products | Demand relationship, evidence context | Demand pressure, balance, demand mix tables | Demand values are public aggregate proxies, not order books. | Disabled by default |
| L10 | Industry fixture, national/policy/macro, enterprise disclosure | `fixture_promoted_public_evidence` | Risk, hazard, market, factory, cyber, labor events | Production dependency, evidence context | Hazard timelines, policy timelines, evidence tables | Event confidence and severity are proxy-only. | Disabled by default |
| L11 | National/policy/macro, industry fixture | `fixture_promoted_public_evidence` | Policies, sanctions, restricted items/entities, compliance risk | Production dependency, evidence context | Restriction impact, compliance matrix/tables | Registry matches are sanitized summaries; legal interpretation is out of scope. | Disabled by default |

## Source Status Legend

| Source status | Meaning |
| --- | --- |
| `fixture_promoted_public_evidence` | The stage has fixture/promoted public-evidence records that can support sanitized charts, tables, and graph relationships. |
| `incomplete_fixture_proxy` | The stage has useful fixture evidence, but important values remain proxy-only or incomplete. |
| `unavailable_controlled` | The stage must render a controlled unavailable state rather than authoritative rows. |
| `deferred_registry_only` | The stage/source is documented for future registry use but is not fetchable or authoritative. |

## Limitations

The matrix intentionally records source gaps, proxy limitations, and fixture-only controls. Supplier shares, capacity values, qualification times, route volumes, event severity, and product demand values are proxy summaries unless a source explicitly supports them. No row should be interpreted as operational certification.
