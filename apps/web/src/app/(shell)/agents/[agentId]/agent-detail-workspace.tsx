"use client";

import * as React from "react";
import Link from "next/link";
import { Bot, ChevronDown, ShieldCheck } from "lucide-react";
import type { AgentRecord } from "../agent-data";
import { StatusBadge } from "@/components/badge/status-badge";
import { RUN_FIXTURES } from "@/app/(shell)/runs/run-data";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState } from "@/components/state/error-state";
import { PageHeader } from "@/components/layout/page-header";
import { SignedOutState } from "@/components/state/signed-out-state";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  archiveDashboardAgent,
  dashboardApiBaseUrl,
  disconnectDashboardAgent,
  readDashboardAgents,
  readDashboardRuns,
  readDashboardSessionOrRequireSignIn,
  reconnectDashboardAgent,
  rotateDashboardAgentCredential,
  toAgentRecords,
  toRunRecords,
  type DashboardRuntimeMode,
} from "@/lib/dashboard-runtime";
import { CONTROL_CENTER_ROUTES, controlCenterExecutionHref } from "@/lib/control-center-routes";
import { cn } from "@/lib/utils";

type TabId = "activity" | "governance";
type LifecycleAction = "rotate" | "disconnect" | "reconnect" | "archive";

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

const LIFECYCLE_ACTIONS: Record<
  LifecycleAction,
  {
    label: string;
    confirm: string;
    success: string;
    variant: "secondary" | "destructive";
  }
> = {
  rotate: {
    label: "Rotate credential",
    confirm:
      "Rotate this agent credential? Atlas will issue a new one-time token and keep the previous token valid for exactly 24 hours.",
    success:
      "Credential rotated. Copy the new token now; Atlas will not show it again.",
    variant: "secondary",
  },
  disconnect: {
    label: "Disconnect",
    confirm:
      "Disconnect this agent from Atlas? Atlas will immediately revoke telemetry credentials. The external runtime may still be running outside Atlas.",
    success:
      "Agent disconnected. Credentials were revoked and telemetry is now rejected.",
    variant: "secondary",
  },
  reconnect: {
    label: "Reconnect",
    confirm:
      "Reconnect this agent? Atlas will issue a new one-time credential and wait for the next heartbeat before marking it connected.",
    success:
      "Agent reconnected. Copy the new token now; the agent remains pending until heartbeat.",
    variant: "secondary",
  },
  archive: {
    label: "Archive",
    confirm:
      "Archive this agent? Atlas will revoke credentials, hide it from default active views, and retain history. The external runtime may still exist outside Atlas.",
    success:
      "Agent archived. It is hidden from default active views and history is retained.",
    variant: "destructive",
  },
};

