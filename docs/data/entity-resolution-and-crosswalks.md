# Entity Resolution And Crosswalks

The entity-resolution helpers in `sra_core.entity_resolution` normalize public
source mentions into stable graph identifiers without fabricating relationships.

## Resolution Result

Every resolver returns:

- `resolved_id`
- `confidence`
- `method`
- `source_refs`
- optional `warning`

Low-confidence or unknown mentions remain unresolved with
`unresolved_low_confidence_mention`.

## Crosswalks

Company aliases include TSMC, ASML, Samsung Electronics, Intel, and Applied
Materials.

Country aliases include 中国台湾/中国台湾/TW, United States/USA/US, South
Korea/Korea Rep./KR, Netherlands/NL, and Japan/JP.

Commodity mappings cover semiconductor-related HS proxy codes including
integrated circuits, memory, semiconductor manufacturing machines, doped
chemical elements, photoresist-related proxies, and high-purity silicon proxies.
These are public-data proxies and not complete supply-chain truth.

Policy item mappings cover EUV/lithography, semiconductor manufacturing
equipment, advanced computing chips, HBM/memory, photoresist, and chemicals.

## Safety Limits

Resolution never creates supply-chain relationships by itself. It only returns a
candidate identifier, confidence, and warning. Graph edges must be created by a
separate provenance-checked graph pipeline.
