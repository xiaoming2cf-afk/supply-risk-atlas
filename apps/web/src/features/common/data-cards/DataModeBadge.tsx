import { MetadataBadge, type BadgeProps } from "./DataCards";

export function DataModeBadge(props: Omit<BadgeProps, "label"> & { label?: string }) {
  return <MetadataBadge label={props.label ?? "data_mode"} tone={props.tone ?? "warn"} value={props.value} />;
}
