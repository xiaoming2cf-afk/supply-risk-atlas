"use client";

import { useState, type ReactNode } from "react";
import { formatDisplayLabel, formatDisplayValue } from "./displayLabels";

export type AuditDetailItem = {
  label: string;
  value: unknown;
};

export type MetadataSummaryItem = {
  label: string;
  tone?: "default" | "good" | "warning" | "degraded";
};

const INTERNAL_METADATA_SUMMARY_LABELS = new Set([
  "calibration_status",
  "data_mode",
  "failed_endpoint",
  "graph_mode",
  "graph_version",
  "last_checked_at",
  "not_production_ready",
  "retry_hint",
  "source_manifest_id",
  "source_status",
  "transport_attempts",
]);

export function MetadataSummary({
  items,
  ariaLabel = "Data status summary",
}: {
  items: MetadataSummaryItem[];
  ariaLabel?: string;
}) {
  const visibleItems = items.filter((item) => isUserFacingSummaryLabel(item.label));
  if (visibleItems.length === 0) return null;

  return (
    <div className="metadata-summary" aria-label={ariaLabel} data-display-tier="supporting">
      {visibleItems.map((item) => (
        <span className={`metadata-summary-badge is-${item.tone ?? "default"}`} key={item.label}>
          {String(formatDisplayValue(item.label))}
        </span>
      ))}
    </div>
  );
}

function isUserFacingSummaryLabel(label: string) {
  const trimmed = label.trim();
  if (!trimmed) return false;
  const rawKey = trimmed.split(":")[0]?.trim().toLowerCase();
  return !INTERNAL_METADATA_SUMMARY_LABELS.has(rawKey);
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
                  <dt>{formatDisplayLabel(item.label)}</dt>
                  <dd>{formatAuditValue(item.value, item.label)}</dd>
                </div>
              ))}
            </dl>
          ) : null}
          {visibleWarnings.length ? (
            <div className="audit-warning-list">
              <strong>Warnings</strong>
              <ul>
                {visibleWarnings.slice(0, 8).map((warning) => (
                  <li key={warning}>{formatPublicWarning(warning)}</li>
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

export function formatPublicWarning(warning: string) {
  if (warning.includes("relationship_endpoint_unavailable")) {
    return "Backend relationship data unavailable; authoritative rows are hidden.";
  }
  if (warning.includes("semirisk_fixture_metadata")) return "Fixture graph metadata available";
  if (warning.includes("fixture_source_freshness_degraded")) return "Some public fixture source freshness is limited";
  if (warning.includes("not_production_ready") || warning.includes("fixture_graph")) return "Research fixture mode";
  if (warning.includes("raw_payload_excluded")) return "Raw source payloads are excluded from the UI";
  if (warning.includes("private_diagnostics_excluded")) return "Private diagnostics are excluded";
  return String(formatDisplayValue(warning));
}

function formatAuditValue(value: unknown, label?: string) {
  if (label === "not_production_ready" && value === true) return "Research fixture mode";
  if (label === "calibration_status" && typeof value === "string" && value.includes("fixture_proxy_not_calibrated")) {
    return "Research fixture calibration";
  }
  if (Array.isArray(value)) {
    const values = value.map((item) => String(formatDisplayValue(String(item)))).filter(Boolean);
    return values.length ? values.slice(0, 6).join(", ") : "none";
  }
  if (typeof value === "boolean") return value ? "yes" : "no";
  if (typeof value === "number") return Number.isFinite(value) ? String(value) : "unavailable";
  if (typeof value === "string") return String(formatDisplayValue(value));
  if (typeof value === "object") return "structured metadata";
  return String(value);
}
