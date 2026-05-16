import type { GraphSupplyDemandBalanceData } from "@supply-risk/shared-types";
import { SupplyDemandBalanceChart } from "../common/charts";
import type { GraphViewModel } from "./graphViewModel";

export function SupplyDemandBalanceView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = endpointData as GraphSupplyDemandBalanceData | undefined;
  void view;
  const rows = Array.isArray(data?.balance_rows) ? data.balance_rows : [];
  const isEndpointUnavailable = !data;

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Supply-Demand Balance view</div>
      <p className="inspector-note">Balance rows compare bounded fixture/promoted demand signals with supply and production-dependency counts.</p>
      {data ? (
        <div className="graph-view-summary">
          <span>{data.graph_mode ?? "fixture"} graph</span>
          <span>{data.source_manifest_id}</span>
          <span>{(data.warnings ?? []).slice(0, 1).join(", ")}</span>
        </div>
      ) : (
        <p className="inspector-note unavailable-preview">
          Backend balance endpoint unavailable; local graph nodes are excluded from balance charts, tables, exports, reports, and source coverage.
        </p>
      )}
      <SupplyDemandBalanceChart
        data={!isEndpointUnavailable ? rows.slice(0, 6).map((row) => ({
          label: String((row as Record<string, unknown>).product_grade_id ?? "product"),
          value: Number((row as Record<string, unknown>).shortage_proxy ?? 0),
          secondaryValue: Number((row as Record<string, unknown>).demand_edge_count ?? 0),
        })) : []}
        metadata={
          data
            ? {
                graphVersion: data.graph_version,
                sourceManifestId: data.source_manifest_id,
                warnings: data.warnings,
              }
            : undefined
        }
      />
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Product grade</th>
            <th>Demand</th>
            <th>Supply</th>
            <th>Shortage proxy</th>
          </tr>
        </thead>
        <tbody>
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview">
              <td colSpan={4}>Backend supply-demand balance endpoint unavailable; no authoritative balance rows are shown.</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={4}>No authoritative supply-demand balance rows are available for this selection.</td>
            </tr>
          ) : rows.slice(0, 16).map((row, index) => (
            <tr key={String(row.product_grade_id ?? index)}>
              <td>{String(row.product_grade_id ?? "")}</td>
              <td>{String(row.demand_edge_count ?? 0)}</td>
              <td>{String(row.supply_edge_count ?? 0)}</td>
              <td>{String(row.shortage_proxy ?? 0)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
