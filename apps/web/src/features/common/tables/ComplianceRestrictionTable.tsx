import { DataTable, type EvidenceTableProps } from "./DataTable";

export function ComplianceRestrictionTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Compliance restrictions"} {...props} />;
}
