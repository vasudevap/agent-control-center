import { Loader2, CircleDashed } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/state/empty-state";
import { cn } from "@/lib/utils";
import type { AgentRecord } from "@/app/(shell)/agents/agent-data";

const ACTION_BY_AGENT: Record<string, string> = {
  "agent-invoice-reconcile": "Matching invoices against approved purchase orders",
  "agent-calendar-briefing": "Assembling tomorrow's meeting briefs",
  "agent-connectors-health": "Polling connector freshness across integrations",
  "agent-recruiting-triage": "Classifying queued candidate intake items",
  "agent-support-drafts": "Drafting responses from approved knowledge articles",
  "agent-policy-digest": "Awaiting operator investigation",
};

/**
 * Derived from MOCK_AGENTS status, not a separate run-history fixture.
 * Run state (running/queued) and agent health are kept as two visibly
 * distinct badges here rather than one mixed status vocabulary, unlike
 * the baseline where a single status field mixed "queued" (a run
 * state) with "offline" (a health state) in the same badge.
 */
export function ActiveRunsSection({ agents }: { agents: AgentRecord[] }) {
  const active = agents.filter((agent) => agent.status === "running" || agent.status === "active" || agent.status === "queued");

  return (
    <Card>
      <CardHeader>
        <CardTitle>Active work</CardTitle>
        <CardDescription>Agents currently running or queued</CardDescription>
      </CardHeader>
      {active.length === 0 ? (
        <EmptyState icon={CircleDashed} title="No active work" description="No agents are currently running or queued." className="py-10" />
      ) : (
        <CardContent className="grid gap-2">
          {active.map((agent) => {
            const running = agent.status === "running" || agent.status === "active";
            return (
              <div key={agent.id} className="flex items-center gap-3 overflow-hidden rounded-atlas-sm border border-border-default bg-surface-secondary px-3 py-2.5">
                {running ? (
                  <Loader2 className="size-4 shrink-0 animate-spin text-brand" aria-hidden="true" />
                ) : (
                  <CircleDashed className="size-4 shrink-0 text-foreground-tertiary" aria-hidden="true" />
                )}
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">{agent.name}</p>
                  <p className="truncate text-xs text-foreground-secondary">{ACTION_BY_AGENT[agent.id] ?? agent.description}</p>
                </div>
                <span className={cn("shrink-0 rounded-atlas-sm px-2 py-0.5 text-[11px] font-medium", running ? "bg-brand-subtle text-brand" : "bg-surface-tertiary text-foreground-secondary")}>
                  {running ? "Running" : "Queued"}
                </span>
              </div>
            );
          })}
        </CardContent>
      )}
    </Card>
  );
}
