"use client";

import * as React from "react";
import Link from "next/link";
import { ClipboardList, FilterX, LockKeyhole } from "lucide-react";
import {
  type AuditAction,
  type AuditEvent,
  type AuditResourceType,
  type AuditResult,
} from "./audit-data";
import { StatusBadge } from "@/components/badge/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
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
import {
  dashboardApiBaseUrl,
  dashboardSignInUrl,
  type DashboardRuntimeMode,
  readDashboardAudit,
  readDashboardSession,
  toAuditEvents,
} from "@/lib/dashboard-runtime";

type SortKey = "result" | "event" | "actor" | "resource" | "occurred";
const SELECT_CLASS =
  "h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none hover:border-border-strong focus:border-brand";
const RESULT_RANK: Record<AuditResult, number> = {
  failed: 0,
  rejected: 1,
  approved: 2,
  succeeded: 3,
};

function EventDetails({ event }: { event: AuditEvent }) {
  return (
    <details className="mt-2 whitespace-normal">
      <summary className="w-fit cursor-pointer text-xs font-medium text-brand hover:underline">
        View event details
      </summary>
      <div className="mt-3 grid gap-3 rounded-atlas-md border border-border-subtle bg-surface-secondary p-3 text-xs">
        <p className="leading-relaxed text-foreground-secondary">
          {event.reason}
        </p>
        <dl className="grid gap-2 sm:grid-cols-2">
          <div>
            <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
              Correlation
            </dt>
            <dd className="break-all font-mono">{event.correlationId}</dd>
          </div>
          <div>
            <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
              Actor type
            </dt>
            <dd>{event.actorType}</dd>
          </div>
        </dl>
        {event.relatedHref && (
          <Button asChild variant="secondary" size="sm" className="w-fit">
            <Link href={event.relatedHref}>View related fixture</Link>
          </Button>
        )}
      </div>
    </details>
  );
}

