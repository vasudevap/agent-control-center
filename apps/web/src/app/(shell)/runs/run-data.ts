import type { AtlasStatus } from "@/components/badge/status-badge";

export type RunStatus = Extract<
  AtlasStatus,
  | "queued"
  | "running"
  | "waiting"
  | "succeeded"
  | "partially-succeeded"
  | "failed"
  | "cancelled"
  | "timed-out"
>;
export type RunTrigger = "Manual" | "Scheduled" | "Event";
export type LogSeverity = "Info" | "Warning" | "Error";

export interface RunStep {
  id: string;
  name: string;
  type:
    | "Connector call"
    | "Model call"
    | "Policy evaluation"
    | "Approval wait"
    | "Output write";
  status: RunStatus;
  startedAt: string;
  duration: string;
  summary: string;
}

export interface RunLog {
  id: string;
  at: string;
  severity: LogSeverity;
  component: string;
  message: string;
}

export interface RunRecord {
  id: string;
  agent: { id: string; name: string };
  status: RunStatus;
  trigger: RunTrigger;
  startedAt: string;
  completedAt?: string;
  duration: string;
  retryCount: number;
  correlationId: string;
  summary: string;
  costEstimate: string;
  error?: {
    code: string;
    category: string;
    retryable: boolean;
    summary: string;
  };
  approvalIds: string[];
  artifactIds: string[];
  steps: RunStep[];
  logs: RunLog[];
}

const HOUR = 60 * 60 * 1000;
const FIXTURE_NOW = Date.parse("2026-07-16T13:00:00.000Z");
const now = () => FIXTURE_NOW;
const hoursAgo = (hours: number) =>
  new Date(now() - hours * HOUR).toISOString();

const steps = (id: string, status: RunStatus): RunStep[] => [
  {
    id: `${id}-step-1`,
    name: "Resolve approved context",
    type: "Connector call",
    status: "succeeded",
    startedAt: hoursAgo(3),
    duration: "1.8s",
    summary:
      "Resolved fictional connector metadata; no provider call occurred.",
  },
  {
    id: `${id}-step-2`,
    name: "Evaluate governed action",
    type: "Policy evaluation",
    status: status === "failed" ? "failed" : "succeeded",
    startedAt: hoursAgo(2.9),
    duration: "0.6s",
    summary:
      status === "failed"
        ? "Fixture policy evidence was incomplete."
        : "Fixture policy outcome allowed the local workflow to continue.",
  },
  {
    id: `${id}-step-3`,
    name:
      status === "waiting"
        ? "Wait for human approval"
        : "Write output metadata",
    type: status === "waiting" ? "Approval wait" : "Output write",
    status,
    startedAt: hoursAgo(2.8),
    duration: status === "running" ? "In progress" : "2.4s",
    summary:
      status === "waiting"
        ? "Paused at a fictional approval boundary."
        : "Prepared fictional output metadata only.",
  },
];

const logs = (id: string, status: RunStatus): RunLog[] => [
  {
    id: `${id}-log-1`,
    at: hoursAgo(3),
    severity: "Info",
    component: "agent-runtime",
    message: "Fixture run accepted for local prototype display.",
  },
  {
    id: `${id}-log-2`,
    at: hoursAgo(2.9),
    severity: status === "failed" ? "Error" : "Info",
    component: "policy",
    message:
      status === "failed"
        ? "Normalized fixture failure: required evidence unavailable."
        : "Fixture policy evaluation completed.",
  },
  {
    id: `${id}-log-3`,
    at: hoursAgo(2.8),
    severity: status === "partially-succeeded" ? "Warning" : "Info",
    component: "output",
    message:
      "No secret-bearing or external content is included in this fictional log excerpt.",
  },
];

