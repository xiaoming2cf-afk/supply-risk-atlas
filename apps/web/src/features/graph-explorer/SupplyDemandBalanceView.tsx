import type { GraphSupplyDemandBalanceData } from "@supply-risk/shared-types";
import { SupplyDemandBalanceChart } from "../common/charts";
import type { GraphViewModel } from "./graphViewModel";

const SUPPLY_DEMAND_BALANCE_CLASS = "SUPPLY_DEMAND_BALANCE";

export function SupplyDemandBalanceView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = balanceEndpointData(endpointData);
  void view;
  const rows = balanceRows(data);
  const isEndpointUnavailable = !data;
  const payloadEvidenceRefs = (data as BalancePayloadMetadata | undefined)?.evidence_refs;

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Supply-Demand Balance view</div>
      <p className="inspector-note">Balance rows compare bounded fixture/promoted demand signals with supply and production-dependency counts.</p>
      {data ? (
        <div className="graph-view-summary">
          <span>{data.relationship_class}</span>
          <span>{data.graph_mode ?? "fixture"} graph</span>
          <span>{data.data_mode ?? "fixture"} data</span>
          <span>{data.source_manifest_id}</span>
          <span>{formatCell((data as BalancePayloadMetadata).calibration_status)}</span>
          <span>{formatCell((data as BalancePayloadMetadata).source_status)}</span>
          <span>{formatSourceRefs(payloadEvidenceRefs)}</span>
          <span>{(data.warnings ?? []).slice(0, 1).join(", ")}</span>
        </div>
      ) : (
        <p className="inspector-note unavailable-preview" data-preview-state="unavailable_preview">
          unavailable_preview: Backend balance endpoint unavailable; local graph nodes are excluded from balance charts, tables, exports, reports, and source coverage.
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
            <th>Production deps</th>
            <th>Shortage proxy</th>
            <th>Evidence refs</th>
          </tr>
        </thead>
        <tbody>
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview" data-preview-state="unavailable_preview">
              <td colSpan={6}>unavailable_preview: Backend supply-demand balance endpoint unavailable; no authoritative balance rows are shown.</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={6}>No authoritative supply-demand balance rows are available for this selection.</td>
            </tr>
          ) : rows.slice(0, 16).map((row, index) => (
            <tr key={String(row.product_grade_id ?? index)}>
              <td>{formatCell(row.product_grade_id)}</td>
              <td>{formatCell(row.demand_edge_count ?? 0)}</td>
              <td>{formatCell(row.supply_edge_count ?? 0)}</td>
              <td>{formatCell(row.production_dependency_count ?? 0)}</td>
              <td>{formatCell(row.shortage_proxy ?? 0)}</td>
              <td>{formatSourceRefs(row.source_refs ?? row.evidence_refs ?? payloadEvidenceRefs)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type BalancePayloadMetadata = {
  calibration_status?: unknown;
  evidence_refs?: unknown;
  source_status?: unknown;
};

function balanceEndpointData(endpointData: unknown) {
  if (!isRecord(endpointData)) return undefined;
  if (endpointData.relationship_class !== SUPPLY_DEMAND_BALANCE_CLASS) return undefined;
  if (!Array.isArray(endpointData.balance_rows)) return undefined;
  return endpointData as unknown as GraphSupplyDemandBalanceData;
}

function balanceRows(data: GraphSupplyDemandBalanceData | undefined) {
  return (data?.balance_rows ?? []).filter(
    (row): row is Record<string, unknown> => isRecord(row) && row.relationship_class === SUPPLY_DEMAND_BALANCE_CLASS,
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function formatCell(value: unknown) {
  if (value === null || value === undefined || value === "") return "n/a";
  return String(value);
}

function formatSourceRefs(value: unknown) {
  if (!Array.isArray(value)) return "n/a";
  const refs = value.map((item) => String(item)).filter(Boolean);
  return refs.length > 0 ? refs.slice(0, 3).join(", ") : "n/a";
}
