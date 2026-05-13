import { DataTable, type EvidenceTableProps } from "./DataTable";

export function StageNodeCatalogTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Stage node catalog"} {...props} />;
}
