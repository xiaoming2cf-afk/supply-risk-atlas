import { DataTable, type EvidenceTableProps } from "./DataTable";

export function RiskRankingTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "RiskRanking"} {...props} />;
}
