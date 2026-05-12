import type { ReactNode } from "react";

export interface EvidenceTableProps {
  title?: string;
  rows?: Array<Record<string, unknown>>;
  columns?: string[];
  loading?: boolean;
  degraded?: boolean;
  limit?: number;
  metadata?: {
    graphVersion?: string | null;
    sourceManifestId?: string | null;
    warnings?: string[];
  };
  emptyLabel?: string;
}

export function DataTable({
  title,
  rows = [],
  columns,
  loading,
  degraded,
  limit = 50,
  metadata,
  emptyLabel = "No table data available.",
}: EvidenceTableProps) {
  const visibleRows = rows.slice(0, Math.max(1, limit));
  const visibleColumns = columns ?? inferColumns(visibleRows);
  return (
    <section className="table-frame" data-component="evidence-table">
      {title ? <h3>{title}</h3> : null}
      {loading ? <p className="muted">Loading table data...</p> : null}
      {!loading && visibleRows.length === 0 ? <p className="muted">{emptyLabel}</p> : null}
      {visibleRows.length ? (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>{visibleColumns.map((column) => <th key={column}>{column}</th>)}</tr>
            </thead>
            <tbody>
              {visibleRows.map((row, index) => (
                <tr key={String(row.id ?? row.edge_id ?? row.node_id ?? index)}>
                  {visibleColumns.map((column) => <td key={column}>{renderCell(row[column])}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      {degraded ? <p className="warning-text">Data source unavailable or degraded.</p> : null}
      {metadata ? (
        <p className="metadata-line">
          {metadata.graphVersion ? `graph_version=${metadata.graphVersion}` : null}
          {metadata.sourceManifestId ? ` source_manifest_id=${metadata.sourceManifestId}` : null}
          {metadata.warnings?.length ? ` warnings=${metadata.warnings.length}` : null}
        </p>
      ) : null}
    </section>
  );
}

function inferColumns(rows: Array<Record<string, unknown>>) {
  const columns = new Set<string>();
  rows.slice(0, 5).forEach((row) => Object.keys(row).slice(0, 8).forEach((key) => columns.add(key)));
  return [...columns];
}

function renderCell(value: unknown): ReactNode {
  if (value === null || value === undefined) return "unavailable";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return value.slice(0, 3).map(String).join(", ");
  return JSON.stringify(value);
}

