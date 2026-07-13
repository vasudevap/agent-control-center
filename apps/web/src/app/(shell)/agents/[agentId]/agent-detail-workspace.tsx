"use client";

import * as React from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowDown,
  Banknote,
  Bot,
  CheckCircle2,
  FileText,
  Mail,
  Play,
  ShieldCheck,
  Sheet,
  SlidersHorizontal,
} from "lucide-react";
import {
  HEALTH_LABELS,
  HEALTH_VARIANTS,
  STATUS_LABELS,
  STATUS_VARIANTS,
  type AgentRecord,
} from "../agent-data";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

type TabId = "activity" | "approvals" | "prompt";

interface MetricCard {
  label: string;
  value: string;
  note: string;
  tone: "info" | "success" | "warning" | "error";
}

interface RunRecord {
  time: string;
  status: "Success" | "Action Required" | "Failed";
  work: string;
  outcome: string;
  duration: string;
}

const toneStyles: Record<MetricCard["tone"], { icon: React.ElementType; className: string }> = {
  info: {
    icon: FileText,
    className: "bg-info-bg text-info border-info-border",
  },
  success: {
    icon: CheckCircle2,
    className: "bg-success-bg text-success border-success-border",
  },
  warning: {
    icon: Banknote,
    className: "bg-warning-bg text-warning border-warning-border",
  },
  error: {
    icon: AlertTriangle,
    className: "bg-error-bg text-error border-error-border",
  },
};

function getDetailProfile(agent: AgentRecord) {
  const hasIssue = Boolean(agent.currentIssue);

  return {
    tags: agent.capabilities.slice(0, 4),
    metrics: [
      {
        label: "Runs Completed",
        value: agent.status === "paused" ? "18" : "42",
        note: agent.status === "running" ? "Active monitoring window" : "Last 30 days",
        tone: "info" as const,
      },
      {
        label: "Automation Confidence",
        value: agent.health === "healthy" ? "99.2%" : "84.0%",
        note: agent.health === "healthy" ? "Within approved threshold" : "Below preferred threshold",
        tone: agent.health === "healthy" ? ("success" as const) : ("warning" as const),
      },
      {
        label: "Operator Time Saved",
        value: agent.health === "offline" ? "Pending" : "6.4 hrs",
        note: agent.health === "offline" ? "Paused until investigation" : "Estimated this week",
        tone: "warning" as const,
      },
      {
        label: "Approvals Required",
        value: hasIssue ? "3" : "0",
        note: hasIssue ? agent.issueSummary ?? "Needs review" : "No pending approvals",
        tone: hasIssue ? ("error" as const) : ("success" as const),
      },
    ],
    flow: [
      { name: agent.connectors[0] ?? "Source workspace", meta: "Trigger: approved source scan", icon: Mail },
      { name: agent.name, meta: `Model policy: ${agent.version}`, icon: Bot },
      { name: agent.connectors[1] ?? "Review workspace", meta: "Destination: operator review queue", icon: Sheet },
      { name: agent.connectors[2] ?? "Audit archive", meta: "Evidence: governed activity record", icon: ShieldCheck },
    ],
    config: [
      { label: "Review confidence threshold", value: agent.health === "healthy" ? "90%" : "85%" },
      { label: "Schedule", value: agent.nextRun },
      { label: "Owner queue", value: agent.owner },
      { label: "Technical agent ID", value: agent.id },
    ],
    runs: [
      {
        time: "Jul 12, 2026, 09:00 AM",
        status: hasIssue ? ("Action Required" as const) : ("Success" as const),
        work: hasIssue ? "3 items reviewed" : "8 items reviewed",
        outcome: hasIssue ? "Queued for operator review" : "Completed within policy",
        duration: "24.2s",
      },
      {
        time: "Jul 10, 2026, 11:24 AM",
        status: "Success" as const,
        work: "5 items reviewed",
        outcome: "No exceptions detected",
        duration: "18.6s",
      },
      {
        time: "Jul 05, 2026, 09:00 AM",
        status: agent.health === "offline" ? ("Failed" as const) : ("Success" as const),
        work: agent.health === "offline" ? "0 items reviewed" : "12 items reviewed",
        outcome: agent.health === "offline" ? "Connector export failed" : "Evidence archived",
        duration: agent.health === "offline" ? "4.1s" : "38.1s",
      },
    ],
    approvals: hasIssue
      ? [
          {
            approvalId: agent.id === "agent-beta" ? "apr-2026-001" : undefined,
            title: agent.issueSummary ?? "Operator review required",
            confidence: "84%",
            reason: agent.currentIssue ?? "Confidence was below the approved threshold.",
            received: "Jul 12, 2026",
          },
          {
            approvalId: agent.id === "agent-beta" ? "apr-2026-002" : undefined,
            title: "Policy exception confirmation",
            confidence: "78%",
            reason: "The agent found an ambiguous category and needs a human decision.",
            received: "Jul 10, 2026",
          },
          {
            approvalId: agent.id === "agent-gamma" ? "apr-2026-003" : undefined,
            title: "Evidence packet review",
            confidence: "89%",
            reason: "The generated summary should be checked before audit archive.",
            received: "Jul 10, 2026",
          },
        ]
      : [],
    prompt: [
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
      "3. Never expose secrets, credentials, private account identifiers, or raw personal data.",
      "4. Record material actions as auditable events before presenting completion.",
    ].join("\n"),
  };
}

