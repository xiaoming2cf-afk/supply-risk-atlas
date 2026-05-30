import { DataTable, type EvidenceTableProps } from "./DataTable";

export function CriticalInputTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Critical inputs"} {...props} />;
}
