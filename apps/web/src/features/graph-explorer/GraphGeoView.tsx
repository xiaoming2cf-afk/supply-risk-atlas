import type { GraphExplorerData, GraphGeoData } from "@supply-risk/shared-types";
import type { GraphViewModel } from "./graphViewModel";

export function GraphGeoView({
  endpointData,
  graph,
  view,
}: {
  endpointData?: unknown;
  graph: GraphExplorerData;
  view: GraphViewModel;
}) {
  const countries = Array.isArray((endpointData as GraphGeoData | undefined)?.countries)
    ? ((endpointData as GraphGeoData).countries ?? [])
    : graph.availableCountries ?? graph.countryLens?.countries ?? [];
  return (
    <div className="graph-v3-panel graph-v3-geo-panel">
      <div className="section-kicker">Geo mode</div>
      <p className="inspector-note">Geo aggregates countries, regions, trade/dependency links, logistics context, and hazard exposure overlays.</p>
      <div className="inspector-grid">
        <span>Rendered geo nodes: {view.visibleNodes.length}</span>
        <span>Rendered geo links: {view.visibleLinks.length}</span>
      </div>
      <ul className="evidence-list compact">
        {countries.slice(0, 6).map((country, index) => (
          <li key={String((country as Record<string, unknown>).code ?? (country as Record<string, unknown>).id ?? index)}>
            {String((country as Record<string, unknown>).label ?? (country as Record<string, unknown>).countryName ?? (country as Record<string, unknown>).code ?? "country")}
          </li>
        ))}
      </ul>
    </div>
  );
}
