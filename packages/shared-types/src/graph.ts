import type { RiskLevel } from "./common";
import type { DataCatalogSummary } from "./health";

export interface GraphSnapshotPayload {
  snapshot: {
    snapshot_id: string;
    graph_version: string;
    as_of_time: string;
    node_count: number;
    edge_count: number;
    checksum: string;
  };
  edge_states: Array<{
    edge_id: string;
    source_id: string;
    target_id: string;
    edge_type: string;
    weight: number;
    confidence: number;
    risk_score: number;
  }>;
  path_index: Array<{
    path_id: string;
    source_id: string;
    target_id: string;
    meta_path: string;
    node_sequence: string[];
    edge_sequence: string[];
    path_length: number;
    path_weight: number;
    path_risk: number;
    path_confidence: number;
  }>;
  source_manifest: {
    manifest_ref: string;
    checksum: string;
    sources: string[];
    freshness: Array<{
      source_id: string;
      status: "fresh" | "stale" | "partial" | "unavailable";
      last_successful_ingest: string;
      max_stale_minutes: number;
      record_count: number;
      checksum: string;
    }>;
  };
}

export type GraphNodeKind =
  | "company"
  | "supplier"
  | "facility"
  | "commodity"
  | "route"
  | "country"
  | "risk"
  | "data"
  | "raw_material"
  | "component"
  | "product_grade"
  | "supplier_tier"
  | "factory"
  | "warehouse"
  | "route_lane"
  | "carrier";

export type GraphPathDirection = "upstream" | "downstream" | "both";

export interface GraphExplorerQuery {
  selectedNodeId?: string;
  pathDirection?: GraphPathDirection;
  countryCode?: string | null;
  provinceCode?: string | null;
  geoId?: string | null;
  nodeKinds?: GraphNodeKind[];
  edgeTypes?: string[];
}

export interface GraphNode {
  id: string;
  label: string;
  kind: GraphNodeKind;
  level: RiskLevel;
  score: number;
  x: number;
  y: number;
  metadata: Record<string, string | number | boolean | null>;
  countryCode?: string;
  entityType?: string;
  riskScore?: number;
  centralityScore?: number;
  criticalityScore?: number;
  criticalityRank?: number;
  inDegree?: number;
  outDegree?: number;
  weightedDegree?: number;
  pathThroughCount?: number;
  riskDrivers?: string[];
  geoId?: string;
  geoLevel?: "country" | "province" | "region" | "aggregate" | "unknown" | string;
  provinceCode?: string | null;
  parentGeoId?: string | null;
  sourceCountryCode?: string | null;
  displayName?: string;
}

export interface GraphLink {
  id: string;
  source: string;
  target: string;
  label: string;
  weight: number;
  level: RiskLevel;
  edgeType?: string;
  riskScore?: number;
  confidence?: number;
  sourceId?: string;
  transmissionWeight?: number;
  lagDays?: number;
  sourceCountry?: string;
  targetCountry?: string;
  edgeRole?: "transmission" | "governance" | "evidence" | "location" | "classification" | "context" | string;
  metadata?: Record<string, string | number | boolean | null>;
}

export interface GraphStatCount {
  kind?: GraphNodeKind;
  source?: string;
  count: number;
}

export interface GraphExplorerStats {
  totalNodes: number;
  totalLinks: number;
  renderedNodeLimit: number;
  renderedLinkLimit: number;
  highRiskNodes: number;
  highRiskLinks: number;
  byKind: GraphStatCount[];
  bySource: GraphStatCount[];
}

export interface CriticalGraphNode {
  id: string;
  label: string;
  kind: GraphNodeKind;
  level: RiskLevel;
  score: number;
  countryCode?: string;
  entityType?: string;
  riskScore?: number;
  centralityScore?: number;
  criticalityScore?: number;
  criticalityRank?: number;
  inDegree?: number;
  outDegree?: number;
  weightedDegree?: number;
  pathThroughCount?: number;
  drivers: string[];
  riskDrivers?: string[];
  geoId?: string;
  geoLevel?: "country" | "province" | "region" | "aggregate" | "unknown" | string;
  provinceCode?: string | null;
  parentGeoId?: string | null;
  sourceCountryCode?: string | null;
}

export interface TransmissionPathStep {
  id: string;
  nodeId: string;
  label: string;
  kind: GraphNodeKind | "signal";
  level: RiskLevel;
  contribution: number;
  countryCode?: string;
  evidence: string;
  edgeId?: string | null;
  edgeType?: string | null;
  confidence?: number;
  sourceId?: string;
  geoId?: string;
  geoLevel?: string;
  provinceCode?: string | null;
}

