import { AlertTriangle } from "lucide-react";
import { StatusPill } from "../../app/components";
import { AuditDetails, formatPublicWarning, MetadataSummary } from "../common/AuditDetails";
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
        <span>Research fixture mode</span>
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
          Evidence context
        </span>
      </div>
      <p className="inspector-warning">Evidence context is inspection support, not supply-chain dependency.</p>
      <MetadataSummary items={[{ label: "Public evidence mode" }]} />
      <AuditDetails
        items={[
          { label: "graph_version", value: metadata.graphVersion },
          { label: "source_manifest_id", value: metadata.sourceManifestId },
          { label: "as_of_time", value: metadata.asOfTime },
          { label: "fixture_graph", value: metadata.fixtureGraph ? "true" : "unknown" },
        ]}
        warnings={metadata.warnings}
      />
      <ul className="evidence-list compact">
        {visibleWarningLabels(metadata.warnings).map((label) => (
          <li key={label}>
            <StatusPill status="degraded" /> {label}
          </li>
        ))}
      </ul>
    </div>
  );
}

function visibleWarningLabels(warnings: string[]) {
  const labels = warnings.map(formatPublicWarning);
  if (labels.length === 0) labels.push("Research fixture mode");
  return Array.from(new Set(labels));
}
