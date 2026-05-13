import { DataTable, type EvidenceTableProps } from "./DataTable";

export function EquipmentSupplierTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Equipment suppliers"} {...props} />;
}
