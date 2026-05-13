import { HeatmapChart, type BasicChartProps } from "./ChartPrimitives";

export function ComplianceRestrictionMatrixChart(props: BasicChartProps) {
  return <HeatmapChart title={props.title ?? "Compliance restriction matrix"} {...props} />;
}
