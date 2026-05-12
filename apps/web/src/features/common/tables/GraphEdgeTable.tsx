import { DataTable, type EvidenceTableProps } from "./DataTable";

export function GraphEdgeTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "GraphEdge"} {...props} />;
}
