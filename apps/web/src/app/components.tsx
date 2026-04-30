import type { ButtonHTMLAttributes, CSSProperties, ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import type { RiskLevel, RiskMetric, TrendDirection } from "@supply-risk/shared-types";
import { formatCompactNumber, riskClassByLevel, riskLabelByLevel } from "@supply-risk/design-system";

type ButtonVariant = "default" | "primary";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: LucideIcon;
  variant?: ButtonVariant;
}

export function Button({ icon: Icon, variant = "default", children, className = "", ...props }: ButtonProps) {
  return (
    <button className={`control-button ${variant === "primary" ? "primary" : ""} ${className}`.trim()} type="button" {...props}>
      {Icon ? <Icon aria-hidden="true" /> : null}
      {children}
    </button>
  );
}

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: LucideIcon;
  label: string;
}

export function IconButton({ icon: Icon, label, ...props }: IconButtonProps) {
  return (
    <button aria-label={label} className="icon-button" title={label} type="button" {...props}>
      <Icon aria-hidden="true" />
    </button>
  );
}

interface PanelProps {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}

export function Panel({ title, subtitle, action, children, className = "", bodyClassName = "" }: PanelProps) {
  return (
    <section className={`panel ${className}`.trim()}>
      <div className="panel-header">
        <div>
          <h2 className="panel-title">{title}</h2>
          {subtitle ? <p className="panel-subtitle">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      <div className={`panel-body ${bodyClassName}`.trim()}>{children}</div>
    </section>
  );
}

export function RiskPill({ level }: { level: RiskLevel }) {
  return <span className={`risk-pill ${riskClassByLevel[level]}`}>{riskLabelByLevel[level]}</span>;
}

export function StatusPill({ status }: { status: string }) {
  return <span className={`status-pill ${status.toLowerCase().replace(/\s+/g, "-")}`}>{status}</span>;
}

export function MetricTile({ metric }: { metric: RiskMetric }) {
  const displayValue = metric.displayValue ?? formatCompactNumber(metric.value);
  return (
    <article className="metric-tile">
      <div className="metric-head">
        <p className="metric-label">{metric.label}</p>
        <RiskPill level={metric.level} />
      </div>
      <div>
        <p className="metric-value">
          {displayValue}
          {metric.unit ? <span className="metric-unit">{metric.unit}</span> : null}
        </p>
        <TrendDelta delta={metric.delta} trend={metric.trend} />
      </div>
      <p className="metric-detail">{metric.detail}</p>
    </article>
  );
}

export function TrendDelta({ delta, trend }: { delta: number; trend: TrendDirection }) {
  const prefix = trend === "up" ? "+" : trend === "down" ? "-" : "";
  return <span className={`delta ${trend}`}>{`${prefix}${Math.abs(delta).toFixed(1)}% vs prior build`}</span>;
}

export function ProgressBar({ value, level }: { value: number; level?: RiskLevel }) {
  const width = `${Math.max(0, Math.min(value, 100))}%`;
  const className = level ? riskClassByLevel[level] : "tone-guarded";
  return (
    <div className="bar-track" aria-label={`${Math.round(value)} percent`}>
      <div className={`bar-fill ${className}`} style={{ width }} />
    </div>
  );
}

export function ScoreDial({ score, level, label }: { score: number; level: RiskLevel; label: string }) {
  return (
    <div
      className={`score-dial ${riskClassByLevel[level]}`}
      style={{ "--score-deg": `${score * 3.6}deg` } as CSSProperties}
      aria-label={`${label}: ${score} of 100`}
    >
      <div className="score-dial-value">
        <strong>{score}</strong>
        <span>{label}</span>
      </div>
    </div>
  );
}

export function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="field">
      <span className="field-label">{label}</span>
      <span className="field-value">{value}</span>
    </div>
  );
}
