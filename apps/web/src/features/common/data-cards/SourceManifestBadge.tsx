import { MetadataBadge, type BadgeProps } from "./DataCards";

export function SourceManifestBadge(props: Omit<BadgeProps, "label"> & { label?: string }) {
  return <MetadataBadge label={props.label ?? "Source manifest"} tone={props.tone ?? "neutral"} value={props.value} />;
}
