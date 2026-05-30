import { DataTable, type EvidenceTableProps } from "./DataTable";

export function ReverseStressResultTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Ranked shock sets"} {...props} />;
}
