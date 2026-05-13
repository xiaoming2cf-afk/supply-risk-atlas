import { DataTable, type EvidenceTableProps } from "./DataTable";

export function SupplyRelationshipTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "SupplyRelationship"} {...props} />;
}
