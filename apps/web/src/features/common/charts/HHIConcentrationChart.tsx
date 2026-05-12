import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function HHIConcentrationChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "HHI concentration"} {...props} />;
}
