import type { ApiEnvelope, Entity, GraphSnapshotPayload, Prediction, SimulationResult } from "@supply-risk/shared-types";

export const metadata = {
  graph_version: "g_20260201T000000Z_demo",
  feature_version: "f_20260201T000000Z_demo",
  label_version: "l_20260201T000000Z",
  model_version: "baseline_v0.1.0",
  as_of_time: "2026-02-01T00:00:00Z",
  audit_ref: "audit_synthetic_demo",
  lineage_ref: "lineage_synthetic_seed_42",
};

function envelope<T>(data: T): ApiEnvelope<T> {
  return {
    request_id: "req_web_mock",
    status: "success",
    data,
    metadata,
    warnings: [],
    errors: [],
  };
}

export const mockEntities = envelope<Entity[]>([
  { canonical_id: "firm_anchor", entity_type: "firm", display_name: "Atlas Motors", country: "US", industry: "Automotive", confidence: 0.98 },
  { canonical_id: "firm_chip", entity_type: "firm", display_name: "Formosa Silicon", country: "TW", industry: "Semiconductors", confidence: 0.98 },
  { canonical_id: "firm_sensor", entity_type: "firm", display_name: "Kyoto Sensors", country: "JP", industry: "Electronics", confidence: 0.97 },
  { canonical_id: "port_kaohsiung", entity_type: "port", display_name: "Port of Kaohsiung", country: "TW", confidence: 0.99 },
  { canonical_id: "product_chip", entity_type: "product", display_name: "Automotive MCU", confidence: 0.97 },
]);

export const mockGraph = envelope<GraphSnapshotPayload>({
  snapshot: {
    snapshot_id: "snapshot_demo",
    graph_version: metadata.graph_version,
    as_of_time: metadata.as_of_time,
    node_count: 17,
    edge_count: 13,
    checksum: "b7f4f1d6a890",
  },
  edge_states: [
    { edge_id: "edge_supply_chip_anchor", source_id: "firm_chip", target_id: "firm_anchor", edge_type: "supplies_to", weight: 0.7, confidence: 0.9, risk_score: 0.66 },
    { edge_id: "edge_sensor_anchor", source_id: "firm_sensor", target_id: "firm_anchor", edge_type: "supplies_to", weight: 0.61, confidence: 0.88, risk_score: 0.22 },
    { edge_id: "edge_chip_port", source_id: "firm_chip", target_id: "port_kaohsiung", edge_type: "ships_through", weight: 0.58, confidence: 0.86, risk_score: 0.34 },
  ],
  path_index: [
    { path_id: "path_chip_anchor", source_id: "firm_chip", target_id: "firm_anchor", meta_path: "supplies_to", path_length: 1, path_risk: 0.66, path_confidence: 0.9 },
    { path_id: "path_port_anchor", source_id: "firm_chip", target_id: "firm_anchor", meta_path: "ships_through>route_connects>supplies_to", path_length: 3, path_risk: 0.74, path_confidence: 0.71 },
  ],
});

export const mockPredictions = envelope<Prediction[]>([
  {
    prediction_id: "pred_anchor",
    target_id: "firm_anchor",
    target_type: "firm",
    prediction_time: metadata.as_of_time,
    horizon: 30,
    risk_score: 0.72,
    risk_level: "high",
    confidence_low: 0.6,
    confidence_high: 0.84,
    model_version: metadata.model_version,
    graph_version: metadata.graph_version,
    feature_version: metadata.feature_version,
    label_version: metadata.label_version,
    top_drivers: ["incoming_risk_mean", "path_risk_max", "inbound_edge_count"],
    top_paths: ["path_chip_anchor", "path_port_anchor"],
  },
  {
    prediction_id: "pred_chip",
    target_id: "firm_chip",
    target_type: "firm",
    prediction_time: metadata.as_of_time,
    horizon: 30,
    risk_score: 0.61,
    risk_level: "medium",
    confidence_low: 0.49,
    confidence_high: 0.73,
    model_version: metadata.model_version,
    graph_version: metadata.graph_version,
    feature_version: metadata.feature_version,
    label_version: metadata.label_version,
    top_drivers: ["event_affects", "ships_through", "policy_targets"],
    top_paths: ["path_port_anchor"],
  },
]);

export const mockSimulation = envelope<SimulationResult>({
  intervention_type: "close_port",
  target_id: "port_kaohsiung",
  base_graph_version: metadata.graph_version,
  counterfactual_graph_version: "cf_port_kaohsiung_demo",
  removed_edges: ["edge_chip_port"],
  risk_delta: -0.34,
});
