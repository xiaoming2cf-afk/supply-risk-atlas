# Semiconductor Supply-Chain Content Coverage

This note documents the fixture-first content layer added for stage-centered semiconductor analysis. The content is designed to make the product useful for demonstrations and review while preserving the platform boundary: public-evidence summaries, no live fetch on startup or tests, and no raw payload exposure.

## Coverage Scope

- National and regional exposure: country and region summaries for policy, macro, trade, logistics, minerals, hazard, and compliance context.
- Enterprise exposure: public-filing and annual-report/manual-upload summaries for representative companies across design, EDA/IP, equipment, materials, fabrication, packaging/testing, memory, analog, and downstream sectors.
- Industry value-chain exposure: layer summaries for EDA/IP, design, wafers, photoresist, specialty gases, CMP materials, lithography, etch, deposition, ion implantation, metrology, wafer fabrication, foundry, OSAT, advanced packaging, AI accelerators, automotive electronics, communications equipment, industrial control, medical electronics, and consumer/IoT demand.
- Relationship summaries: supply, demand, production dependency, and evidence-context classes remain separate. Evidence-context records are inspection links and are not propagation edges.
- Chokepoints: representative bottleneck summaries for lithography, advanced foundry, advanced packaging, memory, EDA/IP, critical minerals, logistics, policy screening, specialty chemicals, and downstream AI demand.

## Canonical Geography

- Region node: `region:china_taiwan`
- Display label: 中国台湾
- Parent country context: `country:CN` / 中国

External-source wording is represented only through sanitized summaries. API-visible content, chart/table labels, graph labels, and page copy must keep this canonical form.

## Source Families

- `national_policy_macro_public`: OECD, World Bank, BIS, Federal Register, OFAC/CSL, USGS, UN Comtrade, WITS, NGA ports.
- `enterprise_public_disclosure`: SEC EDGAR and annual-report/manual-upload summaries.
- `industry_public_fixture`: ETO/CSET, WSTS, GDELT, OpenAlex/Crossref summaries.

## API Surface

- `GET /api/v1/semiconductor/coverage`
- `GET /api/v1/semiconductor/value-chain/layers`
- `GET /api/v1/semiconductor/country-exposures`
- `GET /api/v1/semiconductor/entities`
- `GET /api/v1/semiconductor/entities/{entity_id}`
- `GET /api/v1/semiconductor/chokepoints`
- `GET /api/v1/semiconductor/relationships`
- `GET /api/v1/semiconductor/source-coverage`

Each response keeps graph/source/data-mode metadata and warnings for audit consumers. The web UI summarizes those details by default and keeps technical lineage in folded audit details.

The relationship endpoint exposes bounded, sanitized relationship summaries by `relationship_class`, `edge_type`, `source_id`, `target_id`, `layer_id`, `stage`, and source family. It standardizes `source_refs`, `evidence_refs`, validity window fields, and class-specific fields so supply, demand, production dependency, and evidence-context links remain distinct.

The source-coverage endpoint rolls up public source support by value-chain layer. It shows which source families support each layer, which relationship classes are represented, and where source gaps remain. Live fetch remains disabled; this is an index over reviewed fixture summaries, not a raw source-data feed.

## Current Limitations

- The dataset is a curated fixture for public-evidence research workflows.
- Live connector paths remain disabled by default.
- Coverage is intentionally summarized; it does not include raw filings, raw news text, raw trade tables, or bulk source payloads.
- Capacity, demand, lead-time, and substitution fields are proxy summaries unless a source-specific fixture explicitly supports the value.
