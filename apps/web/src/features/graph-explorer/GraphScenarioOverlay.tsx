import type { GraphScenarioOverlayData } from "@supply-risk/shared-types";
import { AuditDetails, MetadataSummary } from "../common/AuditDetails";
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
        <span>Selected run: {overlay?.run_id ? "available" : "none selected"}</span>
        <span>Affected entities: {affectedNodes.length || view.visibleNodes.length}</span>
      </div>
      <MetadataSummary items={[{ label: "Research fixture mode", tone: "warning" }]} />
      <AuditDetails
        items={[{ label: "run_id", value: overlay?.run_id }]}
        warnings={overlay?.warnings}
      />
    </div>
  );
}
