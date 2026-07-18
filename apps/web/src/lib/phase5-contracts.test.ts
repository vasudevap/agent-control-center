import { describe, expect, it } from "vitest";

import {
  DASHBOARD_PHASE5_COMPATIBILITY_MAP,
  type Phase5AgentDescriptor,
  type Phase5ApprovalEvidence,
  type Phase5Run,
  phase5CompatibilitySummary,
  toDashboardAgent,
  toDashboardApproval,
  toDashboardRun,
} from "./phase5-contracts";

const createdAt = "2026-07-18T12:00:00.000Z";

describe("Phase 5 dashboard contract compatibility", () => {
  it("maps the required Phase 5 surfaces without inventing missing routes", () => {
    expect(DASHBOARD_PHASE5_COMPATIBILITY_MAP).toEqual([
      expect.objectContaining({
        surface: "agents",
        backendRoute: "/api/v1/agents",
        dashboardRoute: "/agents",
        compatibility: "mapped",
      }),
      expect.objectContaining({
        surface: "runs",
        backendRoute: "/api/v1/runs",
        dashboardRoute: "/runs",
        compatibility: "mapped",
      }),
      expect.objectContaining({
        surface: "approvals",
        backendRoute: "/api/v1/approvals",
        dashboardRoute: "/approvals",
        compatibility: "mapped",
      }),
      expect.objectContaining({
        surface: "manual-handling",
        backendRoute: "/api/v1/manual-handling",
        dashboardRoute: null,
        compatibility: "deferred",
      }),
      expect.objectContaining({
        surface: "audit",
        backendRoute: "audit_events",
        dashboardRoute: "/audit",
        compatibility: "mapped",
      }),
      expect.objectContaining({
        surface: "knowledge-facts",
        backendRoute: "/api/v1/knowledge/facts",
        dashboardRoute: null,
        compatibility: "deferred",
      }),
      expect.objectContaining({
        surface: "knowledge-questions",
        backendRoute: "/api/v1/knowledge/questions",
        dashboardRoute: null,
        compatibility: "deferred",
      }),
    ]);
    expect(phase5CompatibilitySummary()).toEqual({
      mapped: 4,
      deferred: 3,
      total: 7,
    });
  });

  it("adapts Phase 5 agent descriptors to dashboard inventory fields", () => {
    const descriptor: Phase5AgentDescriptor = {
      agent_id: "agt_1",
      slug: "gmail-agent",
      display_name: "Gmail Agent",
      description: "Governed mailbox assistant.",
      version: "0.1.0",
      descriptor_version: 1,
      status: "active",
      health_status: "healthy",
      risk_level: "medium",
      capabilities: ["mail.classify"],
      allowed_tools: ["connector.gmail.readonly"],
      required_connectors: ["gmail"],
      configuration_schema_ref: null,
      configuration_schema: {},
      supports_manual_run: true,
      supports_scheduled_run: true,
      created_at: createdAt,
      updated_at: createdAt,
    };

    expect(toDashboardAgent(descriptor)).toEqual({
      id: "agt_1",
      name: "Gmail Agent",
      description: "Governed mailbox assistant.",
      status: "active",
      health: "healthy",
      version: "0.1.0",
      risk: "medium",
      capabilities: ["mail.classify"],
      connectors: ["gmail"],
      permissions: ["connector.gmail.readonly"],
      supportsManualRun: true,
      supportsScheduledRun: true,
    });
  });

  it("adapts Phase 5 run lifecycle fields without fixture-only statuses", () => {
    const run: Phase5Run = {
      run_id: "run_1",
      agent_id: "agt_1",
      status: "queued",
      trigger_source: "manual",
      correlation_id: "corr_1",
      queue_job_id: "job_1",
      timeout_seconds: 300,
      retry_count: 0,
      failure_reason_code: null,
      started_at: null,
      completed_at: null,
      cancelled_at: null,
      created_at: createdAt,
      updated_at: createdAt,
    };

    expect(toDashboardRun(run)).toEqual({
      id: "run_1",
      agentId: "agt_1",
      status: "queued",
      trigger: "Manual",
      correlationId: "corr_1",
      retryCount: 0,
      failureReasonCode: null,
      startedAt: null,
      completedAt: null,
    });
  });

  it("adapts approval evidence while preserving continuation state", () => {
    const approval: Phase5ApprovalEvidence = {
      approval_id: "apr_1",
      status: "approved",
      revision: 2,
      action_type: "send_draft",
      action_reference: "draft_1",
      expires_at: null,
      created_at: createdAt,
      action_payload_hash: "sha256:123",
      evidence_summary: { risk: "medium" },
      decision_context_manifest: { exact_content_binding: true },
      continuation_status: "pending",
      superseded_by_approval_id: null,
    };

    expect(toDashboardApproval(approval)).toEqual({
      id: "apr_1",
      state: "Approved",
      revision: 2,
      action: "send_draft",
      target: "draft_1",
      requestedAt: createdAt,
      expiresAt: null,
      continuationStatus: "pending",
    });
  });
});
