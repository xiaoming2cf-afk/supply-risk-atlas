import type { GraphExplorerData, GraphGeoData } from "@supply-risk/shared-types";
import { formatDisplayValue, formatNodeDisplayRef } from "../common/displayLabels";
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
        <span>Shown geographies: {view.visibleNodes.length}</span>
        <span>Shown relationships: {view.visibleLinks.length}</span>
      </div>
      <ul className="evidence-list compact">
        {countries.slice(0, 6).map((country, index) => (
          <li key={String((country as Record<string, unknown>).code ?? (country as Record<string, unknown>).id ?? index)}>
            {formatGeoLabel(country as Record<string, unknown>)}
          </li>
        ))}
      </ul>
    </div>
  );
}

function formatGeoLabel(country: Record<string, unknown>) {
  const raw = country.label ?? country.countryName ?? country.id ?? country.code ?? "geography";
  const value = String(raw);
  return formatNodeDisplayRef(value) || String(formatDisplayValue(value));
}
