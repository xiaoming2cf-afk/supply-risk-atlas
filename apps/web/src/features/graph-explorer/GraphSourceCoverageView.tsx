import type { GraphSourceCoverageData } from "@supply-risk/shared-types";
import { formatDisplayLabel, formatDisplayValue, formatSourceDisplayRef } from "../common/displayLabels";

export function GraphSourceCoverageView({
  endpointData,
}: {
  endpointData?: unknown;
  view?: unknown;
}) {
  const sourceCoverage = (endpointData as GraphSourceCoverageData | undefined)?.source_coverage;
  const rows = Array.isArray((sourceCoverage as Record<string, unknown> | undefined)?.rows)
    ? ((sourceCoverage as { rows: Array<Record<string, unknown>> }).rows ?? [])
    : [];
  const nodeCoverage = (sourceCoverage as Record<string, unknown> | undefined)?.node_catalog_coverage as
    | Record<string, unknown>
    | undefined;

  return (
    <div className="graph-v3-panel graph-v3-source-coverage-panel">
      <div className="section-kicker">Source coverage</div>
      <p className="inspector-note">Coverage is a transparency table and does not render the full graph.</p>
      {nodeCoverage ? (
        <div className="graph-view-summary">
          <span>{formatDisplayLabel("catalog_node_count")}: {String(nodeCoverage.catalog_node_count ?? "n/a")}</span>
          <span>{formatDisplayLabel("covered_catalog_node_count")}: {String(nodeCoverage.covered_catalog_node_count ?? "n/a")}</span>
          <span>{formatDisplayLabel("source_status")}: {String(formatDisplayValue(String(nodeCoverage.status ?? "partial")))}</span>
        </div>
      ) : null}
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>Evidence records</th>
          </tr>
        </thead>
        <tbody>
          {rows.length ? (
            rows.slice(0, 16).map((row, index) => (
              <tr key={String(row.source_id ?? index)}>
                <td>{formatSourceCell(row.source_id ?? "source_ref")}</td>
                <td>
                  {String(
                    (row as Record<string, unknown>).reference_count ??
                      (row as Record<string, unknown>).count ??
                      0,
                  )}
                </td>
              </tr>
            ))
          ) : (
            <tr className="unavailable-preview" data-preview-state="source_coverage_endpoint_unavailable">
              <td colSpan={2}>Backend source coverage data unavailable; authoritative rows are hidden.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function formatSourceCell(value: unknown) {
  if (typeof value !== "string") return "Public evidence source";
  return formatSourceDisplayRef(value) || String(formatDisplayValue(value));
}
