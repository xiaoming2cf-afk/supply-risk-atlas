import { DataTable, type EvidenceTableProps } from "./DataTable";

export function ProductionDependencyTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Production dependencies"} {...props} />;
}
