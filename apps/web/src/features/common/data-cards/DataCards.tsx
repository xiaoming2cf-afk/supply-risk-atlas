import type { ReactNode } from "react";
import { formatDisplayLabel, formatDisplayValue } from "../displayLabels";

export interface BadgeProps {
  label: string;
  value?: string | number | null;
  tone?: "neutral" | "good" | "warn" | "bad";
}

export function MetadataBadge({ label, value, tone = "neutral" }: BadgeProps) {
  return (
    <span className={`metadata-badge metadata-badge-${tone}`} data-component="metadata-badge">
      <span>{formatDisplayLabel(label)}</span>
      <strong>{value === undefined || value === null ? "unavailable" : formatDisplayValue(value)}</strong>
    </span>
  );
}

export function DataCard({
  title,
  value,
  detail,
  children,
}: {
  title: string;
  value?: string | number | null;
  detail?: string;
  children?: ReactNode;
}) {
  return (
    <section className="data-card" data-component="data-card">
      <h3>{title}</h3>
      {value !== undefined ? <strong>{value ?? "unavailable"}</strong> : null}
      {detail ? <p>{detail}</p> : null}
      {children}
    </section>
  );
}
