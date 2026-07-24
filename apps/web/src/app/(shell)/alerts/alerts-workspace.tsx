"use client";

import * as React from "react";
import Link from "next/link";
import {
  AlertOctagon,
  AlertTriangle,
  BellRing,
  FilterX,
  Info,
  Siren,
} from "lucide-react";
import {
  ALERT_SEVERITY_LABELS,
  type AlertRecord,
  type AlertSeverity,
  type AlertStatus,
} from "./alert-data";
import {
  dashboardApiBaseUrl,
  type DashboardRuntimeMode,
  readDashboardMonitoring,
  readDashboardSessionOrRequireSignIn,
  toMonitoringAlerts,
} from "@/lib/dashboard-runtime";
import {
  controlCenterAgentHref,
  controlCenterExecutionHref,
} from "@/lib/control-center-routes";
import { StatusBadge } from "@/components/badge/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
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
import { cn } from "@/lib/utils";

type SortKey = "severity" | "alert" | "status" | "source" | "raised";
const SELECT_CLASS =
  "h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none hover:border-border-strong focus:border-brand";
const SEVERITY_RANK: Record<AlertSeverity, number> = {
  critical: 0,
  high: 1,
  warning: 2,
  information: 3,
};
const STATUS_RANK: Record<AlertStatus, number> = {
  active: 0,
  investigating: 1,
  resolved: 2,
};

function Severity({ severity }: { severity: AlertSeverity }) {
  const config = {
    critical: {
      icon: AlertOctagon,
      className: "text-error",
      label: "Critical",
    },
    high: { icon: Siren, className: "text-risk-high", label: "High" },
    warning: {
      icon: AlertTriangle,
      className: "text-warning",
      label: "Warning",
    },
    information: { icon: Info, className: "text-info", label: "Information" },
  }[severity];
  const Icon = config.icon;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-medium",
        config.className,
      )}
    >
      <Icon className="size-3.5" aria-hidden="true" />
      <span>{config.label}</span>
    </span>
  );
}

function AlertDetails({
  alert,
  defaultOpen,
}: {
  alert: AlertRecord;
  defaultOpen?: boolean;
}) {
  return (
    <details
      className="group mt-2 whitespace-normal"
      open={defaultOpen || undefined}
    >
      <summary className="relative z-20 w-fit cursor-pointer text-xs font-medium text-brand hover:underline">
        View alert details
      </summary>
      <div className="relative z-20 mt-3 grid gap-3 rounded-atlas-md border border-border-subtle bg-surface-secondary p-3 text-xs">
        <p className="leading-relaxed text-foreground-secondary">
          {alert.evidence}
        </p>
        <dl className="grid gap-2 sm:grid-cols-2">
          <div>
            <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
              Correlation
            </dt>
            <dd className="break-all font-mono text-foreground">
              {alert.correlationId}
            </dd>
          </div>
          <div>
            <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
              Category
            </dt>
            <dd>{alert.category}</dd>
          </div>
        </dl>
        <div className="flex flex-wrap gap-2">
          {alert.sourceAgentId && (
            <Button asChild variant="secondary" size="sm">
              <Link href={controlCenterAgentHref(alert.sourceAgentId)}>View agent</Link>
            </Button>
          )}
          {alert.relatedRunId && (
            <Button asChild variant="secondary" size="sm">
              <Link href={controlCenterExecutionHref(alert.relatedRunId)}>View run</Link>
            </Button>
          )}
        </div>
      </div>
    </details>
  );
}

