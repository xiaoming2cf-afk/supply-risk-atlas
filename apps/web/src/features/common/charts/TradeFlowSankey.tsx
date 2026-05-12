import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function TradeFlowSankey(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Trade flow"} {...props} />;
}
