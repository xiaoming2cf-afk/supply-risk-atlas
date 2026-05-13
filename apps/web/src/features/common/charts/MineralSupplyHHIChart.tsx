import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function MineralSupplyHHIChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Mineral supply HHI"} {...props} />;
}
