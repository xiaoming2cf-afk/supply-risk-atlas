import type { GraphViewModel, GraphVersionMetadata } from "../graphViewModel";
import { AuditDetails, MetadataSummary } from "../../common/AuditDetails";
import { formatDisplayLabel, formatDisplayValue, formatNodeDisplayRef, formatSourceDisplayRef } from "../../common/displayLabels";

export type StageId =
  | "L0_policy_macro"
  | "L1_raw_minerals"
  | "L2_materials_chemicals"
  | "L3_design_eda_ip"
  | "L4_equipment"
  | "L5_fabrication"
  | "L6_products"
  | "L7_packaging_testing"
  | "L8_logistics"
  | "L9_downstream_demand"
  | "L10_risk_events"
  | "L11_compliance";

export type RelationshipClassFilter =
  | "all"
  | "SUPPLY_RELATIONSHIP"
  | "DEMAND_RELATIONSHIP"
  | "PRODUCTION_DEPENDENCY"
  | "EVIDENCE_CONTEXT";

export type StageViewDefinition = {
  id: StageId;
  label: string;
  viewName: string;
  businessQuestion: string;
  nodeTypes: string[];
};

export const stageViewOptions: StageViewDefinition[] = [
  {
    id: "L0_policy_macro",
    label: "L0 Policy / macro",
    viewName: "PolicyMacroGraphView",
    businessQuestion: "Which policy, macro, sanctions, and export-control signals shape exposure?",
    nodeTypes: ["country", "region", "policy_event", "sanction_event"],
  },
  {
    id: "L1_raw_minerals",
    label: "L1 Critical minerals",
    viewName: "MineralDependencyGraphView",
    businessQuestion: "Which critical minerals and raw materials create upstream concentration?",
    nodeTypes: ["critical_mineral", "raw_material", "commodity"],
  },
  {
    id: "L2_materials_chemicals",
    label: "L2 Materials / chemicals",
    viewName: "MaterialChemicalDependencyGraphView",
    businessQuestion: "Which wafers, chemicals, gases, substrates, masks, and CMP inputs constrain production?",
    nodeTypes: ["material", "chemical", "wafer_material", "photoresist"],
  },
  {
    id: "L3_design_eda_ip",
    label: "L3 Design / EDA / IP",
    viewName: "DesignIPDependencyGraphView",
    businessQuestion: "Which design firms, EDA capabilities, and IP blocks create capability dependencies?",
    nodeTypes: ["company", "design_company", "eda_tool", "ip_core"],
  },
  {
    id: "L4_equipment",
    label: "L4 Equipment",
    viewName: "EquipmentProcessDependencyGraphView",
    businessQuestion: "Which manufacturing equipment and suppliers create process bottlenecks?",
    nodeTypes: ["equipment", "equipment_supplier", "process_stage"],
  },
  {
    id: "L5_fabrication",
    label: "L5 Fabrication",
    viewName: "FabProcessGraphView",
    businessQuestion: "Which fabs, process stages, technology nodes, and hazards drive resilience?",
    nodeTypes: ["facility", "fab", "foundry", "process_stage", "technology_node"],
  },
  {
    id: "L6_products",
    label: "L6 Products",
    viewName: "ProductDemandGraphView",
    businessQuestion: "Which product grades connect demand pressure to upstream process needs?",
    nodeTypes: ["product_grade", "chip_type", "component", "demand_indicator"],
  },
  {
    id: "L7_packaging_testing",
    label: "L7 Packaging / testing",
    viewName: "PackagingTestingGraphView",
    businessQuestion: "Which OSAT, advanced packaging, substrate, and test stages constrain output?",
    nodeTypes: ["osat_company", "packaging_stage", "advanced_packaging", "testing_stage"],
  },
  {
    id: "L8_logistics",
    label: "L8 Logistics",
    viewName: "LogisticsRouteGraphView",
    businessQuestion: "Which ports, airports, routes, and hazards shape logistics exposure?",
    nodeTypes: ["logistics_facility", "port", "airport", "route"],
  },
  {
    id: "L9_downstream_demand",
    label: "L9 Downstream demand",
    viewName: "DownstreamDemandGraphView",
    businessQuestion: "Which downstream sectors and demand signals pressure product grades?",
    nodeTypes: ["downstream_sector", "customer_industry", "demand_indicator", "product_grade"],
  },
  {
    id: "L10_risk_events",
    label: "L10 Risk events",
    viewName: "EventTimelineGraphView",
    businessQuestion: "Which hazards, disruptions, market, cyber, factory, or labor events may affect stages?",
    nodeTypes: ["risk_event", "hazard_event", "market_event", "factory_event"],
  },
  {
    id: "L11_compliance",
    label: "L11 Compliance",
    viewName: "ComplianceRiskGraphView",
    businessQuestion: "Which restricted items, entities, and policies create compliance exposure?",
    nodeTypes: ["policy_event", "sanction_event", "restricted_item", "restricted_entity"],
  },
];

