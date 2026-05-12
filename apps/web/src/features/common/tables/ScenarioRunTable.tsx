import { DataTable, type EvidenceTableProps } from "./DataTable";

export function ScenarioRunTable(props: EvidenceTableProps) {
  return <DataTable title={props.title ?? "ScenarioRun"} {...props} />;
}
