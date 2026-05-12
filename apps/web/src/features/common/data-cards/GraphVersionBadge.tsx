import { MetadataBadge, type BadgeProps } from "./DataCards";

export function GraphVersionBadge(props: Omit<BadgeProps, "label"> & { label?: string }) {
  return <MetadataBadge label={props.label ?? "graph_version"} tone={props.tone ?? "neutral"} value={props.value} />;
}
