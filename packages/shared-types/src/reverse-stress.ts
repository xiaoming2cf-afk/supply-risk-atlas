import type { ForwardScenarioAffectedNode, ForwardScenarioInput, ForwardScenarioTransmissionPath } from "./scenario";
import type { RunReference } from "./runs";

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
  scenario_run?: RunReference | null;
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
