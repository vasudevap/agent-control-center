export type AgentHealth = "healthy" | "degraded" | "offline";
export type RunStatus = "running" | "queued" | "healthy" | "offline";
export type ApprovalStatus = "pending" | "approved" | "rejected";
export type AlertSeverity = "critical" | "warning" | "information";

export interface FleetAgentRow {
  id: string;
  name: string;
  health: AgentHealth;
  status: string;
  lastRun: string;
  nextRun: string;
}

export interface ActiveRun {
  id: string;
  agentName: string;
  action: string;
  status: RunStatus;
  startedAt: string;
  duration: string;
}

export interface PendingApproval {
  id: string;
  agentName: string;
  action: string;
  requestedAt: string;
  risk: "low" | "medium" | "high";
  status: ApprovalStatus;
}

export interface AlertItem {
  id: string;
  severity: AlertSeverity;
  title: string;
  description: string;
  timestamp: string;
  source: string;
}

export interface ScheduleItem {
  id: string;
  agentName: string;
  task: string;
  time: string;
  cadence: string;
}
