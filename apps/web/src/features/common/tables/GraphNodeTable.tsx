import { DataTable, type EvidenceTableProps } from "./DataTable";

export function GraphNodeTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "GraphNode"} {...props} />;
}
