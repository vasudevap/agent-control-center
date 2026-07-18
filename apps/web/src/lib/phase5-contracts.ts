export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };
export type JsonObject = { [key: string]: JsonValue };

export interface Phase5PageMeta {
  correlation_id: string | null;
  next_cursor?: string | null;
}

export interface Phase5Envelope<T> {
  data: T;
  meta: Phase5PageMeta;
}

export type Phase5ListEnvelope<T> = Phase5Envelope<T[]>;

export type Phase5AgentStatus = "active" | "disabled" | "retired";
export type Phase5AgentHealth = "unknown" | "healthy" | "degraded" | "unhealthy";
export type Phase5RiskLevel = "low" | "medium" | "high";

export interface Phase5AgentDescriptor {
  agent_id: string;
  slug: string;
  display_name: string;
  description: string;
  version: string;
  descriptor_version: number;
  status: Phase5AgentStatus;
  risk_level: Phase5RiskLevel;
  capabilities: string[];
  allowed_tools: string[];
  required_connectors: string[];
  health_status?: Phase5AgentHealth;
  configuration_schema_ref: string | null;
  configuration_schema: JsonObject;
  supports_manual_run: boolean;
  supports_scheduled_run: boolean;
  created_at: string;
  updated_at: string;
}

export type DashboardAgentStatus = "active" | "paused";
export type DashboardAgentHealth = "healthy" | "degraded" | "offline";

export interface DashboardAgentCompatibility {
  id: string;
  name: string;
  description: string;
  status: DashboardAgentStatus;
  health: DashboardAgentHealth;
  version: string;
  risk: Phase5RiskLevel;
  capabilities: string[];
  connectors: string[];
  permissions: string[];
  supportsManualRun: boolean;
  supportsScheduledRun: boolean;
}

export type Phase5RunStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled";
export type Phase5RunTrigger = "manual" | "scheduled";

export interface Phase5Run {
  run_id: string;
  agent_id: string;
  status: Phase5RunStatus;
  trigger_source: Phase5RunTrigger;
  correlation_id: string;
  queue_job_id: string | null;
  timeout_seconds: number;
  retry_count: number;
  failure_reason_code: string | null;
  started_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
}

export type DashboardRunStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled";
export type DashboardRunTrigger = "Manual" | "Scheduled";

export interface DashboardRunCompatibility {
  id: string;
  agentId: string;
  status: DashboardRunStatus;
  trigger: DashboardRunTrigger;
  correlationId: string;
  retryCount: number;
  failureReasonCode: string | null;
  startedAt: string | null;
  completedAt: string | null;
}

export type Phase5ApprovalStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "expired"
  | "superseded";

export interface Phase5ApprovalSummary {
  approval_id: string;
  status: Phase5ApprovalStatus;
  revision: number;
  action_type: string;
  action_reference: string;
  expires_at: string | null;
  created_at: string;
}

export interface Phase5ApprovalEvidence extends Phase5ApprovalSummary {
  action_payload_hash: string;
  evidence_summary: JsonObject;
  decision_context_manifest: JsonObject;
  continuation_status: string;
  superseded_by_approval_id: string | null;
}

export type DashboardApprovalState =
  | "Pending"
  | "Approved"
  | "Rejected"
  | "Expired"
  | "Cancelled";

export interface DashboardApprovalCompatibility {
  id: string;
  state: DashboardApprovalState;
  revision: number;
  action: string;
  target: string;
  requestedAt: string;
  expiresAt: string | null;
  continuationStatus?: string;
}

export interface Phase5ManualHandlingRecord {
  manual_handling_id: string;
  status: string;
  agent_id: string | null;
  run_id: string | null;
  source_reference: string;
  reason_category: string;
  sensitivity_classification: string;
  held_at: string;
  resolved_at: string | null;
  metadata_json: JsonObject;
  created_at: string;
}

export interface Phase5KnowledgeFact {
  knowledge_fact_id: string;
  fact_key: string;
  status: string;
  classification: string;
  current_revision_id: string;
  last_confirmed_at: string | null;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
  current_revision: {
    knowledge_fact_revision_id: string;
    revision_number: number;
    display_value: string;
    content_hash: string;
    source_type: string;
    source_reference: string | null;
    provenance_summary: string;
    is_volatile: boolean;
    confirmed_at: string | null;
    created_at: string;
  };
}

