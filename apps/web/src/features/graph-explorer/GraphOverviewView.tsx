import type { GraphExplorerData } from "@supply-risk/shared-types";
import { AuditDetails, MetadataSummary } from "../common/AuditDetails";
import type { GraphVersionMetadata, GraphViewModel } from "./graphViewModel";

export function GraphOverviewView({
  graph,
  metadata,
  view,
}: {
  graph: GraphExplorerData;
  metadata: GraphVersionMetadata;
  view: GraphViewModel;
}) {
  const sourceRows = graph.graphStats?.bySource ?? [];
  return (
    <div className="graph-v3-panel graph-v3-overview-panel">
      <div className="section-kicker">Overview mode source coverage summary</div>
      <div className="inspector-grid">
        <span>Visible nodes: {view.visibleNodes.length} / 20</span>
        <span>Visible links: {view.visibleLinks.length} / 35</span>
      </div>
      <MetadataSummary items={[{ label: "Public evidence mode" }]} />
      <AuditDetails
        items={[
          { label: "graph_version", value: metadata.graphVersion },
          { label: "source_manifest_id", value: metadata.sourceManifestId },
        ]}
      />
      <ul className="evidence-list compact">
        {sourceRows.slice(0, 6).map((row) => (
          <li key={row.source ?? row.kind ?? "source"}>
            {row.source ?? row.kind ?? "source"}: {row.count}
          </li>
        ))}
        {sourceRows.length === 0 ? <li>Source coverage will appear when public evidence graph records are available for this view.</li> : null}
      </ul>
    </div>
  );
}
