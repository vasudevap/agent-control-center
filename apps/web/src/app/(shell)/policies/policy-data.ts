import type { AtlasStatus } from "@/components/badge/status-badge";
import type { RiskLevel } from "@/components/risk/risk-indicator";

export type PolicyStatus = Extract<AtlasStatus, "active" | "paused">;
export type PolicyType = "Approval" | "Access" | "Retention" | "Execution";

export interface PolicyRecord {
  id: string;
  name: string;
  type: PolicyType;
  version: number;
  status: PolicyStatus;
  risk: RiskLevel;
  scope: string;
  assignedAgents: Array<{ id: string; name: string }>;
  summary: string;
  ruleSummary: string[];
  updatedAt: string;
}

export const POLICY_FIXTURES: PolicyRecord[] = [
  {
    id: "P-214",
    name: "External communications approval",
    type: "Approval",
    version: 8,
    status: "active",
    risk: "Critical",
    scope: "Outbound communication drafts",
    assignedAgents: [
      { id: "agent-support-drafts", name: "Support Draft Agent" },
    ],
    summary:
      "Requires human confirmation before a fictional high-impact external communication could proceed.",
    ruleSummary: [
      "Critical requests require step-up confirmation.",
      "Model output never authorizes the action.",
      "Approval evidence must reference the originating run.",
    ],
    updatedAt: "2026-07-16T11:00:00.000Z",
  },
  {
    id: "P-118",
    name: "Evidence retention declaration",
    type: "Retention",
    version: 3,
    status: "paused",
    risk: "Medium",
    scope: "Governance evidence metadata",
    assignedAgents: [
      { id: "agent-policy-digest", name: "Policy Digest Agent" },
    ],
    summary: "Declares fictional retention metadata for governance evidence.",
    ruleSummary: [
      "No enforcement exists in this frontend prototype.",
      "Retention dates must be explicit metadata.",
      "Expired content must not be presented as available.",
    ],
    updatedAt: "2026-07-14T14:32:00.000Z",
  },
  {
    id: "P-307",
    name: "Connector least privilege",
    type: "Access",
    version: 5,
    status: "active",
    risk: "High",
    scope: "All connector operations",
    assignedAgents: [
      { id: "agent-connectors-health", name: "Connector Health Sentinel" },
      { id: "agent-calendar-briefing", name: "Calendar Briefing Agent" },
    ],
    summary:
      "Declares that agent tools may request only named connector operations and scopes.",
    ruleSummary: [
      "Deny operations not explicitly declared.",
      "Never expose provider clients or credentials to agents.",
      "Material scope changes require review.",
    ],
    updatedAt: "2026-07-12T16:10:00.000Z",
  },
  {
    id: "P-402",
    name: "Duplicate run safeguard",
    type: "Execution",
    version: 2,
    status: "active",
    risk: "Low",
    scope: "Scheduled agent runs",
    assignedAgents: [],
    summary: "Describes a future safeguard against overlapping scheduled runs.",
    ruleSummary: [
      "Check the active-run key before queueing.",
      "Do not imply that this UI performs the check.",
      "Record a normalized blocked outcome in a future runtime.",
    ],
    updatedAt: "2026-07-10T09:15:00.000Z",
  },
];
