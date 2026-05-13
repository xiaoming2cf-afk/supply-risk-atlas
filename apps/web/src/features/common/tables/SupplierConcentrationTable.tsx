import { DataTable, type EvidenceTableProps } from "./DataTable";

export function SupplierConcentrationTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "SupplierConcentration"} {...props} />;
}
