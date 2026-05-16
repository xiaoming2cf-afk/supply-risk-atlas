import type { GraphRelationshipData } from "@supply-risk/shared-types";
import { SupplierConcentrationHHIChart } from "../common/charts";
import type { GraphViewModel } from "./graphViewModel";

const SUPPLY_RELATIONSHIP_CLASS = "SUPPLY_RELATIONSHIP";

export function SupplyRelationshipView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const data = relationshipEndpointData(endpointData, SUPPLY_RELATIONSHIP_CLASS);
  void view;
  const rows = relationshipRows(data, SUPPLY_RELATIONSHIP_CLASS);
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
            <th>Source refs</th>
          </tr>
        </thead>
        <tbody>
          {isEndpointUnavailable ? (
            <tr className="unavailable-preview" data-preview-state="unavailable_preview">
              <td colSpan={5}>unavailable_preview: Backend supply relationship endpoint unavailable; no authoritative supply rows are shown.</td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td colSpan={5}>No authoritative supply relationship rows are available for this selection.</td>
            </tr>
          ) : rows.slice(0, 16).map((row, index) => (
            <tr key={String(row.edge_id ?? index)}>
              <td>{formatCell(row.supplier_id)}</td>
              <td>{formatCell(row.supplied_item_id ?? row.service_or_capacity_item_id)}</td>
              <td>{formatCell(row.buyer_or_stage_id)}</td>
              <td>{formatPercent(row.confidence)}</td>
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
        unavailable_preview: Backend relationship endpoint unavailable; local graph links are excluded from relationship charts, tables, exports, reports, and source coverage.
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

function formatPercent(value: unknown) {
  if (value === null || value === undefined) return "n/a";
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "n/a";
  return `${Math.round(numeric * 100)}%`;
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
