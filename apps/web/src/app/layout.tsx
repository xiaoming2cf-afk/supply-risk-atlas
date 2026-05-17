import type { Metadata } from "next";
import "./globals.css";
import "@xyflow/react/dist/style.css";
import "@supply-risk/design-system/styles.css";

const webBuildCommit = process.env.NEXT_PUBLIC_SUPPLY_RISK_WEB_COMMIT ?? "not_verified";
const webBuildTime = process.env.NEXT_PUBLIC_SUPPLY_RISK_WEB_BUILD_TIME ?? "not_verified";

export const metadata: Metadata = {
  title: "SupplyRiskAtlas",
  description: "Dynamic causal heterogeneous graph intelligence for global industrial risk.",
  other: {
    "supply-risk-web-commit": webBuildCommit,
    "supply-risk-web-build-time": webBuildTime
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
