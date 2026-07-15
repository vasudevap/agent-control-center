import type { BadgeProps } from "@/components/ui/badge";

const MINUTE = 60 * 1000;
const now = () => Date.now();
const minutesAgo = (m: number) => new Date(now() - m * MINUTE).toISOString();
const minutesFromNow = (m: number) => new Date(now() + m * MINUTE).toISOString();

export type AgentStatus = "running" | "active" | "paused" | "queued";
export type AgentHealth = "healthy" | "degraded" | "offline";

export interface AgentRecord {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  health: AgentHealth;
  owner: string;
  lastRun: string;
  lastRunAt: string;
  nextRun: string;
  nextRunAt?: string;
  version: string;
  currentIssue?: string;
  issueSummary?: string;
  responsibilities: string[];
  capabilities: string[];
  connectors: string[];
  permissions: string[];
  recentActivity: string[];
}

export const STATUS_LABELS: Record<AgentStatus, string> = {
  running: "Running",
  active: "Active",
  paused: "Paused",
  queued: "Queued",
};

export const HEALTH_LABELS: Record<AgentHealth, string> = {
  healthy: "Healthy",
  degraded: "Degraded",
  offline: "Offline",
};

export const STATUS_VARIANTS: Record<AgentStatus, BadgeProps["variant"]> = {
  running: "info",
  active: "success",
  paused: "neutral",
  queued: "warning",
};

export const HEALTH_VARIANTS: Record<AgentHealth, BadgeProps["variant"]> = {
  healthy: "success",
  degraded: "warning",
  offline: "error",
};

