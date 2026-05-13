import type { GraphRelationshipData } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function SupplyRelationshipView({
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
        supplier_id: link.source,
        supplied_item_id: link.target,
        buyer_or_stage_id: link.target,
        confidence: link.confidence ?? 0,
        source_refs: [link.sourceId ?? "fixture_source"],
      }));

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Supply Relationship view</div>
      <p className="inspector-note">Supplier rows are table-first and show supplied item, source refs, and confidence without rendering a dense graph.</p>
      <RelationshipMetadata data={data} />
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Supplier</th>
            <th>Supplied item</th>
            <th>Buyer or stage</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 16).map((row, index) => {
            const item = row as Record<string, unknown>;
            return (
            <tr key={String(item.edge_id ?? index)}>
              <td>{String(item.supplier_id ?? "")}</td>
              <td>{String(item.supplied_item_id ?? item.service_or_capacity_item_id ?? "")}</td>
              <td>{String(item.buyer_or_stage_id ?? "")}</td>
              <td>{formatPercent(item.confidence)}</td>
            </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function RelationshipMetadata({ data }: { data?: GraphRelationshipData }) {
  if (!data) return <p className="inspector-note">Backend relationship endpoint unavailable; showing controlled local graph rows.</p>;
  return (
    <div className="graph-view-summary">
      <span>{data.graph_mode ?? "fixture"} graph</span>
      <span>{data.source_manifest_id}</span>
      <span>{(data.warnings ?? []).slice(0, 1).join(", ")}</span>
    </div>
  );
}

function formatPercent(value: unknown) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "n/a";
  return `${Math.round(numeric * 100)}%`;
}
