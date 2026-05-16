import type { GraphRelationshipData } from "@supply-risk/shared-types";
import { CriticalInputBottleneckChart } from "../common/charts";
import type { GraphViewModel } from "./graphViewModel";

const PRODUCTION_DEPENDENCY_CLASS = "PRODUCTION_DEPENDENCY";

export function ProductionDependencyView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = relationshipEndpointData(endpointData, PRODUCTION_DEPENDENCY_CLASS);
  void view;
  const rows = relationshipRows(data, PRODUCTION_DEPENDENCY_CLASS);
  const isEndpointUnavailable = !data;

  return (
    <div className="graph-v3-panel graph-v3-relationship-panel">
      <div className="section-kicker">Production Dependency view</div>
      <p className="inspector-note">Production dependency rows separate required inputs, bottleneck flags, and propagation hints from evidence-context links.</p>
      <RelationshipMetadata data={data} />
      <CriticalInputBottleneckChart
        data={!isEndpointUnavailable ? criticalInputChartData(rows) : []}
        metadata={metadataForRelationshipData(data)}
      />
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Source</th>
            <th>Dependency target</th>
            <th>Type</th>
            <th>Bottleneck</th>
            <th>Source refs</th>
          </tr>
        </thead>
        <tbody>
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview" data-preview-state="unavailable_preview">
              <td colSpan={5}>unavailable_preview: Backend production dependency endpoint unavailable; no authoritative dependency rows are shown.</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={5}>No authoritative production dependency rows are available for this selection.</td>
            </tr>
          ) : rows.slice(0, 16).map((row, index) => (
            <tr key={String(row.edge_id ?? index)}>
              <td>{formatCell(row.dependency_source_id)}</td>
              <td>{formatCell(row.dependency_target_id)}</td>
              <td>{formatCell(row.dependency_type)}</td>
              <td>{row.bottleneck_flag === true ? "yes" : "no"}</td>
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
        unavailable_preview: Backend dependency endpoint unavailable; local graph links are excluded from dependency charts, tables, exports, reports, and source coverage.
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

function criticalInputChartData(rows: Array<Record<string, unknown>>) {
  return rows.slice(0, 6).map((row) => ({
    label: String(row.dependency_target_id ?? row.dependency_type ?? "dependency"),
    value: row.bottleneck_flag === true ? 1 : 0.25,
  }));
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
