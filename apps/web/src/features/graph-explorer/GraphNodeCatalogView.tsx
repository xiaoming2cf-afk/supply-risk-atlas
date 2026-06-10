import type { GraphNodeCatalogData } from "@supply-risk/shared-types";
import { formatDisplayLabel, formatDisplayValue, formatNodeDisplayRef, formatSourceDisplayRef } from "../common/displayLabels";

export function GraphNodeCatalogView({
  endpointData,
}: {
  endpointData?: unknown;
  view?: unknown;
}) {
  const rows = Array.isArray((endpointData as GraphNodeCatalogData | undefined)?.node_catalog)
    ? ((endpointData as GraphNodeCatalogData).node_catalog ?? [])
    : [];

  return (
    <div className="graph-v3-panel graph-v3-node-catalog-panel">
      <div className="section-kicker">Entity catalog</div>
      <p className="inspector-note">Entity catalog shows canonical rows and evidence sources, not a dense graph view.</p>
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Entity</th>
            <th>Layer</th>
            <th>Type</th>
            <th>Evidence sources</th>
          </tr>
        </thead>
        <tbody>
          {rows.length ? (
            rows.slice(0, 16).map((row, index) => (
              <tr key={String((row as Record<string, unknown>).node_id ?? index)}>
                <td>{formatNodeCell(row as Record<string, unknown>)}</td>
                <td>{String(formatDisplayValue(String((row as Record<string, unknown>).layer ?? "")))}</td>
                <td>{formatDisplayLabel(String((row as Record<string, unknown>).node_type ?? ""))}</td>
                <td>
                  {Array.isArray((row as Record<string, unknown>).source_candidates)
                    ? ((row as { source_candidates: unknown[] }).source_candidates ?? []).slice(0, 3).map(formatSourceCandidate).join(", ")
                    : "evidence source unavailable"}
                </td>
              </tr>
            ))
          ) : (
            <tr className="unavailable-preview" data-preview-state="node_catalog_endpoint_unavailable">
              <td colSpan={4}>Entity catalog data is temporarily unavailable; review source coverage to confirm entity evidence.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function formatNodeCell(row: Record<string, unknown>) {
  const nodeId = typeof row.node_id === "string" ? row.node_id : "";
  const label = typeof row.label === "string" ? row.label : "";
  return label || formatNodeDisplayRef(nodeId) || "Catalog entity";
}

function formatSourceCandidate(value: unknown) {
  if (typeof value !== "string") return "Public evidence source";
  return formatSourceDisplayRef(value) || String(formatDisplayValue(value));
}
