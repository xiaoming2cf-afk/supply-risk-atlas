"use client";

import { useState, type ReactNode } from "react";

export type AuditDetailItem = {
  label: string;
  value: unknown;
};

export type MetadataSummaryItem = {
  label: string;
  tone?: "default" | "good" | "warning" | "degraded";
};

export function MetadataSummary({
  items,
  ariaLabel = "Data status summary",
}: {
  items: MetadataSummaryItem[];
  ariaLabel?: string;
}) {
  const visibleItems = items.filter((item) => item.label.trim().length > 0);
  if (visibleItems.length === 0) return null;

  return (
    <div className="metadata-summary" aria-label={ariaLabel} data-display-tier="supporting">
      {visibleItems.map((item) => (
        <span className={`metadata-summary-badge is-${item.tone ?? "default"}`} key={item.label}>
          {item.label}
        </span>
      ))}
    </div>
  );
}

export function AuditDetails({
  label = "Data audit details",
  items,
  warnings,
  children,
  open = false,
}: {
  label?: string;
  items?: AuditDetailItem[];
  warnings?: string[];
  children?: ReactNode;
  open?: boolean;
}) {
  const visibleItems = (items ?? []).filter((item) => item.value !== undefined && item.value !== null && item.value !== "");
  const visibleWarnings = (warnings ?? []).filter(Boolean);
  const [expanded, setExpanded] = useState(open);
  if (visibleItems.length === 0 && visibleWarnings.length === 0 && !children) return null;

  return (
    <details
      className="audit-details"
      data-display-tier="audit_details"
      open={expanded}
      onToggle={(event) => setExpanded(event.currentTarget.open)}
    >
      <summary>{label}</summary>
      {expanded ? (
        <div className="audit-details-body">
          {visibleItems.length ? (
            <dl className="audit-detail-grid">
              {visibleItems.map((item) => (
                <div className="audit-detail-row" key={item.label}>
                  <dt>{item.label}</dt>
                  <dd>{formatAuditValue(item.value)}</dd>
                </div>
              ))}
            </dl>
          ) : null}
          {visibleWarnings.length ? (
            <div className="audit-warning-list">
              <strong>Warnings</strong>
              <ul>
                {visibleWarnings.slice(0, 8).map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {children}
        </div>
      ) : null}
    </details>
  );
}

export function DiagnosticDetails({
  items,
  label = "View diagnostics",
}: {
  items: AuditDetailItem[];
  label?: string;
}) {
  const visibleItems = items.filter((item) => item.value !== undefined && item.value !== null && item.value !== "");
  if (visibleItems.length === 0) return null;
  return <AuditDetails label={label} items={visibleItems} />;
}

export function publicDataModeLabel(mode?: string | null, sourceStatus?: string | null) {
  if (sourceStatus === "unavailable") return "Data temporarily unavailable";
  if (mode === "fixture" || mode === "fixture_or_promoted" || sourceStatus === "fixture") {
    return "Research fixture mode";
  }
  return "Public evidence mode";
}

function formatAuditValue(value: unknown) {
  if (Array.isArray(value)) {
    const values = value.map(String).filter(Boolean);
    return values.length ? values.slice(0, 6).join(", ") : "none";
  }
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "unavailable";
  if (typeof value === "string") return value;
  if (typeof value === "object") return "structured metadata";
  return String(value);
}
