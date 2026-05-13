import { DataTable, type EvidenceTableProps } from "./DataTable";

export function OptimizerActionTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "OptimizerAction"} {...props} />;
}
