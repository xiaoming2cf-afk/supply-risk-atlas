import type { GraphSupplyDemandBalanceData } from "@supply-risk/shared-types";
import { AuditDetails, MetadataSummary } from "../common/AuditDetails";
import { SupplyDemandBalanceChart } from "../common/charts";
import { formatDisplayValue, formatNodeDisplayRef, formatSourceDisplayRef } from "../common/displayLabels";
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
      <div className="section-kicker">Supply-demand balance</div>
      <p className="inspector-note">Balance rows compare bounded public evidence demand signals with supply and production-dependency counts.</p>
      {data ? (
        <div className="graph-view-summary">
          <MetadataSummary
            items={[
              { label: "Supply-demand balance" },
              { label: "Public evidence mode" },
              { label: "Source-backed balance" },
              data.warnings?.length ? { label: `${data.warnings.length} warning(s)`, tone: "warning" } : { label: "" },
            ]}
          />
          <AuditDetails
            items={[
              { label: "graph_mode", value: data.graph_mode ?? "fixture" },
              { label: "data_mode", value: data.data_mode ?? "fixture" },
              { label: "source_manifest_id", value: data.source_manifest_id },
              { label: "graph_version", value: data.graph_version },
              { label: "calibration_status", value: (data as BalancePayloadMetadata).calibration_status },
              { label: "Source coverage", value: (data as BalancePayloadMetadata).source_status },
              { label: "Evidence references", value: payloadEvidenceRefs },
            ]}
            warnings={data.warnings}
          />
        </div>
      ) : (
        <p className="inspector-note unavailable-preview" data-preview-state="unavailable_preview">
          Supply-demand balance data is temporarily unavailable. Open Source coverage to review public evidence support before using balance charts, tables, exports, or reports.
        </p>
      )}
      <SupplyDemandBalanceChart
        data={!isEndpointUnavailable ? rows.slice(0, 6).map((row) => ({
          label: formatCell((row as Record<string, unknown>).product_grade_id ?? "product"),
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
            <th>Evidence records</th>
          </tr>
        </thead>
        <tbody>
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview" data-preview-state="unavailable_preview">
              <td colSpan={6}>Supply-demand balance data is temporarily unavailable; coverage review is needed before this table can be used.</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={6}>No supply-demand balance rows are available for this selection.</td>
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
    (row): row is Record<string, unknown> =>
      isRecord(row) &&
      row.relationship_class === SUPPLY_DEMAND_BALANCE_CLASS &&
      row.row_type === "aggregate" &&
      row.not_supply_chain_dependency === true,
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function formatCell(value: unknown) {
  if (value === null || value === undefined || value === "") return "n/a";
  if (typeof value === "string") {
    return formatNodeDisplayRef(value) || String(formatDisplayValue(value));
  }
  return String(formatDisplayValue(value));
}

function formatSourceRefs(value: unknown) {
  if (!Array.isArray(value)) return "n/a";
  const refs = value.map((item) => formatSourceRef(item)).filter(Boolean);
  return refs.length > 0 ? refs.slice(0, 3).join(", ") : "n/a";
}

function formatSourceRef(value: unknown) {
  if (typeof value === "string") return formatSourceDisplayRef(value) || String(formatDisplayValue(value));
  if (typeof value === "object" && value !== null) {
    const record = value as Record<string, unknown>;
    const source = typeof record.source_id === "string" ? record.source_id : undefined;
    return formatSourceDisplayRef(source) || "Public evidence source";
  }
  return "";
}
