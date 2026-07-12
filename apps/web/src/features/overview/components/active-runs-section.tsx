import { Activity } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/badge/status-badge";
import { EmptyState } from "@/components/state/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { ActiveRun } from "../types/overview.types";

export interface ActiveRunsSectionProps {
  runs: ActiveRun[];
  state?: "success" | "loading" | "empty";
}

export function ActiveRunsSection({ runs, state = "success" }: ActiveRunsSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Active Runs</CardTitle>
        <CardDescription>Newest executions first</CardDescription>
      </CardHeader>

      {state === "loading" && (
        <CardContent className="flex flex-col gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full" />
          ))}
        </CardContent>
      )}

      {state === "empty" && (
        <EmptyState
          icon={Activity}
          title="No active runs"
          description="Runs will appear here as agents execute."
        />
      )}

      {state === "success" && (
        <CardContent>
          <ol className="flex flex-col">
            {runs.map((run, i) => (
              <li key={run.id} className="relative flex gap-4 pb-6 last:pb-0">
                {i !== runs.length - 1 && (
                  <span
                    aria-hidden="true"
                    className="absolute left-[7px] top-4 h-full w-px bg-border-default"
                  />
                )}
                <span
                  aria-hidden="true"
                  className={cn(
                    "relative mt-1.5 size-3.5 shrink-0 rounded-full border-2 border-surface",
                    run.status === "running" && "bg-info",
                    run.status === "queued" && "bg-foreground-tertiary",
                    run.status === "healthy" && "bg-success",
                    run.status === "offline" && "bg-error"
                  )}
                />
                <div className="flex min-w-0 flex-1 flex-col gap-1">
                  <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
                    <span className="text-sm font-medium text-foreground">{run.agentName}</span>
                    <StatusBadge status={run.status} />
                  </div>
                  <p className="text-xs text-foreground-secondary">{run.action}</p>
                  <div className="flex gap-3 font-mono text-[11px] text-foreground-tertiary">
                    <span>started {run.startedAt}</span>
                    <span>·</span>
                    <span>{run.duration}</span>
                  </div>
                </div>
              </li>
            ))}
          </ol>
        </CardContent>
      )}
    </Card>
  );
}
