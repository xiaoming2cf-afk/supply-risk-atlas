import { MetadataBadge, type BadgeProps } from "./DataCards";

export function SourceManifestBadge(props: Omit<BadgeProps, "label"> & { label?: string }) {
  return <MetadataBadge label={props.label ?? "source_manifest_id"} tone={props.tone ?? "neutral"} value={props.value} />;
}
