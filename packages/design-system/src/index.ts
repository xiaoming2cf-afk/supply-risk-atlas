import type { RiskLevel } from "@supply-risk/shared-types";

export const tokens = {
  color: {
    background: "#07110f",
    surface: "#101a18",
    surfaceStrong: "#17231f",
    border: "rgba(212, 226, 219, 0.16)",
    text: "#eef7f2",
    muted: "#9fb2a9",
    teal: "#42e3bd",
    amber: "#f2b84b",
    red: "#f05d5e",
    violet: "#9b8cff",
  },
  radius: {
    sm: "4px",
    md: "8px",
  },
  shadow: {
    soft: "0 18px 60px rgba(0, 0, 0, 0.36)",
  },
};

export const industrialTokens = {
  color: {
    page: "#090b0a",
    shell: "#111312",
    panel: "#151816",
    panelRaised: "#1d211d",
    rail: "#24281f",
    text: "#f2f5ed",
    muted: "#a7b1a6",
    subtle: "#767f75",
    line: "rgba(220, 230, 215, 0.13)",
    lineStrong: "rgba(221, 233, 211, 0.25)",
    accent: "#d7ff5f",
    cyan: "#59d8d2",
    amber: "#ffbe48",
    copper: "#e68645",
    red: "#ff655f",
  },
  radius: {
    sm: "4px",
    md: "6px",
    lg: "8px",
  },
  motion: {
    quick: "120ms ease",
    normal: "180ms ease",
  },
} as const;

export const riskClassByLevel: Record<RiskLevel, string> = {
  low: "tone-low",
  guarded: "tone-guarded",
  elevated: "tone-elevated",
  severe: "tone-severe",
  critical: "tone-critical",
};

export const riskLabelByLevel: Record<RiskLevel, string> = {
  low: "Low",
  guarded: "Guarded",
  elevated: "Elevated",
  severe: "Severe",
  critical: "Critical",
};

export const formatCompactNumber = (value: number) =>
  new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 1,
    notation: "compact",
  }).format(value);

export const formatPercent = (value: number, digits = 0) =>
  new Intl.NumberFormat("en-US", {
    style: "percent",
    maximumFractionDigits: digits,
  }).format(value);

export const formatUsdCompact = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 1,
    notation: "compact",
  }).format(value);
