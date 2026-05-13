import type { GraphRelationshipData } from "@supply-risk/shared-types";
import { DownstreamDemandPressureChart } from "../common/charts";
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
      <DownstreamDemandPressureChart
        data={demandChartData(rows)}
        metadata={metadataForRelationshipData(data)}
      />
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

function demandChartData(rows: Array<Record<string, unknown>>) {
  const counts = new Map<string, number>();
  rows.forEach((row) => {
    const key = String(row.product_grade_id ?? "product_grade");
    counts.set(key, (counts.get(key) ?? 0) + 1);
  });
  return [...counts.entries()].slice(0, 6).map(([label, value]) => ({ label, value }));
}

function metadataForRelationshipData(data?: GraphRelationshipData) {
  return data
    ? {
        graphVersion: data.graph_version,
        sourceManifestId: data.source_manifest_id,
        warnings: data.warnings,
      }
    : undefined;
}
