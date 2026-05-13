import { BarChart, type BasicChartProps } from "./ChartPrimitives";

export function MaterialSupplierConcentrationChart(props: BasicChartProps) {
  return <BarChart title={props.title ?? "Material supplier concentration"} {...props} />;
}
