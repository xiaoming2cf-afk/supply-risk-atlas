import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function PolicyRestrictionImpactChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Policy restriction impact"} {...props} />;
}
