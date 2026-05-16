import type { GraphRelationshipData } from "@supply-risk/shared-types";
import { SupplierConcentrationHHIChart } from "../common/charts";
import type { GraphViewModel } from "./graphViewModel";

export function SupplyRelationshipView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = endpointData as GraphRelationshipData | undefined;
  void view;
  const rows = Array.isArray(data?.relationships) ? data.relationships : [];
  const isEndpointUnavailable = !data;

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Supply Relationship view</div>
      <p className="inspector-note">Supplier rows are table-first and show supplied item, source refs, and confidence without rendering a dense graph.</p>
      <RelationshipMetadata data={data} />
      <SupplierConcentrationHHIChart
        data={!isEndpointUnavailable ? (data?.supplier_concentration ?? []).slice(0, 6).map((row) => ({
          label: String(row.supplier_id ?? "supplier"),
          value: Number(row.hhi_component ?? row.share ?? 0),
        })) : []}
        metadata={metadataForRelationshipData(data)}
      />
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
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview">
              <td colSpan={4}>Backend supply relationship endpoint unavailable; no authoritative supply rows are shown.</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={4}>No authoritative supply relationship rows are available for this selection.</td>
            </tr>
          ) : rows.slice(0, 16).map((row, index) => {
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
  if (!data) {
    return (
      <p className="inspector-note unavailable-preview">
        Backend relationship endpoint unavailable; local graph links are excluded from relationship charts, tables, exports, reports, and source coverage.
      </p>
    );
  }
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

function metadataForRelationshipData(data?: GraphRelationshipData) {
  return data
    ? {
        graphVersion: data.graph_version,
        sourceManifestId: data.source_manifest_id,
        warnings: data.warnings,
      }
    : undefined;
}