export function AlertsWorkspace({
  alerts,
  initialAlertId,
}: {
  alerts: AlertRecord[];
  initialAlertId?: string;
}) {
  const [runtimeMode, setRuntimeMode] =
    React.useState<DashboardRuntimeMode>(() =>
      dashboardApiBaseUrl() ? "loading" : "fixture",
    );
  const [liveAlerts, setLiveAlerts] = React.useState<AlertRecord[]>([]);
  const [query, setQuery] = React.useState("");
  const [severity, setSeverity] = React.useState<AlertSeverity | "all">("all");
  const [status, setStatus] = React.useState<AlertStatus | "all">("all");
  const [source, setSource] = React.useState("all");
  const [sort, setSort] = React.useState<SortKey>("severity");
  const [direction, setDirection] = React.useState<SortDirection>("asc");
  React.useEffect(() => {
    let cancelled = false;
    async function loadRuntime() {
      if (!dashboardApiBaseUrl()) {
        setRuntimeMode("fixture");
        return;
      }
      setRuntimeMode("loading");
      try {
        await readDashboardSessionOrRequireSignIn();
        const monitoring = await readDashboardMonitoring();
        if (!cancelled) {
          setLiveAlerts(toMonitoringAlerts(monitoring));
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

  const activeAlerts = runtimeMode === "live" ? liveAlerts : alerts;
  const records = activeAlerts;
  const normalized = query.trim().toLowerCase();
  const visible = records
    .filter(
      (alert) =>
        (!normalized ||
          [
            alert.id,
            alert.title,
            alert.description,
            alert.source,
            alert.correlationId,
          ]
            .join(" ")
            .toLowerCase()
            .includes(normalized)) &&
        (severity === "all" || alert.severity === severity) &&
        (status === "all" || alert.status === status) &&
        (source === "all" || alert.source === source),
    )
    .sort((a, b) => {
      const multiplier = direction === "asc" ? 1 : -1;
      if (sort === "severity")
        return (
          (SEVERITY_RANK[a.severity] - SEVERITY_RANK[b.severity]) * multiplier
        );
      if (sort === "status")
        return (STATUS_RANK[a.status] - STATUS_RANK[b.status]) * multiplier;
      if (sort === "alert") return a.title.localeCompare(b.title) * multiplier;
      if (sort === "source")
        return a.source.localeCompare(b.source) * multiplier;
      return (+new Date(a.raisedAt) - +new Date(b.raisedAt)) * multiplier;
    });
  const hasFilters = Boolean(
    query || severity !== "all" || status !== "all" || source !== "all",
  );
  const clear = () => {
    setQuery("");
    setSeverity("all");
    setStatus("all");
    setSource("all");
  };
  const onSort = (next: SortKey) => {
    if (next === sort)
      setDirection((value) => (value === "asc" ? "desc" : "asc"));
    else {
      setSort(next);
      setDirection("asc");
    }
  };
  return (
    <div className="flex flex-col gap-5">
      <PageHeader
        eyebrow="Operations"
        title="Alerts"
        description={
          runtimeMode === "live"
            ? "Review lightweight hosted runtime monitoring posture from the Atlas API."
            : "Triage operational signals across the Atlas runtime."
        }
        icon={BellRing}
      />
      {runtimeMode === "unauthenticated" && (
        <SignedOutState description="Sign in to load runtime alert monitoring from the Atlas API." />
      )}
      {runtimeMode !== "unauthenticated" && (
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        {runtimeMode === "live" ? (
          <>
            <strong>Live runtime.</strong> Monitoring evidence is loaded from
            the owner-authenticated Atlas API dashboard facade.
          </>
        ) : runtimeMode === "loading" ? (
          "Loading owner-authenticated monitoring posture..."
        ) : runtimeMode === "error" ? (
          "Runtime monitoring is unavailable. Fixture alerts remain quarantined from release evidence."
        ) : (
          <>
            <strong>Frontend prototype.</strong> No runtime API base URL is
            configured for this build; alert evidence and status are local
            fixtures.
          </>
        )}
      </div>
      )}
      {runtimeMode !== "unauthenticated" && runtimeMode !== "loading" && (
      <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-default bg-surface p-3 sm:flex-row sm:flex-wrap sm:items-center">
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search alerts"
          className="w-full sm:max-w-sm"
        />
        <label htmlFor="alert-severity" className="sr-only">
          Severity
        </label>
        <select
          id="alert-severity"
          className={SELECT_CLASS}
          value={severity}
          onChange={(event) =>
            setSeverity(event.target.value as AlertSeverity | "all")
          }
        >
          <option value="all">All severities</option>
          {Object.entries(ALERT_SEVERITY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <label htmlFor="alert-status" className="sr-only">
          Status
        </label>
        <select
          id="alert-status"
          className={SELECT_CLASS}
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as AlertStatus | "all")
          }
        >
          <option value="all">All statuses</option>
          <option value="active">Active</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
        </select>
        <label htmlFor="alert-source" className="sr-only">
          Source
        </label>
        <select
          id="alert-source"
          className={SELECT_CLASS}
          value={source}
          onChange={(event) => setSource(event.target.value)}
        >
          <option value="all">All sources</option>
          {[...new Set(activeAlerts.map((alert) => alert.source))].map((value) => (
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
          {visible.length} of {activeAlerts.length}{" "}
          {runtimeMode === "live" ? "runtime alerts" : "fictional alerts"}
        </p>
      </div>
      )}
      {runtimeMode !== "unauthenticated" && runtimeMode !== "loading" && (
      <>
      {visible.length === 0 ? (
        <Card>
          <EmptyState
            icon={BellRing}
            title={hasFilters ? "No alerts match these filters" : "No alerts"}
            description={
              hasFilters
                ? "Clear filters to restore the fictional alert inventory."
                : runtimeMode === "live"
                  ? "No runtime monitoring alerts are available."
                  : "No alert fixtures are available."
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
              <caption className="sr-only">Alerts inventory</caption>
              <TableHeader>
                <TableRow>
                  {(
                    [
                      "severity",
                      "alert",
                      "status",
                      "source",
                      "raised",
                    ] as SortKey[]
                  ).map((key) => (
                    <TableHead
                      key={key}
                      aria-sort={getAriaSort(sort === key, direction)}
                      className={key === "alert" ? "w-[38%]" : undefined}
                    >
                      <SortHeader
                        label={
                          key === "raised"
                            ? "Raised"
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
                {visible.map((alert) => (
                  <TableRow key={alert.id} id={alert.id}>
                    <TableCell className="align-top text-xs">
                      <Severity severity={alert.severity} />
                    </TableCell>
                    <TableCell className="align-top text-xs whitespace-normal">
                      <p className="font-medium">{alert.title}</p>
                      <p className="mt-1 text-foreground-secondary">
                        {alert.description}
                      </p>
                      <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                        {alert.id}
                      </p>
                      <AlertDetails
                        alert={alert}
                        defaultOpen={initialAlertId === alert.id}
                      />
                    </TableCell>
                    <TableCell className="align-top text-xs">
                      <StatusBadge
                        status={alert.status}
                        plain
                        className="text-xs"
                      />
                    </TableCell>
                    <TableCell className="align-top text-xs text-foreground-secondary">
                      {alert.source}
                    </TableCell>
                    <TableCell className="align-top text-xs text-foreground-secondary">
                      {alert.timestamp}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
          <ul className="grid gap-3 md:hidden">
            {visible.map((alert) => (
              <li key={alert.id} id={`${alert.id}-mobile`}>
                <Card>
                  <CardContent className="grid gap-3 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <Severity severity={alert.severity} />
                        <h2 className="mt-2 font-medium">{alert.title}</h2>
                        <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                          {alert.id}
                        </p>
                      </div>
                      <StatusBadge status={alert.status} />
                    </div>
                    <p className="text-sm text-foreground-secondary">
                      {alert.description}
                    </p>
                    <dl className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Source
                        </dt>
                        <dd>{alert.source}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Raised
                        </dt>
                        <dd>{alert.timestamp}</dd>
                      </div>
                    </dl>
                    <AlertDetails
                      alert={alert}
                      defaultOpen={initialAlertId === alert.id}
                    />
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
