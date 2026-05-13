import type { GraphEvidenceData, GraphLink } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function GraphEvidenceView({
  endpointData,
  view,
}: {
  endpointData?: unknown;
  view: GraphViewModel;
}) {
  const evidenceRows = Array.isArray((endpointData as GraphEvidenceData | undefined)?.evidence_refs)
    ? ((endpointData as GraphEvidenceData).evidence_refs ?? [])
    : evidenceRowsFromLinks(view.visibleLinks);
  return (
    <div className="graph-v3-panel graph-v3-evidence-panel">
      <div className="section-kicker">Evidence mode</div>
      <p className="inspector-warning">This is not a supply-chain dependency edge.</p>
      <p className="inspector-note">Evidence-context link rows are separated from real graph edges and scenario traces.</p>
      <table className="graph-evidence-table">
        <thead>
          <tr>
            <th>Evidence ref</th>
            <th>Edge semantics</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {evidenceRows.slice(0, 12).map((row, index) => (
            <tr key={String((row as Record<string, unknown>).edge_id ?? (row as Record<string, unknown>).id ?? index)}>
              <td>{String((row as Record<string, unknown>).source_id ?? (row as Record<string, unknown>).edge_id ?? "evidence_ref")}</td>
              <td>
                {String((row as Record<string, unknown>).edge_type ?? "evidence-context link")}
                {Boolean((row as Record<string, unknown>).not_supply_chain_dependency) ? " / not supply-chain dependency" : ""}
              </td>
              <td>{Number((row as Record<string, unknown>).confidence ?? 0).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function evidenceRowsFromLinks(links: GraphLink[]) {
  return links.map((link) => ({
    edge_id: link.id,
    edge_type: link.edgeType ?? link.edgeRole ?? "graph_edge",
    source_id: link.sourceId ?? String(link.metadata?.source ?? "source_ref"),
    confidence: link.confidence ?? 0,
    not_supply_chain_dependency: link.metadata?.not_supply_chain_dependency === true,
  }));
}
