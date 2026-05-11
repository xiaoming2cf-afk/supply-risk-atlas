import type { RiskLevel } from "./common";
import type { GraphLink, GraphNode } from "./graph";

export interface SimulationResult {
  intervention_type: string;
  target_id: string;
  base_graph_version: string;
  counterfactual_graph_version: string;
  removed_edges: string[];
  risk_delta: number;
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
