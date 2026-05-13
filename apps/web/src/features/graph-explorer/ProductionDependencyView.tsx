import type { GraphRelationshipData } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function ProductionDependencyView({
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
        dependency_source_id: link.source,
        dependency_target_id: link.target,
        dependency_type: link.edgeType ?? "dependency",
        criticality: "unknown",
        substitutability: "unknown",
        bottleneck_flag: false,
      }));

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Production Dependency view</div>
      <p className="inspector-note">Production dependency rows separate required inputs, bottleneck flags, and propagation hints from evidence-context links.</p>
      <RelationshipMetadata data={data} />
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>Dependency target</th>
            <th>Type</th>
            <th>Bottleneck</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 16).map((row, index) => (
            <tr key={String(row.edge_id ?? index)}>
              <td>{String(row.dependency_source_id ?? "")}</td>
              <td>{String(row.dependency_target_id ?? "")}</td>
              <td>{String(row.dependency_type ?? "dependency")}</td>
              <td>{row.bottleneck_flag === true ? "yes" : "no"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RelationshipMetadata({ data }: { data?: GraphRelationshipData }) {
  if (!data) return <p className="inspector-note">Backend dependency endpoint unavailable; showing controlled local graph rows.</p>;
  return (
    <div className="graph-view-summary">
      <span>{data.graph_mode ?? "fixture"} graph</span>
      <span>{data.source_manifest_id}</span>
      <span>{(data.warnings ?? []).slice(0, 1).join(", ")}</span>
    </div>
  );
}
