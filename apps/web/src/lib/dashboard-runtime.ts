import type {
  AgentHealth,
  AgentRecord,
  AgentStatus,
} from "@/app/(shell)/agents/agent-data";
import type {
  AuthenticationType,
  ConnectorRecord,
  ConnectorStatus,
} from "@/app/(shell)/connectors/connector-data";
import type { RunRecord, RunStatus, RunTrigger } from "@/app/(shell)/runs/run-data";
import type { ApprovalRecord, ApprovalState } from "@/app/(shell)/approvals/approval-data";
import type { AuditEvent, AuditResult } from "@/app/(shell)/audit/audit-data";
import type {
  AlertRecord,
  AlertSeverity,
  AlertStatus,
} from "@/app/(shell)/alerts/alert-data";

export type DashboardRuntimeMode =
  | "fixture"
  | "loading"
  | "live"
  | "unauthenticated"
  | "error";

interface ApiEnvelope<T> {
  data: T;
  meta?: { correlation_id?: string; next_cursor?: string | null };
  error?: { code?: string; message?: string };
}

export interface DashboardSession {
  authenticated: boolean;
  csrf_token: string;
  user: {
    user_id: string;
    email: string | null;
    display_name: string | null;
    identity_provider: string;
    status: string;
  };
}

export interface DashboardConnectorDescriptor {
  connector_type: string;
  display_name: string;
  version: string;
  authentication_type: string;
  status: string;
  supported_operations: string[];
  required_scopes: string[] | Record<string, string[]>;
  supports_health_check: boolean;
  supports_revocation: boolean;
  supports_refresh: boolean;
}

export interface DashboardConnection {
  connection_id: string;
  connector_type: string;
  display_name: string;
  account_identifier: string;
  status: string;
  granted_scopes: string[];
  health_status: string;
  last_success_at: string | null;
  last_failure_at: string | null;
  last_health_checked_at: string | null;
  last_error_code: string | null;
}

export interface DashboardAgent {
  agent_id: string;
  slug: string;
  display_name: string;
  description: string;
  version?: string;
  status: string;
  risk_level: string;
  capabilities?: string[];
  allowed_tools?: string[];
  required_connectors?: string[];
  supports_manual_run: boolean;
  supports_scheduled_run?: boolean;
  health_status?: string;
  health_checked_at?: string | null;
  last_error_code?: string | null;
  owner_user_id?: string | null;
  lifecycle_status?: string;
  environment?: string;
  monitoring_mode?: "heartbeat" | "activity_only";
  heartbeat_interval_seconds?: number | null;
  tags?: string[];
  repository_url?: string | null;
  deployment_url?: string | null;
  expected_version?: string | null;
  observed_health?: string;
  reported_health?: string;
  last_agent_version?: string | null;
  last_build_sha?: string | null;
  active_surface_visible?: boolean;
}

export interface DashboardRun {
  agent_execution_id: string;
  agent_id: string;
  external_execution_id: string;
  status: string;
  trigger: string;
  started_at: string | null;
  finished_at: string | null;
  duration_ms: number | null;
  summary: string | null;
  error_code: string | null;
  correlation_id: string | null;
  agent_version: string | null;
  build_sha: string | null;
  first_reported_at: string;
  last_reported_at: string;
  terminal_at: string | null;
}

export interface DashboardAlert {
  alert_id: string;
  agent_id: string;
  condition_key: string;
  status: "open" | "acknowledged" | "resolved";
  severity: "info" | "warning" | "error" | "critical";
  first_seen_at: string;
  last_seen_at: string;
  acknowledged_at: string | null;
  acknowledged_by_user_id: string | null;
  resolved_at: string | null;
  resolved_reason: string | null;
  evidence_json: Record<string, unknown>;
}

export interface DashboardActivityEvent {
  activity_event_id: string;
  agent_id: string | null;
  source_type: string;
  source_id: string;
  event_type: string;
  severity: "info" | "warning" | "error" | "critical";
  summary: string;
  correlation_id: string | null;
  actor_type: string;
  actor_id: string | null;
  metadata_json: Record<string, unknown>;
  occurred_at: string;
}

export interface DashboardEnrollmentRequest {
  slug: string;
  display_name: string;
  description: string;
  environment: string;
  monitoring_mode: "heartbeat" | "activity_only";
  heartbeat_interval_seconds: number | null;
  tags?: string[];
  repository_url?: string | null;
  deployment_url?: string | null;
  expected_version?: string | null;
}