export function AuditWorkspace({ events }: { events: AuditEvent[] }) {
  const [runtimeMode, setRuntimeMode] =
    React.useState<DashboardRuntimeMode>("fixture");
  const [liveEvents, setLiveEvents] = React.useState<AuditEvent[]>([]);
  const [query, setQuery] = React.useState("");
  const [action, setAction] = React.useState<AuditAction | "all">("all");
  const [result, setResult] = React.useState<AuditResult | "all">("all");
  const [actor, setActor] = React.useState("all");
  const [resource, setResource] = React.useState<AuditResourceType | "all">(
    "all",
  );
  const [sort, setSort] = React.useState<SortKey>("occurred");
  const [direction, setDirection] = React.useState<SortDirection>("desc");
  React.useEffect(() => {
    let cancelled = false;
    async function loadRuntime() {
      if (!dashboardApiBaseUrl()) {
        setRuntimeMode("fixture");
        return;
      }
      setRuntimeMode("loading");
      try {
        await readDashboardSession();
        const runtimeEvents = await readDashboardAudit();
        if (!cancelled) {
          setLiveEvents(toAuditEvents(runtimeEvents));
          setRuntimeMode("live");
        }
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
  }, []);

  const activeEvents = runtimeMode === "live" ? liveEvents : events;
  const normalized = query.trim().toLowerCase();
  const visible = activeEvents
    .filter(
      (event) =>
        (!normalized ||
          [
            event.id,
            event.actor,
            event.action,
            event.resourceId,
            event.summary,
            event.correlationId,
          ]
            .join(" ")
            .toLowerCase()
            .includes(normalized)) &&
        (action === "all" || event.action === action) &&
        (result === "all" || event.result === result) &&
        (actor === "all" || event.actor === actor) &&
        (resource === "all" || event.resourceType === resource),
    )
    .sort((a, b) => {
      const multiplier = direction === "asc" ? 1 : -1;
      if (sort === "result")
        return (RESULT_RANK[a.result] - RESULT_RANK[b.result]) * multiplier;
      if (sort === "event")
        return a.action.localeCompare(b.action) * multiplier;
      if (sort === "actor") return a.actor.localeCompare(b.actor) * multiplier;
      if (sort === "resource")
        return a.resourceId.localeCompare(b.resourceId) * multiplier;
      return (+new Date(a.occurredAt) - +new Date(b.occurredAt)) * multiplier;
    });
  const hasFilters = Boolean(
    query ||
      action !== "all" ||
      result !== "all" ||
      actor !== "all" ||
      resource !== "all",
  );
  const clear = () => {
    setQuery("");
    setAction("all");
    setResult("all");
    setActor("all");
    setResource("all");
  };
  const onSort = (next: SortKey) => {
    if (next === sort)
      setDirection((value) => (value === "asc" ? "desc" : "asc"));
    else {
      setSort(next);
      setDirection("asc");
    }
  };
  const unique = <T,>(values: T[]) => [...new Set(values)];

  return (
    <div className="flex flex-col gap-5">
      <PageHeader
        eyebrow="Governance"
        title="Audit"
        description={
          runtimeMode === "live"
            ? "Inspect metadata-only Atlas audit events and correlation context."
            : "Inspect fictional governance history and correlation context."
        }
        icon={ClipboardList}
        meta={
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-foreground-secondary">
            <LockKeyhole className="size-3.5" aria-hidden="true" />
            Read only
          </span>
        }
      />
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        {runtimeMode === "live" ? (
          <>
            <strong>Live runtime.</strong> Audit events are loaded from the
            owner-authenticated Atlas API dashboard facade. This view exposes
            metadata only.
          </>
        ) : runtimeMode === "unauthenticated" ? (
          <>
            <strong>Owner sign-in required.</strong> Runtime audit evidence is
            blocked until the owner session is established.{" "}
            <a className="font-medium text-brand hover:underline" href={dashboardSignInUrl()}>
              Sign in with Google
            </a>
            .
          </>
        ) : runtimeMode === "loading" ? (
          "Loading owner-authenticated audit metadata..."
        ) : runtimeMode === "error" ? (
          "Runtime audit metadata is unavailable. Fixture history remains quarantined from release evidence."
        ) : (
          <>
            <strong>Frontend prototype.</strong> No runtime API base URL is
            configured for this build; these examples are not operational audit
            records or a system of record.
          </>
        )}
      </div>
      <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-default bg-surface p-3 sm:flex-row sm:flex-wrap sm:items-center">
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search audit events"
          className="w-full sm:max-w-sm"
        />
        <label htmlFor="audit-action" className="sr-only">
          Action
        </label>
        <select
          id="audit-action"
          className={SELECT_CLASS}
          value={action}
          onChange={(event) =>
            setAction(event.target.value as AuditAction | "all")
          }
        >
          <option value="all">All actions</option>
          {unique(activeEvents.map((event) => event.action)).map((value) => (
            <option key={value}>{value}</option>
          ))}
        </select>
        <label htmlFor="audit-result" className="sr-only">
          Result
        </label>
        <select
          id="audit-result"
          className={SELECT_CLASS}
          value={result}
          onChange={(event) =>
            setResult(event.target.value as AuditResult | "all")
          }
        >
          <option value="all">All results</option>
          {unique(activeEvents.map((event) => event.result)).map((value) => (
            <option key={value} value={value}>
              {value[0].toUpperCase() + value.slice(1)}
            </option>
          ))}
        </select>
        <label htmlFor="audit-actor" className="sr-only">
          Actor
        </label>
        <select
          id="audit-actor"
          className={SELECT_CLASS}
          value={actor}
          onChange={(event) => setActor(event.target.value)}
        >
          <option value="all">All actors</option>
          {unique(activeEvents.map((event) => event.actor)).map((value) => (
            <option key={value}>{value}</option>
          ))}
        </select>
        <label htmlFor="audit-resource" className="sr-only">
          Resource
        </label>
        <select
          id="audit-resource"
          className={SELECT_CLASS}
          value={resource}
          onChange={(event) =>
            setResource(event.target.value as AuditResourceType | "all")
          }
        >
          <option value="all">All resources</option>
          {unique(activeEvents.map((event) => event.resourceType)).map((value) => (
            <option key={value}>{value}</option>
          ))}
        </select>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clear}>
            <FilterX aria-hidden="true" />
            Clear filters
          </Button>
        )}
        <p className="text-xs text-foreground-secondary sm:ml-auto">
          {visible.length} of {activeEvents.length}{" "}
          {runtimeMode === "live" ? "runtime events" : "fictional events"}
        </p>
      </div>
      {visible.length === 0 ? (
        <Card>
          <EmptyState
            icon={ClipboardList}
            title={
              hasFilters ? "No events match these filters" : "No audit events"
            }
            description={
              hasFilters
                ? "Clear filters to restore the fictional history."
                : runtimeMode === "live"
                  ? "No runtime audit events are available."
                  : "No audit fixtures are available."
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
            <Table>
              <caption className="sr-only">Audit event history</caption>
              <TableHeader>
                <TableRow>
                  {(
                    [
                      "result",
                      "event",
                      "actor",
                      "resource",
                      "occurred",
                    ] as SortKey[]
                  ).map((key) => (
                    <TableHead
                      key={key}
                      aria-sort={getAriaSort(sort === key, direction)}
                      className={key === "event" ? "w-[38%]" : undefined}
                    >
                      <SortHeader
                        label={
                          key === "occurred"
                            ? "Occurred"
                            : key[0].toUpperCase() + key.slice(1)
                        }
                        sortKey={key}
                        active={sort === key}
                        direction={direction}
                        onSort={onSort}
                      />
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {visible.map((event) => (
                  <TableRow key={event.id}>
                    <TableCell className="align-top text-xs">
                      <StatusBadge
                        status={event.result}
                        plain
                        className="text-xs"
                      />
                    </TableCell>
                    <TableCell className="align-top whitespace-normal text-xs">
                      <p className="font-medium">{event.action}</p>
                      <p className="mt-1 text-foreground-secondary">
                        {event.summary}
                      </p>
                      <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                        {event.id}
                      </p>
                      <EventDetails event={event} />
                    </TableCell>
                    <TableCell className="align-top text-xs text-foreground-secondary">
                      {event.actor}
                    </TableCell>
                    <TableCell className="align-top text-xs">
                      <span className="block text-foreground-secondary">
                        {event.resourceType}
                      </span>
                      <span className="font-mono text-[10px] text-foreground-tertiary">
                        {event.resourceId}
                      </span>
                    </TableCell>
                    <TableCell className="align-top text-xs text-foreground-secondary">
                      {new Date(event.occurredAt).toLocaleString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
          <ul className="grid gap-3 md:hidden">
            {visible.map((event) => (
              <li key={event.id}>
                <Card>
                  <CardContent className="grid gap-3 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium">{event.action}</p>
                        <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                          {event.id}
                        </p>
                      </div>
                      <StatusBadge status={event.result} />
                    </div>
                    <p className="text-sm text-foreground-secondary">
                      {event.summary}
                    </p>
                    <dl className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Actor
                        </dt>
                        <dd>{event.actor}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Occurred
                        </dt>
                        <dd>{new Date(event.occurredAt).toLocaleString()}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Resource
                        </dt>
                        <dd className="break-all">{event.resourceId}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Type
                        </dt>
                        <dd>{event.resourceType}</dd>
                      </div>
                    </dl>
                    <EventDetails event={event} />
                  </CardContent>
                </Card>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
