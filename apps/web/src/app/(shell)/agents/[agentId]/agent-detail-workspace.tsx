"use client";

import * as React from "react";
import Link from "next/link";
import { ChevronDown, ShieldCheck } from "lucide-react";
import type { AgentRecord } from "../agent-data";
import { StatusBadge } from "@/components/badge/status-badge";
import { RUN_FIXTURES } from "@/app/(shell)/runs/run-data";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { controlCenterExecutionHref } from "@/lib/control-center-routes";
import { cn } from "@/lib/utils";

type TabId = "activity" | "governance";

function SidebarFact({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2 text-sm">
      <dt className="text-foreground-secondary">{label}</dt>
      <dd className="font-medium text-foreground">{value}</dd>
    </div>
  );
}

function SystemPromptDisclosure({ agent }: { agent: AgentRecord }) {
  const [open, setOpen] = React.useState(false);
  const prompt = [
    `# System prompt for ${agent.name}`,
    "SYSTEM_INSTRUCTIONS:",
    `You are ${agent.name}, a governed Atlas automation agent.`,
    "Operate only inside approved tools, connectors, permissions, and policy boundaries.",
    "",
    "PRIMARY_RESPONSIBILITIES:",
    ...agent.responsibilities.map((responsibility, index) => `${index + 1}. ${responsibility}`),
    "",
    "VALIDATION_RULES:",
    "1. Treat model output as untrusted until schema, policy, and confidence checks pass.",
    "2. Route uncertain or low-confidence results to human review.",
  ].join("\n");

  return (
    <div className="overflow-hidden rounded-atlas-md border border-border-default">
      <h2>
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          aria-expanded={open}
          className="flex w-full items-center justify-between gap-2 bg-surface-secondary px-4 py-3 text-left font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-foreground-secondary transition-colors hover:bg-surface-hover"
        >
          System prompt reference
          <ChevronDown className={cn("size-4 shrink-0 text-foreground-tertiary transition-transform", open && "rotate-180")} aria-hidden="true" />
        </button>
      </h2>
      {open && (
        <pre className="max-h-72 overflow-auto border-t border-border-default bg-surface-secondary p-4 font-mono text-xs leading-relaxed text-foreground-secondary">
          <code>{prompt}</code>
        </pre>
      )}
    </div>
  );
}

/**
 * Three deliberate departures from the baseline detail page:
 *
 * 1. No invented metric tiles ("Automation Confidence," "Operator
 *    Time Saved"). Those numbers had no defined source and read as
 *    dashboard decoration rather than operational fact. This version
 *    only shows facts already present in the agent record.
 * 2. "Agent System Prompt" is no longer a top-level tab. Exposing a
 *    raw system prompt as primary navigation reads like an AI-demo
 *    pattern the brand strategy explicitly warns against. The same
 *    content is still reachable, as a collapsed reference inside
 *    Governance, not billed as a primary feature.
 * 3. A right-rail "At a glance" fact panel echoes the same
 *    fact-panel-plus-investigation-tabs structure used on Approval
 *    Detail, so the two most important object-detail screens in
 *    Atlas share one layout language instead of two unrelated ones.
 */
