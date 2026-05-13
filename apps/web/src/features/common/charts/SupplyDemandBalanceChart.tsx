import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function SupplyDemandBalanceChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Supply-demand balance"} {...props} />;
}
