"use client";

import * as React from "react";
import Link from "next/link";
import { FilterX, Workflow } from "lucide-react";
import {
  RUN_FIXTURES,
  RUN_STATUS_LABELS,
  type RunRecord,
  type RunStatus,
  type RunTrigger,
} from "./run-data";
import {
  dashboardApiBaseUrl,
  type DashboardRuntimeMode,
  readDashboardAgents,
  readDashboardRuns,
  readDashboardSessionOrRequireSignIn,
  toRunRecords,
} from "@/lib/dashboard-runtime";
import { controlCenterExecutionHref } from "@/lib/control-center-routes";
import { StatusBadge } from "@/components/badge/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
import { ErrorState } from "@/components/state/error-state";
import { SignedOutState } from "@/components/state/signed-out-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SearchField } from "@/components/ui/search-field";
import {
  getAriaSort,
  SortHeader,
  type SortDirection,
} from "@/components/ui/sort-header";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type SortKey = "status" | "run" | "agent" | "started" | "duration" | "cost";
type ViewState = "loaded" | "error";

const STATUS_RANK: Record<RunStatus, number> = {
  failed: 0,
  "timed-out": 1,
  waiting: 2,
  "partially-succeeded": 3,
  running: 4,
  queued: 5,
  cancelled: 6,
  succeeded: 7,
};
const SELECT_CLASS =
  "h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none hover:border-border-strong focus:border-brand";

function durationSeconds(value: string) {
  const hours = Number(value.match(/(\d+)h/)?.[1] ?? 0);
  const minutes = Number(value.match(/(\d+)m/)?.[1] ?? 0);
  const seconds = Number(value.match(/(\d+)s/)?.[1] ?? 0);
  return hours * 3600 + minutes * 60 + seconds;
}

function filterRuns(
  runs: RunRecord[],
  query: string,
  status: RunStatus | "all",
  trigger: RunTrigger | "all",
) {
  const normalized = query.trim().toLowerCase();
  return runs.filter((run) => {
    const searchable = [run.id, run.agent.name, run.summary, run.correlationId]
      .join(" ")
      .toLowerCase();
    return (
      (!normalized || searchable.includes(normalized)) &&
      (status === "all" || run.status === status) &&
      (trigger === "all" || run.trigger === trigger)
    );
  });
}

function sortRuns(runs: RunRecord[], sort: SortKey, direction: SortDirection) {
  const multiplier = direction === "asc" ? 1 : -1;
  return [...runs].sort((a, b) => {
    if (sort === "status")
      return (STATUS_RANK[a.status] - STATUS_RANK[b.status]) * multiplier;
    if (sort === "run") return a.id.localeCompare(b.id) * multiplier;
    if (sort === "agent")
      return a.agent.name.localeCompare(b.agent.name) * multiplier;
    if (sort === "duration")
      return (
        (durationSeconds(a.duration) - durationSeconds(b.duration)) * multiplier
      );
    if (sort === "cost")
      return (
        (Number(a.costEstimate.replace(/[^0-9.]/g, "")) -
          Number(b.costEstimate.replace(/[^0-9.]/g, ""))) *
        multiplier
      );
    return (+new Date(a.startedAt) - +new Date(b.startedAt)) * multiplier;
  });
}

function FieldPair({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="grid gap-0.5">
      <dt className="font-mono text-[10px] uppercase tracking-wider text-foreground-tertiary">
        {label}
      </dt>
      <dd className="text-sm text-foreground">{value}</dd>
    </div>
  );
}

