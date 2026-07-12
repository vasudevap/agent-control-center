import { Bot, PlayCircle, HeartPulse, CheckSquare } from "lucide-react";
import { MetricCard } from "@/components/cards/metric-card";

export interface MetricsRowProps {
  metrics: {
    totalAgents: number;
    runningAgents: number;
    healthyAgents: number;
    pendingApprovals: number;
  };
  state?: "success" | "loading";
}

export function MetricsRow({ metrics, state = "success" }: MetricsRowProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard
        label="Total Agents"
        value={metrics.totalAgents}
        icon={Bot}
        tone="default"
        state={state}
        className="bg-surface-secondary"
      />
      <MetricCard
        label="Running Agents"
        value={metrics.runningAgents}
        icon={PlayCircle}
        tone="default"
        state={state}
        className="bg-surface-secondary"
      />
      <MetricCard
        label="Healthy Agents"
        value={metrics.healthyAgents}
        icon={HeartPulse}
        tone="success"
        state={state}
        className="bg-surface-secondary"
      />
      <MetricCard
        label="Pending Approvals"
        value={metrics.pendingApprovals}
        icon={CheckSquare}
        tone="warning"
        state={state}
        className="bg-surface-secondary"
      />
    </div>
  );
}
