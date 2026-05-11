import type { RiskLevel } from "./common";

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
