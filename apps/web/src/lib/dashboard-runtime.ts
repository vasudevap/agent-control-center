import type {
  AuthenticationType,
  ConnectorRecord,
  ConnectorStatus,
} from "@/app/(shell)/connectors/connector-data";
import type { RunRecord, RunStatus, RunTrigger } from "@/app/(shell)/runs/run-data";
import type { ApprovalRecord, ApprovalState } from "@/app/(shell)/approvals/approval-data";
import type { AuditEvent, AuditResult } from "@/app/(shell)/audit/audit-data";
import type { AlertRecord } from "@/app/(shell)/alerts/alert-data";

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
  status: string;
  risk_level: string;
  supports_manual_run: boolean;
}

export interface DashboardRun {
  run_id: string;
  agent_id: string;
  status: string;
  trigger_source: string;
  correlation_id: string | null;
  timeout_seconds: number;
  retry_count: number;
  failure_reason_code: string | null;
  started_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
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

export interface DashboardAuditEvent {
  audit_event_id: string;
  event_type: string;
  actor_type: string;
  actor_id: string;
  channel: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  result: string;
  reason_code: string | null;
  correlation_id: string | null;
  redaction_state: string;
  metadata_json: Record<string, unknown>;
  occurred_at: string;
}

export interface DashboardMonitoring {
  readiness_status: "ready" | "not_ready";
  readiness_problem_count: number;
  agent_count: number;
  runtime_origin: string;
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

export function dashboardApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "";
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

export const readDashboardConnectors = () =>
  dashboardRequest<{
    descriptors: DashboardConnectorDescriptor[];
    connections: DashboardConnection[];
  }>("/api/v1/dashboard/connectors");

export const readDashboardAgents = () =>
  dashboardRequest<DashboardAgent[]>("/api/v1/dashboard/agents");

export const readDashboardRuns = () =>
  dashboardRequest<DashboardRun[]>("/api/v1/dashboard/runs");

export const readDashboardRun = (runId: string) =>
  dashboardRequest<DashboardRun>(
    `/api/v1/dashboard/runs/${encodeURIComponent(runId)}`,
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
  dashboardRequest<DashboardAuditEvent[]>("/api/v1/dashboard/audit");

export const readDashboardMonitoring = () =>
  dashboardRequest<DashboardMonitoring>("/api/v1/dashboard/monitoring");

export const createDashboardRun = (agentId: string, csrfToken: string) =>
  dashboardRequest<DashboardRun>("/api/v1/dashboard/runs", {
    method: "POST",
    body: JSON.stringify({ agent_id: agentId }),
    headers: {
      "Idempotency-Key": `dashboard-${crypto.randomUUID()}`,
      "X-Atlas-CSRF-Token": csrfToken,
    },
  });

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
    const startedAt = run.started_at ?? run.created_at;
    return {
      id: run.run_id,
      agent: {
        id: run.agent_id,
        name: agent?.display_name ?? run.agent_id,
      },
      status: runStatus(run.status),
      trigger: runTrigger(run.trigger_source),
      startedAt,
      completedAt: run.completed_at ?? undefined,
      duration: durationLabel(startedAt, run.completed_at),
      retryCount: run.retry_count,
      correlationId: run.correlation_id ?? "correlation_unavailable",
      summary: run.failure_reason_code
        ? `Runtime run recorded failure code ${run.failure_reason_code}.`
        : `Runtime ${run.trigger_source} run is ${run.status}.`,
      costEstimate: "Not estimated",
      error: run.failure_reason_code
        ? {
            code: run.failure_reason_code,
            category: "Runtime",
            retryable: false,
            summary: "Runtime reported a normalized failure reason.",
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

export function toAuditEvents(events: DashboardAuditEvent[]): AuditEvent[] {
  return events.map((event) => ({
    id: event.audit_event_id,
    occurredAt: event.occurred_at,
    actor: event.actor_id,
    actorType: event.actor_type === "human_owner" ? "Human" : event.actor_type,
    action: event.action || event.event_type,
    result: auditResult(event.result),
    resourceType: event.resource_type,
    resourceId: event.resource_id ?? "resource_unavailable",
    summary: `${event.event_type} ${event.result}.`,
    reason: event.reason_code
      ? `Reason code: ${event.reason_code}. Redaction: ${event.redaction_state}.`
      : `Redaction: ${event.redaction_state}.`,
    correlationId: event.correlation_id ?? "correlation_unavailable",
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
      evidence: `${monitoring.agent_count} agent registration(s) visible through the owner-authenticated dashboard facade.`,
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

function authenticationType(value: string): AuthenticationType {
  const normalized = value.toLowerCase();
  if (normalized.includes("webhook")) return "Webhook signature";
  if (normalized.includes("service")) return "Service identity";
  return "OAuth 2.0";
}

function runStatus(value: string): RunStatus {
  if (
    value === "queued" ||
    value === "running" ||
    value === "succeeded" ||
    value === "failed" ||
    value === "cancelled"
  ) {
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

function auditResult(value: string): AuditResult {
  if (value === "approved" || value === "rejected" || value === "failed") {
    return value;
  }
  return "succeeded";
}

function lastCheckLabel(value: string | null) {
  if (!value) return "Never";
  return new Date(value).toLocaleString();
}

function durationLabel(startedAt: string, completedAt: string | null) {
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
