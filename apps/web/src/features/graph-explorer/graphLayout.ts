import type { GraphLink, GraphNode, GraphNodeKind, RiskLevel } from "@supply-risk/shared-types";

export type GraphPosition = { x: number; y: number };

export const graphColorByLevel: Record<RiskLevel, string> = {
  low: "#52d7d0",
  guarded: "#9fb2a9",
  elevated: "#f2b84b",
  severe: "#ff7a4d",
  critical: "#ff4d6d",
};

const graphKindRankHint: Record<GraphNodeKind, number> = {
  country: 0,
  route: 1,
  route_lane: 1,
  carrier: 1,
  data: 1,
  risk: 1,
  raw_material: 2,
  component: 2,
  product_grade: 2,
  supplier_tier: 2,
  supplier: 2,
  facility: 2,
  factory: 2,
  warehouse: 2,
  commodity: 2,
  company: 3,
};

const riskFlowNodeWidth = 188;
const riskFlowNodeHeight = 96;
const riskFlowNodeGap = 28;

export function graphScore(value: number | undefined, fallback = 0) {
  const score = value ?? fallback;
  if (!Number.isFinite(score)) return 0;
  return Math.round(score <= 1 ? score * 100 : score);
}

export function riskLevelRank(level: RiskLevel) {
  return { low: 0, guarded: 1, elevated: 2, severe: 3, critical: 4 }[level];
}

export function graphKindRank(kind: GraphNodeKind | string) {
  return graphKindRankHint[kind as GraphNodeKind] ?? 1;
}

export function compareGraphNodesForLayout(activePathNodeIndex: Map<string, number>) {
  return (a: GraphNode, b: GraphNode) => {
    const aPathIndex = activePathNodeIndex.get(a.id);
    const bPathIndex = activePathNodeIndex.get(b.id);
    if (aPathIndex !== undefined || bPathIndex !== undefined) {
      return (aPathIndex ?? Number.POSITIVE_INFINITY) - (bPathIndex ?? Number.POSITIVE_INFINITY);
    }
    return (
      riskLevelRank(b.level) - riskLevelRank(a.level) ||
      graphScore(b.criticalityScore ?? b.score) - graphScore(a.criticalityScore ?? a.score) ||
      graphKindRank(a.kind) - graphKindRank(b.kind) ||
      a.label.localeCompare(b.label) ||
      a.id.localeCompare(b.id)
    );
  };
}

export function computeRankedTopologyLayout(
  nodes: GraphNode[],
  links: GraphLink[],
  activePathNodeIndex = new Map<string, number>(),
): Map<string, GraphPosition> {
  const visibleIds = new Set(nodes.map((node) => node.id));
  const sortedNodes = [...nodes].sort(compareGraphNodesForLayout(activePathNodeIndex));
  const sortedLinks = [...links]
    .filter((link) => visibleIds.has(link.source) && visibleIds.has(link.target) && link.source !== link.target)
    .sort((a, b) => a.source.localeCompare(b.source) || a.target.localeCompare(b.target) || a.id.localeCompare(b.id));

  const outgoing = new Map<string, GraphLink[]>();
  const indegree = new Map<string, number>();
  const rankById = new Map<string, number>();
  for (const node of sortedNodes) {
    outgoing.set(node.id, []);
    indegree.set(node.id, 0);
    rankById.set(node.id, graphKindRank(node.kind));
  }
  for (const link of sortedLinks) {
    outgoing.get(link.source)?.push(link);
    indegree.set(link.target, (indegree.get(link.target) ?? 0) + 1);
  }

  const queue = sortedNodes.filter((node) => (indegree.get(node.id) ?? 0) === 0);
  for (let index = 0; index < queue.length; index += 1) {
    const node = queue[index];
    for (const link of outgoing.get(node.id) ?? []) {
      rankById.set(link.target, Math.max(rankById.get(link.target) ?? 0, (rankById.get(node.id) ?? 0) + 1));
      indegree.set(link.target, Math.max(0, (indegree.get(link.target) ?? 0) - 1));
      if (indegree.get(link.target) === 0) {
        const target = sortedNodes.find((candidate) => candidate.id === link.target);
        if (target) queue.push(target);
      }
    }
  }

  for (const link of sortedLinks) {
    const sourceRank = rankById.get(link.source) ?? 0;
    const targetRank = rankById.get(link.target) ?? 0;
    if (targetRank <= sourceRank) rankById.set(link.target, sourceRank + 1);
  }

  const compressedRanks = new Map<number, number>();
  [...new Set([...rankById.values()].sort((a, b) => a - b))].forEach((rank, index) => compressedRanks.set(rank, index));
  const rankGroups = new Map<number, GraphNode[]>();
  for (const node of sortedNodes) {
    const rank = compressedRanks.get(rankById.get(node.id) ?? 0) ?? 0;
    rankGroups.set(rank, [...(rankGroups.get(rank) ?? []), node]);
  }

  const maxRank = Math.max(0, ...rankGroups.keys());
  const positions = new Map<string, GraphPosition>();
  const rankGap = nodes.length <= 12 ? 248 : 218;
  const rowGap = nodes.length <= 12 ? 112 : 96;
  for (const [rank, rankNodes] of [...rankGroups.entries()].sort((a, b) => a[0] - b[0])) {
    const ordered = [...rankNodes].sort(compareGraphNodesForLayout(activePathNodeIndex));
    const count = ordered.length;
    ordered.forEach((node, index) => {
      const centerOffset = index - (count - 1) / 2;
      const denseRankOffset = count > 7 ? ((index % 2) - 0.5) * 54 : 0;
      positions.set(node.id, {
        x: (rank - maxRank / 2) * rankGap + denseRankOffset,
        y: centerOffset * rowGap,
      });
    });
  }
  return resolveGraphNodeCollisions(nodes, positions);
}

