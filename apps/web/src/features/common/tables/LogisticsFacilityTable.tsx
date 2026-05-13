import { DataTable, type EvidenceTableProps } from "./DataTable";

export function LogisticsFacilityTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "LogisticsFacility"} {...props} />;
}
