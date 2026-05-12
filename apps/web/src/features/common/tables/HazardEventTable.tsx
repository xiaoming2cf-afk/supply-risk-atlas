import { DataTable, type EvidenceTableProps } from "./DataTable";

export function HazardEventTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "HazardEvent"} {...props} />;
}
