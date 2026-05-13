import { DataTable, type EvidenceTableProps } from "./DataTable";

export function SupplyDemandBalanceTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "SupplyDemandBalance"} {...props} />;
}
