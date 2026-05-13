import type { GraphExplorerData } from "@supply-risk/shared-types";
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
        <span>graph_version: {metadata.graphVersion}</span>
        <span>source_manifest_id: {metadata.sourceManifestId}</span>
      </div>
      <ul className="evidence-list compact">
        {sourceRows.slice(0, 6).map((row) => (
          <li key={row.source ?? row.kind ?? "source"}>
            {row.source ?? row.kind ?? "source"}: {row.count}
          </li>
        ))}
        {sourceRows.length === 0 ? <li>Source coverage is provided by the fixture/proxy dashboard graph.</li> : null}
      </ul>
    </div>
  );
}
