export type RunType =
  | "forward_scenario"
  | "reverse_stress"
  | "intervention_optimization"
  | "investigation_report";

export interface RunVersions {
  model_version?: string | null;
  feature_version?: string | null;
  simulation_version?: string | null;
  optimization_version?: string | null;
  report_version?: string | null;
}

export interface RunReference {
  run_id: string;
  run_type: RunType;
  created_at: string;
  graph_version: string;
  source_manifest_id: string;
  status: string;
  warnings: string[];
  summary: Record<string, unknown>;
  evidence_refs: Array<Record<string, unknown> | string>;
  versions: RunVersions;
  fixture_limitations?: string[];
}

export interface RunHistoryData {
  run_store_version: string;
  graph_version: string;
  source_manifest_id: string;
  as_of_time: string;
  count: number;
  max_items: number;
  runs: RunReference[];
  warnings: string[];
}

export interface RunDetailData extends RunReference {
  run_store_version: string;
  raw_payload_excluded: boolean;
  private_diagnostics_excluded: boolean;
}
