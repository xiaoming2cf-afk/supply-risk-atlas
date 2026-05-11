export type ApiStatus = "success" | "error";

export type ApiMode = "real";

export type ApiSourceStatus = "fresh" | "stale" | "partial" | "unavailable" | "unauthorized" | "fallback" | "error";

export interface VersionMetadata {
  graph_version: string;
  feature_version: string;
  label_version: string;
  model_version: string;
  as_of_time: string;
  audit_ref?: string | null;
  lineage_ref?: string | null;
  data_mode?: "real";
  freshness_status?: "fresh" | "stale" | "partial" | "unavailable";
  source_count?: number;
  source_manifest_ref?: string | null;
}

export interface ApiError {
  code: string;
  message: string;
  field?: string | null;
}

export interface ApiEnvelope<T> {
  request_id: string;
  status: ApiStatus;
  data: T | null;
  metadata: VersionMetadata;
  warnings: string[];
  errors: ApiError[];
  mode?: ApiMode;
  source_status?: ApiSourceStatus;
  source?: {
    name?: string;
    url?: string;
    lineage_ref?: string | null;
    license?: string | null;
  };
}

export interface ApiResult<T> {
  data: T | null;
  envelope: ApiEnvelope<T>;
  mode: ApiMode;
  sourceStatus: ApiSourceStatus;
  receivedAt: string;
  httpStatus?: number;
}

export interface Entity {
  canonical_id: string;
  entity_type: string;
  display_name: string;
  country?: string | null;
  industry?: string | null;
  external_ids?: Record<string, string>;
  confidence: number;
  geoId?: string;
  geoLevel?: "country" | "province" | "region" | "aggregate" | "unknown" | string;
  countryCode?: string;
  provinceCode?: string | null;
  parentGeoId?: string | null;
  sourceCountryCode?: string | null;
  displayName?: string;
}

export interface PredictionScoreComponents {
  baseline?: number;
  degree_exposure?: number;
  graph_propagation?: number;
  path_transmission?: number;
  scenario_shock?: number;
  evidence_coverage?: number;
  [key: string]: number | undefined;
}

export interface PredictionDriverContribution {
  driver: string;
  score: number;
  weight: number;
  contribution: number;
  pathId?: string;
}

export interface PredictionPathDetail {
  pathId: string;
  nodeSequence: string[];
  edgeSequence: string[];
  nodeLabels: string[];
  edgeTypes: string[];
  pathRisk: number;
  pathConfidence: number;
  transmissionScore: number;
  pathContribution?: number;
  bottleneckEdgeId?: string | null;
  bottleneckEdgeType?: string | null;
  bottleneckScore?: number | null;
  evidenceRefs: string[];
}

export interface PredictionSourceCoverage {
  sourceCount: number;
  coveredSourceCount: number;
  coverageScore: number;
  coveredSources: string[];
  manifestRef: string;
}

export interface PredictionSensitivityDiagnostic {
  factor: string;
  baselineValue: number;
  direction: "up" | "down" | "flat" | string;
  deltaIfReduced10Pct: number;
  deltaIfIncreased10Pct: number;
  pathId?: string;
  edgeId?: string;
  edgeType?: string;
}

export interface Prediction {
  prediction_id: string;
  target_id: string;
  target_type: string;
  prediction_time: string;
  horizon: number;
  risk_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  confidence_low: number;
  confidence_high: number;
  model_version: string;
  graph_version: string;
  feature_version: string;
  label_version: string;
  top_drivers: string[];
  top_paths: string[];
  score_components?: PredictionScoreComponents;
  driver_contributions?: PredictionDriverContribution[];
  prediction_form?: string;
  mechanism?: string;
  confidence_interval?: {
    low: number;
    high: number;
    horizonDays: number;
  };
  path_details?: PredictionPathDetail[];
  evidence_refs?: string[];
  source_coverage?: PredictionSourceCoverage;
  sensitivity_diagnostics?: PredictionSensitivityDiagnostic[];
}

export interface PredictionMechanismSummary {
  mechanism: string;
  count: number;
  maxRisk: number;
  averageRisk: number;
  averageSourceCoverage?: number;
}

