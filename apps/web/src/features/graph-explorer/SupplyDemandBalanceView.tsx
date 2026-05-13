import type { GraphSupplyDemandBalanceData } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function SupplyDemandBalanceView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = endpointData as GraphSupplyDemandBalanceData | undefined;
  const rows = Array.isArray(data?.balance_rows)
    ? data.balance_rows
    : view.visibleNodes.slice(0, 12).map((node) => ({
        product_grade_id: node.id,
        demand_edge_count: 0,
        supply_edge_count: 0,
        production_dependency_count: 0,
        shortage_proxy: 0,
      }));

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
        <p className="inspector-note">Backend balance endpoint unavailable; showing controlled local graph rows.</p>
      )}
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
          {rows.slice(0, 16).map((row, index) => (
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
