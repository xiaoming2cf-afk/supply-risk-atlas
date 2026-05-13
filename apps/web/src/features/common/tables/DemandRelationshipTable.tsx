import { DataTable, type EvidenceTableProps } from "./DataTable";

export function DemandRelationshipTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "DemandRelationship"} {...props} />;
}
