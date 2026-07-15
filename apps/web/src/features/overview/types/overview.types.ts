export type AlertSeverity = "critical" | "warning" | "information";

export interface AlertItem {
  id: string;
  severity: AlertSeverity;
  title: string;
  description: string;
  timestamp: string;
  source: string;
  sourceAgentId?: string;
}

export interface ScheduleItem {
  id: string;
  agentId: string;
  agentName: string;
  task: string;
  time: string;
  cadence: string;
}

export interface ActiveRun {
  id: string;
  agentId: string;
  agentName: string;
  action: string;
  runState: "running" | "queued";
  startedAt: string;
  duration: string;
}
