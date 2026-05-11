import { ChevronRight } from "lucide-react";
import type { GraphLink, GraphNode } from "@supply-risk/shared-types";
import { graphModeLabel, type GraphViewMode } from "./graphViewModel";

export function GraphBreadcrumbs({
  mode,
  selectedEdge,
  selectedNode,
}: {
  mode: GraphViewMode;
  selectedEdge?: GraphLink;
  selectedNode?: GraphNode;
}) {
  return (
    <nav aria-label="Graph breadcrumbs" className="graph-breadcrumbs">
      <span>{graphModeLabel(mode)}</span>
      {selectedNode ? (
        <>
          <ChevronRight aria-hidden="true" />
          <span>{selectedNode.label}</span>
        </>
      ) : null}
      {selectedEdge ? (
        <>
          <ChevronRight aria-hidden="true" />
          <span>{selectedEdge.label}</span>
        </>
      ) : null}
    </nav>
  );
}
