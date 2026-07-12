/**
 * Realistic mock data for the Overview Dashboard.
 * No backend contract exists yet — see BOUNDARIES.md. Shapes here are
 * design-owned placeholders for UI development only.
 */
import type {
  FleetAgentRow,
  ActiveRun,
  PendingApproval,
  AlertItem,
  ScheduleItem,
} from "../types/overview.types";

export const mockMetrics = {
  totalAgents: 42,
  runningAgents: 12,
  healthyAgents: 38,
  pendingApprovals: 3,
};

export const mockFleetHealth: FleetAgentRow[] = [
  {
    id: "agt-001",
    name: "Invoice Reconciler",
    health: "healthy",
    status: "Idle",
    lastRun: "12 min ago",
    nextRun: "in 48 min",
  },
  {
    id: "agt-002",
    name: "Support Triage",
    health: "healthy",
    status: "Running",
    lastRun: "2 min ago",
    nextRun: "Continuous",
  },
  {
    id: "agt-003",
    name: "Contract Extractor",
    health: "degraded",
    status: "Retrying",
    lastRun: "4 min ago",
    nextRun: "in 6 min",
  },
  {
    id: "agt-004",
    name: "Vendor Risk Scanner",
    health: "healthy",
    status: "Idle",
    lastRun: "1 hr ago",
    nextRun: "in 3 hr",
  },
  {
    id: "agt-005",
    name: "Payroll Auditor",
    health: "offline",
    status: "Stopped",
    lastRun: "6 hr ago",
    nextRun: "Paused",
  },
  {
    id: "agt-006",
    name: "Lead Enrichment",
    health: "healthy",
    status: "Running",
    lastRun: "just now",
    nextRun: "Continuous",
  },
  {
    id: "agt-007",
    name: "Compliance Monitor",
    health: "healthy",
    status: "Idle",
    lastRun: "34 min ago",
    nextRun: "in 26 min",
  },
];

export const mockActiveRuns: ActiveRun[] = [
  {
    id: "run-1042",
    agentName: "Support Triage",
    action: "Classifying inbound ticket #8841",
    status: "running",
    startedAt: "17:41:02",
    duration: "00:02:14",
  },
  {
    id: "run-1041",
    agentName: "Lead Enrichment",
    action: "Enriching 240 contacts from Q3 import",
    status: "running",
    startedAt: "17:38:55",
    duration: "00:04:21",
  },
  {
    id: "run-1040",
    agentName: "Contract Extractor",
    action: "Retrying clause extraction on MSA-2291",
    status: "queued",
    startedAt: "17:36:10",
    duration: "00:06:52",
  },
  {
    id: "run-1039",
    agentName: "Invoice Reconciler",
    action: "Matched 128/130 line items",
    status: "healthy",
    startedAt: "17:29:47",
    duration: "00:03:08",
  },
  {
    id: "run-1038",
    agentName: "Payroll Auditor",
    action: "Run halted — connector auth expired",
    status: "offline",
    startedAt: "11:52:00",
    duration: "00:00:41",
  },
];

export const mockPendingApprovals: PendingApproval[] = [
  {
    id: "apr-501",
    agentName: "Payroll Auditor",
    action: "Issue off-cycle payment of $4,220.00 to vendor #2291",
    requestedAt: "18 min ago",
    risk: "high",
    status: "pending",
  },
  {
    id: "apr-502",
    agentName: "Contract Extractor",
    action: "Send extracted terms to Legal review queue",
    requestedAt: "41 min ago",
    risk: "low",
    status: "pending",
  },
  {
    id: "apr-503",
    agentName: "Vendor Risk Scanner",
    action: "Suspend vendor account #1187 pending review",
    requestedAt: "1 hr ago",
    risk: "medium",
    status: "pending",
  },
];

export const mockAlerts: AlertItem[] = [
  {
    id: "alt-901",
    severity: "critical",
    title: "Connector authentication expired",
    description: "Payroll Auditor lost access to the ADP connector. Runs are paused.",
    timestamp: "6 hr ago",
    source: "Payroll Auditor",
  },
  {
    id: "alt-902",
    severity: "warning",
    title: "Elevated retry rate",
    description: "Contract Extractor has retried 4 times in the last 10 minutes.",
    timestamp: "4 min ago",
    source: "Contract Extractor",
  },
  {
    id: "alt-903",
    severity: "information",
    title: "Policy updated",
    description: "\"Financial transactions over $1,000\" policy now requires dual approval.",
    timestamp: "2 hr ago",
    source: "Policies",
  },
];

export const mockSchedule: ScheduleItem[] = [
  {
    id: "sch-1",
    agentName: "Compliance Monitor",
    task: "Nightly SOC 2 evidence sweep",
    time: "Today, 22:00",
    cadence: "Daily",
  },
  {
    id: "sch-2",
    agentName: "Invoice Reconciler",
    task: "Reconcile Q3 close batch",
    time: "Today, 23:30",
    cadence: "Weekly",
  },
  {
    id: "sch-3",
    agentName: "Vendor Risk Scanner",
    task: "Re-score vendor risk tiers",
    time: "Tomorrow, 06:00",
    cadence: "Weekly",
  },
  {
    id: "sch-4",
    agentName: "Lead Enrichment",
    task: "Import + enrich new CRM leads",
    time: "Tomorrow, 08:00",
    cadence: "Daily",
  },
];
