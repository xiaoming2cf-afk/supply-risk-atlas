import type { GraphSourceCoverageData } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function GraphSourceCoverageView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const sourceCoverage = (endpointData as GraphSourceCoverageData | undefined)?.source_coverage;
  const rows = Array.isArray((sourceCoverage as Record<string, unknown> | undefined)?.rows)
    ? ((sourceCoverage as { rows: Array<Record<string, unknown>> }).rows ?? [])
    : fallbackRows(view);
  const nodeCoverage = (sourceCoverage as Record<string, unknown> | undefined)?.node_catalog_coverage as
    | Record<string, unknown>
    | undefined;

  return (
    <div className="graph-v3-panel graph-v3-source-coverage-panel">
      <div className="section-kicker">Source Coverage mode</div>
      <p className="inspector-note">Coverage is a transparency table and does not render the full graph.</p>
      {nodeCoverage ? (
        <div className="graph-view-summary">
          <span>catalog nodes: {String(nodeCoverage.catalog_node_count ?? "n/a")}</span>
          <span>covered: {String(nodeCoverage.covered_catalog_node_count ?? "n/a")}</span>
          <span>status: {String(nodeCoverage.status ?? "partial")}</span>
        </div>
      ) : null}
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>References</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 16).map((row, index) => (
            <tr key={String(row.source_id ?? index)}>
              <td>{String(row.source_id ?? "source_ref")}</td>
              <td>
                {String(
                  (row as Record<string, unknown>).reference_count ??
                    (row as Record<string, unknown>).count ??
                    0,
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function fallbackRows(view: GraphViewModel) {
  const counts = new Map<string, number>();
  for (const link of view.visibleLinks) {
    const source = String(link.sourceId ?? link.metadata?.source ?? "fixture_source");
    counts.set(source, (counts.get(source) ?? 0) + 1);
  }
  return [...counts.entries()].map(([source_id, reference_count]) => ({ source_id, reference_count }));
}
