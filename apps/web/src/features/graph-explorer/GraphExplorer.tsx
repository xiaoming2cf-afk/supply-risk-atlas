import { useEffect, useMemo, useState } from "react";
import type { SupplyRiskDashboardData } from "@supply-risk/api-client";
import type { GraphNodeKind } from "@supply-risk/shared-types";
import { Panel } from "../../app/components";
import { useI18n } from "../../app/i18n";
import { GraphBreadcrumbs } from "./GraphBreadcrumbs";
import { GraphCanvas } from "./GraphCanvas";
import { GraphControls } from "./GraphControls";
import { GraphEmptyState } from "./GraphEmptyState";
import { GraphInspector } from "./GraphInspector";
import { GraphLayers } from "./GraphLayers";
import { GraphLegend } from "./GraphLegend";
import { defaultGraphLayerSet, findFirstGraphSearchMatch, type GraphLayerCategory } from "./graphFilters";
import {
  buildGraphViewModel,
  criticalGraphNodes,
  graphModeLabel,
  graphViewModeUsesPath,
  normalizeGraphViewMode,
  type GraphFocusDirection,
  type GraphVersionMetadata,
  type GraphViewMode,
  type LegacyGraphExplorerMode,
} from "./graphViewModel";

export function GraphExplorer({
  data,
  initialMode = "overview",
}: {
  data: SupplyRiskDashboardData;
  initialMode?: LegacyGraphExplorerMode;
}) {
  const { t } = useI18n();
  const graph = data.graphExplorer;
  const [mode, setMode] = useState<GraphViewMode>(() => normalizeGraphViewMode(initialMode));
  const [nodeKind, setNodeKind] = useState<GraphNodeKind | "all">("all");
  const [query, setQuery] = useState("");
  const [selectedNodeId, setSelectedNodeId] = useState(graph.selectedNodeId);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [selectedPathId, setSelectedPathId] = useState(graph.transmissionPaths?.[0]?.id ?? data.pathExplainer.selectedPathId);
  const [selectedPathStepIndex, setSelectedPathStepIndex] = useState(0);
  const [selectedCountryCode, setSelectedCountryCode] = useState(
    graph.countryLens?.selectedCountryCode ?? graph.availableCountries?.[0]?.code ?? "US",
  );
  const [enabledLayers, setEnabledLayers] = useState<Set<GraphLayerCategory>>(() => new Set(defaultGraphLayerSet));
  const [hideLowConfidence, setHideLowConfidence] = useState(false);
  const [showEdgeLabels, setShowEdgeLabels] = useState(false);
  const [focusDepth, setFocusDepth] = useState(1);
  const [focusDirection, setFocusDirection] = useState<GraphFocusDirection>("both");
  const [pinnedNodeIds, setPinnedNodeIds] = useState<Set<string>>(() => new Set());
  const metadata = useMemo(() => graphMetadata(data), [data]);
  const countries = graph.availableCountries ?? graph.countryLens?.countries ?? [];
  const criticalNodes = useMemo(() => criticalGraphNodes(graph), [graph]);

  useEffect(() => {
    const nextMode = normalizeGraphViewMode(initialMode);
    setMode(nextMode);
    setSelectedEdgeId(null);
  }, [initialMode]);

  useEffect(() => {
    const match = findFirstGraphSearchMatch(graph.nodes, query, nodeKind);
    if (!query.trim() || !match) return;
    if (selectedNodeId !== match.id) setSelectedNodeId(match.id);
    setMode((current) => (current === "overview" || current === "geo" || current === "scenario" ? "focus" : current));
    setFocusDepth(1);
    setFocusDirection("both");
  }, [graph.nodes, nodeKind, query, selectedNodeId]);

  useEffect(() => {
    setSelectedPathStepIndex(0);
  }, [selectedPathId]);

  const view = useMemo(
    () =>
      buildGraphViewModel({
        graph,
        mode,
        selectedNodeId,
        selectedEdgeId,
        selectedPathId,
        selectedPathStepIndex,
        selectedCountryCode,
        searchQuery: query,
        nodeKind,
        enabledLayers,
        hideLowConfidence,
        pinnedNodeIds,
        focusDepth,
        focusDirection,
      }),
    [
      enabledLayers,
      focusDepth,
      focusDirection,
      graph,
      hideLowConfidence,
      mode,
      nodeKind,
      pinnedNodeIds,
      query,
      selectedCountryCode,
      selectedEdgeId,
      selectedNodeId,
      selectedPathId,
      selectedPathStepIndex,
    ],
  );
  const selectedPathStepEdgeId =
    view.selectedPathStep?.edgeId ??
    (view.activePath && selectedPathStepIndex > 0 ? view.activePath.edgeSequence[selectedPathStepIndex - 1] : undefined);

  const toggleLayer = (layer: GraphLayerCategory) => {
    setEnabledLayers((current) => {
      const next = new Set(current);
      if (next.has(layer)) next.delete(layer);
      else next.add(layer);
      return next;
    });
  };

  const pinSelectedNode = () => {
    const nodeId = view.selectedNode?.id;
    if (!nodeId) return;
    setPinnedNodeIds((current) => {
      const next = new Set(current);
      if (next.has(nodeId)) next.delete(nodeId);
      else next.add(nodeId);
      return next;
    });
  };

  const changeMode = (nextMode: GraphViewMode) => {
    setMode(nextMode);
    setSelectedEdgeId(null);
    if (nextMode === "focus") {
      setFocusDepth(1);
      setFocusDirection("both");
    }
  };

  return (
    <div className="graph-workbench graph-workbench-v2">
      <Panel title="Graph scope" subtitle="Graph Explorer v2 layered views." className="graph-side-panel">
        <div className="graph-version-strip">
          <strong>Graph Explorer v2</strong>
          <span>{graphModeLabel(mode)}</span>
        </div>
        <GraphControls
          countries={countries}
          criticalNodes={criticalNodes}
          filters={graph.filters}
          focusDepth={focusDepth}
          focusDirection={focusDirection}
          mode={mode}
          nodeKind={nodeKind}
          onCountrySelect={(countryCode) => {
            setSelectedCountryCode(countryCode);
            setSelectedEdgeId(null);
            setMode("geo");
          }}
          onCriticalNodeSelect={(nodeId) => {
            setSelectedNodeId(nodeId);
            setSelectedEdgeId(null);
            setMode("focus");
            setFocusDepth(1);
            setFocusDirection("both");
          }}
          onFocusChange={(direction, depth) => {
            setFocusDirection(direction);
            setFocusDepth(depth);
            setMode("focus");
          }}
          onModeChange={changeMode}
          onNodeKindChange={setNodeKind}
          onPathSelect={(pathId) => {
            setSelectedPathId(pathId);
            setSelectedEdgeId(null);
            setMode("path");
          }}
          onPinSelected={pinSelectedNode}
          onSearchChange={setQuery}
          paths={graph.transmissionPaths ?? []}
          query={query}
          renderCounts={{
            edgeLimit: view.renderLimits.edgeLimit,
            nodeLimit: view.renderLimits.nodeLimit,
            totalEligibleEdges: view.totalEligibleEdges,
            totalEligibleNodes: view.totalEligibleNodes,
            visibleLinks: view.visibleLinks.length,
            visibleNodes: view.visibleNodes.length,
          }}
          selectedCountryCode={view.selectedCountry?.code}
          selectedNodeId={view.selectedNode?.id}
          selectedPathId={view.activePath?.id}
        />
        <GraphLayers
          enabledLayers={enabledLayers}
          hideLowConfidence={hideLowConfidence}
          onLayerToggle={toggleLayer}
          onToggleHideLowConfidence={() => setHideLowConfidence((current) => !current)}
          onToggleShowEdgeLabels={() => setShowEdgeLabels((current) => !current)}
          showEdgeLabels={showEdgeLabels}
        />
        <GraphLegend metadata={metadata} />
      </Panel>

      <Panel
        title="Entity network"
        subtitle={`${graphModeLabel(mode)} view; ${view.visibleNodes.length} nodes and ${view.visibleLinks.length} edges rendered.`}
        className="graph-main-panel"
        translateSubtitle={false}
      >
        <GraphBreadcrumbs mode={mode} selectedEdge={view.selectedEdge} selectedNode={view.selectedNode} />
        <div className="graph-view-summary">
          <span>initial cap: 20 nodes / 35 edges</span>
          <span>focus cap: 25 nodes / 40 edges</span>
          <span>edge labels hidden by default</span>
        </div>
        <div className="graph-canvas">
          {view.visibleNodes.length > 0 ? (
            <GraphCanvas
              activePathEdgeIds={view.activePathEdgeIds}
              activePathNodeIds={view.activePathNodeIds}
              activePathNodeIndex={view.activePathNodeIndex}
              links={view.visibleLinks}
              matchedNodeIds={view.matchedNodeIds}
              mode={mode}
              nodes={view.visibleNodes}
              onSelectEdge={(edgeId) => {
                setSelectedEdgeId(edgeId);
              }}
              onSelectNode={(nodeId) => {
                setSelectedNodeId(nodeId);
                setSelectedEdgeId(null);
                if (mode === "overview") setMode("focus");
              }}
              pinnedNodeIds={pinnedNodeIds}
              selectedEdgeId={selectedEdgeId}
              selectedNodeId={view.selectedNode?.id}
              selectedPathStepEdgeId={selectedPathStepEdgeId}
              selectedPathStepNodeId={view.selectedPathStep?.nodeId}
              showEdgeLabels={showEdgeLabels}
            />
          ) : (
            <GraphEmptyState message={view.emptyReason ?? "No entities match the active graph filters."} />
          )}
        </div>
      </Panel>

      <Panel title="Inspector" subtitle="Evidence, selection, and fixture limits." className="graph-inspector-panel">
        {view.emptyReason && mode === "scenario" ? <p className="inspector-note">{t(view.emptyReason)}</p> : null}
        <GraphInspector
          activePath={graphViewModeUsesPath(mode) ? view.activePath : undefined}
          countryLens={graph.countryLens}
          edge={view.selectedEdge}
          node={view.selectedEdge ? undefined : view.selectedNode}
          onSelectPathStep={(index, nodeId) => {
            setSelectedPathStepIndex(index);
            setSelectedNodeId(nodeId);
            setSelectedEdgeId(null);
          }}
          selectedCountry={mode === "geo" ? view.selectedCountry : undefined}
          selectedPath={graphViewModeUsesPath(mode)}
          selectedPathStepIndex={selectedPathStepIndex}
        />
      </Panel>
    </div>
  );
}

function graphMetadata(data: SupplyRiskDashboardData): GraphVersionMetadata {
  const health = data.systemHealthCenter?.semiconductorGraph;
  return {
    graphVersion: health?.graphVersion ?? "fixture_graph:v0.1",
    sourceManifestId: health?.sourceManifestId ?? "fixture_manifest:semirisk:v0.1",
    asOfTime: health?.asOfTime ?? "fixture_as_of_time:unavailable",
    fixtureGraph: health?.fixtureGraph ?? true,
    warnings: Array.from(new Set([...(health?.warnings ?? []), "fixture_graph:not_production_ready"])),
  };
}
