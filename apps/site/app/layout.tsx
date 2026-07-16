import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Atlas | Enterprise Agent Control Center",
  description:
    "Atlas is an enterprise-inspired control plane for understanding, governing, and controlling autonomous work.",
  applicationName: "Atlas",
  keywords: [
    "agent control center",
    "AI agent governance",
    "agent operations",
    "agent control plane",
    "human approval",
    "AI observability",
  ],
  robots: { index: true, follow: true },
  openGraph: {
    type: "website",
    title: "Atlas | Keep autonomous work under control",
    description:
      "A governed operating environment for agents, runs, approvals, connectors, and operational evidence.",
    siteName: "Atlas",
  },
  twitter: {
    card: "summary_large_image",
    title: "Atlas | Keep autonomous work under control",
    description:
      "A governed operating environment for agents, runs, approvals, connectors, and operational evidence.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
