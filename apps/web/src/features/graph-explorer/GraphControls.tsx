import {
  Clock3,
  Download,
  FileSearch,
  Filter,
  Grid3X3,
  Map as MapIcon,
  Pin,
  RotateCcw,
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
  { id: "matrix", label: "Matrix", icon: Grid3X3 },
  { id: "scenario", label: "Scenario overlay", icon: Workflow },
  { id: "evidence", label: "Evidence", icon: FileSearch },
];

export function GraphControls({
  confidenceMin,
  countries,
  countryFilter,
  criticalNodes,
  evidenceOnly,
  filters,
  focusDepth,
  focusDirection,
  mode,
  nodeKind,
  onConfidenceMinChange,
  onCountryFilterChange,
  onCountrySelect,
  onCriticalNodeSelect,
  onEvidenceOnlyChange,
  onExportView,
  onFocusChange,
  onModeChange,
  onNodeKindChange,
  onPathSelect,
  onPinSelected,
  onProductFilterChange,
  onResetView,
  onSearchChange,
  onSourceFilterChange,
  paths,
  productFilter,
  productOptions,
  query,
  renderCounts,
  selectedCountryCode,
  selectedNodeId,
  selectedPathId,
  sourceFilter,
  sourceOptions,
}: {
  confidenceMin: number;
  countries: CountryRiskSummary[];
  countryFilter: string;
  criticalNodes: GraphNode[];
  evidenceOnly: boolean;
  filters: GraphNodeKind[];
  focusDepth: number;
  focusDirection: GraphFocusDirection;
  mode: GraphViewMode;
  nodeKind: GraphNodeKind | "all";
  onConfidenceMinChange: (value: number) => void;
  onCountryFilterChange: (countryCode: string) => void;
  onCountrySelect: (countryCode: string) => void;
  onCriticalNodeSelect: (nodeId: string) => void;
  onEvidenceOnlyChange: (enabled: boolean) => void;
  onExportView: () => void;
  onFocusChange: (direction: GraphFocusDirection, depth: number) => void;
  onModeChange: (mode: GraphViewMode) => void;
  onNodeKindChange: (kind: GraphNodeKind | "all") => void;
  onPathSelect: (pathId: string) => void;
  onPinSelected: () => void;
  onProductFilterChange: (value: string) => void;
  onResetView: () => void;
  onSearchChange: (query: string) => void;
  onSourceFilterChange: (value: string) => void;
  paths: GraphTransmissionPath[];
  productFilter: string;
  productOptions: string[];
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
  sourceFilter: string;
  sourceOptions: string[];
}) {
  const { t } = useI18n();
  return (
    <>
      <div className="section-kicker">View mode selector</div>
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

      <div className="graph-list-section graph-v3-filter-panel">
        <div className="section-kicker">
          <Filter aria-hidden="true" /> Evidence-bound filters
        </div>
        <label className="form-control compact">
          <span>{t("Source filter")}</span>
          <select value={sourceFilter} onChange={(event) => onSourceFilterChange(event.target.value)}>
            <option value="all">{t("All sources")}</option>
            {sourceOptions.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
        <label className="form-control compact">
          <span>{t("Country filter")}</span>
          <select value={countryFilter} onChange={(event) => onCountryFilterChange(event.target.value)}>
            <option value="all">{t("All countries")}</option>
            {countries.map((country) => (
              <option key={country.code} value={country.code}>
                {country.label}
              </option>
            ))}
          </select>
        </label>
        <label className="form-control compact">
          <span>{t("Product grade filter")}</span>
          <select value={productFilter} onChange={(event) => onProductFilterChange(event.target.value)}>
            <option value="all">{t("All product grades")}</option>
            {productOptions.map((product) => (
              <option key={product} value={product}>
                {product}
              </option>
            ))}
          </select>
        </label>
        <label className="form-control compact">
          <span>{t("Confidence threshold")} {Math.round(confidenceMin * 100)}%</span>
          <input
            aria-label={t("Confidence threshold")}
            max={0.95}
            min={0}
            onChange={(event) => onConfidenceMinChange(Number(event.target.value))}
            step={0.05}
            type="range"
            value={confidenceMin}
          />
        </label>
        <label className="graph-layer-toggle evidence-only-toggle">
          <input checked={evidenceOnly} onChange={(event) => onEvidenceOnlyChange(event.target.checked)} type="checkbox" />
          <span>{t("Evidence only")}</span>
        </label>
        <div className="graph-toggle-row">
          <button className="control-button" onClick={onResetView} type="button">
            <RotateCcw aria-hidden="true" /> Reset view
          </button>
          <button className="control-button" onClick={onExportView} type="button">
            <Download aria-hidden="true" /> Export view summary JSON
          </button>
        </div>
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
