import { DataTable, type EvidenceTableProps } from "./DataTable";

export function LogisticsRouteTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Logistics routes"} {...props} />;
}
