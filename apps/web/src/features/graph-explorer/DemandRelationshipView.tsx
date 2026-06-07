import type { GraphRelationshipData } from "@supply-risk/shared-types";
import { AuditDetails, MetadataSummary } from "../common/AuditDetails";
import { DownstreamDemandPressureChart } from "../common/charts";
import { formatDisplayValue, formatNodeDisplayRef, formatSourceDisplayRef } from "../common/displayLabels";
import type { GraphViewModel } from "./graphViewModel";

const DEMAND_RELATIONSHIP_CLASS = "DEMAND_RELATIONSHIP";

export function DemandRelationshipView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = relationshipEndpointData(endpointData, DEMAND_RELATIONSHIP_CLASS);
  void view;
  const rows = relationshipRows(data, DEMAND_RELATIONSHIP_CLASS);
  const isEndpointUnavailable = !data;

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Demand relationships</div>
      <p className="inspector-note">Demand rows show downstream source, product grade, and proxy type; demand relationships are not supplier relationships.</p>
      <RelationshipMetadata data={data} />
      <DownstreamDemandPressureChart
        data={!isEndpointUnavailable ? demandChartData(rows) : []}
        metadata={metadataForRelationshipData(data)}
      />
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Demand source</th>
            <th>Product grade</th>
            <th>Region</th>
            <th>Proxy</th>
            <th>Period</th>
            <th>Sources</th>
          </tr>
        </thead>
        <tbody>
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview" data-preview-state="unavailable_preview">
              <td colSpan={6}>Backend relationship data unavailable; authoritative rows are hidden.</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={6}>No authoritative demand relationship rows are available for this selection.</td>
            </tr>
          ) : rows.slice(0, 16).map((row, index) => (
            <tr key={String(row.edge_id ?? index)}>
              <td>{formatCell(row.demand_source_id)}</td>
              <td>{formatCell(row.product_grade_id)}</td>
              <td>{formatCell(row.region)}</td>
              <td>{formatCell(row.demand_proxy_type)}</td>
              <td>{formatCell(row.period)}</td>
              <td>{formatSourceRefs(row.source_refs ?? row.evidence_refs)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RelationshipMetadata({ data }: { data?: GraphRelationshipData }) {
  if (!data) {
    return (
      <p className="inspector-note unavailable-preview" data-preview-state="unavailable_preview">
        Backend relationship data unavailable; authoritative rows are hidden. Local graph links are excluded from demand charts, tables, exports, reports, and source coverage.
      </p>
    );
  }
  const metadata = data as GraphRelationshipData & RelationshipPayloadMetadata;
  return (
    <div className="graph-view-summary">
      <MetadataSummary
        items={[
          { label: "Demand relationships" },
          { label: "Public evidence mode" },
          { label: "Source-backed demand" },
          data.warnings?.length ? { label: `${data.warnings.length} warning(s)`, tone: "warning" } : { label: "" },
        ]}
      />
      <AuditDetails
        items={[
          { label: "graph_mode", value: data.graph_mode ?? "fixture" },
          { label: "data_mode", value: data.data_mode ?? "fixture" },
          { label: "source_manifest_id", value: data.source_manifest_id },
          { label: "graph_version", value: data.graph_version },
          { label: "calibration_status", value: metadata.calibration_status },
          { label: "source_status", value: metadata.source_status },
          { label: "evidence_refs", value: metadata.evidence_refs },
        ]}
        warnings={data.warnings}
      />
    </div>
  );
}

function demandChartData(rows: Array<Record<string, unknown>>) {
  const counts = new Map<string, number>();
  rows.forEach((row) => {
    const key = formatCell(row.product_grade_id ?? "product_grade");
    counts.set(key, (counts.get(key) ?? 0) + 1);
  });
  return [...counts.entries()].slice(0, 6).map(([label, value]) => ({ label, value }));
}

type RelationshipPayloadMetadata = {
  calibration_status?: unknown;
  evidence_refs?: unknown;
  source_status?: unknown;
};

function relationshipEndpointData(endpointData: unknown, relationshipClass: string) {
  if (!isRecord(endpointData)) return undefined;
  if (endpointData.relationship_class !== relationshipClass) return undefined;
  if (!Array.isArray(endpointData.relationships)) return undefined;
  return endpointData as unknown as GraphRelationshipData;
}

function relationshipRows(data: GraphRelationshipData | undefined, relationshipClass: string) {
  return (data?.relationships ?? []).filter(
    (row): row is Record<string, unknown> => isRecord(row) && row.relationship_class === relationshipClass,
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

function metadataForRelationshipData(data?: GraphRelationshipData) {
  return data
    ? {
        graphVersion: data.graph_version,
        sourceManifestId: data.source_manifest_id,
        warnings: data.warnings,
      }
    : undefined;
}
