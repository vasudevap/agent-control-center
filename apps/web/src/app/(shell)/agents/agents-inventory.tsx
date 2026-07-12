"use client";

import * as React from "react";
import Link from "next/link";
import { AlertTriangle, Bot, CircleOff, FilterX } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
import { ErrorState } from "@/components/state/error-state";
import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type AgentStatus = "running" | "active" | "paused" | "queued";
type AgentHealth = "healthy" | "degraded" | "offline";
type InventoryState = "loaded" | "loading" | "error";

export interface AgentRecord {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  health: AgentHealth;
  owner: string;
  lastRun: string;
  nextRun: string;
  version: string;
  currentIssue?: string;
  issueSummary?: string;
}

interface AgentsInventoryProps {
  agents?: AgentRecord[];
  state?: InventoryState;
}

const MOCK_AGENTS: AgentRecord[] = [
  {
    id: "agent-invoice-reconcile",
    name: "Invoice Reconciliation Agent",
    description: "Matches vendor invoices against approved purchase orders.",
    status: "running",
    health: "degraded",
    owner: "Finance Operations",
    lastRun: "8 minutes ago",
    nextRun: "In 22 minutes",
    version: "v1.8.3",
    currentIssue: "Three invoices are waiting on policy review.",
    issueSummary: "Policy review needed",
  },
  {
    id: "agent-calendar-briefing",
    name: "Calendar Briefing Agent",
    description: "Prepares daily meeting briefs from schedule context.",
    status: "active",
    health: "healthy",
    owner: "Executive Operations",
    lastRun: "18 minutes ago",
    nextRun: "Tomorrow 6:00 AM",
    version: "v2.1.0",
  },
  {
    id: "agent-connectors-health",
    name: "Connector Health Sentinel",
    description: "Checks connector freshness, latency, and failed handshakes.",
    status: "running",
    health: "healthy",
    owner: "Platform Reliability",
    lastRun: "2 minutes ago",
    nextRun: "In 13 minutes",
    version: "v1.4.7",
  },
  {
    id: "agent-policy-digest",
    name: "Policy Digest Agent",
    description: "Summarizes policy exceptions for review owners.",
    status: "paused",
    health: "offline",
    owner: "Governance Office",
    lastRun: "Yesterday 4:20 PM",
    nextRun: "Not scheduled",
    version: "v0.9.5",
    currentIssue: "Paused after repeated evidence export failures.",
    issueSummary: "Export failures",
  },
  {
    id: "agent-recruiting-triage",
    name: "Recruiting Triage Agent",
    description: "Classifies candidate intake messages for recruiter review.",
    status: "queued",
    health: "degraded",
    owner: "Talent Operations",
    lastRun: "43 minutes ago",
    nextRun: "In 7 minutes",
    version: "v1.2.2",
  },
  {
    id: "agent-support-drafts",
    name: "Support Draft Agent",
    description: "Drafts support responses from approved knowledge articles.",
    status: "active",
    health: "healthy",
    owner: "Customer Operations",
    lastRun: "11 minutes ago",
    nextRun: "In 19 minutes",
    version: "v3.0.1",
  },
];

const STATUS_LABELS: Record<AgentStatus, string> = {
  running: "Running",
  active: "Active",
  paused: "Paused",
  queued: "Queued",
};

const HEALTH_LABELS: Record<AgentHealth, string> = {
  healthy: "Healthy",
  degraded: "Degraded",
  offline: "Offline",
};

const STATUS_VARIANTS: Record<AgentStatus, BadgeProps["variant"]> = {
  running: "info",
  active: "success",
  paused: "neutral",
  queued: "warning",
};

const HEALTH_VARIANTS: Record<AgentHealth, BadgeProps["variant"]> = {
  healthy: "success",
  degraded: "warning",
  offline: "error",
};

function getAttentionRank(agent: AgentRecord) {
  if (agent.currentIssue) {
    return 0;
  }

  if (agent.health === "degraded" || agent.health === "offline") {
    return 1;
  }

  if (agent.status === "running") {
    return 2;
  }

  return 3;
}

function orderAgentsByAttention(agents: AgentRecord[]) {
  return [...agents].sort((agentA, agentB) => {
    const rankDifference = getAttentionRank(agentA) - getAttentionRank(agentB);

    if (rankDifference !== 0) {
      return rankDifference;
    }

    return agentA.name.localeCompare(agentB.name);
  });
}

