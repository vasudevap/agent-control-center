"use client";

import * as React from "react";
import Link from "next/link";
import { Bot, CircleOff, FilterX } from "lucide-react";
import {
  dashboardApiBaseUrl,
  enrollDashboardAgent,
  readDashboardAgents,
  readDashboardRuns,
  readDashboardSessionOrRequireSignIn,
  toAgentRecords,
  type DashboardEnrollmentResponse,
  type DashboardRuntimeMode,
} from "@/lib/dashboard-runtime";
import { controlCenterAgentHref } from "@/lib/control-center-routes";
import {
  HEALTH_LABELS,
  MOCK_AGENTS,
  STATUS_LABELS,
  type AgentHealth,
  type AgentRecord,
  type AgentStatus,
} from "./agent-data";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
import { StatusBadge } from "@/components/badge/status-badge";
import { ErrorState } from "@/components/state/error-state";
import { SignedOutState } from "@/components/state/signed-out-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import { Skeleton } from "@/components/ui/skeleton";
import { getAriaSort, SortHeader, type SortDirection } from "@/components/ui/sort-header";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export type { AgentRecord } from "./agent-data";

type InventoryState = "loaded" | "loading" | "error";
type SortKey = "attention" | "health" | "agent" | "status" | "owner" | "lastRun" | "nextRun";

interface AgentsInventoryProps {
  agents?: AgentRecord[];
  state?: InventoryState;
  runtimeRequired?: boolean;
}

// Ascending severity, mirroring risk's Low-to-Critical convention in Approvals.
const HEALTH_RANK: Record<AgentHealth, number> = { healthy: 0, degraded: 1, offline: 2 };
// Stable lifecycle ordering for status sorts.
const STATUS_RANK: Record<AgentStatus, number> = { running: 0, active: 1, paused: 2, queued: 3 };

function getAttentionRank(agent: AgentRecord) {
  if (agent.currentIssue) return 0;
  if (agent.health === "degraded" || agent.health === "offline") return 1;
  if (agent.status === "running") return 2;
  return 3;
}

function filterAgents(agents: AgentRecord[], query: string, status: AgentStatus | "all", health: AgentHealth | "all") {
  const q = query.trim().toLowerCase();
  return agents.filter((agent) => {
    const matchesQuery = !q || agent.name.toLowerCase().includes(q) || agent.description.toLowerCase().includes(q) || agent.id.toLowerCase().includes(q);
    return matchesQuery && (status === "all" || agent.status === status) && (health === "all" || agent.health === health);
  });
}

function sortAgents(agents: AgentRecord[], sort: SortKey, direction: SortDirection) {
  const dirMul = direction === "asc" ? 1 : -1;
  return [...agents].sort((a, b) => {
    if (sort === "health") return (HEALTH_RANK[a.health] - HEALTH_RANK[b.health]) * dirMul || a.name.localeCompare(b.name);
    if (sort === "agent") return a.name.localeCompare(b.name) * dirMul;
    if (sort === "status") return (STATUS_RANK[a.status] - STATUS_RANK[b.status]) * dirMul || a.name.localeCompare(b.name);
    if (sort === "owner") return a.owner.localeCompare(b.owner) * dirMul || a.name.localeCompare(b.name);
    if (sort === "lastRun") return (+new Date(a.lastRunAt) - +new Date(b.lastRunAt)) * dirMul;
    if (sort === "nextRun") return (+new Date(a.nextRunAt ?? "9999-01-01") - +new Date(b.nextRunAt ?? "9999-01-01")) * dirMul;
    return (getAttentionRank(a) - getAttentionRank(b) || a.name.localeCompare(b.name)) * dirMul;
  });
}

function FieldPair({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="font-mono text-[10px] font-medium uppercase tracking-wider text-foreground-tertiary">{label}</dt>
      <dd className="text-sm text-foreground">{value}</dd>
    </div>
  );
}

