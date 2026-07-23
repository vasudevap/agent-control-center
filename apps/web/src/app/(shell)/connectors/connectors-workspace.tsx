"use client";

import * as React from "react";
import { Activity, FilterX, PlugZap, RotateCw, ShieldOff } from "lucide-react";
import {
  type AuthenticationType,
  type ConnectorRecord,
  type ConnectorStatus,
} from "./connector-data";
import {
  checkConnectionHealth,
  dashboardApiBaseUrl,
  type DashboardConnection,
  type DashboardRuntimeMode,
  readDashboardConnectors,
  readDashboardSessionOrRequireSignIn,
  startConnectorOAuth,
  toConnectorRecords,
} from "@/lib/dashboard-runtime";
import { StatusBadge } from "@/components/badge/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/state/empty-state";
import { SignedOutState } from "@/components/state/signed-out-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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

const SELECT_CLASS =
  "h-9 rounded-atlas-md border border-border-default bg-surface px-3 text-sm text-foreground outline-none hover:border-border-strong focus:border-brand";
type SortKey =
  | "status"
  | "connector"
  | "authentication"
  | "account"
  | "lastCheck";
const STATUS_RANK: Record<ConnectorStatus, number> = {
  healthy: 0,
  degraded: 1,
  expired: 2,
  revoked: 3,
  offline: 4,
};

function sortConnectors(
  connectors: ConnectorRecord[],
  sort: SortKey,
  direction: SortDirection,
) {
  const multiplier = direction === "asc" ? 1 : -1;
  return [...connectors].sort((a, b) => {
    if (sort === "status")
      return (STATUS_RANK[a.status] - STATUS_RANK[b.status]) * multiplier;
    if (sort === "connector")
      return a.name.localeCompare(b.name) * multiplier;
    if (sort === "authentication")
      return a.authenticationType.localeCompare(b.authenticationType) * multiplier;
    if (sort === "account")
      return a.accountLabel.localeCompare(b.accountLabel) * multiplier;
    return (
      (+new Date(a.lastCheckAt ?? "9999-01-01") -
        +new Date(b.lastCheckAt ?? "9999-01-01")) *
      multiplier
    );
  });
}

function ConnectorDetails({ connector }: { connector: ConnectorRecord }) {
  return (
    <details className="mt-2 whitespace-normal">
      <summary className="w-fit cursor-pointer text-xs font-medium text-brand hover:underline">
        View declared access
      </summary>
      <div className="mt-3 grid gap-3 rounded-atlas-md border border-border-subtle bg-surface-secondary p-3 text-xs">
        <div>
          <p className="font-mono text-[10px] uppercase text-foreground-tertiary">
            Capabilities
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {connector.capabilities.map((value) => (
              <Badge key={value} variant="neutral">
                {value}
              </Badge>
            ))}
          </div>
        </div>
        <div>
          <p className="font-mono text-[10px] uppercase text-foreground-tertiary">
            Declared scopes
          </p>
          <ul className="mt-2 grid gap-1 font-mono text-foreground-secondary">
            {connector.scopes.map((scope) => (
              <li key={scope}>{scope}</li>
            ))}
          </ul>
        </div>
        <p className="text-foreground-secondary">
          Metadata only. No token, secret, provider client, OAuth code, or raw
          permission grant is exposed in this dashboard.
        </p>
      </div>
    </details>
  );
}

