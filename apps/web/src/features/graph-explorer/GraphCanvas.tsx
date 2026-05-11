import { useMemo, useState, type CSSProperties } from "react";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  type Edge as FlowEdge,
  type Node as FlowNode,
  type NodeProps,
} from "@xyflow/react";
import type { GraphLink, GraphNode, RiskLevel } from "@supply-risk/shared-types";
import { formatPercent, riskClassByLevel } from "@supply-risk/design-system";
import { graphColorByLevel, computeRankedTopologyLayout, countGraphPositionOverlaps, graphScore } from "./graphLayout";
import type { GraphViewMode } from "./graphViewModel";

type RiskFlowNodeData = {
  activePath: boolean;
  dimmed: boolean;
  firstNeighbor: boolean;
  graphNode: GraphNode;
  matched: boolean;
  pinned: boolean;
  selected: boolean;
  selectedPathStep: boolean;
};

type RiskFlowNode = FlowNode<RiskFlowNodeData, "risk">;
type RiskFlowEdge = FlowEdge<{ activePath: boolean; label: string; level: RiskLevel }>;

const graphNodeTypes = { risk: RiskFlowNodeCard };

type GraphHoverTooltip = {
  x: number;
  y: number;
  title: string;
  meta: string;
  detail: string;
};

export function GraphCanvas({
  activePathEdgeIds,
  activePathNodeIds,
  activePathNodeIndex,
  links,
  matchedNodeIds,
  mode,
  nodes,
  onSelectEdge,
  onSelectNode,
  pinnedNodeIds,
  selectedEdgeId,
  selectedNodeId,
  selectedPathStepEdgeId,
  selectedPathStepNodeId,
  showEdgeLabels,
}: {
  activePathEdgeIds: Set<string>;
  activePathNodeIds: Set<string>;
  activePathNodeIndex: Map<string, number>;
  links: GraphLink[];
  matchedNodeIds: Set<string>;
  mode: GraphViewMode;
  nodes: GraphNode[];
  onSelectEdge: (edgeId: string) => void;
  onSelectNode: (nodeId: string) => void;
  pinnedNodeIds: Set<string>;
  selectedEdgeId: string | null;
  selectedNodeId?: string;
  selectedPathStepEdgeId?: string;
  selectedPathStepNodeId?: string;
  showEdgeLabels: boolean;
}) {
  const [tooltip, setTooltip] = useState<GraphHoverTooltip | null>(null);
  const positions = useMemo(() => computeRankedTopologyLayout(nodes, links, activePathNodeIndex), [activePathNodeIndex, links, nodes]);
  const firstNeighborNodeIds = useMemo(() => {
    const neighborIds = new Set<string>();
    for (const link of links) {
      if (link.source === selectedNodeId) neighborIds.add(link.target);
      if (link.target === selectedNodeId) neighborIds.add(link.source);
      if (selectedEdgeId && link.id === selectedEdgeId) {
        neighborIds.add(link.source);
        neighborIds.add(link.target);
      }
      if (selectedPathStepNodeId && (link.source === selectedPathStepNodeId || link.target === selectedPathStepNodeId)) {
        neighborIds.add(link.source);
        neighborIds.add(link.target);
      }
    }
    return neighborIds;
  }, [links, selectedEdgeId, selectedNodeId, selectedPathStepNodeId]);

  const flowNodes = useMemo<RiskFlowNode[]>(
    () =>
      nodes.map((node) => {
        const isSelected = node.id === selectedNodeId;
        const inActivePath = activePathNodeIds.has(node.id);
        const firstNeighbor = firstNeighborNodeIds.has(node.id);
        const selectedPathStep = node.id === selectedPathStepNodeId;
        const matched = matchedNodeIds.has(node.id);
        const pinned = pinnedNodeIds.has(node.id);
        const focused = isSelected || firstNeighbor || selectedPathStep || matched || pinned || inActivePath;
        const dimmed = (mode === "path" || mode === "timeline") && activePathNodeIds.size > 0 && !focused;
        return {
          id: node.id,
          type: "risk",
          position: positions.get(node.id) ?? { x: 0, y: 0 },
          data: { graphNode: node, selected: isSelected, dimmed, activePath: inActivePath, firstNeighbor, matched, pinned, selectedPathStep },
          selected: isSelected,
        };
      }),
    [activePathNodeIds, firstNeighborNodeIds, matchedNodeIds, mode, nodes, pinnedNodeIds, positions, selectedNodeId, selectedPathStepNodeId],
  );

  const flowEdges = useMemo<RiskFlowEdge[]>(
    () =>
      links.map((link) => {
        const activePath = activePathEdgeIds.has(link.id);
        const selected = link.id === selectedEdgeId;
        const selectedPathStep = link.id === selectedPathStepEdgeId;
        const selectedAdjacency = link.source === selectedNodeId || link.target === selectedNodeId;
        const firstNeighbor = firstNeighborNodeIds.has(link.source) || firstNeighborNodeIds.has(link.target);
        const focused = activePath || selected || selectedPathStep || selectedAdjacency || firstNeighbor;
        const color = graphColorByLevel[link.level];
        const baseWidth = link.transmissionWeight ?? link.weight;
        return {
          id: link.id,
          source: link.source,
          sourceHandle: "source",
          target: link.target,
          targetHandle: "target",
          type: "smoothstep",
          interactionWidth: 18,
          animated: activePath || selectedPathStep,
          label: showEdgeLabels ? link.label : undefined,
          data: { activePath, label: link.label, level: link.level },
          markerEnd: { type: MarkerType.ArrowClosed, color },
          style: {
            stroke: color,
            strokeOpacity: focused || mode === "overview" || mode === "geo" ? (selected || selectedPathStep ? 0.98 : 0.72) : 0.2,
            strokeWidth: selected || selectedPathStep || activePath ? 4.8 : Math.max(1.1, Math.min(4.2, baseWidth * 4.6)),
          },
        };
      }),
    [activePathEdgeIds, firstNeighborNodeIds, links, mode, selectedEdgeId, selectedNodeId, selectedPathStepEdgeId, showEdgeLabels],
  );

  const flowLayoutKey = useMemo(
    () => [mode, nodes.map((node) => node.id).join("|"), links.map((link) => link.id).join("|")].join("::"),
    [links, mode, nodes],
  );

  return (
    <>
      <span
        aria-hidden="true"
        className="risk-flow-render-metrics"
        data-flow-edge-count={flowEdges.length}
        data-flow-node-count={flowNodes.length}
        data-input-link-count={links.length}
        data-layout-overlap-count={countGraphPositionOverlaps(nodes, positions)}
        data-position-count={positions.size}
      />
      <ReactFlow
        className="risk-flow"
        colorMode="light"
        defaultEdgeOptions={{ type: "smoothstep" }}
        edges={flowEdges}
        fitView
        fitViewOptions={{ padding: 0.14, maxZoom: 1.45 }}
        key={flowLayoutKey}
        maxZoom={2.2}
        minZoom={0.22}
        nodeTypes={graphNodeTypes}
        nodes={flowNodes}
        nodesDraggable={false}
        onEdgeClick={(_, edge) => onSelectEdge(edge.id)}
        onEdgeMouseEnter={(event, edge) => {
          const link = links.find((candidate) => candidate.id === edge.id);
          setTooltip({
            x: event.clientX,
            y: event.clientY,
            title: edge.label ? String(edge.label) : link?.label ?? edge.id,
            meta: `${link?.edgeRole ?? link?.edgeType ?? "edge"} / ${formatPercent(link?.transmissionWeight ?? link?.weight ?? 0)}`,
            detail: `${link?.sourceCountry ?? "global"} -> ${link?.targetCountry ?? "global"}`,
          });
        }}
        onEdgeMouseLeave={() => setTooltip(null)}
        onEdgeMouseMove={(event) => setTooltip((current) => (current ? { ...current, x: event.clientX, y: event.clientY } : current))}
        onNodeClick={(_, node) => onSelectNode(node.id)}
        onNodeMouseEnter={(event, node) => {
          const data = node.data as RiskFlowNodeData;
          setTooltip({
            x: event.clientX,
            y: event.clientY,
            title: data.graphNode.label,
            meta: `${data.graphNode.kind} / ${data.graphNode.countryCode ?? String(data.graphNode.metadata.country ?? "global")}`,
            detail: `risk ${graphScore(data.graphNode.riskScore ?? data.graphNode.score)} / centrality ${graphScore(data.graphNode.centralityScore ?? 0)}`,
          });
        }}
        onNodeMouseLeave={() => setTooltip(null)}
        onNodeMouseMove={(event) => setTooltip((current) => (current ? { ...current, x: event.clientX, y: event.clientY } : current))}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="rgba(22,28,22,0.08)" gap={32} size={1} />
        <MiniMap
          className="risk-flow-minimap"
          nodeColor={(node) => graphColorByLevel[(node.data as RiskFlowNodeData).graphNode.level]}
          pannable
          zoomable
        />
        <Controls className="risk-flow-controls" fitViewOptions={{ padding: 0.2 }} />
      </ReactFlow>
      {tooltip ? (
        <div
          className="risk-flow-tooltip"
          style={{
            left: `clamp(8px, ${tooltip.x + 14}px, calc(100vw - 300px))`,
            top: `clamp(8px, ${tooltip.y + 14}px, calc(100vh - 132px))`,
          }}
        >
          <strong>{tooltip.title}</strong>
          <span>{tooltip.meta}</span>
          <small>{tooltip.detail}</small>
        </div>
      ) : null}
    </>
  );
}

