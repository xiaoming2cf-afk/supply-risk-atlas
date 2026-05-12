import { LineChart, type BasicChartProps } from "./ChartPrimitives";

export function MonteCarloECDF(props: BasicChartProps) {
  return <LineChart title={props.title ?? "Monte Carlo ECDF"} {...props} />;
}