export interface PredictionCenterData {
  lastUpdated: string;
  modelVersion: string;
  predictionForm: string;
  predictions: Prediction[];
  topPredictions: Prediction[];
  mechanisms: PredictionMechanismSummary[];
  highConfidenceCount: number;
  saturatedScoreCount: number;
}

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

export interface SimulationResult {
  intervention_type: string;
  target_id: string;
  base_graph_version: string;
  counterfactual_graph_version: string;
  removed_edges: string[];
  risk_delta: number;
}

export type RiskLevel = "low" | "guarded" | "elevated" | "severe" | "critical";

export type TrendDirection = "up" | "down" | "flat";

export type DashboardPageId =
  | "system-health-center"
  | "global-risk-cockpit"
  | "graph-explorer"
  | "company-risk-360"
  | "prediction-center"
  | "path-analysis"
  | "country-lens"
  | "path-explainer"
  | "shock-simulator"
  | "reverse-stress-lab"
  | "intervention-optimizer"
  | "investigation-report"
  | "causal-evidence-board"
  | "graph-version-studio";

export interface DashboardPage {
  id: DashboardPageId;
  label: string;
  shortLabel: string;
  description: string;
}

export const dashboardPages: DashboardPage[] = [
  {
    id: "system-health-center",
    label: "System Health Center",
    shortLabel: "Health",
    description: "Data pipeline, source registry, freshness, API, and graph service health",
  },
  {
    id: "global-risk-cockpit",
    label: "Global Risk Cockpit",
    shortLabel: "Cockpit",
    description: "Live exposure map, risk pressure, and incident queue",
  },
  {
    id: "graph-explorer",
    label: "Graph Explorer",
    shortLabel: "Graph",
    description: "Supplier, facility, commodity, route, and country network",
  },
  {
    id: "company-risk-360",
    label: "Entity Risk 360",
    shortLabel: "Risk 360",
    description: "Fixture-labeled entity risk score, components, evidence refs, and graph context",
  },
  {
    id: "prediction-center",
    label: "Prediction Center",
    shortLabel: "Predict",
    description: "Ensemble risk forecasts, mechanism labels, confidence bands, and evidence paths",
  },
  {
    id: "path-analysis",
    label: "Path Analysis",
    shortLabel: "Paths",
    description: "Top-K transmission paths with hop-by-hop evidence",
  },
  {
    id: "country-lens",
    label: "Country Lens",
    shortLabel: "Country",
    description: "Country risk, critical nodes, data coverage, and cross-border flow",
  },
  {
    id: "shock-simulator",
    label: "Shock Simulator",
    shortLabel: "Simulator",
    description: "Stress test regions, commodities, severity, and recovery",
  },
  {
    id: "reverse-stress-lab",
    label: "Reverse Stress Lab",
    shortLabel: "Reverse",
    description: "Find plausible shock sets that can breach a normalized failure threshold",
  },
  {
    id: "intervention-optimizer",
    label: "Intervention Optimizer",
    shortLabel: "Optimize",
    description: "Budget-constrained fixture graph resilience action selection",
  },
  {
    id: "investigation-report",
    label: "Investigation Report",
    shortLabel: "Report",
    description: "Auditable JSON and Markdown report export with evidence and version metadata",
  },
  {
    id: "causal-evidence-board",
    label: "Causal Evidence Board",
    shortLabel: "Evidence",
    description: "Evidence quality, causal claims, and disagreement tracking",
  },
  {
    id: "graph-version-studio",
    label: "Graph Version Studio",
    shortLabel: "Versions",
    description: "Compare graph builds, schema drift, and promotion readiness",
  },
];

export interface RiskMetric {
  id: string;
  label: string;
  value: number;
  unit?: string;
  displayValue?: string;
  delta: number;
  trend: TrendDirection;
  level: RiskLevel;
  detail: string;
}

export interface Hotspot {
  id: string;
  label: string;
  region: string;
  level: RiskLevel;
  score: number;
  x: number;
  y: number;
  drivers: string[];
}

export interface Incident {
  id: string;
  title: string;
  region: string;
  level: RiskLevel;
  startedAt: string;
  affectedCompanies: number;
  signalStrength: number;
}