export function resolveGraphNodeCollisions(
  nodes: GraphNode[],
  initialPositions: Map<string, GraphPosition>,
): Map<string, GraphPosition> {
  const positions = new Map(initialPositions);
  const ordered = [...nodes].sort((a, b) => a.id.localeCompare(b.id));
  for (let pass = 0; pass < 22; pass += 1) {
    let moved = false;
    for (let leftIndex = 0; leftIndex < ordered.length; leftIndex += 1) {
      for (let rightIndex = leftIndex + 1; rightIndex < ordered.length; rightIndex += 1) {
        const left = ordered[leftIndex];
        const right = ordered[rightIndex];
        const leftPosition = positions.get(left.id);
        const rightPosition = positions.get(right.id);
        if (!leftPosition || !rightPosition) continue;
        const dx = rightPosition.x - leftPosition.x;
        const dy = rightPosition.y - leftPosition.y;
        const overlapX = riskFlowNodeWidth + riskFlowNodeGap - Math.abs(dx);
        const overlapY = riskFlowNodeHeight + riskFlowNodeGap - Math.abs(dy);
        if (overlapX <= 0 || overlapY <= 0) continue;
        moved = true;
        if (overlapX < overlapY) {
          const direction = dx >= 0 ? 1 : -1;
          positions.set(right.id, { ...rightPosition, x: rightPosition.x + direction * (overlapX / 2 + 4) });
          positions.set(left.id, { ...leftPosition, x: leftPosition.x - direction * (overlapX / 2 + 4) });
        } else {
          const direction = dy >= 0 ? 1 : -1;
          positions.set(right.id, { ...rightPosition, y: rightPosition.y + direction * (overlapY / 2 + 4) });
          positions.set(left.id, { ...leftPosition, y: leftPosition.y - direction * (overlapY / 2 + 4) });
        }
      }
    }
    if (!moved) break;
  }
  return positions;
}

export function countGraphPositionOverlaps(nodes: GraphNode[], positions: Map<string, GraphPosition>): number {
  let count = 0;
  for (let leftIndex = 0; leftIndex < nodes.length; leftIndex += 1) {
    for (let rightIndex = leftIndex + 1; rightIndex < nodes.length; rightIndex += 1) {
      const left = positions.get(nodes[leftIndex].id);
      const right = positions.get(nodes[rightIndex].id);
      if (!left || !right) continue;
      const overlapX = riskFlowNodeWidth - Math.abs(right.x - left.x);
      const overlapY = riskFlowNodeHeight - Math.abs(right.y - left.y);
      if (overlapX > 0 && overlapY > 0) count += 1;
    }
  }
  return count;
}