function MetricTile({ metric }: { metric: MetricCard }) {
  const Icon = toneStyles[metric.tone].icon;

  return (
    <Card className="min-w-0 overflow-hidden border-border-default bg-surface shadow-atlas-sm">
      <CardContent className="flex min-w-0 flex-col gap-4 p-5 pt-5 sm:p-5 sm:pt-5">
        <div className="flex items-start justify-between gap-4">
          <p className="min-w-0 text-sm leading-snug text-foreground-secondary">{metric.label}</p>
          <span className={cn("rounded-atlas-md border p-2", toneStyles[metric.tone].className)}>
            <Icon className="size-4" aria-hidden="true" />
          </span>
        </div>
        <div className="min-w-0">
          <p className={cn("break-words text-2xl font-semibold tracking-tight text-foreground sm:text-3xl xl:text-2xl 2xl:text-3xl", metric.tone === "error" && "text-error")}>
            {metric.value}
          </p>
          <p className="mt-2 text-xs leading-relaxed text-foreground-secondary">{metric.note}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function StatusPill({ label, variant }: { label: string; variant: BadgeProps["variant"] }) {
  return <Badge variant={variant}>{label}</Badge>;
}

function SidebarCard({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function DataFlow({ flow }: { flow: ReturnType<typeof getDetailProfile>["flow"] }) {
  return (
    <div className="flex flex-col gap-2">
      {flow.map((step, index) => {
        const Icon = step.icon;

        return (
          <React.Fragment key={step.name}>
            <div className="flex items-center gap-3 rounded-atlas-md border border-border-default bg-surface-secondary p-3">
              <span className="flex size-9 shrink-0 items-center justify-center rounded-atlas-md bg-surface text-brand shadow-atlas-sm">
                <Icon className="size-4" aria-hidden="true" />
              </span>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-foreground">{step.name}</p>
                <p className="truncate text-xs text-foreground-secondary">{step.meta}</p>
              </div>
            </div>
            {index < flow.length - 1 && (
              <div className="flex justify-center text-foreground-tertiary">
                <ArrowDown className="size-4" aria-hidden="true" />
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

function RunsTable({ runs }: { runs: RunRecord[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Execution Time</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Work</TableHead>
          <TableHead>Outcome</TableHead>
          <TableHead>Duration</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {runs.map((run) => (
          <TableRow key={`${run.time}-${run.status}`}>
            <TableCell className="font-medium">{run.time}</TableCell>
            <TableCell>
              <Badge
                variant={
                  run.status === "Success"
                    ? "success"
                    : run.status === "Failed"
                      ? "error"
                      : "warning"
                }
              >
                {run.status}
              </Badge>
            </TableCell>
            <TableCell className="text-foreground-secondary">{run.work}</TableCell>
            <TableCell className="text-foreground-secondary">{run.outcome}</TableCell>
            <TableCell className="text-foreground-secondary">{run.duration}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function AgentDetailWorkspace({ agent }: { agent: AgentRecord }) {
  const [activeTab, setActiveTab] = React.useState<TabId>("activity");
  const profile = getDetailProfile(agent);

  const tabs: Array<{ id: TabId; label: string; count?: number }> = [
    { id: "activity", label: "Activity & History" },
    { id: "approvals", label: "Human Approvals", count: profile.approvals.length },
    { id: "prompt", label: "Agent System Prompt" },
  ];

  return (
    <div className="flex flex-col gap-7">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" aria-label="Agent operating metrics">
        {profile.metrics.map((metric) => (
          <MetricTile key={metric.label} metric={metric} />
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[22rem_minmax(0,1fr)]">
        <aside className="flex flex-col gap-4">
          <SidebarCard title="Agent Description">
            <div className="flex flex-col gap-4">
              <p className="text-sm leading-relaxed text-foreground-secondary">{agent.description}</p>
              <div className="flex flex-wrap gap-2">
                {profile.tags.map((tag) => (
                  <Badge key={tag} variant="neutral">{tag}</Badge>
                ))}
              </div>
            </div>
          </SidebarCard>

          <SidebarCard title="Integration & Data Flow" description="Read-only view of the approved operating path.">
            <DataFlow flow={profile.flow} />
          </SidebarCard>

          <SidebarCard title="Effective Configuration" description="Read-only snapshot from the approved agent registry.">
            <div className="mb-4 rounded-atlas-md border border-border-default bg-surface-secondary px-3 py-2">
              <div className="flex items-center justify-between gap-3 text-xs">
                <span className="font-medium uppercase tracking-wide text-foreground-tertiary">Version</span>
                <span className="font-semibold text-foreground">{agent.version}</span>
              </div>
              <div className="mt-2 flex items-center justify-between gap-3 text-xs">
                <span className="font-medium uppercase tracking-wide text-foreground-tertiary">Change control</span>
                <span className="font-semibold text-foreground">Approval required</span>
              </div>
            </div>
            <dl className="divide-y divide-border-default border-y border-border-default">
              {profile.config.map((item) => (
                <div key={item.label} className="grid gap-1 py-3">
                  <dt className="text-[11px] font-semibold uppercase tracking-wide text-foreground-tertiary">{item.label}</dt>
                  <dd className="text-sm font-medium leading-relaxed text-foreground">{item.value}</dd>
                </div>
              ))}
            </dl>
          </SidebarCard>
        </aside>

        <Card className="overflow-hidden border-border-strong shadow-atlas-md">
          <div className="flex flex-col border-b border-border-default bg-surface-secondary sm:flex-row">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center justify-center gap-2 border-b-2 border-transparent px-5 py-4 text-sm font-medium text-foreground-secondary transition-colors hover:text-foreground",
                  activeTab === tab.id && "border-brand text-brand"
                )}
              >
                {tab.label}
                {typeof tab.count === "number" && tab.count > 0 && (
                  <span className="rounded-full bg-error-bg px-1.5 py-0.5 text-[10px] font-semibold text-error">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          <CardContent className="p-5 sm:p-7">
            {activeTab === "activity" && (
              <div className="flex flex-col gap-5">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-foreground">Execution History</h2>
                    <p className="text-sm text-foreground-secondary">
                      Showing recent fictional runs for investigation context.
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <StatusPill label={STATUS_LABELS[agent.status]} variant={STATUS_VARIANTS[agent.status]} />
                    <StatusPill label={HEALTH_LABELS[agent.health]} variant={HEALTH_VARIANTS[agent.health]} />
                  </div>
                </div>
                <div className="overflow-hidden rounded-atlas-lg border border-border-default">
                  <RunsTable runs={profile.runs} />
                </div>
                <div className="rounded-atlas-lg border border-border-default bg-surface-secondary p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                    <Play className="size-4 text-brand" aria-hidden="true" />
                    Future operation controls
                  </div>
                  <p className="mt-2 text-sm leading-relaxed text-foreground-secondary">
                    Run, pause, and resume controls are available in the page header as a frontend prototype. Runtime execution, approval, and rejection remain read-only in this milestone.
                    This page documents operational state without authorizing actions.
                  </p>
                </div>
              </div>
            )}

            {activeTab === "approvals" && (
              <div className="flex flex-col gap-5">
                <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_minmax(16rem,0.8fr)]">
                  <div>
                    <h2 className="text-lg font-semibold text-foreground">Pending Human Review</h2>
                    <p className="text-sm text-foreground-secondary">
                      Items appear here when confidence, policy, or evidence thresholds require operator judgment.
                    </p>
                  </div>
                  <p className="text-sm leading-relaxed text-foreground-secondary">
                    These cards are read-only. Approval and rejection workflows will require a separate governed action work order.
                  </p>
                </div>

                {profile.approvals.length > 0 ? (
                  <div className="grid gap-4 lg:grid-cols-2">
                    {profile.approvals.map((approval) => (
                      <div key={approval.title} className="rounded-atlas-lg border border-border-default bg-surface-secondary p-4">
                        <div className="flex items-start justify-between gap-3">
                          <Badge variant="warning">Confidence: {approval.confidence}</Badge>
                          <span className="text-xs text-foreground-tertiary">{approval.received}</span>
                        </div>
                        {approval.approvalId ? (
                          <Link href={`/approvals/${approval.approvalId}`} className="mt-4 block text-sm font-semibold text-foreground hover:text-brand hover:underline">
                            {approval.title}
                          </Link>
                        ) : <h3 className="mt-4 text-sm font-semibold text-foreground">{approval.title}</h3>}
                        <p className="mt-2 text-sm leading-relaxed text-foreground-secondary">{approval.reason}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="rounded-atlas-lg border border-success-border bg-success-bg p-5 text-sm text-success">
                    No human approvals are pending for this agent.
                  </div>
                )}
              </div>
            )}

            {activeTab === "prompt" && (
              <div className="flex flex-col gap-5">
                <div>
                  <h2 className="text-lg font-semibold text-foreground">System Prompt & Instructions</h2>
                  <p className="text-sm text-foreground-secondary">
                    Defines the governed identity, boundaries, and review rules for this mock agent.
                  </p>
                </div>
                <pre className="max-h-[28rem] overflow-auto rounded-atlas-lg border border-border-default bg-surface-secondary p-5 font-mono text-xs leading-relaxed text-foreground-secondary">
                  <code>{profile.prompt}</code>
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-3">
        <SidebarCard title="Responsibilities" description="What this agent is expected to do.">
          <ul className="grid gap-2">
            {agent.responsibilities.map((item) => (
              <li key={item} className="text-sm leading-relaxed text-foreground-secondary">{item}</li>
            ))}
          </ul>
        </SidebarCard>

        <SidebarCard title="Capabilities" description="Approved functional abilities.">
          <div className="flex flex-wrap gap-2">
            {agent.capabilities.map((item) => (
              <Badge key={item} variant="brand">{item}</Badge>
            ))}
          </div>
        </SidebarCard>

        <SidebarCard title="Permission Boundary" description="What the agent may access in this mock screen.">
          <div className="flex flex-col gap-3">
            {agent.permissions.map((item) => (
              <div key={item} className="flex items-start gap-2 text-sm text-foreground-secondary">
                <SlidersHorizontal className="mt-0.5 size-4 shrink-0 text-brand" aria-hidden="true" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </SidebarCard>
      </section>
    </div>
  );
}
