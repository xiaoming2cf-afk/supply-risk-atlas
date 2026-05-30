import type { GraphNodeCatalogData } from "@supply-risk/shared-types";
import { formatDisplayLabel, formatDisplayValue, formatNodeDisplayRef, formatSourceDisplayRef } from "../common/displayLabels";
import type { GraphViewModel } from "./graphViewModel";

export function GraphNodeCatalogView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const rows = Array.isArray((endpointData as GraphNodeCatalogData | undefined)?.node_catalog)
    ? ((endpointData as GraphNodeCatalogData).node_catalog ?? [])
    : view.visibleNodes.slice(0, 16).map((node) => ({
        node_id: node.id,
        node_type: node.kind,
        layer: node.metadata.layer ?? "fixture_layer",
        label: node.label,
        source_candidates: [node.metadata.source ?? node.metadata.source_id ?? "fixture_source"],
      }));

  return (
    <div className="graph-v3-panel graph-v3-node-catalog-panel">
      <div className="section-kicker">Node Catalog mode</div>
      <p className="inspector-note">Node Catalog mode shows canonical catalog rows and source candidates, not a dense node cloud.</p>
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Node</th>
            <th>Layer</th>
            <th>Type</th>
            <th>Source candidates</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 16).map((row, index) => (
            <tr key={String((row as Record<string, unknown>).node_id ?? index)}>
              <td>{formatNodeCell(row as Record<string, unknown>)}</td>
              <td>{String(formatDisplayValue(String((row as Record<string, unknown>).layer ?? "")))}</td>
              <td>{formatDisplayLabel(String((row as Record<string, unknown>).node_type ?? ""))}</td>
              <td>
                {Array.isArray((row as Record<string, unknown>).source_candidates)
                  ? ((row as { source_candidates: unknown[] }).source_candidates ?? []).slice(0, 3).map(formatSourceCandidate).join(", ")
                  : "source candidate unavailable"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatNodeCell(row: Record<string, unknown>) {
  const nodeId = typeof row.node_id === "string" ? row.node_id : "";
  const label = typeof row.label === "string" ? row.label : "";
  return label || formatNodeDisplayRef(nodeId) || "Catalog node";
}

function formatSourceCandidate(value: unknown) {
  if (typeof value !== "string") return "Public evidence source";
  return formatSourceDisplayRef(value) || String(formatDisplayValue(value));
}