export function RunsWorkspace({
  runs = RUN_FIXTURES,
  state = "loaded",
}: {
  runs?: RunRecord[];
  state?: ViewState;
}) {
  const [runtimeMode, setRuntimeMode] =
    React.useState<DashboardRuntimeMode>(() =>
      dashboardApiBaseUrl() ? "loading" : "fixture",
    );
  const [liveRuns, setLiveRuns] = React.useState<RunRecord[]>([]);
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState<RunStatus | "all">("all");
  const [trigger, setTrigger] = React.useState<RunTrigger | "all">("all");
  const [sort, setSort] = React.useState<SortKey>("started");
  const [direction, setDirection] = React.useState<SortDirection>("desc");
  const [viewState, setViewState] = React.useState(state);
  const loadRuntime = React.useCallback(async () => {
    if (!dashboardApiBaseUrl()) {
      setRuntimeMode("fixture");
      return;
    }
    setRuntimeMode("loading");
    try {
      await readDashboardSessionOrRequireSignIn();
      const [runtimeAgents, runtimeRuns] = await Promise.all([
        readDashboardAgents(),
        readDashboardRuns(),
      ]);
      setLiveRuns(toRunRecords(runtimeRuns, runtimeAgents));
      setRuntimeMode("live");
      setViewState("loaded");
    } catch (error) {
      if (
        error instanceof Error &&
        "status" in error &&
        (error as { status: number }).status === 401
      ) {
        setRuntimeMode("unauthenticated");
      } else {
        setRuntimeMode("error");
        setViewState("error");
      }
    }
  }, []);

  React.useEffect(() => {
    const timeout = window.setTimeout(() => {
      void loadRuntime();
    }, 0);
    return () => window.clearTimeout(timeout);
  }, [loadRuntime]);

  const activeRuns = runtimeMode === "live" ? liveRuns : runs;
  const visibleRuns = sortRuns(
    filterRuns(activeRuns, query, status, trigger),
    sort,
    direction,
  );
  const hasFilters = Boolean(query || status !== "all" || trigger !== "all");

  const clear = () => {
    setQuery("");
    setStatus("all");
    setTrigger("all");
  };
  const onSort = (next: SortKey) => {
    if (next === sort)
      setDirection((current) => (current === "asc" ? "desc" : "asc"));
    else {
      setSort(next);
      setDirection("asc");
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <PageHeader
        eyebrow="Operations"
        title="Executions"
        description={
          runtimeMode === "live"
            ? "Inspect owner-authenticated external-agent execution history reported to Atlas."
            : "Inspect execution history across the Atlas agent fleet."
        }
        icon={Workflow}
      />
      {runtimeMode === "unauthenticated" && (
        <SignedOutState description="Sign in to load runtime run history from the Atlas API." />
      )}
      {runtimeMode !== "unauthenticated" && (
        <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        {runtimeMode === "live" ? (
          <>
            <strong>Live runtime.</strong> Runs are loaded from the Atlas API
            dashboard facade. Atlas is observing reported executions, not
            dispatching agent work.
          </>
        ) : runtimeMode === "loading" ? (
          "Loading owner-authenticated run data..."
        ) : runtimeMode === "error" ? (
          "Runtime run data is unavailable. Fixture history remains quarantined from release evidence."
        ) : (
          <>
            <strong>Frontend prototype.</strong> No runtime API base URL is
            configured for this build; runs, logs, costs, and controls are
            fictional local fixtures.
          </>
        )}
        </div>
      )}
      {runtimeMode !== "unauthenticated" && runtimeMode !== "loading" && (
      <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-default bg-surface p-3 sm:flex-row sm:flex-wrap sm:items-center">
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search runs"
          className="w-full sm:max-w-sm"
        />
        <label className="sr-only" htmlFor="run-status">
          Status
        </label>
        <select
          id="run-status"
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as RunStatus | "all")
          }
          className={SELECT_CLASS}
        >
          <option value="all">All statuses</option>
          {Object.entries(RUN_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <label className="sr-only" htmlFor="run-trigger">
          Trigger
        </label>
        <select
          id="run-trigger"
          value={trigger}
          onChange={(event) =>
            setTrigger(event.target.value as RunTrigger | "all")
          }
          className={SELECT_CLASS}
        >
          <option value="all">All triggers</option>
          <option>Manual</option>
          <option>Scheduled</option>
          <option>Event</option>
        </select>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clear}>
            <FilterX aria-hidden="true" />
            Clear filters
          </Button>
        )}
        <p className="text-xs text-foreground-secondary sm:ml-auto">
          {visibleRuns.length} of {activeRuns.length}{" "}
          {runtimeMode === "live" ? "runtime runs" : "fictional runs"}
        </p>
      </div>
      )}

      {runtimeMode !== "unauthenticated" && runtimeMode !== "loading" && (
      <>
      {viewState === "error" ? (
        <Card>
          <ErrorState
            title="Executions unavailable"
            description="Execution history could not be displayed."
            onRetry={() => setViewState("loaded")}
          />
        </Card>
      ) : visibleRuns.length === 0 ? (
        <Card>
          <EmptyState
            icon={Workflow}
            title={hasFilters ? "No executions match these filters" : "No executions yet"}
            description={
              hasFilters
                ? "Clear filters to restore the fictional history."
                : "Execution history will appear when records are reported."
            }
            action={
              hasFilters ? (
                <Button variant="secondary" size="sm" onClick={clear}>
                  Clear filters
                </Button>
              ) : undefined
            }
          />
        </Card>
      ) : (
        <>
          <Card className="hidden overflow-hidden md:block">
            <Table className="table-fixed">
              <caption className="sr-only">Executions inventory</caption>
              <TableHeader>
                <TableRow>
                  <TableHead
                    className="w-44"
                    aria-sort={getAriaSort(sort === "status", direction)}
                  >
                    <SortHeader
                      label="Status"
                      sortKey="status"
                      active={sort === "status"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead aria-sort={getAriaSort(sort === "run", direction)}>
                    <SortHeader
                      label="Run"
                      sortKey="run"
                      active={sort === "run"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    className="w-52"
                    aria-sort={getAriaSort(sort === "agent", direction)}
                  >
                    <SortHeader
                      label="Agent"
                      sortKey="agent"
                      active={sort === "agent"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    className="w-44"
                    aria-sort={getAriaSort(sort === "started", direction)}
                  >
                    <SortHeader
                      label="Started"
                      sortKey="started"
                      active={sort === "started"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    className="w-28"
                    aria-sort={getAriaSort(sort === "duration", direction)}
                  >
                    <SortHeader
                      label="Duration"
                      sortKey="duration"
                      active={sort === "duration"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "cost", direction)}
                    className="hidden w-28 lg:table-cell"
                  >
                    <SortHeader
                      label="Cost"
                      sortKey="cost"
                      active={sort === "cost"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {visibleRuns.map((run) => (
                  <TableRow key={run.id} className="relative">
                    <TableCell className="text-xs">
                      <StatusBadge
                        status={run.status}
                        plain
                        className="text-xs"
                      />
                    </TableCell>
                    <TableCell className="min-w-0 overflow-hidden text-xs">
                      <Link
                        href={controlCenterExecutionHref(run.id)}
                        className="relative z-10 block overflow-hidden font-mono font-medium text-foreground after:absolute after:inset-0 after:content-[''] hover:text-brand"
                      >
                        <span className="block truncate">{run.id}</span>
                        <span className="block truncate font-sans font-normal text-foreground-secondary">
                          {run.summary}
                        </span>
                      </Link>
                    </TableCell>
                    <TableCell className="overflow-hidden text-ellipsis text-xs text-foreground-secondary">
                      {run.agent.name}
                    </TableCell>
                    <TableCell className="text-xs text-foreground-secondary">
                      {new Date(run.startedAt).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-xs text-foreground-secondary">
                      {run.duration}
                    </TableCell>
                    <TableCell className="hidden text-xs text-foreground-secondary lg:table-cell">
                      {run.costEstimate}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
          <ul className="grid gap-3 md:hidden">
            {visibleRuns.map((run) => (
              <li key={run.id}>
                <Card className="relative">
                  <CardContent className="grid gap-4 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <Link
                        href={controlCenterExecutionHref(run.id)}
                        className="font-mono text-sm font-semibold text-foreground after:absolute after:inset-0 after:content-['']"
                      >
                        {run.id}
                      </Link>
                      <StatusBadge status={run.status} />
                    </div>
                    <p className="text-sm text-foreground-secondary">
                      {run.summary}
                    </p>
                    <dl className="grid grid-cols-2 gap-3">
                      <FieldPair label="Agent" value={run.agent.name} />
                      <FieldPair label="Trigger" value={run.trigger} />
                      <FieldPair
                        label="Started"
                        value={new Date(run.startedAt).toLocaleString()}
                      />
                      <FieldPair label="Duration" value={run.duration} />
                    </dl>
                  </CardContent>
                </Card>
              </li>
            ))}
          </ul>
        </>
      )}
      </>
      )}
    </div>
  );
}
