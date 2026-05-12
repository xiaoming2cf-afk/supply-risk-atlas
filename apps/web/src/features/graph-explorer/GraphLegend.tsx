import { AlertTriangle } from "lucide-react";
import { Field, StatusPill } from "../../app/components";
import { graphColorByLevel } from "./graphLayout";
import type { GraphVersionMetadata } from "./graphViewModel";

const legendLevels = [
  ["critical", "Critical"],
  ["severe", "Severe"],
  ["elevated", "Elevated"],
  ["guarded", "Guarded"],
  ["low", "Low"],
] as const;

export function GraphLegend({ metadata }: { metadata: GraphVersionMetadata }) {
  return (
    <div className="graph-list-section graph-legend-panel">
      <div className="section-kicker">Legend</div>
      <div className="graph-warning-banner" role="note">
        <AlertTriangle aria-hidden="true" />
        <span>fixture_graph:not_production_ready</span>
      </div>
      <div className="graph-legend-grid">
        {legendLevels.map(([level, label]) => (
          <span className="graph-legend-item" key={level}>
            <i style={{ background: graphColorByLevel[level] }} />
            {label}
          </span>
        ))}
        <span className="graph-legend-item graph-legend-link-kind">
          <i className="evidence-context-swatch" />
          evidence-context link
        </span>
      </div>
      <p className="inspector-warning">This is not a supply-chain dependency edge.</p>
      <div className="inspector-grid">
        <Field label="graph_version" value={metadata.graphVersion} />
        <Field label="source_manifest_id" value={metadata.sourceManifestId} />
        <Field label="as_of_time" value={metadata.asOfTime} />
        <Field label="fixture_graph" value={metadata.fixtureGraph ? "true" : "unknown"} />
      </div>
      <ul className="evidence-list compact">
        {metadata.warnings.length ? (
          metadata.warnings.map((warning) => (
            <li key={warning}>
              <StatusPill status="degraded" /> {warning}
            </li>
          ))
        ) : (
          <li>
            <StatusPill status="degraded" /> fixture_graph:not_production_ready
          </li>
        )}
      </ul>
    </div>
  );
}
