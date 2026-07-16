import type { AtlasStatus } from "@/components/badge/status-badge";

export type ConnectorStatus = Extract<
  AtlasStatus,
  "healthy" | "degraded" | "expired" | "revoked" | "offline"
>;
export type AuthenticationType =
  | "OAuth 2.0"
  | "Service identity"
  | "Webhook signature";

export interface ConnectorRecord {
  id: string;
  name: string;
  provider: string;
  version: string;
  status: ConnectorStatus;
  authenticationType: AuthenticationType;
  accountLabel: string;
  capabilities: string[];
  scopes: string[];
  lastCheck: string;
  lastCheckAt: string | null;
  statusSummary: string;
}

export const CONNECTOR_FIXTURES: ConnectorRecord[] = [
  {
    id: "conn-mail-ops",
    name: "Operations Mail",
    provider: "Fictional Mail",
    version: "1.4.0",
    status: "healthy",
    authenticationType: "OAuth 2.0",
    accountLabel: "Operations mailbox fixture",
    capabilities: [
      "List message metadata",
      "Create draft",
      "Apply approved label",
    ],
    scopes: ["mail.metadata.read", "mail.draft.create", "mail.label.apply"],
    lastCheck: "8 minutes ago",
    lastCheckAt: "2026-07-16T10:52:00.000Z",
    statusSummary:
      "Fictional handshake and freshness checks are within threshold.",
  },
  {
    id: "conn-calendar-brief",
    name: "Briefing Calendar",
    provider: "Fictional Calendar",
    version: "2.0.2",
    status: "degraded",
    authenticationType: "OAuth 2.0",
    accountLabel: "Executive calendar fixture",
    capabilities: ["Read event metadata", "Read attendee display names"],
    scopes: ["calendar.events.read", "calendar.attendees.read"],
    lastCheck: "18 minutes ago",
    lastCheckAt: "2026-07-16T10:42:00.000Z",
    statusSummary: "The local fixture reports elevated response latency.",
  },
  {
    id: "conn-policy-archive",
    name: "Policy Evidence Archive",
    provider: "Atlas internal",
    version: "0.9.5",
    status: "expired",
    authenticationType: "Service identity",
    accountLabel: "Governance archive fixture",
    capabilities: ["Read evidence metadata", "Write approved export manifest"],
    scopes: ["evidence.metadata.read", "manifest.approved.write"],
    lastCheck: "6 hours ago",
    lastCheckAt: "2026-07-16T05:00:00.000Z",
    statusSummary:
      "The fictional authorization lease is expired; no credential exists in this prototype.",
  },
  {
    id: "conn-recruiting-hook",
    name: "Recruiting Intake",
    provider: "Fictional Webhook",
    version: "1.1.0",
    status: "offline",
    authenticationType: "Webhook signature",
    accountLabel: "Not configured",
    capabilities: ["Receive normalized intake event"],
    scopes: ["intake.event.receive"],
    lastCheck: "Never",
    lastCheckAt: null,
    statusSummary: "No connection instance is configured in the fixture.",
  },
];