export interface Phase5KnowledgeQuestion {
  knowledge_question_id: string;
  status: string;
  required_fact_key: string;
  question_text: string;
  agent_id: string | null;
  source_reference: string | null;
  correlation_id: string;
  expires_at: string | null;
  answered_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Phase5AuditEvent {
  audit_event_id: string;
  event_type: string;
  actor_type: string;
  actor_id: string | null;
  channel: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  result: string;
  reason_code: string | null;
  correlation_id: string;
  redaction_state: "metadata_only";
  metadata_json: JsonObject;
  occurred_at: string;
}

export type DashboardContractSurface =
  | "agents"
  | "runs"
  | "approvals"
  | "manual-handling"
  | "audit"
  | "knowledge-facts"
  | "knowledge-questions";

export interface DashboardContractCompatibility {
  surface: DashboardContractSurface;
  backendRoute: string;
  dashboardRoute: string | null;
  compatibility: "mapped" | "deferred";
  notes: string;
}

export const DASHBOARD_PHASE5_COMPATIBILITY_MAP = [
  {
    surface: "agents",
    backendRoute: "/api/v1/agents",
    dashboardRoute: "/agents",
    compatibility: "mapped",
    notes: "Inventory and detail views can consume descriptors after auth wiring.",
  },
  {
    surface: "runs",
    backendRoute: "/api/v1/runs",
    dashboardRoute: "/runs",
    compatibility: "mapped",
    notes: "Run list/detail fields map to the Phase 5 run lifecycle contract.",
  },
  {
    surface: "approvals",
    backendRoute: "/api/v1/approvals",
    dashboardRoute: "/approvals",
    compatibility: "mapped",
    notes: "Queue/detail can map summaries and evidence without executing actions.",
  },
  {
    surface: "manual-handling",
    backendRoute: "/api/v1/manual-handling",
    dashboardRoute: null,
    compatibility: "deferred",
    notes: "No first-class route exists yet; surface is reserved for Phase 4 work.",
  },
  {
    surface: "audit",
    backendRoute: "audit_events",
    dashboardRoute: "/audit",
    compatibility: "mapped",
    notes: "Dashboard fixture shape aligns with durable audit identity fields.",
  },
  {
    surface: "knowledge-facts",
    backendRoute: "/api/v1/knowledge/facts",
    dashboardRoute: null,
    compatibility: "deferred",
    notes: "No knowledge route exists yet; contract can support future fact review.",
  },
  {
    surface: "knowledge-questions",
    backendRoute: "/api/v1/knowledge/questions",
    dashboardRoute: null,
    compatibility: "deferred",
    notes: "No knowledge route exists yet; contract can support ask-instead-of-guess.",
  },
] satisfies DashboardContractCompatibility[];

export function toDashboardAgent(
  agent: Phase5AgentDescriptor,
): DashboardAgentCompatibility {
  return {
    id: agent.agent_id,
    name: agent.display_name,
    description: agent.description,
    status: agent.status === "active" ? "active" : "paused",
    health: toDashboardAgentHealth(agent.health_status ?? "unknown"),
    version: agent.version,
    risk: agent.risk_level,
    capabilities: agent.capabilities,
    connectors: agent.required_connectors,
    permissions: agent.allowed_tools,
    supportsManualRun: agent.supports_manual_run,
    supportsScheduledRun: agent.supports_scheduled_run,
  };
}

export function toDashboardRun(run: Phase5Run): DashboardRunCompatibility {
  return {
    id: run.run_id,
    agentId: run.agent_id,
    status: run.status,
    trigger: run.trigger_source === "manual" ? "Manual" : "Scheduled",
    correlationId: run.correlation_id,
    retryCount: run.retry_count,
    failureReasonCode: run.failure_reason_code,
    startedAt: run.started_at,
    completedAt: run.completed_at ?? run.cancelled_at,
  };
}

export function toDashboardApproval(
  approval: Phase5ApprovalSummary | Phase5ApprovalEvidence,
): DashboardApprovalCompatibility {
  return {
    id: approval.approval_id,
    state: toDashboardApprovalState(approval.status),
    revision: approval.revision,
    action: approval.action_type,
    target: approval.action_reference,
    requestedAt: approval.created_at,
    expiresAt: approval.expires_at,
    continuationStatus:
      "continuation_status" in approval
        ? approval.continuation_status
        : undefined,
  };
}

export function phase5CompatibilitySummary() {
  const mapped = DASHBOARD_PHASE5_COMPATIBILITY_MAP.filter(
    (item) => item.compatibility === "mapped",
  ).length;
  const deferred = DASHBOARD_PHASE5_COMPATIBILITY_MAP.length - mapped;
  return { mapped, deferred, total: DASHBOARD_PHASE5_COMPATIBILITY_MAP.length };
}

function toDashboardAgentHealth(
  health: Phase5AgentHealth,
): DashboardAgentHealth {
  if (health === "healthy") {
    return "healthy";
  }
  if (health === "degraded" || health === "unhealthy") {
    return "degraded";
  }
  return "offline";
}

function toDashboardApprovalState(
  status: Phase5ApprovalStatus,
): DashboardApprovalState {
  if (status === "approved") {
    return "Approved";
  }
  if (status === "rejected") {
    return "Rejected";
  }
  if (status === "expired") {
    return "Expired";
  }
  if (status === "superseded") {
    return "Cancelled";
  }
  return "Pending";
}
