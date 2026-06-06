import type { GraphExplorerData, GraphTimelineData } from "@supply-risk/shared-types";
import { formatDisplayValue } from "../common/displayLabels";
import type { GraphViewModel } from "./graphViewModel";

export function GraphTimelineView({
  endpointData,
  graph,
  view,
}: {
  endpointData?: unknown;
  graph: GraphExplorerData;
  view: GraphViewModel;
}) {
  const endpointEvents = Array.isArray((endpointData as GraphTimelineData | undefined)?.events)
    ? ((endpointData as GraphTimelineData).events ?? [])
    : [];
  const pathSteps = view.activePath?.steps ?? graph.transmissionPaths?.[0]?.steps ?? [];
  return (
    <div className="graph-v3-panel graph-v3-timeline-panel">
      <div className="section-kicker">Timeline mode</div>
      <p className="inspector-note">Event timeline shows event nodes and affected graph nodes over hop order; it does not render the full graph.</p>
      <ul className="timeline-list compact">
        {endpointEvents.slice(0, 6).map((event, index) => (
          <li key={String(event.id ?? index)}>{formatTimelineEventLabel(event, index)} / hop {String(event.hop_order ?? index)}</li>
        ))}
        {endpointEvents.length === 0
          ? pathSteps.slice(0, 6).map((step, index) => (
              <li key={step.id}>{step.label} / hop {index} / {step.evidence}</li>
            ))
          : null}
      </ul>
    </div>
  );
}

function formatTimelineEventLabel(event: Record<string, unknown>, index: number) {
  const value = event.label ?? event.event_type ?? `event ${index + 1}`;
  return String(formatDisplayValue(String(value)));
}
