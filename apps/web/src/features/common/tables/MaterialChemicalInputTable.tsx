import { DataTable, type EvidenceTableProps } from "./DataTable";

export function MaterialChemicalInputTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "Material and chemical inputs"} {...props} />;
}