function lifecycleLabel(value?: string) {
  if (!value) return "Unknown";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
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
export function AgentDetailWorkspace({
  agent: initialAgent,
  requestedId,
  runtimeRequired = false,
}: {
  agent?: AgentRecord;
  requestedId?: string;
  runtimeRequired?: boolean;
}) {
  const [activeTab, setActiveTab] = React.useState<TabId>("activity");
  const [runtimeMode, setRuntimeMode] =
    React.useState<DashboardRuntimeMode>(() =>
      dashboardApiBaseUrl() ? "loading" : runtimeRequired ? "error" : "fixture",
    );
  const [liveAgent, setLiveAgent] = React.useState<AgentRecord | null>(null);
  const [liveRuns, setLiveRuns] = React.useState(RUN_FIXTURES);
  const [csrfToken, setCsrfToken] = React.useState("");
  const [lifecycleBusy, setLifecycleBusy] =
    React.useState<LifecycleAction | null>(null);
  const [lifecycleMessage, setLifecycleMessage] = React.useState("");
  const [lifecycleError, setLifecycleError] = React.useState("");
  const [lifecycleCredential, setLifecycleCredential] = React.useState<{
    plaintextToken: string;
    scope: string;
    credentialId: string;
  } | null>(null);
  const agentId = requestedId ?? initialAgent?.id ?? "";

  React.useEffect(() => {
    let cancelled = false;
    async function loadRuntime() {
      if (!agentId) return;
      if (!dashboardApiBaseUrl()) {
        setRuntimeMode(runtimeRequired ? "error" : "fixture");
        return;
      }
      setRuntimeMode("loading");
      try {
        const session = await readDashboardSessionOrRequireSignIn();
        const [runtimeAgents, runtimeRuns] = await Promise.all([
          readDashboardAgents(),
          readDashboardRuns(),
        ]);
        if (cancelled) return;
        setCsrfToken(session.csrf_token);
        const agents = toAgentRecords(runtimeAgents, runtimeRuns);
        setLiveAgent(agents.find((agent) => agent.id === agentId) ?? null);
        setLiveRuns(toRunRecords(runtimeRuns, runtimeAgents));
        setRuntimeMode("live");
      } catch (error) {
        if (cancelled) return;
        if (
          error instanceof Error &&
          "status" in error &&
          (error as { status: number }).status === 401
        ) {
          setRuntimeMode("unauthenticated");
        } else {
          setRuntimeMode("error");
        }
      }
    }
    void loadRuntime();
    return () => {
      cancelled = true;
    };
  }, [agentId, runtimeRequired]);

  const handleLifecycleAction = React.useCallback(
    async (action: LifecycleAction) => {
      if (!agentId || !csrfToken || lifecycleBusy) return;
      const config = LIFECYCLE_ACTIONS[action];
      if (!window.confirm(config.confirm)) return;

      setLifecycleBusy(action);
      setLifecycleMessage("");
      setLifecycleError("");
      setLifecycleCredential(null);
      try {
        const response =
          action === "rotate"
            ? await rotateDashboardAgentCredential(agentId, csrfToken)
            : action === "disconnect"
              ? await disconnectDashboardAgent(agentId, csrfToken)
              : action === "reconnect"
                ? await reconnectDashboardAgent(agentId, csrfToken)
                : await archiveDashboardAgent(agentId, csrfToken);
        const [updatedAgent] = toAgentRecords([response.agent]);
        setLiveAgent(updatedAgent ?? null);
        if (response.credential) {
          setLifecycleCredential({
            plaintextToken: response.credential.plaintext_token,
            scope: response.credential.scope,
            credentialId: response.credential.credential_id,
          });
        }
        setLifecycleMessage(config.success);
      } catch {
        setLifecycleError(
          "Lifecycle action failed. Refresh the live agent state and try again.",
        );
      } finally {
        setLifecycleBusy(null);
      }
    },
    [agentId, csrfToken, lifecycleBusy],
  );

  const agent = runtimeMode === "live" ? liveAgent : initialAgent;
  const runs = (runtimeMode === "live" ? liveRuns : RUN_FIXTURES)
    .filter((run) => run.agent.id === agentId)
    .slice(0, 3);

  const tabs: Array<{ id: TabId; label: string; count?: number }> = [
    { id: "activity", label: "Activity" },
    { id: "governance", label: "Governance" },
  ];

  if (runtimeMode === "loading") {
    return (
      <div className="flex flex-col gap-6">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (runtimeMode === "unauthenticated") {
    return <SignedOutState description="Sign in to load this agent from the Atlas API." />;
  }

  if (!agent || runtimeMode === "error") {
    return (
      <Card>
        <ErrorState
          title="Agent unavailable"
          description={
            runtimeRequired
              ? "This active control-center surface could not load a live agent record from the Atlas API."
              : "This agent could not be displayed."
          }
          className="py-12"
        />
      </Card>
    );
  }

  const lifecycleStatus = agent.lifecycleStatus ?? "unknown";
  const isDisconnected = lifecycleStatus === "disconnected";
  const isArchived = lifecycleStatus === "archived";

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Agent"
        title={agent.name}
        identifier={agent.id}
        icon={Bot}
        description={agent.description}
        actions={
          <Button asChild variant="ghost" size="sm" className="w-full justify-start sm:w-auto">
            <Link href={CONTROL_CENTER_ROUTES.agents}>Back to Agents</Link>
          </Button>
        }
      />

      {runtimeMode === "live" && (
        <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
          <strong>Live runtime.</strong> Agent identity, observed health, and
          execution history are loaded from owner-authenticated Atlas APIs.
        </div>
      )}

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
                <SidebarFact label="Observed" value={agent.observedHealth ?? "Fixture health"} />
                <SidebarFact label="Reported" value={agent.reportedHealth ?? "Fixture health"} />
                <SidebarFact label="Status" value={<StatusBadge status={agent.status} plain />} />
                <SidebarFact label="Lifecycle" value={lifecycleLabel(lifecycleStatus)} />
                <SidebarFact label="Owner" value={agent.owner} />
                <SidebarFact label="Environment" value={agent.environment ?? agent.owner} />
                <SidebarFact label="Version" value={agent.version} />
                <SidebarFact label="Build" value={agent.buildSha ?? "Unreported"} />
                <SidebarFact label="Last run" value={agent.lastRun} />
                <SidebarFact label="Next run" value={agent.nextRun} />
                <SidebarFact label="Change control" value="Approval required" />
              </dl>
              {agent.currentIssue && (
                <p className="mt-3 text-xs leading-relaxed text-warning">{agent.currentIssue}</p>
              )}
            </CardContent>
          </Card>

          {runtimeMode === "live" && (
            <Card>
              <CardHeader divided>
                <CardTitle>Lifecycle controls</CardTitle>
                <CardDescription>
                  Owner-authorized credential and visibility actions
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 pt-3 sm:pt-3">
                <p className="text-xs leading-relaxed text-foreground-secondary">
                  Atlas controls the enrolled identity and telemetry credential.
                  It does not start, stop, or delete external agent runtimes.
                </p>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    type="button"
                    variant={LIFECYCLE_ACTIONS.rotate.variant}
                    size="sm"
                    disabled={Boolean(lifecycleBusy) || isDisconnected || isArchived}
                    onClick={() => void handleLifecycleAction("rotate")}
                  >
                    {lifecycleBusy === "rotate" ? "Rotating…" : LIFECYCLE_ACTIONS.rotate.label}
                  </Button>
                  <Button
                    type="button"
                    variant={LIFECYCLE_ACTIONS.disconnect.variant}
                    size="sm"
                    disabled={Boolean(lifecycleBusy) || isDisconnected || isArchived}
                    onClick={() => void handleLifecycleAction("disconnect")}
                  >
                    {lifecycleBusy === "disconnect" ? "Disconnecting…" : LIFECYCLE_ACTIONS.disconnect.label}
                  </Button>
                  <Button
                    type="button"
                    variant={LIFECYCLE_ACTIONS.reconnect.variant}
                    size="sm"
                    disabled={Boolean(lifecycleBusy) || !isDisconnected}
                    onClick={() => void handleLifecycleAction("reconnect")}
                  >
                    {lifecycleBusy === "reconnect" ? "Reconnecting…" : LIFECYCLE_ACTIONS.reconnect.label}
                  </Button>
                  <Button
                    type="button"
                    variant={LIFECYCLE_ACTIONS.archive.variant}
                    size="sm"
                    disabled={Boolean(lifecycleBusy) || isArchived}
                    onClick={() => void handleLifecycleAction("archive")}
                  >
                    {lifecycleBusy === "archive" ? "Archiving…" : LIFECYCLE_ACTIONS.archive.label}
                  </Button>
                </div>
                {lifecycleMessage && (
                  <p className="rounded-atlas-sm border border-success-border bg-success-bg px-3 py-2 text-xs leading-relaxed text-success">
                    {lifecycleMessage}
                  </p>
                )}
                {lifecycleError && (
                  <p className="rounded-atlas-sm border border-error-border bg-error-bg px-3 py-2 text-xs leading-relaxed text-error">
                    {lifecycleError}
                  </p>
                )}
                {lifecycleCredential && (
                  <div className="grid gap-2 rounded-atlas-md border border-warning-border bg-warning-bg p-3">
                    <div>
                      <p className="font-mono text-[10px] font-semibold uppercase tracking-[0.08em] text-warning">
                        One-time credential
                      </p>
                      <p className="text-xs leading-relaxed text-foreground-secondary">
                        Copy this token into the external agent runtime now.
                        Atlas only displays it once.
                      </p>
                    </div>
                    <textarea
                      readOnly
                      rows={4}
                      value={lifecycleCredential.plaintextToken}
                      aria-label="One-time agent credential"
                      className="w-full resize-none rounded-atlas-sm border border-border-default bg-surface px-2 py-2 font-mono text-xs text-foreground"
                    />
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        void navigator.clipboard?.writeText(
                          lifecycleCredential.plaintextToken,
                        );
                      }}
                    >
                      Copy credential
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

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
                <p className="text-xs text-foreground-secondary">
                  {runtimeMode === "live"
                    ? "Recent owner-visible executions reported by this agent."
                    : "Recent fictional runs for investigation context."}
                </p>
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
                        <TableCell className="hidden text-xs text-foreground-secondary md:table-cell">
                          {runtimeMode === "live"
                            ? run.error?.code ?? "Reported summary only"
                            : run.artifactIds.length
                              ? `${run.artifactIds.length} artifact fixture`
                              : "No artifact fixture"}
                        </TableCell>
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
    </div>
  );
}
