import type { GraphRelationshipData } from "@supply-risk/shared-types";
import { DownstreamDemandPressureChart } from "../common/charts";
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
      <div className="section-kicker">Demand Relationship view</div>
      <p className="inspector-note">Demand rows show downstream source, product grade, and proxy type; demand edges are not supplier edges.</p>
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
            <th>Source refs</th>
          </tr>
        </thead>
        <tbody>
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview" data-preview-state="unavailable_preview">
              <td colSpan={6}>unavailable_preview: Backend demand relationship endpoint unavailable; no authoritative demand rows are shown.</td>
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
        unavailable_preview: Backend demand endpoint unavailable; local graph links are excluded from demand charts, tables, exports, reports, and source coverage.
      </p>
    );
  }
  const metadata = data as GraphRelationshipData & RelationshipPayloadMetadata;
  return (
    <div className="graph-view-summary">
      <span>{data.relationship_class}</span>
      <span>{data.graph_mode ?? "fixture"} graph</span>
      <span>{data.data_mode ?? "fixture"} data</span>
      <span>{data.source_manifest_id}</span>
      <span>{formatCell(metadata.calibration_status)}</span>
      <span>{formatCell(metadata.source_status)}</span>
      <span>{formatSourceRefs(metadata.evidence_refs)}</span>
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
  return String(value);
}

function formatSourceRefs(value: unknown) {
  if (!Array.isArray(value)) return "n/a";
  const refs = value.map((item) => String(item)).filter(Boolean);
  return refs.length > 0 ? refs.slice(0, 3).join(", ") : "n/a";
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
