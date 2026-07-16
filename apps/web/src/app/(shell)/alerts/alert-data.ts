import type { AtlasStatus } from "@/components/badge/status-badge";

export type AlertSeverity = "critical" | "high" | "warning" | "information";
export type AlertStatus = Extract<
  AtlasStatus,
  "active" | "investigating" | "resolved"
>;

export interface AlertRecord {
  id: string;
  severity: AlertSeverity;
  status: AlertStatus;
  title: string;
  description: string;
  timestamp: string;
  raisedAt: string;
  source: string;
  sourceAgentId?: string;
  category: "Connector" | "Policy" | "Runtime" | "Scheduler";
  evidence: string;
  correlationId: string;
  relatedRunId?: string;
}

export const ALERT_SEVERITY_LABELS: Record<AlertSeverity, string> = {
  critical: "Critical",
  high: "High",
  warning: "Warning",
  information: "Information",
};

export const ALERT_FIXTURES: AlertRecord[] = [
  {
    id: "alt-901",
    severity: "critical",
    status: "active",
    title: "Connector authentication expired",
    description:
      "Policy Digest Agent lost access to its evidence-export connector. Runs are paused.",
    timestamp: "6 hours ago",
    raisedAt: "2026-07-16T07:00:00.000Z",
    source: "Policy Digest Agent",
    sourceAgentId: "agent-policy-digest",
    category: "Connector",
    evidence:
      "The fictional connector health check returned an expired credential state. No provider was contacted.",
    correlationId: "corr-alert-0901",
    relatedRunId: "run-2026-07-12-001",
  },
  {
    id: "alt-904",
    severity: "high",
    status: "investigating",
    title: "Repeated governed run failures",
    description:
      "Connector Health Sentinel reached the local fixture failure threshold.",
    timestamp: "9 hours ago",
    raisedAt: "2026-07-16T04:00:00.000Z",
    source: "Connector Health Sentinel",
    sourceAgentId: "agent-connectors-health",
    category: "Runtime",
    evidence:
      "Three fictional attempts share the same normalized policy failure code.",
    correlationId: "corr-alert-0904",
    relatedRunId: "run-2026-07-05-011",
  },
  {
    id: "alt-902",
    severity: "warning",
    status: "active",
    title: "Elevated policy-review backlog",
    description:
      "Invoice Reconciliation Agent has three invoices waiting on policy review.",
    timestamp: "12 minutes ago",
    raisedAt: "2026-07-16T12:48:00.000Z",
    source: "Invoice Reconciliation Agent",
    sourceAgentId: "agent-invoice-reconcile",
    category: "Policy",
    evidence:
      "The local queue fixture exceeds its warning threshold by one item.",
    correlationId: "corr-alert-0902",
  },
  {
    id: "alt-903",
    severity: "information",
    status: "resolved",
    title: "Policy updated",
    description:
      '"External Communications P-214" now requires step-up confirmation for Critical requests.',
    timestamp: "2 hours ago",
    raisedAt: "2026-07-16T11:00:00.000Z",
    source: "Policies",
    category: "Policy",
    evidence: "A fictional policy-version fixture changed from 7 to 8.",
    correlationId: "corr-alert-0903",
  },
];