export const RUN_FIXTURES: RunRecord[] = [
  {
    id: "run-2026-07-12-001",
    agent: { id: "agent-policy-digest", name: "Policy Digest Agent" },
    status: "waiting",
    trigger: "Scheduled",
    startedAt: hoursAgo(3),
    duration: "3h 04m",
    retryCount: 0,
    correlationId: "corr-run-0712-001",
    summary:
      "Prepared a billing remediation review packet and paused at human approval.",
    costEstimate: "$0.18",
    approvalIds: ["apr-2026-001"],
    artifactIds: ["art-2026-0712-001"],
    steps: steps("run-2026-07-12-001", "waiting"),
    logs: logs("run-2026-07-12-001", "waiting"),
  },
  {
    id: "run-2026-07-12-042",
    agent: { id: "agent-support-drafts", name: "Support Draft Agent" },
    status: "succeeded",
    trigger: "Manual",
    startedAt: hoursAgo(5),
    completedAt: hoursAgo(4.9),
    duration: "4m 12s",
    retryCount: 0,
    correlationId: "corr-run-0712-042",
    summary: "Prepared a reviewed internal operations summary.",
    costEstimate: "$0.07",
    approvalIds: ["apr-2026-004"],
    artifactIds: ["art-2026-0712-042"],
    steps: steps("run-2026-07-12-042", "succeeded"),
    logs: logs("run-2026-07-12-042", "succeeded"),
  },
  {
    id: "run-2026-07-13-006",
    agent: { id: "agent-recruiting-triage", name: "Recruiting Triage Agent" },
    status: "running",
    trigger: "Event",
    startedAt: hoursAgo(0.2),
    duration: "12m",
    retryCount: 0,
    correlationId: "corr-run-0713-006",
    summary: "Classifying a fictional recruiting intake batch.",
    costEstimate: "$0.04 so far",
    approvalIds: ["apr-2026-008"],
    artifactIds: [],
    steps: steps("run-2026-07-13-006", "running"),
    logs: logs("run-2026-07-13-006", "running"),
  },
  {
    id: "run-2026-07-05-011",
    agent: { id: "agent-connectors-health", name: "Connector Health Sentinel" },
    status: "failed",
    trigger: "Scheduled",
    startedAt: hoursAgo(200),
    completedAt: hoursAgo(199.9),
    duration: "4m 08s",
    retryCount: 2,
    correlationId: "corr-run-0705-011",
    summary: "Could not prepare the governed connector evidence export.",
    costEstimate: "$0.03",
    error: {
      code: "EVIDENCE_PROVENANCE_INCOMPLETE",
      category: "Policy",
      retryable: false,
      summary:
        "Source checksum and original export are unavailable in the fixture.",
    },
    approvalIds: ["apr-2026-003"],
    artifactIds: ["art-2026-0705-011"],
    steps: steps("run-2026-07-05-011", "failed"),
    logs: logs("run-2026-07-05-011", "failed"),
  },
  {
    id: "run-2026-07-09-013",
    agent: { id: "agent-support-drafts", name: "Support Draft Agent" },
    status: "partially-succeeded",
    trigger: "Scheduled",
    startedAt: hoursAgo(120),
    completedAt: hoursAgo(119.8),
    duration: "11m 31s",
    retryCount: 1,
    correlationId: "corr-run-0709-013",
    summary:
      "Drafted nine responses; two items were routed for specialist review.",
    costEstimate: "$0.12",
    approvalIds: ["apr-2026-005"],
    artifactIds: ["art-2026-0709-013"],
    steps: steps("run-2026-07-09-013", "partially-succeeded"),
    logs: logs("run-2026-07-09-013", "partially-succeeded"),
  },
  {
    id: "run-2026-07-01-002",
    agent: { id: "agent-connectors-health", name: "Connector Health Sentinel" },
    status: "timed-out",
    trigger: "Manual",
    startedAt: hoursAgo(320),
    completedAt: hoursAgo(319.5),
    duration: "30m 00s",
    retryCount: 0,
    correlationId: "corr-run-0701-002",
    summary: "The fictional evidence packaging window elapsed.",
    costEstimate: "$0.09",
    error: {
      code: "RUN_TIMEOUT",
      category: "Timeout",
      retryable: true,
      summary: "The local fixture exceeded its declared display timeout.",
    },
    approvalIds: ["apr-2026-007"],
    artifactIds: [],
    steps: steps("run-2026-07-01-002", "timed-out"),
    logs: logs("run-2026-07-01-002", "timed-out"),
  },
];

export const RUN_STATUS_LABELS: Record<RunStatus, string> = {
  queued: "Queued",
  running: "Running",
  waiting: "Waiting for approval",
  succeeded: "Succeeded",
  "partially-succeeded": "Partially succeeded",
  failed: "Failed",
  cancelled: "Cancelled",
  "timed-out": "Timed out",
};

export function findRunById(id: string) {
  return RUN_FIXTURES.find((run) => run.id === id);
}
