import type { GraphViewModel, GraphVersionMetadata } from "../graphViewModel";

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
  metadata: GraphVersionMetadata;
  relationshipClassFilter: RelationshipClassFilter;
  stage: StageViewDefinition;
  view: GraphViewModel;
};

export function StageGraphView({
  endpointData,
  metadata,
  relationshipClassFilter,
  stage,
  view,
}: StageGraphViewProps) {
  const endpointNodes = rows(endpointData?.nodes).slice(0, 6);
  const endpointEdges = rows(endpointData?.edges).slice(0, 6);
  const sourceCoverage = rows(endpointData?.source_coverage).slice(0, 5);
  const sourceFamilyCoverage = rows(endpointData?.source_family_coverage).slice(0, 4);
  const evidenceRefs = rows(endpointData?.evidence_refs).slice(0, 5);
  const sourceGaps = list(endpointData?.source_gaps).slice(0, 3);
  const proxyLimitations = list(endpointData?.proxy_limitations).slice(0, 3);
  const fallbackNodes: Array<Record<string, unknown>> = view.visibleNodes
    .filter((node) => stage.nodeTypes.includes(node.kind))
    .slice(0, 6)
    .map((node) => ({ id: node.id, label: node.label, kind: node.kind }));
  const fallbackEdges: Array<Record<string, unknown>> = view.visibleLinks
    .filter((edge) => relationshipClassFilter === "all" || edge.metadata?.relationship_class === relationshipClassFilter)
    .slice(0, 6)
    .map((edge) => ({ id: edge.id, edge_type: edge.edgeType, source: edge.source, target: edge.target }));
  const visibleNodes = endpointNodes.length ? endpointNodes : fallbackNodes;
  const visibleEdges = endpointEdges.length ? endpointEdges : fallbackEdges;
  const propagates =
    relationshipClassFilter === "SUPPLY_RELATIONSHIP" || relationshipClassFilter === "PRODUCTION_DEPENDENCY";

  return (
    <section className="graph-list-section stage-graph-view" data-testid="stage-graph-view" data-stage-id={stage.id}>
      <div className="section-kicker">Supply-chain stage view</div>
      <h3>{stage.viewName}</h3>
      <p className="muted">{stage.label}: {stage.businessQuestion}</p>
      <div className="inspector-grid">
        <Metric label="graph_version" value={String(endpointData?.graph_version ?? metadata.graphVersion)} />
        <Metric label="source_manifest_id" value={String(endpointData?.source_manifest_id ?? metadata.sourceManifestId)} />
        <Metric label="data_mode" value={String(endpointData?.data_mode ?? "fixture")} />
        <Metric label="graph_mode" value={String(endpointData?.graph_mode ?? "fixture")} />
      </div>
      <p className="warning-text">
        fixture/promoted public-evidence view; evidence-context links are inspection links, not dependency edges.
      </p>
      <div className="graph-view-summary">
        <span>relationship class: {relationshipClassFilter}</span>
        <span>Can this edge propagate risk? {propagates ? "yes, if evidence-backed" : "no"}</span>
        <span>stage cap: 18 nodes / 30 edges</span>
      </div>
      {visibleNodes.length ? (
        <ul className="compact-list">
          {visibleNodes.map((node) => (
            <li key={String(node.id)}>
              <strong>{String(node.label ?? node.id)}</strong>
              <span>{String(node.kind ?? node.node_type ?? "node")}</span>
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
              <strong>{String(edge.edge_type ?? "edge")}</strong>
              <span>{String(edge.source)} {"->"} {String(edge.target)}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="muted">No stage edges are available for the active relationship class.</p>
      )}
      <div className="graph-view-summary">
        <span>source coverage: {sourceCoverage.length || "fallback"}</span>
        <span>source families: {sourceFamilyCoverage.length || "not recorded"}</span>
        <span>evidence refs: {evidenceRefs.length || "fallback"}</span>
      </div>
      {sourceFamilyCoverage.length ? (
        <ul className="compact-list">
          {sourceFamilyCoverage.map((family) => (
            <li key={String(family.source_family)}>
              <strong>{String(family.source_family)}</strong>
              <span>{String(family.source_status ?? "partial")} | sources: {String(family.source_count ?? "n/a")}</span>
            </li>
          ))}
        </ul>
      ) : null}
      {sourceGaps.length || proxyLimitations.length ? (
        <div className="graph-view-summary">
          <span>source gaps: {sourceGaps.join("; ") || "none"}</span>
          <span>proxy limitations: {proxyLimitations.join("; ") || "none"}</span>
        </div>
      ) : null}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function rows(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object") : [];
}

function list(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)).filter(Boolean) : [];
}