export interface DashboardEnrollmentResponse {
  agent: DashboardAgent;
  credential: {
    credential_id: string;
    credential_lookup_id: string;
    plaintext_token: string;
    scope: string;
  };
}

export interface DashboardLifecycleResponse {
  agent: DashboardAgent;
  credential?: DashboardEnrollmentResponse["credential"];
}

export interface DashboardApproval {
  approval_id: string;
  status: string;
  revision: number;
  action_type: string;
  action_reference: string;
  expires_at: string | null;
  created_at: string;
}

export interface DashboardMonitoring {
  readiness_status: "ready" | "not_ready";
  readiness_problem_count: number;
  readiness_problems?: string[];
  agent_count: number;
  runtime_origin: string;
  agent_health_evaluator?: {
    enabled: boolean;
    status: string;
    last_completed_at?: string | null;
    stale_after_seconds?: number;
  };
}

export class DashboardApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "DashboardApiError";
  }
}

const LOCAL_DASHBOARD_API_BASE_URL = "https://api.atlas.grafley.com";

export function dashboardApiBaseUrl() {
  const configuredUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
  if (configuredUrl) return configuredUrl;

  if (
    process.env.NODE_ENV === "development" &&
    typeof window !== "undefined" &&
    ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname)
  ) {
    return LOCAL_DASHBOARD_API_BASE_URL;
  }

  return "";
}

export function dashboardSignInUrl() {
  const baseUrl = dashboardApiBaseUrl();
  return baseUrl ? `${baseUrl}/auth/owner/google/start` : "";
}