function AgentIdentity({ agent }: { agent: AgentRecord }) {
  const issueLabel = agent.issueSummary ?? agent.currentIssue;
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <Link href={controlCenterAgentHref(agent.id)} className="relative z-10 w-fit font-medium text-foreground underline-offset-4 after:absolute after:inset-0 after:content-[''] hover:text-brand hover:underline">
        {agent.name}
      </Link>
      <p className="max-w-md truncate text-xs text-foreground-secondary">{agent.description}</p>
      {issueLabel && (
        // No icon here: the leading Health column already carries
        // "something needs a look" via AlertTriangle for Degraded. A
        // second AlertTriangle on this line would visually claim to be
        // that same signal when it's actually just explaining why —
        // the color alone (already an established, not sole, channel
        // elsewhere) is enough supporting context for a caption line.
        <p className="truncate text-xs text-warning">{issueLabel}</p>
      )}
    </div>
  );
}

function AgentsTable({ agents, sort, direction, onSort }: { agents: AgentRecord[]; sort: SortKey; direction: SortDirection; onSort: (key: SortKey) => void }) {
  return (
    <Card className="hidden overflow-hidden md:block">
      <Table>
        <caption className="sr-only">Agents inventory</caption>
        <TableHeader>
          <TableRow>
            <TableHead aria-sort={getAriaSort(sort === "health", direction)}><SortHeader label="Health" sortKey="health" active={sort === "health"} direction={direction} onSort={onSort} /></TableHead>
            <TableHead aria-sort={getAriaSort(sort === "agent", direction)}><SortHeader label="Agent" sortKey="agent" active={sort === "agent"} direction={direction} onSort={onSort} /></TableHead>
            <TableHead aria-sort={getAriaSort(sort === "status", direction)}><SortHeader label="Status" sortKey="status" active={sort === "status"} direction={direction} onSort={onSort} /></TableHead>
            <TableHead aria-sort={getAriaSort(sort === "owner", direction)} className="hidden lg:table-cell"><SortHeader label="Owner" sortKey="owner" active={sort === "owner"} direction={direction} onSort={onSort} /></TableHead>
            <TableHead aria-sort={getAriaSort(sort === "lastRun", direction)}><SortHeader label="Last run" sortKey="lastRun" active={sort === "lastRun"} direction={direction} onSort={onSort} /></TableHead>
            <TableHead aria-sort={getAriaSort(sort === "nextRun", direction)}><SortHeader label="Next run" sortKey="nextRun" active={sort === "nextRun"} direction={direction} onSort={onSort} /></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id} className="relative">
              <TableCell className="py-2.5 text-xs"><StatusBadge status={agent.health} plain /></TableCell>
              <TableCell className="min-w-[18rem] py-2.5"><AgentIdentity agent={agent} /></TableCell>
              <TableCell className="py-2.5 text-xs"><StatusBadge status={agent.status} plain /></TableCell>
              <TableCell className="hidden py-2.5 text-xs text-foreground-secondary lg:table-cell">{agent.owner}</TableCell>
              <TableCell className="py-2.5 text-xs text-foreground-secondary">{agent.lastRun}</TableCell>
              <TableCell className="py-2.5 text-xs text-foreground-secondary">{agent.nextRun}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}

