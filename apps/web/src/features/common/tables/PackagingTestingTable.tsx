import { DataTable, type EvidenceTableProps } from "./DataTable";

export function PackagingTestingTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Packaging and testing"} {...props} />;
}