export const MOCK_AGENTS: AgentRecord[] = [
  {
    id: "agent-invoice-reconcile",
    name: "Invoice Reconciliation Agent",
    description: "Matches vendor invoices against approved purchase orders.",
    status: "running",
    health: "degraded",
    owner: "Finance Operations",
    lastRun: "8 minutes ago",
    lastRunAt: minutesAgo(8),
    nextRun: "In 22 minutes",
    nextRunAt: minutesFromNow(22),
    version: "v1.8.3",
    currentIssue: "Three invoices are waiting on policy review.",
    issueSummary: "Policy review needed",
    responsibilities: [
      "Compare submitted invoices with approved purchase order records.",
      "Flag policy exceptions before payment packages are prepared.",
      "Prepare reconciliation summaries for finance review owners.",
    ],
    capabilities: [
      "Invoice classification",
      "Purchase order matching",
      "Exception summarization",
      "Review packet drafting",
    ],
    connectors: ["Finance workspace", "Procurement records", "Approval queue"],
    permissions: ["Read invoice metadata", "Read purchase order records", "Draft review notes"],
    recentActivity: [
      "Matched 42 invoices in the current operating window.",
      "Escalated three exceptions to Finance Operations.",
      "Generated a reconciliation packet for review.",
    ],
  },
  {
    id: "agent-calendar-briefing",
    name: "Calendar Briefing Agent",
    description: "Prepares daily meeting briefs from schedule context.",
    status: "active",
    health: "healthy",
    owner: "Executive Operations",
    lastRun: "18 minutes ago",
    lastRunAt: minutesAgo(18),
    nextRun: "Tomorrow 6:00 AM",
    nextRunAt: minutesFromNow(840),
    version: "v2.1.0",
    responsibilities: [
      "Assemble meeting context for upcoming executive calendar events.",
      "Summarize relevant project notes into concise briefing cards.",
      "Highlight unresolved preparation items before the business day starts.",
    ],
    capabilities: ["Schedule analysis", "Brief generation", "Context summarization", "Preparation tracking"],
    connectors: ["Calendar workspace", "Project notes", "Briefing archive"],
    permissions: ["Read calendar metadata", "Read approved project notes", "Draft briefing summaries"],
    recentActivity: [
      "Prepared five meeting briefs for tomorrow morning.",
      "Detected one preparation gap for an upcoming steering review.",
      "Archived completed briefing notes for operator review.",
    ],
  },
  {
    id: "agent-connectors-health",
    name: "Connector Health Sentinel",
    description: "Checks connector freshness, latency, and failed handshakes.",
    status: "running",
    health: "healthy",
    owner: "Platform Reliability",
    lastRun: "2 minutes ago",
    lastRunAt: minutesAgo(2),
    nextRun: "In 13 minutes",
    nextRunAt: minutesFromNow(13),
    version: "v1.4.7",
    responsibilities: [
      "Monitor connector freshness across approved integration surfaces.",
      "Detect failed handshakes and unusual latency patterns.",
      "Summarize connector reliability signals for platform operators.",
    ],
    capabilities: ["Connector polling", "Latency trend detection", "Handshake failure grouping", "Reliability reporting"],
    connectors: ["Connector registry", "Health event stream", "Reliability dashboard"],
    permissions: ["Read connector status", "Read health events", "Draft reliability summaries"],
    recentActivity: [
      "Checked 18 connector health records.",
      "Confirmed all monitored connectors are within freshness thresholds.",
      "Prepared the next reliability snapshot.",
    ],
  },
  {
    id: "agent-policy-digest",
    name: "Policy Digest Agent",
    description: "Summarizes policy exceptions for review owners.",
    status: "paused",
    health: "offline",
    owner: "Governance Office",
    lastRun: "Yesterday 4:20 PM",
    lastRunAt: minutesAgo(1200),
    nextRun: "Not scheduled",
    version: "v0.9.5",
    currentIssue: "Paused after repeated evidence export failures.",
    issueSummary: "Export failures",
    responsibilities: [
      "Collect policy exception signals from approved governance sources.",
      "Summarize exception patterns for assigned review owners.",
      "Prepare evidence packets for governance follow-up.",
    ],
    capabilities: ["Policy exception grouping", "Evidence summarization", "Reviewer routing", "Digest preparation"],
    connectors: ["Policy register", "Evidence archive", "Governance review queue"],
    permissions: ["Read policy records", "Read evidence metadata", "Draft governance digests"],
    recentActivity: [
      "Paused after two failed evidence export attempts.",
      "Preserved the latest exception summary for review.",
      "Awaiting operator investigation before the next scheduled run.",
    ],
  },
  {
    id: "agent-recruiting-triage",
    name: "Recruiting Triage Agent",
    description: "Classifies candidate intake messages for recruiter review.",
    status: "queued",
    health: "degraded",
    owner: "Talent Operations",
    lastRun: "43 minutes ago",
    lastRunAt: minutesAgo(43),
    nextRun: "In 7 minutes",
    nextRunAt: minutesFromNow(7),
    version: "v1.2.2",
    responsibilities: [
      "Classify fictional candidate intake items into recruiter review buckets.",
      "Identify missing intake fields before recruiter follow-up.",
      "Prepare review summaries without making hiring decisions.",
    ],
    capabilities: ["Intake classification", "Missing-field detection", "Recruiter queue preparation", "Summary drafting"],
    connectors: ["Talent intake queue", "Role catalog", "Recruiter review board"],
    permissions: ["Read intake metadata", "Read role requirements", "Draft recruiter summaries"],
    recentActivity: [
      "Queued after detecting elevated intake volume.",
      "Classified 16 intake items in the previous run.",
      "Flagged four items with incomplete fictional profiles.",
    ],
  },
  {
    id: "agent-support-drafts",
    name: "Support Draft Agent",
    description: "Drafts support responses from approved knowledge articles.",
    status: "active",
    health: "healthy",
    owner: "Customer Operations",
    lastRun: "11 minutes ago",
    lastRunAt: minutesAgo(11),
    nextRun: "In 19 minutes",
    nextRunAt: minutesFromNow(19),
    version: "v3.0.1",
    responsibilities: [
      "Draft support responses from approved fictional knowledge articles.",
      "Route uncertain requests to human support specialists.",
      "Keep response drafts aligned with approved service language.",
    ],
    capabilities: ["Knowledge article retrieval", "Response drafting", "Escalation detection", "Tone alignment"],
    connectors: ["Support knowledge base", "Draft response queue", "Escalation tracker"],
    permissions: ["Read approved article metadata", "Draft support responses", "Read escalation categories"],
    recentActivity: [
      "Drafted nine support responses for specialist review.",
      "Escalated two requests that required human judgment.",
      "Confirmed all drafts used approved knowledge sources.",
    ],
  },
];

export function findAgentById(agentId: string) {
  return MOCK_AGENTS.find((agent) => agent.id === agentId);
}
