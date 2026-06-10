import type { GraphMatrixData } from "@supply-risk/shared-types";

export function GraphMatrixView({
  endpointData,
}: {
  endpointData?: unknown;
  graph?: unknown;
  view?: unknown;
}) {
  const matrixRows = Array.isArray((endpointData as GraphMatrixData | undefined)?.dependency_matrix)
    ? ((endpointData as GraphMatrixData).dependency_matrix ?? [])
    : [];
  return (
    <div className="graph-v3-panel graph-v3-matrix-panel">
      <div className="section-kicker">Matrix mode</div>
      <p className="inspector-note">Matrix mode uses bounded tables and heatmap-style cells instead of a dense node cloud.</p>
      <table className="graph-matrix-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>Target</th>
            <th>Type</th>
            <th>Weight</th>
          </tr>
        </thead>
        <tbody>
          {matrixRows.length ? (
            matrixRows.slice(0, 12).map((row, index) => (
              <tr key={String((row as Record<string, unknown>).id ?? index)}>
                <td>{String((row as Record<string, unknown>).source ?? "")}</td>
                <td>{String((row as Record<string, unknown>).target ?? "")}</td>
                <td>{String((row as Record<string, unknown>).edge_type ?? (row as Record<string, unknown>).layer ?? "")}</td>
                <td>
                  <span className="matrix-weight-cell">
                    {Number((row as Record<string, unknown>).value ?? (row as Record<string, unknown>).weight ?? 0).toFixed(2)}
                  </span>
                </td>
              </tr>
            ))
          ) : (
            <tr className="unavailable-preview" data-preview-state="matrix_endpoint_unavailable">
              <td colSpan={4}>Matrix data is temporarily unavailable; review source coverage before using this view.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