function filterAgents(
  agents: AgentRecord[],
  searchQuery: string,
  statusFilter: AgentStatus | "all",
  healthFilter: AgentHealth | "all"
) {
  const normalizedQuery = searchQuery.trim().toLowerCase();

  return orderAgentsByAttention(agents).filter((agent) => {
    const matchesSearch =
      !normalizedQuery ||
      agent.name.toLowerCase().includes(normalizedQuery) ||
      agent.description.toLowerCase().includes(normalizedQuery) ||
      agent.id.toLowerCase().includes(normalizedQuery);

    const matchesStatus = statusFilter === "all" || agent.status === statusFilter;
    const matchesHealth = healthFilter === "all" || agent.health === healthFilter;

    return matchesSearch && matchesStatus && matchesHealth;
  });
}

function AgentBadge({
  label,
  variant,
}: {
  label: string;
  variant: BadgeProps["variant"];
}) {
  return <Badge variant={variant}>{label}</Badge>;
}

function FieldPair({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <dt className="font-mono text-[11px] font-medium uppercase tracking-wider text-foreground-tertiary">
        {label}
      </dt>
      <dd className="text-sm text-foreground">{value}</dd>
    </div>
  );
}

function AgentIdentity({ agent }: { agent: AgentRecord }) {
  const issueLabel = agent.issueSummary ?? agent.currentIssue;

  return (
    <div className="flex min-w-0 flex-col gap-1">
      <Link
        href={`/agents/${agent.id}`}
        className="font-medium text-foreground underline-offset-4 hover:text-brand hover:underline"
      >
        {agent.name}
      </Link>
      <p className="max-w-md truncate text-xs text-foreground-secondary">
        {agent.description}
      </p>
      {issueLabel && (
        <p className="mt-1 flex items-center gap-1.5 text-xs text-warning">
          <AlertTriangle className="size-3.5 shrink-0" aria-hidden="true" />
          <span className="truncate">Issue: {issueLabel}</span>
        </p>
      )}
    </div>
  );
}

function AgentsTable({ agents }: { agents: AgentRecord[] }) {
  return (
    <Card className="hidden overflow-hidden border-border-strong shadow-atlas-md md:block">
      <Table>
        <caption className="sr-only">Agents inventory</caption>
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Health</TableHead>
            <TableHead className="hidden lg:table-cell">Owner</TableHead>
            <TableHead>Last Run</TableHead>
            <TableHead>Next Run</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id}>
              <TableCell className="min-w-[18rem]">
                <AgentIdentity agent={agent} />
              </TableCell>
              <TableCell>
                <AgentBadge label={STATUS_LABELS[agent.status]} variant={STATUS_VARIANTS[agent.status]} />
              </TableCell>
              <TableCell>
                <AgentBadge label={HEALTH_LABELS[agent.health]} variant={HEALTH_VARIANTS[agent.health]} />
              </TableCell>
              <TableCell className="hidden text-sm text-foreground-secondary lg:table-cell">
                {agent.owner}
              </TableCell>
              <TableCell className="text-sm text-foreground-secondary">{agent.lastRun}</TableCell>
              <TableCell className="text-sm text-foreground-secondary">{agent.nextRun}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}

function MobileAgentsList({ agents }: { agents: AgentRecord[] }) {
  return (
    <div className="grid gap-3 md:hidden" aria-label="Agents inventory summaries">
      {agents.map((agent) => (
        <Link
          key={agent.id}
          href={`/agents/${agent.id}`}
          className="block rounded-atlas-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus-ring"
          aria-label={`${agent.name} details`}
        >
          <Card className="border-border-strong transition-colors hover:bg-surface-hover">
            <CardContent className="flex flex-col gap-4 p-4">
              <div className="flex flex-col gap-2">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="text-sm font-semibold text-foreground">{agent.name}</h2>
                  </div>
                </div>
              </div>

              <dl className="grid grid-cols-2 gap-4">
                <FieldPair
                  label="Status"
                  value={<AgentBadge label={STATUS_LABELS[agent.status]} variant={STATUS_VARIANTS[agent.status]} />}
                />
                <FieldPair
                  label="Health"
                  value={<AgentBadge label={HEALTH_LABELS[agent.health]} variant={HEALTH_VARIANTS[agent.health]} />}
                />
                <FieldPair label="Last Run" value={agent.lastRun} />
                <FieldPair label="Next Run" value={agent.nextRun} />
              </dl>

              {(agent.issueSummary ?? agent.currentIssue) && (
                <div className="rounded-atlas-md border border-warning-border bg-warning-bg px-3 py-2 text-xs leading-relaxed text-warning">
                  <span className="font-medium">Issue:</span> {agent.issueSummary ?? agent.currentIssue}
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
    <div className="flex flex-col gap-6" aria-label="Loading agents inventory">
      <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_12rem_12rem_auto]">
        <Skeleton className="h-9" />
        <Skeleton className="h-9" />
        <Skeleton className="h-9" />
        <Skeleton className="h-9" />
      </div>
      <Card className="hidden p-4 md:block">
        <div className="flex flex-col gap-3">
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-16" />
          ))}
        </div>
      </Card>
      <div className="grid gap-3 md:hidden">
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="h-44" />
        ))}
      </div>
    </div>
  );
}