export async function dashboardRequest<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const baseUrl = dashboardApiBaseUrl();
  if (!baseUrl) {
    throw new DashboardApiError(
      0,
      "dashboard_api_unconfigured",
      "Dashboard API base URL is not configured.",
    );
  }
  const response = await fetch(`${baseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...init.headers,
    },
  });
  const payload = (await response.json().catch(() => ({}))) as ApiEnvelope<T>;
  if (!response.ok) {
    throw new DashboardApiError(
      response.status,
      payload.error?.code ?? "dashboard_api_error",
      payload.error?.message ?? "Dashboard API request failed.",
    );
  }
  return payload.data;
}

export const readDashboardSession = () =>
  dashboardRequest<DashboardSession>("/api/v1/dashboard/session");

export async function readDashboardSessionOrRequireSignIn() {
  try {
    return await readDashboardSession();
  } catch (error) {
    if (error instanceof DashboardApiError && error.status === 401) {
      throw error;
    }
    throw new DashboardApiError(
      401,
      "owner_session_missing",
      "Owner session is not authorized.",
    );
  }
}

export const readDashboardConnectors = () =>
  dashboardRequest<{
    descriptors: DashboardConnectorDescriptor[];
    connections: DashboardConnection[];
  }>("/api/v1/dashboard/connectors");

export const readDashboardAgents = () =>
  dashboardRequest<DashboardAgent[]>("/api/v1/dashboard/agents");

export const readDashboardRuns = () =>
  dashboardRequest<DashboardRun[]>("/api/v1/executions");

export const readDashboardRun = (runId: string) =>
  dashboardRequest<DashboardRun>(
    `/api/v1/executions/${encodeURIComponent(runId)}`,
  );

export const readDashboardApprovals = (status = "pending") =>
  dashboardRequest<DashboardApproval[]>(
    `/api/v1/dashboard/approvals?status=${encodeURIComponent(status)}`,
  );

export const readDashboardApproval = (approvalId: string) =>
  dashboardRequest<DashboardApproval>(
    `/api/v1/dashboard/approvals/${encodeURIComponent(approvalId)}`,
  );

export const readDashboardAudit = () =>
  dashboardRequest<DashboardActivityEvent[]>("/api/v1/activity");

export const readDashboardAlerts = () =>
  dashboardRequest<DashboardAlert[]>("/api/v1/alerts");

export const acknowledgeDashboardAlert = (alertId: string, csrfToken: string) =>
  dashboardRequest<DashboardAlert>(
    `/api/v1/alerts/${encodeURIComponent(alertId)}/acknowledge`,
    {
      method: "POST",
      headers: { "X-Atlas-CSRF-Token": csrfToken },
    },
  );

export const enrollDashboardAgent = (
  payload: DashboardEnrollmentRequest,
  csrfToken: string,
) =>
  dashboardRequest<DashboardEnrollmentResponse>("/api/v1/dashboard/agents", {
    method: "POST",
    body: JSON.stringify(payload),
    headers: {
      "X-Atlas-CSRF-Token": csrfToken,
      "Idempotency-Key": `agent-enroll-${crypto.randomUUID()}`,
    },
  });

const agentLifecycleRequest = (agentId: string, path: string, csrfToken: string) =>
  dashboardRequest<DashboardLifecycleResponse>(
    `/api/v1/dashboard/agents/${encodeURIComponent(agentId)}${path}`,
    {
      method: "POST",
      headers: {
        "X-Atlas-CSRF-Token": csrfToken,
        "Idempotency-Key": `agent-lifecycle-${crypto.randomUUID()}`,
      },
    },
  );

export const rotateDashboardAgentCredential = (
  agentId: string,
  csrfToken: string,
) => agentLifecycleRequest(agentId, "/credentials/rotate", csrfToken);

export const disconnectDashboardAgent = (agentId: string, csrfToken: string) =>
  agentLifecycleRequest(agentId, "/disconnect", csrfToken);

export const reconnectDashboardAgent = (agentId: string, csrfToken: string) =>
  agentLifecycleRequest(agentId, "/reconnect", csrfToken);

export const archiveDashboardAgent = (agentId: string, csrfToken: string) =>
  agentLifecycleRequest(agentId, "/archive", csrfToken);

export const readDashboardMonitoring = () =>
  dashboardRequest<DashboardMonitoring>("/api/v1/dashboard/monitoring");

export const startConnectorOAuth = (
  connector: ConnectorRecord,
  csrfToken: string,
) =>
  dashboardRequest<{ authorization_url: string }>(
    "/api/v1/dashboard/connectors/oauth/start",
    {
      method: "POST",
      body: JSON.stringify({
        connector_type: connector.id,
        requested_scopes: connector.scopes,
        redirect_uri: `${window.location.origin}/oauth/google/callback`,
      }),
      headers: { "X-Atlas-CSRF-Token": csrfToken },
    },
  );

export const checkConnectionHealth = (
  connectionId: string,
  csrfToken: string,
) =>
  dashboardRequest<DashboardConnection>(
    `/api/v1/dashboard/connections/${encodeURIComponent(connectionId)}/health`,
    {
      method: "POST",
      headers: { "X-Atlas-CSRF-Token": csrfToken },
    },
  );

export function toAgentRecords(
  agents: DashboardAgent[],
  runs: DashboardRun[] = [],
): AgentRecord[] {
  const latestRunByAgent = new Map<string, DashboardRun>();
  for (const run of runs) {
    const current = latestRunByAgent.get(run.agent_id);
    if (
      !current ||
      +new Date(run.last_reported_at) > +new Date(current.last_reported_at)
    ) {
      latestRunByAgent.set(run.agent_id, run);
    }
  }

  return agents.map((agent) => {
    const latestRun = latestRunByAgent.get(agent.agent_id);
    const observedHealth = agent.observed_health ?? agent.health_status;
    const reportedHealth = agent.reported_health ?? "unknown";
    const lastRunAt =
      latestRun?.last_reported_at ?? agent.health_checked_at ?? "";
    const hasSchedule = agent.supports_scheduled_run === true;
      const currentIssue =
        observedHealth && !["online", "not_monitored"].includes(observedHealth)
          ? `Observed health is ${observedHealth}.`
          : reportedHealth && ["degraded", "unhealthy"].includes(reportedHealth)
            ? `Agent reported ${reportedHealth} health.`
            : agent.last_error_code
              ? `Runtime health reported ${agent.last_error_code}.`
              : undefined;

    return {
      id: agent.agent_id,
      name: agent.display_name,
      description: agent.description,
      status: agentStatus(agent, latestRun),
      health: agentHealth(observedHealth, reportedHealth),
      lifecycleStatus: agent.lifecycle_status,
      activeSurfaceVisible: agent.active_surface_visible,
      observedHealth: healthLabel(observedHealth ?? "unknown"),
      reportedHealth: healthLabel(reportedHealth ?? "unknown"),
      owner: agent.environment ?? "Owner enrolled",
      environment: agent.environment ?? "production",
      lastRun: latestRun
        ? lastCheckLabel(latestRun.last_reported_at)
        : "No executions recorded",
      lastRunAt: lastRunAt || "1970-01-01T00:00:00.000Z",
      nextRun:
        agent.monitoring_mode === "heartbeat" && agent.heartbeat_interval_seconds
          ? `Heartbeat every ${agent.heartbeat_interval_seconds}s`
          : hasSchedule
            ? "Schedule configured"
            : "Activity only",
      nextRunAt: undefined,
      version:
        agent.last_agent_version ??
        agent.expected_version ??
        agent.version ??
        "Unreported",
      buildSha: agent.last_build_sha,
      currentIssue,
      issueSummary: currentIssue,
      responsibilities: [agent.description],
      capabilities: agent.capabilities ?? [],
      connectors: agent.required_connectors ?? [],
      permissions: agent.allowed_tools ?? [],
      recentActivity: latestRun
        ? [
            `Latest reported execution ${latestRun.external_execution_id} is ${latestRun.status}.`,
          ]
        : ["No reported execution history is recorded for this agent."],
    };
  });
}

export function fleetPulseFromRuntime(
  agents: AgentRecord[],
  approvals: ApprovalRecord[],
  alerts: AlertRecord[],
) {
  return {
    totalAgents: agents.length,
    healthyAgents: agents.filter((agent) => agent.health === "healthy").length,
    degradedAgents: agents.filter((agent) => agent.health === "degraded").length,
    offlineAgents: agents.filter((agent) => agent.health === "offline").length,
    runningAgents: agents.filter(
      (agent) => agent.status === "running" || agent.status === "active",
    ).length,
    pendingApprovals: approvals.filter((approval) => approval.state === "Pending")
      .length,
    activeAlerts: alerts.filter((alert) => alert.status === "active").length,
  };
}

export function ownerDisplayName(session: DashboardSession | null) {
  return (
    session?.user.display_name?.trim() ||
    session?.user.email?.split("@")[0]?.trim() ||
    "Owner"
  );
}

export function ownerInitials(session: DashboardSession | null) {
  const displayName = ownerDisplayName(session);
  const parts = displayName
    .split(/\s+/)
    .map((part) => part[0])
    .filter(Boolean);
  return (parts.length > 1 ? `${parts[0]}${parts[1]}` : displayName.slice(0, 2))
    .toUpperCase();
}

export function toConnectorRecords(
  descriptors: DashboardConnectorDescriptor[],
  connections: DashboardConnection[],
): ConnectorRecord[] {
  return descriptors.map((descriptor) => {
    const connection = connections.find(
      (item) => item.connector_type === descriptor.connector_type,
    );
    return {
      id: descriptor.connector_type,
      name: descriptor.display_name,
      provider: descriptor.connector_type,
      version: descriptor.version,
      status: connectorStatus(descriptor, connection),
      authenticationType: authenticationType(descriptor.authentication_type),
      accountLabel:
        connection?.account_identifier || connection?.display_name || "Not connected",
      capabilities: descriptor.supported_operations,
      scopes: scopesForDisplay(connection?.granted_scopes, descriptor.required_scopes),
      lastCheck: lastCheckLabel(
        connection?.last_health_checked_at ??
          connection?.last_success_at ??
          connection?.last_failure_at ??
          null,
      ),
      lastCheckAt:
        connection?.last_health_checked_at ??
        connection?.last_success_at ??
        connection?.last_failure_at ??
        null,
      statusSummary: connection
        ? connection.last_error_code
          ? `Runtime health returned ${connection.health_status}; last error ${connection.last_error_code}.`
          : `Runtime connection status is ${connection.status}; health is ${connection.health_status}.`
        : "No owner connection is configured for this connector type.",
    };
  });
}

export function toRunRecords(
  runs: DashboardRun[],
  agents: DashboardAgent[],
): RunRecord[] {
  const agentById = new Map(agents.map((agent) => [agent.agent_id, agent]));
  return runs.map((run) => {
    const agent = agentById.get(run.agent_id);
    const startedAt = run.started_at ?? run.first_reported_at;
    return {
      id: run.agent_execution_id,
      agent: {
        id: run.agent_id,
        name: agent?.display_name ?? run.agent_id,
      },
      status: runStatus(run.status),
      trigger: runTrigger(run.trigger),
      startedAt,
      completedAt: run.finished_at ?? undefined,
      duration: durationLabel(startedAt, run.finished_at, run.duration_ms),
      retryCount: 0,
      correlationId: run.correlation_id ?? "correlation_unavailable",
      summary:
        run.summary ??
        (run.error_code
          ? `Agent execution recorded failure code ${run.error_code}.`
          : `Agent-reported ${run.trigger} execution is ${run.status}.`),
      costEstimate: "Not estimated",
      error: run.error_code
        ? {
            code: run.error_code,
            category: "Agent reported",
            retryable: false,
            summary: "Agent reported a normalized failure reason.",
          }
        : undefined,
      approvalIds: [],
      artifactIds: [],
      steps: [],
      logs: [],
    };
  });
}

export function toApprovalRecords(approvals: DashboardApproval[]): ApprovalRecord[] {
  return approvals.map((approval) => ({
    id: approval.approval_id,
    state: approvalState(approval.status),
    reviewProgress: "Unopened",
    risk: "Medium",
    action: approval.action_type,
    target: approval.action_reference,
    payloadSummary: `Runtime approval revision ${approval.revision}.`,
    consequence: "The runtime will continue only after a governed approval decision.",
    scope: "Runtime approval contract",
    agent: { id: "runtime", name: "Atlas Runtime" },
    runId: approval.action_reference,
    requestedAt: approval.created_at,
    expiresAt: approval.expires_at ?? undefined,
    policy: "Runtime approval policy",
    policyReason: "Approval contract requires human authorization.",
    environment: "Hosted",
    evidence: {
      source: "Atlas API approval facade",
      provenance: "Metadata-only owner-authenticated runtime record.",
      preview: "Sensitive payload details are not exposed in the dashboard list.",
      complete: true,
    },
    activity: [
      {
        at: approval.created_at,
        actor: "Atlas Runtime",
        detail: "Recorded approval request metadata.",
      },
    ],
    executionOutcome: "Not available",
  }));
}

export function toAuditEvents(events: DashboardActivityEvent[]): AuditEvent[] {
  return events.map((event) => ({
    id: event.activity_event_id,
    occurredAt: event.occurred_at,
    actor: event.actor_id ?? event.actor_type,
    actorType: event.actor_type === "human_owner" ? "Human" : event.actor_type,
    action: event.event_type,
    result: activityResult(event.severity),
    resourceType: event.source_type,
    resourceId: event.source_id,
    summary: event.summary,
    reason: `Material activity event ${event.event_type}.`,
    correlationId: event.correlation_id ?? "correlation_unavailable",
  }));
}

export function toAlertRecords(alerts: DashboardAlert[]): AlertRecord[] {
  return alerts.map((alert) => ({
    id: alert.alert_id,
    severity: alertSeverity(alert.severity),
    status: alertStatus(alert.status),
    title: alertTitle(alert),
    description: alertDescription(alert),
    timestamp: lastCheckLabel(alert.last_seen_at),
    raisedAt: alert.first_seen_at,
    source: alert.agent_id,
    sourceAgentId: alert.agent_id,
    category: "Runtime",
    evidence: JSON.stringify(alert.evidence_json),
    correlationId: alert.condition_key,
  }));
}

export function toMonitoringAlerts(monitoring: DashboardMonitoring): AlertRecord[] {
  const ready = monitoring.readiness_status === "ready";
  return [
    {
      id: "runtime-readiness",
      severity: ready ? "information" : "warning",
      status: ready ? "resolved" : "active",
      title: ready ? "Hosted runtime is ready" : "Hosted runtime readiness problem",
      description: ready
        ? "The Atlas API readiness contract reports no active readiness blockers."
        : `${monitoring.readiness_problem_count} readiness problem(s) reported by the Atlas API.`,
      timestamp: "Live",
      raisedAt: new Date().toISOString(),
      source: monitoring.runtime_origin,
      category: "Runtime",
      evidence: `${monitoring.agent_count} agent registration(s) visible through owner-authenticated Atlas APIs.`,
      correlationId: "runtime-monitoring",
    },
  ];
}

function scopesForDisplay(
  grantedScopes: string[] | undefined,
  requiredScopes: DashboardConnectorDescriptor["required_scopes"],
) {
  if (grantedScopes?.length) return grantedScopes;
  if (Array.isArray(requiredScopes)) return requiredScopes;
  return [...new Set(Object.values(requiredScopes).flat())];
}

function connectorStatus(
  descriptor: DashboardConnectorDescriptor,
  connection?: DashboardConnection,
): ConnectorStatus {
  if (!connection) return "offline";
  if (connection.status === "revoked") return "revoked";
  if (connection.status === "expired") return "expired";
  if (connection.health_status === "healthy") return "healthy";
  if (connection.health_status === "degraded") return "degraded";
  if (connection.health_status === "unhealthy") return "offline";
  return descriptor.status === "active" ? "degraded" : "offline";
}

function agentStatus(
  agent: DashboardAgent,
  latestRun: DashboardRun | undefined,
): AgentStatus {
  if (latestRun?.status === "running") return "running";
  if (latestRun?.status === "accepted") return "queued";
  if (agent.lifecycle_status === "disconnected" || agent.lifecycle_status === "archived") {
    return "paused";
  }
  if (agent.status === "disabled" || agent.status === "retired") return "paused";
  return "active";
}

function agentHealth(
  observedValue: string | undefined,
  reportedValue: string | undefined,
): AgentHealth {
  if (observedValue === "online" && reportedValue !== "unhealthy") return "healthy";
  if (
    observedValue === "offline" ||
    observedValue === "disconnected" ||
    observedValue === "archived" ||
    reportedValue === "unhealthy"
  ) {
    return "offline";
  }
  return "degraded";
}

function healthLabel(value: string) {
  return value.replace(/_/g, " ");
}

function authenticationType(value: string): AuthenticationType {
  const normalized = value.toLowerCase();
  if (normalized.includes("webhook")) return "Webhook signature";
  if (normalized.includes("service")) return "Service identity";
  return "OAuth 2.0";
}

function runStatus(value: string): RunStatus {
  if (
    value === "accepted" ||
    value === "running" ||
    value === "succeeded" ||
    value === "failed" ||
    value === "cancelled" ||
    value === "timed_out"
  ) {
    if (value === "accepted") return "queued";
    if (value === "timed_out") return "timed-out";
    return value;
  }
  return "waiting";
}

function runTrigger(value: string): RunTrigger {
  if (value === "scheduled") return "Scheduled";
  if (value === "event") return "Event";
  return "Manual";
}

function approvalState(value: string): ApprovalState {
  const normalized = value.toLowerCase();
  if (normalized === "approved") return "Approved";
  if (normalized === "rejected") return "Rejected";
  if (normalized === "expired") return "Expired";
  if (normalized === "cancelled") return "Cancelled";
  return "Pending";
}

function activityResult(severity: DashboardActivityEvent["severity"]): AuditResult {
  return severity === "critical" || severity === "error" ? "failed" : "succeeded";
}

function alertSeverity(severity: DashboardAlert["severity"]): AlertSeverity {
  if (severity === "critical") return "critical";
  if (severity === "error") return "high";
  if (severity === "warning") return "warning";
  return "information";
}

function alertStatus(status: DashboardAlert["status"]): AlertStatus {
  if (status === "resolved") return "resolved";
  if (status === "acknowledged") return "investigating";
  return "active";
}

function alertTitle(alert: DashboardAlert) {
  const condition = alert.condition_key.split(":").at(-1) ?? "alert";
  return condition.replace(/-/g, " ");
}

function alertDescription(alert: DashboardAlert) {
  if (alert.resolved_reason) return `Resolved: ${alert.resolved_reason}.`;
  if (alert.acknowledged_at) return "Acknowledged; source condition remains tracked.";
  return "Active source condition detected by Atlas.";
}

function lastCheckLabel(value: string | null) {
  if (!value) return "Never";
  return new Date(value).toLocaleString();
}

function durationLabel(
  startedAt: string,
  completedAt: string | null,
  durationMs?: number | null,
) {
  if (durationMs != null) {
    const seconds = Math.round(durationMs / 1000);
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ${seconds % 60}s`;
  }
  if (!completedAt) return "In progress";
  const seconds = Math.max(
    0,
    Math.round((+new Date(completedAt) - +new Date(startedAt)) / 1000),
  );
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${minutes}m ${remainder}s`;
}
