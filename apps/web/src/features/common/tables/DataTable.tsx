import type { ReactNode } from "react";
import { AuditDetails, MetadataSummary } from "../AuditDetails";
import { formatDisplayLabel, formatDisplayValue, formatNodeDisplayRef, formatSourceDisplayRef } from "../displayLabels";

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
      {title ? <h3>{formatDisplayLabel(title)}</h3> : null}
      {loading ? <p className="muted">Loading table data...</p> : null}
      {!loading && visibleRows.length === 0 ? <p className="muted">{emptyLabel}</p> : null}
      {visibleRows.length ? (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>{visibleColumns.map((column) => <th key={column}>{formatDisplayLabel(column)}</th>)}</tr>
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
        <>
          <MetadataSummary
            items={[
              { label: "Public evidence mode", tone: degraded ? "degraded" : "default" },
              metadata.warnings?.length ? { label: `${metadata.warnings.length} warning(s)`, tone: "warning" } : { label: "" },
            ]}
          />
          <AuditDetails
            items={[
              { label: "graph_version", value: metadata.graphVersion },
              { label: "source_manifest_id", value: metadata.sourceManifestId },
            ]}
            warnings={metadata.warnings}
          />
        </>
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
  if (typeof value === "string") return formatPrimaryValue(value);
  if (typeof value === "number" || typeof value === "boolean") return String(formatDisplayValue(value));
  if (Array.isArray(value)) return renderArrayCell(value);
  return "Structured metadata";
}

function renderArrayCell(values: unknown[]) {
  const rendered = values.slice(0, 3).map(renderArrayItem).filter(Boolean);
  if (rendered.length === 0) return "Structured metadata";
  const suffix = values.length > rendered.length ? ` +${values.length - rendered.length} more` : "";
  return `${rendered.join(", ")}${suffix}`;
}

function renderArrayItem(value: unknown) {
  if (value === null || value === undefined) return "";
  if (typeof value === "string") return formatPrimaryValue(value);
  if (typeof value === "number" || typeof value === "boolean") return String(formatDisplayValue(value));
  if (!Array.isArray(value) && typeof value === "object") {
    const record = value as Record<string, unknown>;
    const id =
      record.source_record_id ??
      record.evidence_id ??
      record.ref_id ??
      record.node_id ??
      record.edge_id ??
      record.id ??
      record.label ??
      record.name;
    const source = record.source_id ?? record.source;
    if (source && id) return `${formatPrimaryValue(String(source))} evidence`;
    if (id) return formatPrimaryValue(String(id));
    if (source) return formatPrimaryValue(String(source));
  }
  return "Structured metadata";
}

function formatPrimaryValue(value: string) {
  return formatNodeDisplayRef(value) || formatSourceDisplayRef(value) || String(formatDisplayValue(value));
}
