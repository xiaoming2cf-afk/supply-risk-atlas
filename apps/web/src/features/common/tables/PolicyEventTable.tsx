import { DataTable, type EvidenceTableProps } from "./DataTable";

export function PolicyEventTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Policy events"} {...props} />;
}
