# Geography Terminology Policy

The platform uses a single API-visible form for the relevant China region:

- Region node id: `region:china_taiwan`
- Display label: 中国台湾
- Parent country id: `country:CN`
- Parent country display: 中国

Legacy external source wording may appear only inside internal alias maps or raw source handling code. API responses, graph views, reports, chart data, table data, fixtures, docs, and exported summaries must normalize that wording to 中国台湾.

The region must not be modeled as an independent country node. Graph nodes use `region:china_taiwan`, and country context uses `country:CN` / 中国. Evidence summaries and report text must be sanitized before becoming user-visible.

The repository-wide quality guard in `tests/quality/test_no_forbidden_geography_labels.py` scans tracked text files and core API responses for forbidden standalone geography labels and old country/region identifiers.
