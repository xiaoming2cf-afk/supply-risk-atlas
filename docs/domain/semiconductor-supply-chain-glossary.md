# Semiconductor Supply-Chain Glossary

This glossary defines terms used by the fixture/proxy/promoted-public-evidence
graph. It is a research vocabulary for auditable modeling and user interfaces,
not a production operations dictionary.

## Relationship Terms

- **Supply relationship**: a supplier provides a physical input, equipment item,
  service, capacity proxy, IP, logistics service, or process capability to
  another firm, stage, product, or fab.
- **Demand relationship**: a downstream sector, region market, customer segment,
  or demand indicator creates evidence-bound demand pressure for a chip type or
  product grade.
- **Production dependency**: a product, process, fab, package, or capacity node
  requires inputs, conditions, process steps, equipment, materials, chemicals,
  IP, logistics context, policy context, or hazard context to function.
- **Evidence context link**: a non-causal inspection link between evidence and a
  node or edge. It is not a supply-chain dependency and must never be used for
  propagation, supply modeling, demand modeling, or bottleneck modeling.

## Node Terms

- **Supplier**: a company, facility, logistics provider, equipment supplier,
  material producer, or service provider that supplies an item or capability.
- **Buyer**: a company, facility, process stage, or product node receiving a
  supplied item or capability.
- **Supplied item**: equipment, material, chemical, IP, service, capacity,
  package, test service, logistics service, or product output associated with a
  supply relationship.
- **Demand source**: downstream sector, market indicator, public billing proxy,
  public event signal, company disclosure, or scenario demand shock input that
  indicates product demand.
- **Product grade**: a semiconductor output class such as advanced logic, HBM,
  DRAM, NAND, MCU, RF chip, power semiconductor, or automotive chip.
- **Critical input**: a material, chemical, equipment item, IP block, process
  stage, route, policy condition, or facility condition whose absence can
  constrain production.
- **Bottleneck**: a critical input or dependency with limited substitutability,
  high qualification time, high concentration, or strong propagation effect.
- **Substitutability**: the degree to which another input, supplier, process,
  route, or technology can replace a dependency in the fixture/proxy model.

## Metrics

- **HHI concentration**: Herfindahl-Hirschman Index proxy based on
  fixture/promoted shares. The platform uses it as a concentration signal, not a
  production market-share claim.
- **Demand pressure**: a bounded public-evidence proxy for demand intensity. It
  may come from public billings, public events, filings, or scenario inputs.
- **Supply capacity proxy**: a non-production proxy for relative supply
  availability, based on graph evidence and not private capacity data.
- **Shortage proxy**: a bounded difference or imbalance signal between demand
  evidence and supply/dependency evidence. It is not a forecast.

## Geography Terminology

The canonical region node is `region:china_taiwan`, displayed as `中国台湾`. Its
parent country context is `country:CN` / `中国`. Legacy external-source wording
may be recognized internally for normalization, but API-visible outputs, charts,
tables, reports, and docs use the canonical display.

## Limits

The platform remains fixture/proxy/promoted-public-evidence research
infrastructure. It has no live connectors enabled by default, does not expose
raw payloads, does not provide production readiness claims, and does not provide
restricted compliance workarounds.
