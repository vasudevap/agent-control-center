import type { AtlasStatus } from "@/components/badge/status-badge";

export type ArtifactStatus = Extract<
  AtlasStatus,
  "available" | "review-required" | "expired"
>;
export type ArtifactType =
  | "Evidence packet"
  | "Operations summary"
  | "Draft set"
  | "Connector export";
export type Sensitivity = "Internal" | "Confidential" | "Restricted";

export interface ArtifactRecord {
  id: string;
  name: string;
  description: string;
  type: ArtifactType;
  status: ArtifactStatus;
  sensitivity: Sensitivity;
  agent: { id: string; name: string };
  runId: string;
  createdAt: string;
  retentionUntil?: string;
  contentType: string;
  size: string;
  checksum: string;
  storage: string;
  preview: string[];
}

const DAY = 24 * 60 * 60 * 1000;
const FIXTURE_NOW = Date.parse("2026-07-16T13:00:00.000Z");
const now = () => FIXTURE_NOW;
const daysAgo = (days: number) => new Date(now() - days * DAY).toISOString();
const daysFromNow = (days: number) =>
  new Date(now() + days * DAY).toISOString();

export const ARTIFACT_FIXTURES: ArtifactRecord[] = [
  {
    id: "art-2026-0712-001",
    name: "Billing remediation evidence packet",
    description:
      "Fictional decision evidence prepared for a critical external-message approval.",
    type: "Evidence packet",
    status: "review-required",
    sensitivity: "Restricted",
    agent: { id: "agent-policy-digest", name: "Policy Digest Agent" },
    runId: "run-2026-07-12-001",
    createdAt: daysAgo(1),
    retentionUntil: daysFromNow(364),
    contentType: "application/pdf",
    size: "842 KB",
    checksum: "sha256:fixture-18d9…8a21",
    storage: "External storage unavailable in prototype",
    preview: [
      "Decision context manifest",
      "Redacted source references",
      "Fictional integrity summary",
    ],
  },
  {
    id: "art-2026-0712-042",
    name: "Support operations summary",
    description:
      "Reviewed local summary of support-draft throughput and escalation patterns.",
    type: "Operations summary",
    status: "available",
    sensitivity: "Internal",
    agent: { id: "agent-support-drafts", name: "Support Draft Agent" },
    runId: "run-2026-07-12-042",
    createdAt: daysAgo(2),
    retentionUntil: daysFromNow(178),
    contentType: "application/json",
    size: "46 KB",
    checksum: "sha256:fixture-42c1…01f0",
    storage: "External storage unavailable in prototype",
    preview: [
      "9 fictional responses drafted",
      "2 items routed to specialist review",
      "No customer content retained",
    ],
  },
  {
    id: "art-2026-0709-013",
    name: "Support response draft set",
    description:
      "A metadata-only fixture representing nine governed response drafts.",
    type: "Draft set",
    status: "available",
    sensitivity: "Confidential",
    agent: { id: "agent-support-drafts", name: "Support Draft Agent" },
    runId: "run-2026-07-09-013",
    createdAt: daysAgo(5),
    retentionUntil: daysFromNow(85),
    contentType: "application/zip",
    size: "1.2 MB",
    checksum: "sha256:fixture-9ee4…b612",
    storage: "External storage unavailable in prototype",
    preview: [
      "Draft bodies intentionally not rendered",
      "Metadata contains fictional category counts",
      "Unsafe inline preview disabled",
    ],
  },
  {
    id: "art-2026-0705-011",
    name: "Connector evidence export",
    description:
      "Incomplete fictional export retained to explain a failed governed run.",
    type: "Connector export",
    status: "review-required",
    sensitivity: "Confidential",
    agent: { id: "agent-connectors-health", name: "Connector Health Sentinel" },
    runId: "run-2026-07-05-011",
    createdAt: daysAgo(9),
    retentionUntil: daysFromNow(21),
    contentType: "application/json",
    size: "18 KB",
    checksum: "Unavailable — fixture generation failed",
    storage: "No storage reference created",
    preview: [
      "Source checksum missing",
      "Original export unavailable",
      "Not safe to treat as complete evidence",
    ],
  },
  {
    id: "art-2025-1201-004",
    name: "Expired briefing digest",
    description:
      "Historical metadata retained after the fictional content lifecycle expired.",
    type: "Operations summary",
    status: "expired",
    sensitivity: "Internal",
    agent: { id: "agent-calendar-briefing", name: "Calendar Briefing Agent" },
    runId: "run-unavailable-2025-1201",
    createdAt: daysAgo(220),
    retentionUntil: daysAgo(40),
    contentType: "text/markdown",
    size: "Unavailable",
    checksum: "Metadata only",
    storage: "Content unavailable after fixture expiry",
    preview: [
      "Metadata retained for prototype lineage",
      "Source run route is unavailable",
      "No content can be opened",
    ],
  },
];

export function findArtifactById(id: string) {
  return ARTIFACT_FIXTURES.find((artifact) => artifact.id === id);
}
