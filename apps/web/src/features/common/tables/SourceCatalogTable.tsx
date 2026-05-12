import { DataTable, type EvidenceTableProps } from "./DataTable";

export function SourceCatalogTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "SourceCatalog"} {...props} />;
}