export interface CorridorRisk {
  id: string;
  source: string;
  target: string;
  commodity: string;
  level: RiskLevel;
  score: number;
  volumeShare: number;
}

export interface GlobalRiskCockpitData {
  lastUpdated: string;
  operatingMode: "real";
  metrics: RiskMetric[];
  hotspots: Hotspot[];
  incidents: Incident[];
  corridors: CorridorRisk[];
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
  metadata: Record<string, string | number>;
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

export interface SupplierExposure {
  id: string;
  supplier: string;
  country: string;
  category: string;
  spendShare: number;
  dependency: number;
  level: RiskLevel;
  leadTimeDays: number;
}

export interface CompanyRiskProfile {
  id: string;
  name: string;
  ticker: string;
  sector: string;
  headquarters: string;
  riskScore: number;
  confidence: number;
  level: RiskLevel;
  revenueAtRiskUsd: number;
  suppliers: SupplierExposure[];
  topDrivers: string[];
  mitigations: string[];
}

export interface CompanyRisk360Data {
  companies: CompanyRiskProfile[];
  selectedCompanyId: string;
  featureGates?: {
    watchlistAlertsDefaultEnabled: boolean;
    watchlistAlertsMode: "default" | "experimental" | string;
    reason: string;
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

export interface ShockSimulationInput {
  region: string;
  commodity: string;
  supplier?: string | null;
  route?: string | null;
  severity: number;
  durationDays: number;
  scope: "facility" | "regional" | "global";
}

export type ForwardScenarioType =
  | "earthquake"
  | "export_control"
  | "material_shortage"
  | "demand_spike"
  | "port_disruption"
  | "factory_shutdown"
  | "cyber_incident"
  | "power_outage";

export interface ScenarioDistribution {
  type: "fixed" | "constant" | "triangular" | "beta" | "uniform" | "normal" | "bounded_normal" | "lognormal";
  params: Record<string, number>;
}

export interface ForwardScenarioInput {
  scenario_type: ForwardScenarioType;
  targets: string[];
  severity_distribution: ScenarioDistribution;
  duration_days_distribution: ScenarioDistribution;
  iterations: number;
  seed: number;
  as_of_time: string;
  graph_version?: string | null;
  assumptions?: string[];
  loss_mode?: "affected_mean" | "graph_weighted_loss" | "demand_fulfillment_loss" | "resilience_integral_loss" | "capacity_functionality_loss";
  propagation_mode?: "auto_semiconductor" | "max" | "additive_cap" | "noisy_or" | "leontief_bottleneck" | "psi_recursive";
  functionality_metric?: string;
  weighting_method?: string;
}

export interface ForwardScenarioAffectedNode {
  node_id: string;
  label: string;
  node_type: string;
  loss_score: number;
  evidence_refs: Array<Record<string, unknown>>;
}

export interface ForwardScenarioTransmissionPath {
  path_id: string;
  node_sequence: string[];
  edge_sequence: string[];
  loss_contribution: number;
  evidence_refs: Array<Record<string, unknown>>;
  explanation: string;
}

export interface ForwardScenarioResult {
  run_id: string;
  seed: number;
  graph_version: string;
  source_manifest_id: string;
  simulation_version: "semirisk_forward_mc_v0.1" | string;
  timestamp: string;
  scenario_type: ForwardScenarioType;
  expected_loss: number | null;
  p50_loss: number | null;
  p90_loss: number | null;
  p95_loss: number | null;
  cvar_95: number | null;
  time_to_recover_days: number | null;
  time_to_survive_days: number | null;
  loss_mode: string;
  propagation_mode: string;
  functionality_metric: string;
  functionality_curve: Array<Record<string, number>>;
  functionality_curve_summary: Record<string, number>;
  resilience_integral_loss: number | null;
  graph_weighted_loss: number | null;
  demand_fulfillment_loss: number | null;
  capacity_functionality_loss: number | null;
  affected_mean: number | null;
  weight_basis: Record<string, unknown>;
  formula_refs: string[];
  calibration_status: string;
  affected_nodes: ForwardScenarioAffectedNode[];
  top_transmission_paths: ForwardScenarioTransmissionPath[];
  loss_distribution_summary: Record<string, number | null>;
  warnings: string[];
  assumptions: string[];
  evidence_refs: Array<Record<string, unknown>>;
  input: ForwardScenarioInput;
  fixture_graph: boolean;
}

export type ReverseStressTargetMetric =
  | "capacity_loss"
  | "cvar95_loss"
  | "demand_fulfillment_loss"
  | "affected_critical_nodes";

export interface ReverseStressInput {
  target_metric: ReverseStressTargetMetric;
  failure_threshold: number;
  candidate_scope: {
    node_types: string[];
    edge_types: string[];
  };
  max_combination_size: number;
  beam_width: number;
  iterations_per_candidate: number;
  seed: number;
  as_of_time: string;
  graph_version?: string | null;
  allowed_shock_types?: string[];
  forbidden_shock_types?: string[];
  loss_mode?: ForwardScenarioInput["loss_mode"];
  propagation_mode?: ForwardScenarioInput["propagation_mode"];
  functionality_metric?: string;
  weighting_method?: string;
}

export interface ReverseShockSet {
  shock_set_id: string;
  shocks: Array<Record<string, unknown>>;
  expected_loss: number | null;
  cvar95: number | null;
  threshold_met: boolean;
  plausibility_cost: number;
  affected_nodes: ForwardScenarioAffectedNode[];
  affected_paths: ForwardScenarioTransmissionPath[];
  explanation: string;
  evidence_refs: Array<Record<string, unknown>>;
  assumptions: string[];
  loss_mode?: string;
  propagation_mode?: string;
  threshold_metric_basis?: string;
}

export interface ReverseStressResult {
  run_id: string;
  seed: number;
  graph_version: string;
  source_manifest_id: string;
  simulation_version: "semirisk_reverse_stress_v0.1" | string;
  timestamp: string;
  failure_threshold_input: number;
  failure_threshold_normalized: number;
  threshold_metric_basis: string;
  loss_mode: string;
  propagation_mode: string;
  ranked_shock_sets: ReverseShockSet[];
  expected_loss: number | null;
  cvar95: number | null;
  plausibility_cost: number | null;
  affected_nodes: ForwardScenarioAffectedNode[];
  affected_paths: ForwardScenarioTransmissionPath[];
  explanation: string;
  evidence_refs: Array<Record<string, unknown>>;
  baseline_comparison: Array<Record<string, unknown>>;
  warnings: string[];
  assumptions: string[];
  input: ReverseStressInput;
  fixture_graph: boolean;
}

export interface InterventionOptimizationInput {
  graph_version?: string | null;
  scenario_run?: Record<string, unknown> | null;
  reverse_stress_run?: Record<string, unknown> | null;
  scenario_set?: Array<Record<string, unknown>>;
  forward_scenario_payload?: ForwardScenarioInput | null;
  reverse_stress_payload?: ReverseStressInput | null;
  budget: number;
  allowed_intervention_types: string[];
  max_actions: number;
  risk_aversion_beta: number;
  compliance_constraints: Record<string, boolean>;
  seed: number;
  as_of_time: string;
}

export interface InterventionAction {
  action_id: string;
  intervention_type: string;
  target_id: string;
  target_type: string;
  target_label: string;
  cost: number;
  expected_effect: string;
  expected_loss_reduction: number;
  cvar95_reduction: number;
  target_risk_score: number;
  assumptions: string[];
  constraints: string[];
  evidence_refs: Array<Record<string, unknown>>;
  compliance_note: string;
}

export interface InterventionOptimizationResult {
  run_id: string;
  seed: number;
  graph_version: string;
  source_manifest_id: string;
  optimization_version: "semirisk_intervention_optimizer_v0.1" | string;
  timestamp: string;
  optimization_context_type: string;
  scenario_count: number;
  baseline_run_ids: string[];
  before_simulation_run_ids: string[];
  after_simulation_run_ids: string[];
  recommended_actions: InterventionAction[];
  before_expected_loss: number | null;
  after_expected_loss: number | null;
  before_cvar95: number | null;
  after_cvar95: number | null;
  heuristic_estimated_after_expected_loss: number | null;
  heuristic_estimated_after_cvar95: number | null;
  cost: number;
  budget: number;
  resilience_roi: number;
  affected_paths_reduced: string[];
  baseline_comparison: Array<Record<string, unknown>>;
  assumptions: string[];
  constraints: string[];
  evidence_refs: Array<Record<string, unknown>>;
  warnings: string[];
  fixture_graph: boolean;
}

export interface InvestigationReportInput {
  entity_id: string;
  include_entity_risk: boolean;
  forward_scenario_payload?: ForwardScenarioInput | null;
  reverse_stress_payload?: ReverseStressInput | null;
  optimization_payload?: InterventionOptimizationInput | null;
  format: "json" | "markdown";
}

export interface InvestigationReportData {
  report_id: string;
  report_version: "semirisk_investigation_report_v0.1" | string;
  generated_at: string;
  entity: Record<string, unknown>;
  risk_score: SemiriskEntityRiskScore | null;
  forward_stress: ForwardScenarioResult | null;
  reverse_stress: ReverseStressResult | null;
  intervention_optimization: InterventionOptimizationResult | null;
  evidence_summary: Array<Record<string, unknown>>;
  graph_context: {
    node_id: string;
    depth: number;
    node_count: number;
    edge_count: number;
    nodes: Array<Record<string, unknown>>;
    edges: Array<Record<string, unknown>>;
  };
  versions: {
    graph_version: string;
    source_manifest_id: string;
    feature_version: string | null;
    simulation_version: string | null;
    optimization_version: string | null;
    report_version: string;
  };
  methodology: Record<string, unknown>;
  formula_sources: {
    formula_refs: string[];
    source_principle_note: string;
  };
  model_limitations: string[];
  warnings: string[];
  assumptions: string[];
  limitations: string[];
  compliance_note: string;
  raw_payload_excluded: boolean;
  private_diagnostics_excluded: boolean;
  format: "json" | "markdown";
  markdown?: string;
}

export interface ShockAffectedPath {
  id: string;
  label: string;
  impact: number;
  grossImpact?: number;
  netImpact?: number;
  offsetAppliedPct?: number;
  level: RiskLevel;
}

export interface ScenarioDelta {
  targetId: string;
  targetLabel: string;
  baselineRisk: number;
  grossScenarioRisk?: number;
  scenarioRisk: number;
  netScenarioRisk?: number;
  grossDelta?: number;
  delta: number;
  offsetAppliedPct?: number;
  level: RiskLevel;
}

export type OffsetBreakdownKey =
  | "supplierDiversification"
  | "routeRedundancy"
  | "inventoryRecovery"
  | "substitutionReadiness"
  | "countryResilience"
  | "evidenceCoverage";

export interface OffsetBreakdownItem {
  key: OffsetBreakdownKey;
  label: string;
  score: number;
  weight: number;
  weightedScore: number;
  offsetPctContribution: number;
  confidence: number;
  standardRef: string;
  evidenceRef: string;
  dataSource: string;
}

export interface MitigationStandard {
  name: string;
  framework: string;
  calculation: string;
  standardCap: number;
  references: string[];
  monetaryAmountPolicy: string;
}

export interface ScenarioPathStepDetail {
  hop: number;
  nodeId: string;
  label: string;
  countryCode?: string;
  incomingEdgeId?: string | null;
  outgoingEdgeId?: string | null;
  grossContribution?: number;
}

export interface ScenarioEdgeDelta {
  edgeId: string;
  edgeType?: string;
  grossDelta: number;
  netDelta: number;
  offsetAppliedPct: number;
  confidence: number;
  evidenceRef?: string;
}

export interface ScenarioChangedPath {
  pathId: string;
  sourceId: string;
  targetId: string;
  sourceLabel: string;
  targetLabel: string;
  nodeSequence: string[];
  edgeSequence: string[];
  changedEdges: string[];
  edgeDeltas?: ScenarioEdgeDelta[];
  steps?: ScenarioPathStepDetail[];
  bottleneckEdgeId?: string | null;
  baseScore: number;
  grossScenarioScore?: number;
  scenarioScore: number;
  netScenarioScore?: number;
  grossDelta?: number;
  delta: number;
  offsetAppliedPct?: number;
  standardRefs?: string[];
  level: RiskLevel;
}

export interface ShockCountryImpact {
  countryCode: string;
  countryName: string;
  grossImpactScore: number;
  netImpactScore: number;
  offsetAmountPct: number;
  pathCount: number;
  affectedCompanies: number;
  level: RiskLevel;
}

export interface ShockCompanyImpact {
  companyId: string;
  companyLabel: string;
  countryCode?: string;
  industry?: string | null;
  grossImpactScore: number;
  netImpactScore: number;
  offsetAmountPct: number;
  level: RiskLevel;
}

export interface ScenarioGraphOverlay {
  activePathId?: string | null;
  activePathNodeIds: string[];
  activePathEdgeIds: string[];
  nodes: Array<Omit<GraphNode, "x" | "y" | "metadata"> & { x?: number; y?: number; metadata?: GraphNode["metadata"] }>;
  links: GraphLink[];
  edgeDeltaById?: Record<string, { grossDelta?: number; riskDelta?: number; weightDelta?: number }>;
}

export interface ShockSimulationResult {
  input: ShockSimulationInput;
  impactScore: number;
  grossImpactScore?: number;
  netImpactScore?: number;
  offsetScore?: number;
  offsetAmountPct?: number;
  offsetBreakdown?: OffsetBreakdownItem[];
  mitigationStandard?: MitigationStandard;
  ebitdaAtRiskUsd: number;
  timeToRecoveryDays: number;
  affectedCompanies: number;
  affectedPaths: ShockAffectedPath[];
  scenario_delta?: ScenarioDelta[];
  top_changed_paths?: ScenarioChangedPath[];
  changedPathDetails?: ScenarioChangedPath[];
  countryImpact?: ShockCountryImpact[];
  companyImpact?: ShockCompanyImpact[];
  scenarioGraphOverlay?: ScenarioGraphOverlay;
  diagnostics?: Record<string, string | number | boolean>;
  recommendations: string[];
}

export interface EvidenceItem {
  id: string;
  claim: string;
  source: string;
  method: "event-study" | "diff-in-diff" | "expert" | "graph-inference" | "news-signal";
  confidence: number;
  level: RiskLevel;
  lastReviewed: string;
  disagreement: number;
}

export interface CausalEvidenceBoardData {
  evidence: EvidenceItem[];
  activeClaimId: string;
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

export interface ServiceHealth {
  id: string;
  service: string;
  owner: string;
  status: "operational" | "degraded" | "down";
  latencyMs: number;
  freshnessMinutes: number;
  errorRate: number;
}

export interface PipelineStage {
  id: string;
  label: string;
  status: "complete" | "running" | "queued" | "blocked";
  processed: number;
  total: number;
}

export interface SourceRegistryRow {
  id: string;
  name: string;
  type: string;
  license: string;
  updateFrequency: string;
  reliabilityScore: number;
  owner: string;
  status: "fresh" | "stale" | "partial" | "unavailable";
  recordCount: number;
  maxStaleMinutes: number;
  checksum: string;
  latestRecordTime: string | null;
}

export interface SourceRegistrySummary {
  manifestRef: string;
  checksum: string;
  asOfTime: string;
  catalogSource?: string;
  promotedGraph?: {
    status: "promoted" | "partial";
    manifest: Record<string, unknown> | null;
  };
  sourceCount: number;
  rawRecordCount: number;
  silverEntityCount: number;
  silverEventCount: number;
  goldEdgeEventCount: number;
  dataNodeCount?: number;
  sources: SourceRegistryRow[];
}

export interface EntityResolutionSummary {
  totalEntities: number;
  averageConfidence: number;
  byEntityType: Array<{
    entityType: string;
    count: number;
  }>;
  bySource: Array<{
    sourceId: string;
    entityCount: number;
  }>;
}

export interface EvidenceLineageRecord {
  id: string;
  sourceId: string;
  sourceName: string;
  rawId: string;
  sourceRecordId: string;
  rawChecksum: string;
  rawObservedTime: string;
  silverEventIds: string[];
  silverEntityIds: string[];
  goldEdgeEventIds: string[];
  edgeTypes: string[];
  targetEntities: string[];
  confidence: number;
}

export interface EvidenceLineageSummary {
  manifestRef: string;
  checksum: string;
  asOfTime: string;
  rawRecordCount: number;
  silverEventCount: number;
  goldEdgeEventCount: number;
  records: EvidenceLineageRecord[];
}

export interface DataCatalogSummary {
  catalogSource: string;
  promoted: boolean;
  totalDataNodes: number;
  byType: Array<{
    entityType: string;
    count: number;
  }>;
  bySource: Array<{
    sourceId: string;
    count: number;
  }>;
  licensePolicies: Array<{
    id: string;
    name: string;
    sourceIds: string[];
    licenseUrl: string;
  }>;
  topNodes: Array<{
    id: string;
    name: string;
    entityType: string;
    sourceIds: string[];
    confidence: number;
  }>;
}

export interface SemiconductorGraphHealth {
  label: string;
  status: "ready" | "degraded" | "unavailable";
  fixtureGraph: boolean;
  registryReady: boolean;
  ontologyReady: boolean;
  fixtureManifestReady: boolean;
  fixtureGraphReady: boolean;
  graphVersion: string;
  ontologyVersion: string;
  sourceManifestId: string;
  asOfTime: string;
  nodeCount: number;
  edgeCount: number;
  nodeCountByType: Record<string, number>;
  edgeCountByType: Record<string, number>;
  missingProvenanceCount: number;
  unresolvedEntityCount: number;
  staleSourceCount: number;
  warnings: string[];
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

export interface SemiriskRiskEvidenceRef {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  edge_type: string;
  evidence_text_summary: string;
  source_refs: Array<{
    source_id: string;
    source_record_id: string;
    raw_id: string;
    payload_hash: string;
    provenance_url: string;
    retrieved_at: string;
    as_of_time: string;
  }>;
}

export interface SemiriskRiskComponent {
  name: string;
  value: number | null;
  normalized_value?: number | null;
  status: "available" | "unavailable";
  weight: number | null;
  weighted_contribution: number | null;
  evidence_refs: SemiriskRiskEvidenceRef[];
  explanation: string;
}

export interface SemiriskEntityRiskScore {
  node_id: string;
  entity: {
    node_id: string;
    node_type: string;
    canonical_name: string;
    attributes: Record<string, unknown>;
    confidence: number;
    valid_from: string;
    valid_to: string | null;
  };
  score: number;
  level: RiskLevel;
  scoring_method: string;
  formula_version: string;
  likelihood?: number;
  impact?: number;
  vulnerability_modifier?: number;
  components: SemiriskRiskComponent[];
  component_weights?: Record<string, number>;
  weighting_method?: string;
  weight_source?: string;
  calibration_status: string;
  concentration?: Record<string, unknown>;
  evidence_refs: SemiriskRiskEvidenceRef[];
  formula_refs: string[];
  feature_version: string;
  graph_version: string;
  source_manifest_id: string;
  as_of_time: string;
  fixture_graph: boolean;
  warnings: string[];
}

export interface SemiriskRiskPortfolioData {
  graph_version: string;
  source_manifest_id: string;
  feature_version: string;
  as_of_time: string;
  fixture_graph: boolean;
  node_type: string | null;
  scores: Array<{
    node_id: string;
    canonical_name: string;
    node_type: string;
    score: number;
    level: RiskLevel;
    evidence_ref_count: number;
    scoring_method?: string;
    calibration_status?: string;
  }>;
  warnings: string[];
}

export interface SystemHealthData {
  services: ServiceHealth[];
  stages: PipelineStage[];
  logs: string[];
  sourceRegistry: SourceRegistrySummary;
  entityResolution: EntityResolutionSummary;
  evidenceLineage: EvidenceLineageSummary;
  dataCatalog?: DataCatalogSummary;
  semiconductorGraph?: SemiconductorGraphHealth;
}
