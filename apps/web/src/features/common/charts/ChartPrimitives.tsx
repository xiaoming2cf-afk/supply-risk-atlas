import type { ReactNode } from "react";

export interface ChartDatum {
  label: string;
  value: number;
  secondaryValue?: number;
  color?: string;
}

export interface ChartMetadata {
  graphVersion?: string | null;
  sourceManifestId?: string | null;
  warnings?: string[];
}

export interface BasicChartProps {
  title?: string;
  data?: ChartDatum[];
  metadata?: ChartMetadata;
  loading?: boolean;
  degraded?: boolean;
  emptyLabel?: string;
}

const palette = ["#2563eb", "#16a34a", "#d97706", "#7c3aed", "#dc2626", "#0891b2"];

export function ChartFrame({
  title,
  metadata,
  loading,
  degraded,
  emptyLabel = "No chart data available.",
  children,
}: BasicChartProps & { children?: ReactNode }) {
  const hasMetadata = metadata?.graphVersion || metadata?.sourceManifestId || metadata?.warnings?.length;
  return (
    <section className="chart-frame" data-component="evidence-chart">
      {title ? <h3>{title}</h3> : null}
      {loading ? <p className="muted">Loading chart data...</p> : children || <p className="muted">{emptyLabel}</p>}
      {degraded ? <p className="warning-text">Data source unavailable or degraded.</p> : null}
      {hasMetadata ? (
        <p className="metadata-line">
          {metadata?.graphVersion ? `graph_version=${metadata.graphVersion}` : null}
          {metadata?.sourceManifestId ? ` source_manifest_id=${metadata.sourceManifestId}` : null}
          {metadata?.warnings?.length ? ` warnings=${metadata.warnings.length}` : null}
        </p>
      ) : null}
    </section>
  );
}

export function BarChart(props: BasicChartProps) {
  const data = props.data ?? [];
  const max = Math.max(1, ...data.map((item) => Math.abs(item.value)));
  return (
    <ChartFrame {...props}>
      {data.length ? (
        <div className="bar-chart" role="list">
          {data.map((item, index) => (
            <div className="bar-row" key={`${item.label}-${index}`} role="listitem">
              <span className="bar-label">{item.label}</span>
              <span className="bar-track">
                <span
                  className="bar-fill"
                  style={{
                    width: `${Math.max(2, (Math.abs(item.value) / max) * 100)}%`,
                    background: item.color ?? palette[index % palette.length],
                  }}
                />
              </span>
              <span className="bar-value">{formatValue(item.value)}</span>
            </div>
          ))}
        </div>
      ) : null}
    </ChartFrame>
  );
}

export function StackedBarChart(props: BasicChartProps) {
  const data = props.data ?? [];
  const total = Math.max(1, data.reduce((sum, item) => sum + Math.max(0, item.value), 0));
  return (
    <ChartFrame {...props}>
      {data.length ? (
        <div className="stacked-bar" aria-label={props.title}>
          {data.map((item, index) => (
            <span
              key={`${item.label}-${index}`}
              title={`${item.label}: ${formatValue(item.value)}`}
              style={{
                width: `${(Math.max(0, item.value) / total) * 100}%`,
                background: item.color ?? palette[index % palette.length],
              }}
            />
          ))}
        </div>
      ) : null}
    </ChartFrame>
  );
}

export function LineChart(props: BasicChartProps) {
  const data = props.data ?? [];
  const max = Math.max(1, ...data.map((item) => item.value));
  const points = data
    .map((item, index) => `${(index / Math.max(1, data.length - 1)) * 100},${100 - (item.value / max) * 90}`)
    .join(" ");
  return (
    <ChartFrame {...props}>
      {data.length ? (
        <svg className="line-chart" viewBox="0 0 100 110" role="img" aria-label={props.title}>
          <polyline points={points} fill="none" stroke="#2563eb" strokeWidth="3" />
          {data.map((item, index) => (
            <circle
              key={`${item.label}-${index}`}
              cx={(index / Math.max(1, data.length - 1)) * 100}
              cy={100 - (item.value / max) * 90}
              r="2.5"
              fill="#2563eb"
            />
          ))}
        </svg>
      ) : null}
    </ChartFrame>
  );
}

export function HeatmapChart(props: BasicChartProps) {
  const data = props.data ?? [];
  const max = Math.max(1, ...data.map((item) => Math.abs(item.value)));
  return (
    <ChartFrame {...props}>
      {data.length ? (
        <div className="heatmap-chart">
          {data.map((item, index) => (
            <span
              key={`${item.label}-${index}`}
              title={`${item.label}: ${formatValue(item.value)}`}
              style={{ opacity: 0.25 + 0.75 * (Math.abs(item.value) / max) }}
            >
              {item.label}
            </span>
          ))}
        </div>
      ) : null}
    </ChartFrame>
  );
}

function formatValue(value: number) {
  if (Math.abs(value) >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
  return value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

