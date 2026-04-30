import type { Metadata } from "next";
import "./globals.css";
import "@supply-risk/design-system/styles.css";

export const metadata: Metadata = {
  title: "SupplyRiskAtlas",
  description: "Dynamic causal heterogeneous graph intelligence for global industrial risk.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
