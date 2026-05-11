import type { ForwardScenarioInput } from "./scenario";
import type { ReverseStressInput } from "./reverse-stress";
import type { RunReference } from "./runs";

export interface InterventionOptimizationInput {
  graph_version?: string | null;
  scenario_run?: RunReference | null;
  reverse_stress_run?: RunReference | null;
  scenario_set?: RunReference[];
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
