import type { GraphRelationshipData } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function DemandRelationshipView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = endpointData as GraphRelationshipData | undefined;
  const rows = Array.isArray(data?.relationships)
    ? data.relationships
    : view.visibleLinks.slice(0, 12).map((link) => ({
        edge_id: link.id,
        demand_source_id: link.source,
        product_grade_id: link.target,
        demand_proxy_type: "controlled_unavailable",
        confidence: link.confidence ?? 0,
      }));

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Demand Relationship view</div>
      <p className="inspector-note">Demand rows show downstream source, product grade, and proxy type; demand edges are not supplier edges.</p>
      <RelationshipMetadata data={data} />
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Demand source</th>
            <th>Product grade</th>
            <th>Proxy</th>
            <th>Period</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 16).map((row, index) => {
            const item = row as Record<string, unknown>;
            return (
            <tr key={String(item.edge_id ?? index)}>
              <td>{String(item.demand_source_id ?? "")}</td>
              <td>{String(item.product_grade_id ?? "")}</td>
              <td>{String(item.demand_proxy_type ?? "unavailable")}</td>
              <td>{String(item.period ?? "fixture")}</td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function RelationshipMetadata({ data }: { data?: GraphRelationshipData }) {
  if (!data) return <p className="inspector-note">Backend demand endpoint unavailable; showing controlled local graph rows.</p>;
  return (
    <div className="graph-view-summary">
      <span>{data.graph_mode ?? "fixture"} graph</span>
      <span>{data.source_manifest_id}</span>
      <span>{(data.warnings ?? []).slice(0, 1).join(", ")}</span>
    </div>
  );
}
