import type { InterventionOptimizationInput, InterventionOptimizationResult } from "./optimization";
import type { SemiriskEntityRiskScore } from "./risk";
import type { RunReference } from "./runs";
import type { ForwardScenarioInput, ForwardScenarioResult } from "./scenario";
import type { ReverseStressInput, ReverseStressResult } from "./reverse-stress";

export interface InvestigationReportInput {
  entity_id: string;
  include_entity_risk: boolean;
  forward_scenario_payload?: ForwardScenarioInput | null;
  reverse_stress_payload?: ReverseStressInput | null;
  optimization_payload?: InterventionOptimizationInput | null;
  forward_run?: RunReference | null;
  reverse_stress_run?: RunReference | null;
  optimization_run?: RunReference | null;
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
  selected_run_refs?: RunReference[];
  markdown?: string;
}
