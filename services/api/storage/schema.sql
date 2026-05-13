PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_manifest (
    source_manifest_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    graph_version TEXT,
    source_count INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    status TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS source_status (
    source_id TEXT PRIMARY KEY,
    publisher TEXT NOT NULL,
    enabled_by_default INTEGER NOT NULL DEFAULT 0,
    connector_status TEXT NOT NULL,
    license_or_terms_summary TEXT NOT NULL,
    last_checked_at TEXT,
    freshness_sla_hours INTEGER,
    status TEXT NOT NULL,
    warnings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS raw_record_index (
    raw_record_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    as_of_time TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    raw_payload_summary TEXT NOT NULL,
    provenance_url TEXT NOT NULL,
    license_or_terms_ref TEXT NOT NULL,
    raw_payload_stored INTEGER NOT NULL DEFAULT 0,
    raw_payload_path TEXT
);

CREATE TABLE IF NOT EXISTS silver_entity (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    aliases_json TEXT NOT NULL DEFAULT '[]',
    country_code TEXT,
    sector_tags_json TEXT NOT NULL DEFAULT '[]',
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT
);

CREATE TABLE IF NOT EXISTS silver_event (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_time TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    location_json TEXT NOT NULL DEFAULT '{}',
    affected_entities_json TEXT NOT NULL DEFAULT '[]',
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT
);

CREATE TABLE IF NOT EXISTS market_indicator (
    indicator_id TEXT PRIMARY KEY,
    indicator_type TEXT NOT NULL,
    region TEXT NOT NULL,
    period TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL,
    as_of_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trade_flow (
    trade_flow_id TEXT PRIMARY KEY,
    reporter TEXT NOT NULL,
    partner TEXT NOT NULL,
    commodity_code TEXT NOT NULL,
    commodity_label TEXT NOT NULL,
    flow_type TEXT NOT NULL,
    period TEXT NOT NULL,
    value REAL NOT NULL,
    quantity REAL,
    unit TEXT,
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS policy_event (
    policy_event_id TEXT PRIMARY KEY,
    jurisdiction TEXT NOT NULL,
    policy_type TEXT NOT NULL,
    effective_date TEXT,
    affected_items_json TEXT NOT NULL DEFAULT '[]',
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    compliance_note TEXT NOT NULL,
    confidence REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS logistics_node (
    logistics_node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    name TEXT NOT NULL,
    country_code TEXT,
    latitude REAL,
    longitude REAL,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS hazard_event (
    hazard_event_id TEXT PRIMARY KEY,
    hazard_type TEXT NOT NULL,
    event_time TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    magnitude_or_severity REAL,
    affected_region TEXT NOT NULL,
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS graph_snapshot (
    graph_version TEXT PRIMARY KEY,
    source_manifest_id TEXT NOT NULL,
    ontology_version TEXT NOT NULL,
    as_of_time TEXT NOT NULL,
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,
    node_count_by_type_json TEXT NOT NULL DEFAULT '{}',
    edge_count_by_type_json TEXT NOT NULL DEFAULT '{}',
    quality_report_json TEXT NOT NULL DEFAULT '{}',
    warnings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS graph_node (
    graph_version TEXT NOT NULL,
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    source_refs_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    PRIMARY KEY (graph_version, node_id),
    FOREIGN KEY (graph_version) REFERENCES graph_snapshot(graph_version) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS graph_edge (
    graph_version TEXT NOT NULL,
    edge_id TEXT NOT NULL,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    weight REAL NOT NULL,
    confidence REAL NOT NULL,
    attributes_json TEXT NOT NULL DEFAULT '{}',
    provenance_refs_json TEXT NOT NULL DEFAULT '[]',
    evidence_text_summary TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    PRIMARY KEY (graph_version, edge_id),
    FOREIGN KEY (graph_version) REFERENCES graph_snapshot(graph_version) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS graph_view_cache (
    cache_key TEXT PRIMARY KEY,
    graph_version TEXT NOT NULL,
    view_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    warnings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS run_record (
    run_id TEXT PRIMARY KEY,
    run_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL,
    graph_version TEXT,
    source_manifest_id TEXT,
    request_hash TEXT,
    summary_json TEXT NOT NULL,
    warnings_json TEXT NOT NULL DEFAULT '[]',
    evidence_refs_json TEXT NOT NULL DEFAULT '[]',
    versions_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS report_record (
    report_id TEXT PRIMARY KEY,
    report_run_id TEXT,
    created_at TEXT NOT NULL,
    format TEXT NOT NULL,
    graph_version TEXT,
    source_manifest_id TEXT,
    report_json TEXT,
    report_markdown TEXT,
    content_hash TEXT NOT NULL,
    warnings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS audit_event (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    event_type TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    endpoint TEXT,
    request_hash TEXT,
    status TEXT NOT NULL,
    warnings_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS validation_artifact (
    artifact_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    graph_version TEXT,
    source_manifest_id TEXT,
    config_hash TEXT NOT NULL,
    seed INTEGER,
    artifact_json TEXT NOT NULL,
    artifact_csv_path TEXT,
    warnings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_raw_record_index_source ON raw_record_index(source_id);
CREATE INDEX IF NOT EXISTS idx_run_record_created_at ON run_record(created_at);
CREATE INDEX IF NOT EXISTS idx_report_record_created_at ON report_record(created_at);
CREATE INDEX IF NOT EXISTS idx_graph_node_type ON graph_node(graph_version, node_type);
CREATE INDEX IF NOT EXISTS idx_graph_edge_type ON graph_edge(graph_version, edge_type);