export function ConnectorsWorkspace({
  connectors,
}: {
  connectors: ConnectorRecord[];
}) {
  const [runtimeMode, setRuntimeMode] =
    React.useState<DashboardRuntimeMode>(() =>
      dashboardApiBaseUrl() ? "loading" : "fixture",
    );
  const [liveConnectors, setLiveConnectors] = React.useState<ConnectorRecord[]>([]);
  const [connections, setConnections] = React.useState<
    Record<string, DashboardConnection>
  >({});
  const [csrfToken, setCsrfToken] = React.useState("");
  const [query, setQuery] = React.useState("");
  const [status, setStatus] = React.useState<ConnectorStatus | "all">("all");
  const [auth, setAuth] = React.useState<AuthenticationType | "all">("all");
  const [sort, setSort] = React.useState<SortKey>("connector");
  const [direction, setDirection] = React.useState<SortDirection>("asc");
  const [overrides, setOverrides] = React.useState<
    Record<string, ConnectorStatus>
  >({});
  const [confirmRevoke, setConfirmRevoke] =
    React.useState<ConnectorRecord | null>(null);
  const [notice, setNotice] = React.useState("");

  const loadRuntime = React.useCallback(async () => {
    if (!dashboardApiBaseUrl()) {
      setRuntimeMode("fixture");
      return;
    }
    setRuntimeMode("loading");
    try {
      const session = await readDashboardSessionOrRequireSignIn();
      const payload = await readDashboardConnectors();
      setCsrfToken(session.csrf_token);
      setConnections(
        Object.fromEntries(
          payload.connections.map((connection) => [
            connection.connector_type,
            connection,
          ]),
        ),
      );
      setLiveConnectors(
        toConnectorRecords(payload.descriptors, payload.connections),
      );
      setRuntimeMode("live");
    } catch (error) {
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
  }, []);

  React.useEffect(() => {
    const timeout = window.setTimeout(() => {
      void loadRuntime();
    }, 0);
    return () => window.clearTimeout(timeout);
  }, [loadRuntime]);

  const activeConnectors = runtimeMode === "live" ? liveConnectors : connectors;
  const records = activeConnectors.map((connector) => ({
    ...connector,
    status: overrides[connector.id] ?? connector.status,
  }));
  const normalized = query.trim().toLowerCase();
  const visible = sortConnectors(
    records.filter(
      (connector) =>
        (!normalized ||
          [
            connector.id,
            connector.name,
            connector.provider,
            connector.accountLabel,
          ]
            .join(" ")
            .toLowerCase()
            .includes(normalized)) &&
        (status === "all" || connector.status === status) &&
        (auth === "all" || connector.authenticationType === auth),
    ),
    sort,
    direction,
  );
  const hasFilters = Boolean(query || status !== "all" || auth !== "all");
  const clear = () => {
    setQuery("");
    setStatus("all");
    setAuth("all");
  };
  const onSort = (next: SortKey) => {
    if (next === sort)
      setDirection((value) => (value === "asc" ? "desc" : "asc"));
    else {
      setSort(next);
      setDirection("asc");
    }
  };
  const setSimulated = (
    connector: ConnectorRecord,
    next: ConnectorStatus,
    action: string,
  ) => {
    setOverrides((current) => ({ ...current, [connector.id]: next }));
    setNotice(
      `Simulated ${action} for ${connector.name}. Refresh restores the fixture.`,
    );
  };
  const primaryAction = (connector: ConnectorRecord) =>
    connector.status === "offline"
      ? {
          label: "Simulate connection",
          action: "connection",
          status: "healthy" as const,
        }
      : connector.status === "expired" || connector.status === "revoked"
        ? {
            label: "Simulate reconnect",
            action: "reconnect",
            status: "healthy" as const,
          }
        : null;

  const Actions = ({ connector }: { connector: ConnectorRecord }) => {
    const connection = connections[connector.id];
    const primary = primaryAction(connector);
    return (
      <div className="relative z-20 flex flex-wrap gap-2">
        {primary && (
          <Button
            size="sm"
            onClick={async () => {
              if (runtimeMode === "live") {
                const result = await startConnectorOAuth(connector, csrfToken);
                window.location.assign(result.authorization_url);
                return;
              }
              setSimulated(connector, primary.status, primary.action);
            }}
          >
            <RotateCw aria-hidden="true" />
            {runtimeMode === "live"
              ? connector.status === "offline"
                ? "Connect"
                : "Reconnect"
              : primary.label}
          </Button>
        )}
        <Button
          variant="secondary"
          size="sm"
          disabled={runtimeMode === "live" && !connection}
          onClick={async () => {
            if (runtimeMode === "live" && connection) {
              await checkConnectionHealth(connection.connection_id, csrfToken);
              await loadRuntime();
              setNotice(`Runtime health check completed for ${connector.name}.`);
            } else {
              setNotice(
                `Simulated health check for ${connector.name}. No provider was contacted.`,
              );
            }
          }}
        >
          <Activity aria-hidden="true" />
          {runtimeMode === "live" ? "Run health check" : "Simulate health check"}
        </Button>
        {runtimeMode !== "live" &&
          connector.status !== "offline" &&
          connector.status !== "revoked" && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setConfirmRevoke(connector)}
          >
            <ShieldOff aria-hidden="true" />
            Simulate revoke
          </Button>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-5">
      <PageHeader
        eyebrow="Governance"
        title="Connectors"
        description={
          runtimeMode === "live"
            ? "Review owner-authenticated connector descriptors, connection health, and OAuth start paths."
            : "Review connection descriptors and least-privilege declarations."
        }
        icon={PlugZap}
      />
      {runtimeMode === "unauthenticated" && (
        <SignedOutState description="Sign in to load runtime connector data from the Atlas API." />
      )}
      {runtimeMode !== "unauthenticated" && (
      <div className="rounded-atlas-md border border-info-border bg-info-bg px-4 py-3 text-sm text-foreground">
        {runtimeMode === "live" ? (
          <>
            <strong>Live runtime.</strong> Data is loaded from the
            owner-authenticated Atlas API dashboard facade. Secrets and provider
            tokens stay server-side.
          </>
        ) : runtimeMode === "loading" ? (
          "Loading owner-authenticated connector data..."
        ) : runtimeMode === "error" ? (
          "Runtime connector data is unavailable. Fixture data remains quarantined from release evidence."
        ) : (
          <>
            <strong>Frontend prototype.</strong> No runtime API base URL is
            configured for this build; every action is a session-only
            simulation.
          </>
        )}
      </div>
      )}
      {runtimeMode !== "unauthenticated" && runtimeMode !== "loading" && (
      <p className="sr-only" aria-live="polite">
        {notice}
      </p>
      )}
      {runtimeMode !== "unauthenticated" && runtimeMode !== "loading" && (
      <div className="flex flex-col gap-3 rounded-atlas-lg border border-border-default bg-surface p-3 sm:flex-row sm:flex-wrap sm:items-center">
        <SearchField
          value={query}
          onChange={setQuery}
          placeholder="Search connectors"
          className="w-full sm:max-w-sm"
        />
        <label htmlFor="connector-status" className="sr-only">
          Status
        </label>
        <select
          id="connector-status"
          className={SELECT_CLASS}
          value={status}
          onChange={(event) =>
            setStatus(event.target.value as ConnectorStatus | "all")
          }
        >
          <option value="all">All statuses</option>
          <option value="healthy">Healthy</option>
          <option value="degraded">Degraded</option>
          <option value="expired">Expired</option>
          <option value="revoked">Revoked</option>
          <option value="offline">Offline</option>
        </select>
        <label htmlFor="connector-auth" className="sr-only">
          Authentication type
        </label>
        <select
          id="connector-auth"
          className={SELECT_CLASS}
          value={auth}
          onChange={(event) =>
            setAuth(event.target.value as AuthenticationType | "all")
          }
        >
          <option value="all">All authentication types</option>
          {[
            ...new Set(
              connectors.map((connector) => connector.authenticationType),
            ),
          ].map((value) => (
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
          {visible.length} of {activeConnectors.length}{" "}
          {runtimeMode === "live" ? "runtime connectors" : "fictional connectors"}
        </p>
      </div>
      )}
      {runtimeMode !== "unauthenticated" && runtimeMode !== "loading" && (
      <>
      {visible.length === 0 ? (
        <Card>
          <EmptyState
            icon={PlugZap}
            title="No connectors match these filters"
            description="Clear filters to restore the fictional connector registry."
            action={
              <Button variant="secondary" size="sm" onClick={clear}>
                Clear filters
              </Button>
            }
          />
        </Card>
      ) : (
        <>
          <Card className="hidden overflow-hidden md:block">
            <Table>
              <caption className="sr-only">Connector inventory</caption>
              <TableHeader>
                <TableRow>
                  <TableHead
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
                  <TableHead
                    aria-sort={getAriaSort(sort === "connector", direction)}
                  >
                    <SortHeader
                      label="Connector"
                      sortKey="connector"
                      active={sort === "connector"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(
                      sort === "authentication",
                      direction,
                    )}
                  >
                    <SortHeader
                      label="Authentication"
                      sortKey="authentication"
                      active={sort === "authentication"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "account", direction)}
                  >
                    <SortHeader
                      label="Account"
                      sortKey="account"
                      active={sort === "account"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead
                    aria-sort={getAriaSort(sort === "lastCheck", direction)}
                  >
                    <SortHeader
                      label="Last check"
                      sortKey="lastCheck"
                      active={sort === "lastCheck"}
                      direction={direction}
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead>Session-only actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {visible.map((connector) => (
                  <TableRow key={connector.id}>
                    <TableCell className="align-top text-xs">
                      <StatusBadge
                        status={connector.status}
                        plain
                        className="text-xs"
                      />
                    </TableCell>
                    <TableCell className="min-w-72 align-top whitespace-normal text-xs">
                      <p className="font-medium">{connector.name}</p>
                      <p className="mt-1 text-foreground-secondary">
                        {connector.provider} · v{connector.version}
                      </p>
                      <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                        {connector.id}
                      </p>
                      <ConnectorDetails connector={connector} />
                    </TableCell>
                    <TableCell className="align-top text-xs text-foreground-secondary">
                      {connector.authenticationType}
                    </TableCell>
                    <TableCell className="align-top text-xs text-foreground-secondary">
                      {connector.accountLabel}
                    </TableCell>
                    <TableCell className="align-top text-xs text-foreground-secondary">
                      {connector.lastCheck}
                    </TableCell>
                    <TableCell className="min-w-64 align-top">
                      <Actions connector={connector} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
          <ul className="grid gap-3 md:hidden">
            {visible.map((connector) => (
              <li key={connector.id}>
                <Card>
                  <CardContent className="grid gap-3 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <h2 className="font-medium">{connector.name}</h2>
                        <p className="mt-1 font-mono text-[10px] text-foreground-tertiary">
                          {connector.id}
                        </p>
                      </div>
                      <StatusBadge status={connector.status} />
                    </div>
                    <p className="text-sm text-foreground-secondary">
                      {connector.statusSummary}
                    </p>
                    <dl className="grid grid-cols-2 gap-3 text-xs">
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Provider
                        </dt>
                        <dd>{connector.provider}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Authentication
                        </dt>
                        <dd>{connector.authenticationType}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Account
                        </dt>
                        <dd>{connector.accountLabel}</dd>
                      </div>
                      <div>
                        <dt className="font-mono text-[10px] uppercase text-foreground-tertiary">
                          Last check
                        </dt>
                        <dd>{connector.lastCheck}</dd>
                      </div>
                    </dl>
                    <ConnectorDetails connector={connector} />
                    <Actions connector={connector} />
                  </CardContent>
                </Card>
              </li>
            ))}
          </ul>
        </>
      )}
      {notice && (
        <div
          role="status"
          className="rounded-atlas-md border border-success-border bg-success-bg px-4 py-3 text-sm text-foreground"
        >
          {notice}
        </div>
      )}
      </>
      )}
      <Dialog
        open={Boolean(confirmRevoke)}
        onOpenChange={(open) => {
          if (!open) setConfirmRevoke(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Simulate connector revocation?</DialogTitle>
            <DialogDescription>
              This changes only the selected fixture in memory. No provider
              grant, token, connection, or credential will be touched.
            </DialogDescription>
          </DialogHeader>
          {confirmRevoke && (
            <div className="rounded-atlas-md border border-border-default bg-surface-secondary p-4 text-sm">
              <p className="font-medium">{confirmRevoke.name}</p>
              <p className="mt-1 font-mono text-xs text-foreground-tertiary">
                {confirmRevoke.id}
              </p>
            </div>
          )}
          <DialogFooter>
            <Button variant="ghost" onClick={() => setConfirmRevoke(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (confirmRevoke)
                  setSimulated(confirmRevoke, "revoked", "revocation");
                setConfirmRevoke(null);
              }}
            >
              Confirm simulated revocation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
