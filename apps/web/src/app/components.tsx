import type { ButtonHTMLAttributes, CSSProperties, ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import type { RiskLevel, RiskMetric, TrendDirection } from "@supply-risk/shared-types";
import { formatCompactNumber, riskClassByLevel } from "@supply-risk/design-system";
import { translateRiskLevel, useI18n } from "./i18n";

type ButtonVariant = "default" | "primary";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: LucideIcon;
  variant?: ButtonVariant;
}

export function Button({ icon: Icon, variant = "default", children, className = "", ...props }: ButtonProps) {
  const { t } = useI18n();
  const translatedChildren = typeof children === "string" ? t(children) : children;
  return (
    <button className={`control-button ${variant === "primary" ? "primary" : ""} ${className}`.trim()} type="button" {...props}>
      {Icon ? <Icon aria-hidden="true" /> : null}
      {translatedChildren}
    </button>
  );
}

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  icon: LucideIcon;
  label: string;
}

export function IconButton({ icon: Icon, label, ...props }: IconButtonProps) {
  const { t } = useI18n();
  const translatedLabel = t(label);
  return (
    <button aria-label={translatedLabel} className="icon-button" title={translatedLabel} type="button" {...props}>
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
  const { t } = useI18n();
  return (
    <section className={`panel ${className}`.trim()}>
      <div className="panel-header">
        <div>
          <h2 className="panel-title">{t(title)}</h2>
          {subtitle ? <p className="panel-subtitle">{t(subtitle)}</p> : null}
        </div>
        {action}
      </div>
      <div className={`panel-body ${bodyClassName}`.trim()}>{children}</div>
    </section>
  );
}

export function RiskPill({ level }: { level: RiskLevel }) {
  const { language } = useI18n();
  return <span className={`risk-pill ${riskClassByLevel[level]}`}>{translateRiskLevel(level, language)}</span>;
}

export function StatusPill({ status }: { status: string }) {
  const { t } = useI18n();
  return <span className={`status-pill ${status.toLowerCase().replace(/\s+/g, "-")}`}>{t(status)}</span>;
}

export function MetricTile({ metric }: { metric: RiskMetric }) {
  const { t } = useI18n();
  const displayValue = metric.displayValue ?? formatCompactNumber(metric.value);
  return (
    <article className="metric-tile">
      <div className="metric-head">
        <p className="metric-label">{t(metric.label)}</p>
        <RiskPill level={metric.level} />
      </div>
      <div>
        <p className="metric-value">
          {displayValue}
          {metric.unit ? <span className="metric-unit">{metric.unit}</span> : null}
        </p>
        <TrendDelta delta={metric.delta} trend={metric.trend} />
      </div>
      <p className="metric-detail">{t(metric.detail)}</p>
    </article>
  );
}

export function TrendDelta({ delta, trend }: { delta: number; trend: TrendDirection }) {
  const { t } = useI18n();
  const prefix = trend === "up" ? "+" : trend === "down" ? "-" : "";
  return <span className={`delta ${trend}`}>{t(`${prefix}${Math.abs(delta).toFixed(1)}% vs prior build`)}</span>;
}

export function ProgressBar({ value, level }: { value: number; level?: RiskLevel }) {
  const { t } = useI18n();
  const width = `${Math.max(0, Math.min(value, 100))}%`;
  const className = level ? riskClassByLevel[level] : "tone-guarded";
  return (
    <div className="bar-track" aria-label={t(`${Math.round(value)} percent`)}>
      <div className={`bar-fill ${className}`} style={{ width }} />
    </div>
  );
}

export function ScoreDial({ score, level, label }: { score: number; level: RiskLevel; label: string }) {
  const { t } = useI18n();
  const translatedLabel = t(label);
  return (
    <div
      className={`score-dial ${riskClassByLevel[level]}`}
      style={{ "--score-deg": `${score * 3.6}deg` } as CSSProperties}
      aria-label={`${translatedLabel}: ${score} ${t("of 100")}`}
    >
      <div className="score-dial-value">
        <strong>{score}</strong>
        <span>{translatedLabel}</span>
      </div>
    </div>
  );
}

export function Field({ label, value }: { label: string; value: ReactNode }) {
  const { t } = useI18n();
  const translatedValue = typeof value === "string" ? t(value) : value;
  return (
    <div className="field">
      <span className="field-label">{t(label)}</span>
      <span className="field-value">{translatedValue}</span>
    </div>
  );
}
