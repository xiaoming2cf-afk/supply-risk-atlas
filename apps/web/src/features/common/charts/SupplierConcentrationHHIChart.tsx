import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function SupplierConcentrationHHIChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Supplier concentration HHI"} {...props} />;
}
