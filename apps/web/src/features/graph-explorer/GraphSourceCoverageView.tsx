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
  const supportedSourceSummary = supportedSourcesText(rows);
  const coverageStatusSummary = coverageStatusText(nodeCoverage?.status, rows.length);
  const reviewAction = coverageReviewAction(rows, nodeCoverage);

  return (
    <div className="graph-v3-panel graph-v3-source-coverage-panel">
      <div className="section-kicker">Source coverage</div>
      <p className="inspector-note">Coverage is a transparency table and does not render the full graph.</p>
      <div className="graph-view-summary">
        <span>Supported by: {supportedSourceSummary}</span>
        <span>{coverageStatusSummary}</span>
        <span>Next review: {reviewAction}</span>
      </div>
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
              <td colSpan={2}>Source coverage data is temporarily unavailable; public evidence coverage still needs review.</td>
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

function supportedSourcesText(rows: Array<Record<string, unknown>>) {
  const labels = rows
    .slice(0, 4)
    .map((row) => formatSourceCell(row.source_id ?? row.source ?? "source_ref"))
    .filter(Boolean);
  if (labels.length === 0) return "public evidence sources pending review";
  const remaining = rows.length - labels.length;
  return `${labels.join(", ")}${remaining > 0 ? ` +${remaining} more` : ""}`;
}

function coverageStatusText(value: unknown, rowCount: number) {
  const status = typeof value === "string" ? value : rowCount ? "partial" : "unavailable";
  if (status === "unavailable") return "Unavailable means coverage data is not loaded for this view.";
  if (status === "partial") return "Partial means some catalog entities or source groups still need evidence review.";
  if (status === "complete" || status === "available") return "Coverage is available for the listed public evidence sources.";
  return `${String(formatDisplayValue(status))} coverage needs review.`;
}

function coverageReviewAction(rows: Array<Record<string, unknown>>, nodeCoverage?: Record<string, unknown>) {
  if (rows.length === 0) return "refresh this view, then confirm public evidence sources before using coverage.";
  const catalogCount = Number(nodeCoverage?.catalog_node_count ?? 0);
  const coveredCount = Number(nodeCoverage?.covered_catalog_node_count ?? 0);
  if (catalogCount > 0 && coveredCount < catalogCount) return "review uncovered catalog entities and confirm missing evidence sources.";
  return "compare listed sources with entity catalog coverage and document remaining gaps.";
}
