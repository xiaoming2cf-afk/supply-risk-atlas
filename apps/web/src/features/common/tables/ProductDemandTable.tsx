import { DataTable, type EvidenceTableProps } from "./DataTable";

export function ProductDemandTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "ProductDemand"} {...props} />;
}
