import { MetadataBadge, type BadgeProps } from "./DataCards";

export function VersionBadge(props: Omit<BadgeProps, "label"> & { label?: string }) {
  return <MetadataBadge label={props.label ?? "version"} tone={props.tone ?? "neutral"} value={props.value} />;
}
