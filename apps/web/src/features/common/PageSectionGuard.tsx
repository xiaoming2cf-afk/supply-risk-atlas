import type { ReactNode } from "react";
import type { DashboardPageId } from "@supply-risk/shared-types";
import { getPageRelevancePolicy } from "./pageRelevance";

export function PageSectionGuard({
  children,
  pageId,
  sectionId,
}: {
  children: ReactNode;
  pageId: DashboardPageId;
  sectionId: string;
}) {
  const policy = getPageRelevancePolicy(pageId);
  if (policy.disallowedMajorSections.includes(sectionId)) {
    return null;
  }
  return <>{children}</>;
}