export function AgentDetailWorkspace({ agent }: { agent: AgentRecord }) {
  const [activeTab, setActiveTab] = React.useState<TabId>("activity");
  const runs = RUN_FIXTURES.filter((run) => run.agent.id === agent.id).slice(0, 3);

  const tabs: Array<{ id: TabId; label: string; count?: number }> = [
    { id: "activity", label: "Activity" },
    { id: "governance", label: "Governance" },
  ];

  return (
    <div className="grid gap-6 xl:grid-cols-[22rem_minmax(0,1fr)]">
      <aside className="grid content-start gap-4">
        <div className="sticky top-[calc(var(--statusbar-height)+var(--topbar-height)+1rem)] grid content-start gap-4">
          <Card>
            <CardHeader divided>
              <CardTitle>At a glance</CardTitle>
              <CardDescription>Health, ownership, and schedule at a glance</CardDescription>
            </CardHeader>
            <CardContent className="pt-3 sm:pt-3">
              <dl className="divide-y divide-border-subtle">
                <SidebarFact label="Health" value={<StatusBadge status={agent.health} plain />} />
                <SidebarFact label="Status" value={<StatusBadge status={agent.status} plain />} />
                <SidebarFact label="Owner" value={agent.owner} />
                <SidebarFact label="Version" value={agent.version} />
                <SidebarFact label="Last run" value={agent.lastRun} />
                <SidebarFact label="Next run" value={agent.nextRun} />
                <SidebarFact label="Change control" value="Approval required" />
              </dl>
              {agent.currentIssue && (
                <p className="mt-3 text-xs leading-relaxed text-warning">{agent.currentIssue}</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader divided>
              <CardTitle>Capabilities</CardTitle>
              <CardDescription>What this agent is capable of doing</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-1.5 pt-3 sm:pt-3">
              {agent.capabilities.map((item) => (
                <Badge key={item} variant="neutral">{item}</Badge>
              ))}
            </CardContent>
          </Card>
        </div>
      </aside>

      <Card className="overflow-hidden">
        <div className="flex border-b border-border-default bg-surface-secondary">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              aria-current={activeTab === tab.id ? "true" : undefined}
              className={cn(
                "relative flex items-center gap-2 px-4 py-3 text-sm font-medium text-foreground-secondary transition-colors hover:text-foreground",
                activeTab === tab.id && "text-foreground"
              )}
            >
              {activeTab === tab.id && <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-brand" aria-hidden="true" />}
              {tab.label}
              {typeof tab.count === "number" && tab.count > 0 && (
                <span className="rounded-atlas-sm bg-warning-bg px-1.5 py-0.5 font-mono text-[10px] font-semibold text-warning">{tab.count}</span>
              )}
            </button>
          ))}
        </div>

        <CardContent className="p-4 sm:p-6">
          {activeTab === "activity" && (
            <div className="flex flex-col gap-4">
              <div>
                <h2 className="font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-foreground-secondary">Execution history</h2>
                <p className="text-xs text-foreground-secondary">Recent fictional runs for investigation context.</p>
              </div>
              <div className="overflow-hidden rounded-atlas-md border border-border-default">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Time</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="hidden sm:table-cell">Work</TableHead>
                      <TableHead className="hidden md:table-cell">Outcome</TableHead>
                      <TableHead>Duration</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {runs.map((run) => (
                      <TableRow key={run.id} className="relative">
                        <TableCell className="text-xs text-foreground-secondary"><Link href={controlCenterExecutionHref(run.id)} className="relative z-10 font-medium text-brand after:absolute after:inset-0 after:content-[''] hover:underline">{new Date(run.startedAt).toLocaleString()}</Link></TableCell>
                        <TableCell className="text-xs">
                          <StatusBadge status={run.status} plain className="text-xs" />
                        </TableCell>
                        <TableCell className="hidden max-w-xs truncate text-xs text-foreground-secondary sm:table-cell">{run.summary}</TableCell>
                        <TableCell className="hidden text-xs text-foreground-secondary md:table-cell">{run.artifactIds.length ? `${run.artifactIds.length} artifact fixture` : "No artifact fixture"}</TableCell>
                        <TableCell className="text-xs text-foreground-secondary">{run.duration}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}

          {activeTab === "governance" && (
            <div className="flex flex-col gap-5">
              <div>
                <h2 className="font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-foreground-secondary">Responsibilities</h2>
                <ul className="mt-2 grid gap-1.5 text-sm text-foreground-secondary">
                  {agent.responsibilities.map((item) => (
                    <li key={item} className="flex gap-2">
                      <span className="mt-2 size-1 shrink-0 rounded-full bg-foreground-tertiary" aria-hidden="true" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h2 className="font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-foreground-secondary">Permission boundary</h2>
                <ul className="mt-2 grid gap-1.5 text-sm text-foreground-secondary">
                  {agent.permissions.map((item) => (
                    <li key={item} className="flex gap-2">
                      <ShieldCheck className="mt-0.5 size-3.5 shrink-0 text-brand" aria-hidden="true" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h2 className="font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-foreground-secondary">Connectors</h2>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {agent.connectors.map((item) => (
                    <Badge key={item} variant="neutral">{item}</Badge>
                  ))}
                </div>
              </div>
              <SystemPromptDisclosure agent={agent} />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
