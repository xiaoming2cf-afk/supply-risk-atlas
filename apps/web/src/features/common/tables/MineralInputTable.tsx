import { DataTable, type EvidenceTableProps } from "./DataTable";

export function MineralInputTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Mineral inputs"} {...props} />;
}