export type StageGraphViewProps = {
  endpointData?: Record<string, unknown>;
  endpointStatus?: "active" | "fallback" | "loading";
  metadata: GraphVersionMetadata;
  relationshipClassFilter: RelationshipClassFilter;
  stage: StageViewDefinition;
  view: GraphViewModel;
};

export function StageGraphView({
  endpointData,
  endpointStatus = "fallback",
  metadata,
  relationshipClassFilter,
  stage,
}: StageGraphViewProps) {
  const endpointNodes = rows(endpointData?.nodes).slice(0, 6);
  const endpointEdges = rows(endpointData?.edges).slice(0, 6);
  const sourceCoverage = rows(endpointData?.source_coverage).slice(0, 5);
  const sourceSupportRows = sourceCoverage.slice(0, 3);
  const sourceFamilyCoverage = rows(endpointData?.source_family_coverage).slice(0, 4);
  const evidenceRefs = rows(endpointData?.evidence_refs).slice(0, 5);
  const sourceGaps = list(endpointData?.source_gaps).slice(0, 3);
  const proxyLimitations = list(endpointData?.proxy_limitations).slice(0, 3);
  const failureReason = String(endpointData?.failure_reason ?? "none");
  const narrowPatchPlan = String(endpointData?.required_narrow_patch_if_failed ?? "none");
  const hasAuthoritativeStageData = endpointStatus === "active" && Boolean(endpointData);
  const isStageEndpointLoading = endpointStatus === "loading";
  const isStageEndpointUnavailable = endpointStatus === "fallback";
  const visibleNodes = hasAuthoritativeStageData ? endpointNodes : [];
  const visibleEdges = hasAuthoritativeStageData ? endpointEdges : [];
  const propagates =
    relationshipClassFilter === "SUPPLY_RELATIONSHIP" || relationshipClassFilter === "PRODUCTION_DEPENDENCY";
  const sourceCoverageLabel = sourceCoverage.length
    ? `${sourceCoverage.length} source records`
    : isStageEndpointLoading
      ? "source coverage loading"
      : "source coverage unavailable";
  const sourceFamilyLabel = sourceFamilyCoverage.length
    ? `${sourceFamilyCoverage.length} source families`
    : isStageEndpointLoading
      ? "source families loading"
      : "source families unavailable";
  const evidenceRefsLabel = evidenceRefs.length
    ? `${evidenceRefs.length} evidence refs`
    : isStageEndpointLoading
      ? "evidence refs loading"
      : "evidence refs unavailable";

  return (
    <section className="graph-list-section stage-graph-view" data-testid="stage-graph-view" data-stage-id={stage.id}>
      <div className="section-kicker">Supply-chain stage view</div>
      <h3>{stage.label}</h3>
      <p className="muted">{stage.label}: {stage.businessQuestion}</p>
      <MetadataSummary
        items={[
          { label: "Public evidence mode" },
          { label: sourceCoverage.length ? `${sourceCoverage.length} source candidates` : isStageEndpointLoading ? "Stage source coverage loading" : "Stage source coverage unavailable", tone: sourceCoverage.length ? "default" : "warning" },
          { label: sourceGaps.length || proxyLimitations.length ? "Known proxy gaps" : "No stage gaps recorded", tone: sourceGaps.length || proxyLimitations.length ? "warning" : "default" },
          { label: relationshipClassLabel(relationshipClassFilter) },
        ]}
      />
      <AuditDetails
        items={[
          { label: "graph_version", value: endpointData?.graph_version ?? metadata.graphVersion },
          { label: "source_manifest_id", value: endpointData?.source_manifest_id ?? metadata.sourceManifestId },
          { label: "data_mode", value: endpointData?.data_mode ?? "fixture" },
          { label: "graph_mode", value: endpointData?.graph_mode ?? "fixture" },
          { label: "stage_view_component", value: stage.viewName },
          { label: "known source gaps", value: sourceGaps },
          { label: "proxy limitations", value: proxyLimitations },
          { label: "why coverage is partial", value: failureReason },
          { label: "next narrow patch", value: narrowPatchPlan },
        ]}
        warnings={metadata.warnings}
      />
      <p className="warning-text">
        Public evidence view; evidence-context links are inspection links, not dependency edges.
      </p>
      <div className="graph-view-summary">
        <span>{relationshipClassLabel(relationshipClassFilter)}</span>
        <span>Risk propagation: {propagates ? "available for evidence-backed edges" : "not used for propagation"}</span>
        <span>Focused view: up to 18 nodes / 30 edges</span>
      </div>
      {isStageEndpointLoading ? (
        <p className="inspector-note">Loading authoritative stage graph data.</p>
      ) : null}
      {isStageEndpointUnavailable ? (
        <p className="inspector-note unavailable-preview" data-preview-state="stage_endpoint_unavailable">
          Stage graph data unavailable; backend stage rows are hidden.
        </p>
      ) : null}
      {visibleNodes.length ? (
        <ul className="compact-list">
          {visibleNodes.map((node) => (
            <li key={String(node.id)}>
              <strong>{formatNodeRef(node.label ?? node.id)}</strong>
              <span>{formatDisplayLabel(String(node.kind ?? node.node_type ?? "node"))}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No stage nodes are available for the active filters.</p>
      )}
      {visibleEdges.length ? (
        <ul className="compact-list">
          {visibleEdges.map((edge) => (
            <li key={String(edge.id)}>
              <strong>{formatDisplayLabel(String(edge.user_facing_label ?? edge.edge_type ?? "edge"))}</strong>
              <span>{formatNodeRef(edge.source)} {"->"} {formatNodeRef(edge.target)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No stage edges are available for the active relationship class.</p>
      )}
      <div className="graph-view-summary">
        <span>{sourceCoverageLabel}</span>
        <span>{sourceFamilyLabel}</span>
        <span>{evidenceRefsLabel}</span>
      </div>
      {sourceFamilyCoverage.length ? (
        <ul className="compact-list">
          {sourceFamilyCoverage.map((family) => (
            <li key={String(family.source_family)}>
              <strong>{formatSourceFamilyLabel(String(family.source_family))}</strong>
              <span>
                {String(formatDisplayValue(String(family.source_status ?? "partial")))} | sources: {String(family.source_count ?? "n/a")}
                {formatSourceList(family.source_ids)}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
      {sourceSupportRows.length ? (
        <div className="graph-view-summary source-support-summary">
          <strong>Evidence support by source</strong>
          <ul className="compact-list">
            {sourceSupportRows.map((source) => (
              <li key={String(source.source_id)}>
                <strong>{formatSourceDisplayRef(String(source.source_id)) || formatDisplayLabel(String(source.source_id))}</strong>
                <span>
                  {formatDisplayLabel(String(source.tier ?? "source"))} | {formatCoverageText(source.source_scope, stage.id)}
                </span>
                <span>{formatCoverageText(source.coverage_summary, stage.id)}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {sourceGaps.length || proxyLimitations.length ? (
        <p className="muted">This stage has documented source gaps and proxy limits. Open audit details for the full caveat list.</p>
      ) : null}
    </section>
  );
}

function rows(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object") : [];
}

function list(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)).filter(Boolean) : [];
}

function relationshipClassLabel(value: RelationshipClassFilter) {
  switch (value) {
    case "SUPPLY_RELATIONSHIP":
      return "Supply relationships";
    case "DEMAND_RELATIONSHIP":
      return "Demand relationships";
    case "PRODUCTION_DEPENDENCY":
      return "Production dependencies";
    case "EVIDENCE_CONTEXT":
      return "Evidence context";
    default:
      return "All relationship classes";
  }
}

function formatNodeRef(value: unknown) {
  const raw = String(value ?? "node");
  const directNode = formatNodeDisplayRef(raw);
  if (directNode) return directNode;
  const tail = raw.includes(":") ? raw.split(":").pop() ?? raw : raw;
  return formatDisplayLabel(tail);
}

function formatSourceFamilyLabel(value: string) {
  const sourceLabel = formatSourceDisplayRef(value);
  if (sourceLabel) return sourceLabel;
  switch (value) {
    case "national_policy_macro_public":
      return "National, policy, macro public sources";
    case "enterprise_public_disclosure":
      return "Enterprise public disclosures";
    case "industry_public_fixture":
      return "Industry public fixture sources";
    default:
      return formatDisplayLabel(value);
  }
}

function formatSourceList(value: unknown) {
  if (!Array.isArray(value) || value.length === 0) return "";
  const labels = value
    .slice(0, 2)
    .map((item) => formatSourceDisplayRef(String(item)) || formatDisplayLabel(String(item)))
    .filter(Boolean);
  if (labels.length === 0) return "";
  const suffix = value.length > labels.length ? ` +${value.length - labels.length} more` : "";
  return `: ${labels.join(", ")}${suffix}`;
}

function formatCoverageText(value: unknown, stageId: StageId) {
  const stageLabel = stageViewOptions.find((option) => option.id === stageId)?.label ?? formatDisplayLabel(stageId);
  return String(value ?? "Coverage summary unavailable")
    .replaceAll(stageId, stageLabel)
    .replaceAll("SUPPLY_RELATIONSHIP", "supply relationships")
    .replaceAll("DEMAND_RELATIONSHIP", "demand relationships")
    .replaceAll("PRODUCTION_DEPENDENCY", "production dependencies")
    .replaceAll("EVIDENCE_CONTEXT", "evidence context");
}