function MobileAgentsList({ agents }: { agents: AgentRecord[] }) {
  return (
    <div className="grid gap-2.5 md:hidden" aria-label="Agents inventory summaries">
      {agents.map((agent) => (
        <Link key={agent.id} href={controlCenterAgentHref(agent.id)} className="block rounded-atlas-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring" aria-label={`${agent.name} details`}>
          <Card className="transition-colors hover:bg-surface-hover">
            <CardContent className="flex flex-col gap-3 p-4">
              <h2 className="flex items-center gap-2 text-sm font-semibold text-foreground">
                <StatusBadge status={agent.health} plain />
                {agent.name}
              </h2>
              <dl className="grid grid-cols-2 gap-3">
                <FieldPair label="Status" value={<StatusBadge status={agent.status} />} />
                <FieldPair label="Last run" value={agent.lastRun} />
                <FieldPair label="Next run" value={agent.nextRun} />
              </dl>
              {(agent.issueSummary ?? agent.currentIssue) && (
                <div className="rounded-atlas-sm border border-warning-border bg-warning-bg px-3 py-2 text-xs leading-relaxed text-warning">
                  {agent.issueSummary ?? agent.currentIssue}
                </div>
              )}
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}

function InventorySkeleton() {
  return (
    <div className="flex flex-col gap-4" aria-label="Loading agents inventory">
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_12rem_12rem_auto]">
        <Skeleton className="h-9" /><Skeleton className="h-9" /><Skeleton className="h-9" /><Skeleton className="h-9" />
      </div>
      <Card className="hidden p-4 md:block">
        <div className="flex flex-col gap-3">
          {Array.from({ length: 5 }).map((_, index) => <Skeleton key={index} className="h-12" />)}
        </div>
      </Card>
    </div>
  );
}

function EnrollmentPanel({
  csrfToken,
  onEnrolled,
}: {
  csrfToken: string;
  onEnrolled: (agent: AgentRecord) => void;
}) {
  const [slug, setSlug] = React.useState("");
  const [displayName, setDisplayName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [environment, setEnvironment] = React.useState("production");
  const [monitoringMode, setMonitoringMode] =
    React.useState<"heartbeat" | "activity_only">("heartbeat");
  const [heartbeatInterval, setHeartbeatInterval] = React.useState("300");
  const [expectedVersion, setExpectedVersion] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [credential, setCredential] =
    React.useState<DashboardEnrollmentResponse["credential"] | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage(null);
    try {
      const response = await enrollDashboardAgent(
        {
          slug: slug.trim(),
          display_name: displayName.trim(),
          description: description.trim(),
          environment: environment.trim() || "production",
          monitoring_mode: monitoringMode,
          heartbeat_interval_seconds:
            monitoringMode === "heartbeat"
              ? Number(heartbeatInterval) || 300
              : null,
          expected_version: expectedVersion.trim() || null,
        },
        csrfToken,
      );
      setCredential(response.credential);
      const [agentRecord] = toAgentRecords([response.agent]);
      if (agentRecord) onEnrolled(agentRecord);
      setSlug("");
      setDisplayName("");
      setDescription("");
      setExpectedVersion("");
      setMessage("Agent enrolled. Copy the credential token now; Atlas will not show it again.");
    } catch {
      setMessage("Enrollment failed. Check the fields and try again with a fresh owner session.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardContent className="grid gap-4 p-4 sm:p-5">
        <div>
          <h2 className="text-sm font-semibold text-foreground">Enroll external agent</h2>
          <p className="mt-1 text-xs text-foreground-secondary">
            Register an owner-visible agent and issue its one-time Atlas credential.
          </p>
        </div>
        <form className="grid gap-3 lg:grid-cols-2" onSubmit={submit}>
          <label className="grid gap-1 text-xs font-medium text-foreground-secondary">
            Slug
            <input
              required
              value={slug}
              onChange={(event) => setSlug(event.target.value)}
              placeholder="daily-briefing-agent"
              className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none focus:border-brand"
            />
          </label>
          <label className="grid gap-1 text-xs font-medium text-foreground-secondary">
            Display name
            <input
              required
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              placeholder="Daily Briefing Agent"
              className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none focus:border-brand"
            />
          </label>
          <label className="grid gap-1 text-xs font-medium text-foreground-secondary lg:col-span-2">
            Description
            <input
              required
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Reports heartbeat and execution summaries from its external runtime."
              className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none focus:border-brand"
            />
          </label>
          <label className="grid gap-1 text-xs font-medium text-foreground-secondary">
            Environment
            <input
              required
              value={environment}
              onChange={(event) => setEnvironment(event.target.value)}
              className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none focus:border-brand"
            />
          </label>
          <label className="grid gap-1 text-xs font-medium text-foreground-secondary">
            Expected version
            <input
              value={expectedVersion}
              onChange={(event) => setExpectedVersion(event.target.value)}
              placeholder="Optional"
              className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none focus:border-brand"
            />
          </label>
          <label className="grid gap-1 text-xs font-medium text-foreground-secondary">
            Monitoring mode
            <select
              value={monitoringMode}
              onChange={(event) =>
                setMonitoringMode(event.target.value as "heartbeat" | "activity_only")
              }
              className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none focus:border-brand"
            >
              <option value="heartbeat">Heartbeat</option>
              <option value="activity_only">Activity only</option>
            </select>
          </label>
          <label className="grid gap-1 text-xs font-medium text-foreground-secondary">
            Heartbeat interval seconds
            <input
              type="number"
              min="60"
              disabled={monitoringMode === "activity_only"}
              value={heartbeatInterval}
              onChange={(event) => setHeartbeatInterval(event.target.value)}
              className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none focus:border-brand disabled:opacity-60"
            />
          </label>
          <div className="flex flex-wrap items-center gap-3 lg:col-span-2">
            <Button type="submit" size="sm" disabled={submitting || !csrfToken}>
              {submitting ? "Enrolling..." : "Enroll agent"}
            </Button>
            {message && (
              <p className="text-xs text-foreground-secondary" role="status">
                {message}
              </p>
            )}
          </div>
        </form>
        {credential && (
          <div className="grid gap-2 rounded-atlas-md border border-warning-border bg-warning-bg p-3 text-xs">
            <p className="font-medium text-warning">
              One-time credential. Copy it before leaving this page.
            </p>
            <textarea
              readOnly
              value={credential.plaintext_token}
              className="min-h-20 resize-y rounded-atlas-sm border border-border-default bg-surface p-2 font-mono text-[11px] text-foreground"
              aria-label="One-time agent credential token"
            />
            <Button
              type="button"
              variant="secondary"
              size="sm"
              className="w-fit"
              onClick={() => void navigator.clipboard?.writeText(credential.plaintext_token)}
            >
              Copy token
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function AgentsInventory({ agents = MOCK_AGENTS, state = "loaded", runtimeRequired = false }: AgentsInventoryProps) {
  const [runtimeMode, setRuntimeMode] =
    React.useState<DashboardRuntimeMode>(() =>
      runtimeRequired ? (dashboardApiBaseUrl() ? "loading" : "error") : "fixture",
    );
  const [liveAgents, setLiveAgents] = React.useState<AgentRecord[]>([]);
  const [csrfToken, setCsrfToken] = React.useState("");
  const [viewState, setViewState] = React.useState<InventoryState>(() =>
    runtimeRequired ? (dashboardApiBaseUrl() ? "loading" : "error") : state,
  );
  const [searchQuery, setSearchQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState<AgentStatus | "all">("all");
  const [healthFilter, setHealthFilter] = React.useState<AgentHealth | "all">("all");
  const [sort, setSort] = React.useState<SortKey>("attention");
  const [direction, setDirection] = React.useState<SortDirection>("asc");

  React.useEffect(() => {
    let cancelled = false;
    async function loadRuntime() {
      if (!dashboardApiBaseUrl()) {
        setRuntimeMode(runtimeRequired ? "error" : "fixture");
        setViewState(runtimeRequired ? "error" : state);
        return;
      }
      setRuntimeMode("loading");
      setViewState("loading");
      try {
        const session = await readDashboardSessionOrRequireSignIn();
        const [runtimeAgents, runtimeRuns] = await Promise.all([
          readDashboardAgents(),
          readDashboardRuns(),
        ]);
        if (!cancelled) {
          setCsrfToken(session.csrf_token);
          setLiveAgents(toAgentRecords(runtimeAgents, runtimeRuns));
          setRuntimeMode("live");
          setViewState("loaded");
        }
      } catch (error) {
        if (cancelled) return;
        if (
          error instanceof Error &&
          "status" in error &&
          (error as { status: number }).status === 401
        ) {
          setRuntimeMode("unauthenticated");
          setViewState("error");
        } else {
          setRuntimeMode("error");
          setViewState("error");
        }
      }
    }
    void loadRuntime();
    return () => {
      cancelled = true;
    };
  }, [runtimeRequired, state]);

  const onSort = (key: SortKey) => {
    if (key === sort) setDirection((d) => (d === "asc" ? "desc" : "asc"));
    else { setSort(key); setDirection("asc"); }
  };

  const activeAgents = runtimeMode === "live" ? liveAgents : runtimeRequired ? [] : agents;
  const hasActiveFilters = searchQuery.trim() !== "" || statusFilter !== "all" || healthFilter !== "all";
  const filteredAgents = sortAgents(filterAgents(activeAgents, searchQuery, statusFilter, healthFilter), sort, direction);
  const clearFilters = () => { setSearchQuery(""); setStatusFilter("all"); setHealthFilter("all"); };

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Fleet"
        title="Agents"
        icon={Bot}
        description={
          runtimeMode === "live"
            ? "Monitor owner-authenticated Atlas runtime agent registrations."
            : "Monitor the status, health, and activity of your AI workforce."
        }
      />

      {runtimeMode === "live" && (
        <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
          <strong>Live runtime.</strong> Agent registrations, observed health, and
          latest execution state are loaded from owner-authenticated Atlas APIs.
        </div>
      )}

      {runtimeMode === "live" && (
        <EnrollmentPanel
          csrfToken={csrfToken}
          onEnrolled={(agent) =>
            setLiveAgents((current) => [
              agent,
              ...current.filter((item) => item.id !== agent.id),
            ])
          }
        />
      )}

      {viewState === "loading" && <InventorySkeleton />}

      {viewState === "error" && (
        runtimeMode === "unauthenticated" ? (
          <SignedOutState description="Sign in to load runtime agent registrations from the Atlas API." />
        ) : (
          <Card>
            <ErrorState
              title="Agents inventory could not be displayed"
              description={
                runtimeRequired && !dashboardApiBaseUrl()
                  ? "No runtime API base URL is configured for this build, so the live Agents inventory cannot be displayed."
                  : "The owner-authenticated Atlas APIs could not return agent registrations. No agent operation was started."
              }
              className="py-16"
            />
          </Card>
        )
      )}

      {viewState === "loaded" && activeAgents.length > 0 && (
        <section className="flex flex-col gap-3" aria-labelledby="agents-inventory-heading">
          <div className="flex flex-col gap-3 rounded-atlas-md border border-border-default bg-surface-secondary p-3.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 id="agents-inventory-heading" className="text-xs font-semibold uppercase tracking-wide text-foreground-secondary">
                Showing {filteredAgents.length} of {activeAgents.length}
              </h2>
              {hasActiveFilters && (
                <Button type="button" variant="ghost" size="sm" onClick={clearFilters}>
                  <FilterX aria-hidden="true" />
                  Clear
                </Button>
              )}
            </div>
            <div className="grid gap-2.5 lg:grid-cols-[minmax(0,1fr)_12rem_12rem]">
              <SearchField id="agent-search" value={searchQuery} onChange={setSearchQuery} placeholder="Search name, description, or ID" aria-label="Search agents by name, description, or ID" />
              <select id="agent-status-filter" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as AgentStatus | "all")} aria-label="Filter by status" className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none transition-colors hover:border-border-strong focus:border-brand">
                <option value="all">All statuses</option>
                {Object.entries(STATUS_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
              <select id="agent-health-filter" value={healthFilter} onChange={(e) => setHealthFilter(e.target.value as AgentHealth | "all")} aria-label="Filter by health" className="h-9 rounded-atlas-sm border border-border-default bg-surface px-3 text-sm text-foreground outline-none transition-colors hover:border-border-strong focus:border-brand">
                <option value="all">All health states</option>
                {Object.entries(HEALTH_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </div>
          </div>

          {filteredAgents.length > 0 ? (
            <>
              <AgentsTable agents={filteredAgents} sort={sort} direction={direction} onSort={onSort} />
              <MobileAgentsList agents={filteredAgents} />
            </>
          ) : (
            <Card>
              <EmptyState icon={CircleOff} title="No agents match the current search or filters" description="Adjust the criteria or clear filters to restore the full inventory." action={<Button type="button" variant="secondary" size="sm" onClick={clearFilters}>Clear filters</Button>} className="py-16" />
            </Card>
          )}
        </section>
      )}

      {viewState === "loaded" && activeAgents.length === 0 && (
        <Card>
          <EmptyState
            icon={CircleOff}
            title="No agents are registered"
            description={
              runtimeMode === "live"
                  ? "No owner-visible agents have been enrolled yet."
                : "No local agent fixtures are available."
            }
            className="py-16"
          />
        </Card>
      )}
    </div>
  );
}
