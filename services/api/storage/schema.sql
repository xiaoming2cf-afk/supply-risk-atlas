PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_manifest (
    source_manifest_id TEXT PRIMARY KEY,
    graph_version TEXT,
    as_of_time TEXT,
    source_status TEXT NOT NULL,
    license_terms_json TEXT NOT NULL DEFAULT '[]',
    manifest_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_record_index (
    raw_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    payload_hash TEXT NOT NULL,
    raw_payload_summary TEXT NOT NULL,
    provenance_url TEXT NOT NULL,
    license_or_terms_ref TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    as_of_time TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver_entity (
    entity_id TEXT PRIMARY KEY,
    source_manifest_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    source_refs_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS silver_event (
    event_id TEXT PRIMARY KEY,
    source_manifest_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_time TEXT NOT NULL,
    summary TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    source_refs_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_snapshot (
    graph_version TEXT PRIMARY KEY,
    source_manifest_id TEXT NOT NULL,
    as_of_time TEXT NOT NULL,
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,
    snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_node (
    graph_version TEXT NOT NULL,
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    node_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (graph_version, node_id),
    FOREIGN KEY (graph_version) REFERENCES graph_snapshot(graph_version) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS graph_edge (
    graph_version TEXT NOT NULL,
    edge_id TEXT NOT NULL,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    edge_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (graph_version, edge_id),
    FOREIGN KEY (graph_version) REFERENCES graph_snapshot(graph_version) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS run_record (
    run_id TEXT PRIMARY KEY,
    run_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    graph_version TEXT,
    source_manifest_id TEXT,
    status TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    warnings_json TEXT NOT NULL DEFAULT '[]',
    versions_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS report_record (
    report_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    graph_version TEXT,
    source_manifest_id TEXT,
    format TEXT NOT NULL,
    report_json TEXT NOT NULL,
    report_markdown TEXT,
    warnings_json TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS audit_event (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    entity_id TEXT,
    summary_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_raw_record_index_source ON raw_record_index(source_id);
CREATE INDEX IF NOT EXISTS idx_run_record_created_at ON run_record(created_at);
CREATE INDEX IF NOT EXISTS idx_report_record_created_at ON report_record(created_at);

