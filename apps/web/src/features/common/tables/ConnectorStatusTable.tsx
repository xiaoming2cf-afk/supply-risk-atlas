import { DataTable, type EvidenceTableProps } from "./DataTable";

export function ConnectorStatusTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "ConnectorStatus"} {...props} />;
}
