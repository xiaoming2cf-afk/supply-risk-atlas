import { DataTable, type EvidenceTableProps } from "./DataTable";

export function StageSourceCoverageTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Stage source coverage"} {...props} />;
}