function RiskFlowNodeCard({ data }: NodeProps<RiskFlowNode>) {
  const node = data.graphNode;
  return (
    <div
      className={`risk-flow-node ${riskClassByLevel[node.level]} ${data.selected ? "is-selected" : ""} ${data.dimmed ? "is-dimmed" : ""} ${data.activePath ? "is-path-node" : ""} ${data.firstNeighbor ? "is-neighbor" : ""} ${data.selectedPathStep ? "is-step-node" : ""} ${data.pinned ? "is-pinned" : ""} ${data.matched ? "is-matched" : ""}`}
      style={
        {
          "--node-scale": `${1 + Math.min(0.14, graphScore(node.centralityScore ?? 0) / 650)}`,
          "--critical-ring": `${Math.max(1, Math.min(4, graphScore(node.criticalityScore ?? node.score) / 28))}px`,
        } as CSSProperties
      }
    >
      <Handle className="risk-flow-handle" id="target" position={Position.Left} type="target" />
      <Handle className="risk-flow-handle" id="source" position={Position.Right} type="source" />
      <div className="risk-flow-node-topline">
        <span>{node.kind}</span>
        <strong>{graphScore(node.criticalityScore ?? node.score)}</strong>
      </div>
      <p>{node.label}</p>
      <small>
        R{graphScore(node.riskScore ?? node.score)} / C{graphScore(node.centralityScore ?? 0)} /{" "}
        {node.countryCode ?? String(node.metadata.country ?? "global")}
      </small>
    </div>
  );
}
