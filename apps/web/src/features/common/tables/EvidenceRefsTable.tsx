import { DataTable, type EvidenceTableProps } from "./DataTable";

export function EvidenceRefsTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Evidence refs"} {...props} />;
}
