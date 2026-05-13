import { DataTable, type EvidenceTableProps } from "./DataTable";

export function FabProcessDependencyTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Fab process dependencies"} {...props} />;
}
