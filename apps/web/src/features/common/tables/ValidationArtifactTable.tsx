import { DataTable, type EvidenceTableProps } from "./DataTable";

export function ValidationArtifactTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "ValidationArtifact"} {...props} />;
}
