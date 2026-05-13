import { DataTable, type EvidenceTableProps } from "./DataTable";

export function StageEvidenceRefsTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Stage evidence refs"} {...props} />;
}
