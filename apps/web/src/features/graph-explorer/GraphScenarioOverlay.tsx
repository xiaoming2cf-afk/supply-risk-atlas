import type { GraphScenarioOverlayData } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function GraphScenarioOverlay({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const overlay = endpointData as GraphScenarioOverlayData | undefined;
  const affectedNodes = Array.isArray(overlay?.affected_nodes) ? overlay.affected_nodes : [];
  return (
    <div className="graph-v3-panel graph-v3-scenario-panel">
      <div className="section-kicker">Scenario overlay mode</div>
      <p className="inspector-note">Scenario overlay renders only a selected run. It never displays all runs by default.</p>
      <div className="inspector-grid">
        <span>run_id: {overlay?.run_id ?? "none_selected"}</span>
        <span>affected nodes: {affectedNodes.length || view.visibleNodes.length}</span>
      </div>
    </div>
  );
}