export function AgentsInventory({ agents = MOCK_AGENTS, state = "loaded" }: AgentsInventoryProps) {
  const [searchQuery, setSearchQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState<AgentStatus | "all">("all");
  const [healthFilter, setHealthFilter] = React.useState<AgentHealth | "all">("all");

  const hasActiveFilters = searchQuery.trim() !== "" || statusFilter !== "all" || healthFilter !== "all";
  const filteredAgents = filterAgents(agents, searchQuery, statusFilter, healthFilter);

  const clearFilters = () => {
    setSearchQuery("");
    setStatusFilter("all");
    setHealthFilter("all");
  };

  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        title="Agents"
        description="Monitor the status, health, and activity of your AI workforce."
        icon={Bot}
      />

      {state === "loading" && <InventorySkeleton />}

      {state === "error" && (
        <Card>
          <ErrorState
            title="Agents inventory could not be displayed"
            description="The local inventory state is unavailable. No agent operation was started."
            className="py-16"
          />
        </Card>
      )}

      {state === "loaded" && agents.length === 0 && (
        <Card>
          <EmptyState
            icon={Bot}
            title="No agents are registered yet"
            description="Agents are governed automation workers that will appear here once registration is available in a later milestone."
            className="py-16"
          />
        </Card>
      )}

      {state === "loaded" && agents.length > 0 && (
        <section className="flex flex-col gap-4" aria-labelledby="agents-inventory-heading">
          <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-default bg-surface-secondary p-4 shadow-atlas-sm">
            <div className="flex flex-col gap-1">
              <h2 id="agents-inventory-heading" className="text-sm font-semibold text-foreground">
                Inventory
              </h2>
              <p className="text-xs text-foreground-secondary">
                Showing {filteredAgents.length} of {agents.length} agents
              </p>
            </div>

            <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_12rem_12rem_auto] lg:items-end">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="agent-search" className="text-xs font-medium text-foreground-secondary">
                  Search agents
                </label>
                <SearchField
                  id="agent-search"
                  value={searchQuery}
                  onChange={setSearchQuery}
                  placeholder="Search name, description, or ID"
                  aria-label="Search agents by name, description, or ID"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="agent-status-filter" className="text-xs font-medium text-foreground-secondary">
                  Status
                </label>
                <select
                  id="agent-status-filter"
                  value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value as AgentStatus | "all")}
                  className="h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none transition-colors hover:border-border-strong focus:border-brand"
                >
                  <option value="all">All statuses</option>
                  {Object.entries(STATUS_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="agent-health-filter" className="text-xs font-medium text-foreground-secondary">
                  Health
                </label>
                <select
                  id="agent-health-filter"
                  value={healthFilter}
                  onChange={(event) => setHealthFilter(event.target.value as AgentHealth | "all")}
                  className="h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none transition-colors hover:border-border-strong focus:border-brand"
                >
                  <option value="all">All health states</option>
                  {Object.entries(HEALTH_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              {hasActiveFilters && (
                <Button type="button" variant="secondary" onClick={clearFilters}>
                  <FilterX aria-hidden="true" />
                  Clear Filters
                </Button>
              )}
            </div>
          </div>

          {filteredAgents.length > 0 ? (
            <>
              <AgentsTable agents={filteredAgents} />
              <MobileAgentsList agents={filteredAgents} />
            </>
          ) : (
            <Card>
              <EmptyState
                icon={CircleOff}
                title="No agents match the current search or filters"
                description="Adjust the criteria or clear filters to restore the full inventory."
                action={
                  <Button type="button" variant="secondary" size="sm" onClick={clearFilters}>
                    Clear Filters
                  </Button>
                }
                className="py-16"
              />
            </Card>
          )}
        </section>
      )}
    </div>
  );
}