export interface GraphTransmissionPath {
  id: string;
  title: string;
  sourceId: string;
  targetId: string;
  sourceLabel: string;
  targetLabel: string;
  targetCompany: string;
  scoreMove: number;
  confidence: number;
  pathRisk: number;
  pathConfidence: number;
  pathWeight?: number;
  transmissionScore: number;
  nodeSequence: string[];
  edgeSequence: string[];
  countrySequence: string[];
  bottleneckEdgeId: string;
  steps: TransmissionPathStep[];
  summary: string;
}

export interface GraphTransmissionSummary {
  pathCount: number;
  transmissionEdgeCount: number;
  maxHops: number;
  topK: number;
  pathDirection?: GraphPathDirection;
  contextEdgesSuppressed: number;
}

export interface CountryRiskSummary {
  code: string;
  label: string;
  countryCode: string;
  countryName: string;
  entityCount: number;
  edgeCount: number;
  riskScore: number;
  centralityScore: number;
  inboundRisk: number;
  outboundRisk: number;
  subdivisions?: Array<{
    geoId: string;
    label: string;
    provinceCode?: string;
    entityCount: number;
    riskScore: number;
  }>;
}

export interface CountryTransmissionEdge {
  id: string;
  sourceCountry: string;
  targetCountry: string;
  edgeCount: number;
  riskScore: number;
  transmissionWeight: number;
  topEdgeTypes: Array<{ edgeType: string; count: number }>;
}

export interface CountryDataCoverage {
  countryCode: string;
  sourceId: string;
  nodeCount: number;
  coverageScore: number;
}

export interface CountryLensData {
  selectedCountryCode: string;
  selectedProvinceCode?: string | null;
  selectedGeoId?: string | null;
  countries: CountryRiskSummary[];
  countryEdges: CountryTransmissionEdge[];
  topCriticalNodes: CriticalGraphNode[];
  topPaths: GraphTransmissionPath[];
  dataCoverage: CountryDataCoverage[];
  countryCode: string;
  countryName: string;
  riskScore: number;
  criticalNodes: CriticalGraphNode[];
  transmissionPaths: GraphTransmissionPath[];
}

export interface GraphExplorerData {
  nodes: GraphNode[];
  links: GraphLink[];
  filters: GraphNodeKind[];
  query?: GraphExplorerQuery;
  selectedNodeId: string;
  dataSummary?: DataCatalogSummary;
  graphStats?: GraphExplorerStats;
  criticalNodes?: CriticalGraphNode[];
  transmissionPaths?: GraphTransmissionPath[];
  transmissionSummary?: GraphTransmissionSummary;
  countryLens?: CountryLensData;
  availableCountries?: CountryRiskSummary[];
  truncated?: {
    nodes: boolean;
    links: boolean;
    renderedNodeLimit: number;
    renderedLinkLimit: number;
  };
}

export interface PathStep {
  id: string;
  label: string;
  kind: GraphNodeKind | "signal";
  level: RiskLevel;
  contribution: number;
  evidence: string;
}

export interface ExplainedPath {
  id: string;
  title: string;
  targetCompany: string;
  scoreMove: number;
  confidence: number;
  steps: PathStep[];
  summary: string;
}

export interface PathExplainerData {
  paths: ExplainedPath[];
  selectedPathId: string;
}

export interface GraphVersion {
  id: string;
  label: string;
  createdAt: string;
  author: string;
  status: "draft" | "candidate" | "promoted" | "archived";
  nodes: number;
  edges: number;
  schemaChanges: number;
  riskScoreDelta: number;
  validationPassRate: number;
}

export interface GraphDiffRow {
  id: string;
  area: string;
  change: string;
  severity: RiskLevel;
  count: number;
}

export interface GraphVersionStudioData {
  versions: GraphVersion[];
  baselineVersionId: string;
  candidateVersionId: string;
  diffRows: GraphDiffRow[];
}

export interface SemiriskGraphSnapshotData {
  graph_version: string;
  ontology_version: string;
  source_manifest_id: string;
  as_of_time: string;
  node_count: number;
  edge_count: number;
  node_count_by_type: Record<string, number>;
  edge_count_by_type: Record<string, number>;
  missing_provenance_count: number;
  unresolved_entity_count: number;
  stale_source_count: number;
  nodes: Array<Record<string, unknown>>;
  edges: Array<Record<string, unknown>>;
  quality_report: Record<string, unknown>;
}

export interface SemiriskGraphNeighborhoodData {
  graph_version: string;
  source_manifest_id: string;
  as_of_time: string;
  node_id: string;
  depth: number;
  nodes: Array<Record<string, unknown>>;
  edges: Array<Record<string, unknown>>;
  warnings: string[];
}
