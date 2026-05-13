import { DataTable, type EvidenceTableProps } from "./DataTable";

export function TradeFlowTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "TradeFlow"} {...props} />;
}
