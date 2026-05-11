import {
  Clock3,
  Map as MapIcon,
  Pin,
  Route,
  Share2,
  Workflow,
  type LucideIcon,
} from "lucide-react";
import type { CountryRiskSummary, GraphNode, GraphNodeKind, GraphTransmissionPath } from "@supply-risk/shared-types";
import { Field } from "../../app/components";
import { useI18n } from "../../app/i18n";
import { graphScore } from "./graphLayout";
import { graphModeLabel, type GraphFocusDirection, type GraphViewMode } from "./graphViewModel";

const graphModeOptions: Array<{ id: GraphViewMode; label: string; icon: LucideIcon }> = [
  { id: "overview", label: "Overview", icon: Workflow },
  { id: "focus", label: "Focus", icon: Share2 },
  { id: "path", label: "Path", icon: Route },
  { id: "timeline", label: "Timeline", icon: Clock3 },
  { id: "geo", label: "Geo", icon: MapIcon },
  { id: "scenario", label: "Scenario overlay", icon: Workflow },
];

export function GraphControls({
  countries,
  criticalNodes,
  filters,
  focusDepth,
  focusDirection,
  mode,
  nodeKind,
  onCountrySelect,
  onCriticalNodeSelect,
  onFocusChange,
  onModeChange,
  onNodeKindChange,
  onPathSelect,
  onPinSelected,
  onSearchChange,
  paths,
  query,
  renderCounts,
  selectedCountryCode,
  selectedNodeId,
  selectedPathId,
}: {
  countries: CountryRiskSummary[];
  criticalNodes: GraphNode[];
  filters: GraphNodeKind[];
  focusDepth: number;
  focusDirection: GraphFocusDirection;
  mode: GraphViewMode;
  nodeKind: GraphNodeKind | "all";
  onCountrySelect: (countryCode: string) => void;
  onCriticalNodeSelect: (nodeId: string) => void;
  onFocusChange: (direction: GraphFocusDirection, depth: number) => void;
  onModeChange: (mode: GraphViewMode) => void;
  onNodeKindChange: (kind: GraphNodeKind | "all") => void;
  onPathSelect: (pathId: string) => void;
  onPinSelected: () => void;
  onSearchChange: (query: string) => void;
  paths: GraphTransmissionPath[];
  query: string;
  renderCounts: {
    edgeLimit: number;
    nodeLimit: number;
    totalEligibleEdges: number;
    totalEligibleNodes: number;
    visibleLinks: number;
    visibleNodes: number;
  };
  selectedCountryCode?: string;
  selectedNodeId?: string;
  selectedPathId?: string;
}) {
  const { t } = useI18n();
  return (
    <>
      <div className="graph-mode-toolbar" aria-label={t("Graph analysis mode")}>
        {graphModeOptions.map((option) => {
          const Icon = option.icon;
          return (
            <button
              className={`mode-tab ${mode === option.id ? "is-active" : ""}`}
              key={option.id}
              onClick={() => onModeChange(option.id)}
              type="button"
            >
              <Icon aria-hidden="true" />
              <span>
                <strong>{t(option.label)}</strong>
                <small>{t(graphModeLabel(option.id))}</small>
              </span>
            </button>
          );
        })}
      </div>

      <div className="segmented" aria-label={t("Graph node type")}>
        {(["all", ...filters] as Array<GraphNodeKind | "all">).map((filter) => (
          <button
            className={`segment ${nodeKind === filter ? "is-active" : ""}`}
            key={filter}
            onClick={() => onNodeKindChange(filter)}
            type="button"
          >
            {t(filter)}
          </button>
        ))}
      </div>

      <label className="form-control graph-search-control">
        <span>{t("Entity search")}</span>
        <input
          aria-label={t("Entity search")}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder={t("Search name, source, country, or external id")}
          type="search"
          value={query}
        />
      </label>

      <div className="graph-toggle-row">
        <button className="control-button" onClick={onPinSelected} type="button">
          <Pin aria-hidden="true" /> Pin
        </button>
        <button className={`control-button ${focusDirection === "incoming" ? "primary" : ""}`} onClick={() => onFocusChange("incoming", 2)} type="button">
          Upstream
        </button>
        <button className={`control-button ${focusDirection === "outgoing" ? "primary" : ""}`} onClick={() => onFocusChange("outgoing", 2)} type="button">
          Downstream
        </button>
        <button className={`control-button ${focusDirection === "both" && focusDepth > 1 ? "primary" : ""}`} onClick={() => onFocusChange("both", 2)} type="button">
          Two-hop
        </button>
      </div>

      <div className="inspector-grid graph-stat-grid">
        <Field label="Visible nodes" value={`${renderCounts.visibleNodes}/${renderCounts.nodeLimit}`} />
        <Field label="Visible links" value={`${renderCounts.visibleLinks}/${renderCounts.edgeLimit}`} />
        <Field label="Eligible nodes" value={renderCounts.totalEligibleNodes} />
        <Field label="Eligible links" value={renderCounts.totalEligibleEdges} />
      </div>

      <div className="graph-list-section">
        <div className="section-kicker">Critical nodes</div>
        <ul className="critical-node-list">
          {criticalNodes.slice(0, 10).map((node) => (
            <li key={node.id}>
              <button
                className={`graph-list-button ${node.id === selectedNodeId ? "is-active" : ""}`}
                onClick={() => onCriticalNodeSelect(node.id)}
                type="button"
              >
                <span>
                  <strong>{node.criticalityRank ? `#${node.criticalityRank} ` : ""}{node.label}</strong>
                  <small>{node.kind} / {node.countryCode ?? "global"}</small>
                </span>
                <b>{graphScore(node.criticalityScore ?? node.score)}</b>
              </button>
            </li>
          ))}
        </ul>
      </div>

      {mode === "path" || mode === "timeline" ? (
        <div className="graph-list-section">
          <div className="section-kicker">Transmission paths</div>
          <ul className="path-list">
            {paths.slice(0, 8).map((path) => (
              <li key={path.id}>
                <button
                  className={`graph-list-button path ${path.id === selectedPathId ? "is-active" : ""}`}
                  onClick={() => onPathSelect(path.id)}
                  type="button"
                >
                  <span>
                    <strong>{path.sourceLabel} -&gt; {path.targetLabel}</strong>
                    <small>{path.edgeSequence.length} hops / {path.countrySequence.join(" -> ")}</small>
                  </span>
                  <b>{Math.round(path.transmissionScore * 100)}</b>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {mode === "geo" ? (
        <div className="graph-list-section">
          <div className="section-kicker">Available countries</div>
          <ul className="country-list">
            {countries.slice(0, 12).map((country) => (
              <li key={country.code}>
                <button
                  className={`graph-list-button country ${country.code === selectedCountryCode ? "is-active" : ""}`}
                  onClick={() => onCountrySelect(country.code)}
                  type="button"
                >
                  <span>
                    <strong>{country.label}</strong>
                    <small>{country.entityCount} nodes / {country.edgeCount} edges</small>
                  </span>
                  <b>{graphScore(country.riskScore)}</b>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </>
  );
}
