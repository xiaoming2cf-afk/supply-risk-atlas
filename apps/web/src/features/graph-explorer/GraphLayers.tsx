import { EyeOff, Tags } from "lucide-react";
import { graphLayerCategories, type GraphLayerCategory } from "./graphFilters";

const layerLabels: Record<GraphLayerCategory, string> = {
  dependency: "Dependency",
  supply: "Supply",
  policy: "Policy",
  event: "Event",
  substitution: "Substitution",
  trade: "Trade",
  route: "Route",
  hazard: "Hazard",
  sanctions: "Sanctions",
  simulation_trace: "Simulation trace",
};

export function GraphLayers({
  enabledLayers,
  hideLowConfidence,
  onLayerToggle,
  onToggleHideLowConfidence,
  onToggleShowEdgeLabels,
  showEdgeLabels,
}: {
  enabledLayers: Set<GraphLayerCategory>;
  hideLowConfidence: boolean;
  onLayerToggle: (layer: GraphLayerCategory) => void;
  onToggleHideLowConfidence: () => void;
  onToggleShowEdgeLabels: () => void;
  showEdgeLabels: boolean;
}) {
  return (
    <div className="graph-list-section">
      <div className="section-kicker">Relationship filters</div>
      <div className="graph-layer-grid" role="group" aria-label="Relationship filters">
        {graphLayerCategories.map((layer) => (
          <label className="graph-layer-toggle" key={layer}>
            <input checked={enabledLayers.has(layer)} onChange={() => onLayerToggle(layer)} type="checkbox" />
            <span>{layerLabels[layer]}</span>
          </label>
        ))}
      </div>
      <div className="graph-toggle-row">
        <button className={`control-button ${hideLowConfidence ? "primary" : ""}`} onClick={onToggleHideLowConfidence} type="button">
          <EyeOff aria-hidden="true" /> Low confidence
        </button>
        <button className={`control-button ${showEdgeLabels ? "primary" : ""}`} onClick={onToggleShowEdgeLabels} type="button">
          <Tags aria-hidden="true" /> Relationship labels
        </button>
      </div>
    </div>
  );
}
