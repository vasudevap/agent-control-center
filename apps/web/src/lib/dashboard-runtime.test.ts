import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DashboardApiError,
  dashboardRequest,
  dashboardSignInUrl,
  toAuditEvents,
  toConnectorRecords,
  toMonitoringAlerts,
  toRunRecords,
} from "./dashboard-runtime";

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("dashboard runtime facade client", () => {
  it("fails closed when the browser build has no API base URL", async () => {
    await expect(dashboardRequest("/api/v1/dashboard/session")).rejects.toMatchObject({
      code: "dashboard_api_unconfigured",
      status: 0,
    });
  });

  it("uses credentialed API fetches and surfaces owner-session failures", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.atlas.grafley.com/");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "owner_session_missing",
            message: "Owner session is not authorized.",
          },
        }),
        { status: 401 },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(dashboardRequest("/api/v1/dashboard/session")).rejects.toEqual(
      new DashboardApiError(
        401,
        "owner_session_missing",
        "Owner session is not authorized.",
      ),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.atlas.grafley.com/api/v1/dashboard/session",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(dashboardSignInUrl()).toBe(
      "https://api.atlas.grafley.com/auth/owner/google/start",
    );
  });

  it("maps runtime metadata without exposing secret-bearing values", () => {
    const connectors = toConnectorRecords(
      [
        {
          connector_type: "gmail",
          display_name: "Gmail",
          version: "1.0.0",
          authentication_type: "oauth2",
          status: "active",
          supported_operations: ["message.metadata.read"],
          required_scopes: ["gmail.metadata"],
          supports_health_check: true,
          supports_revocation: true,
          supports_refresh: true,
        },
      ],
      [
        {
          connection_id: "con_123",
          connector_type: "gmail",
          display_name: "Gmail Owner",
          account_identifier: "owner@example.com",
          status: "active",
          granted_scopes: ["gmail.metadata"],
          health_status: "healthy",
          last_success_at: "2026-07-22T00:00:00.000Z",
          last_failure_at: null,
          last_health_checked_at: "2026-07-22T00:01:00.000Z",
          last_error_code: null,
        },
      ],
    );
    const runs = toRunRecords(
      [
        {
          run_id: "run_123",
          agent_id: "agt_123",
          status: "queued",
          trigger_source: "manual",
          correlation_id: "corr_123",
          timeout_seconds: 300,
          retry_count: 0,
          failure_reason_code: null,
          started_at: null,
          completed_at: null,
          cancelled_at: null,
          created_at: "2026-07-22T00:00:00.000Z",
          updated_at: "2026-07-22T00:00:00.000Z",
        },
      ],
      [
        {
          agent_id: "agt_123",
          slug: "gmail-agent",
          display_name: "Gmail Agent",
          description: "Synthetic smoke agent",
          status: "active",
          risk_level: "medium",
          supports_manual_run: true,
        },
      ],
    );
    const audit = toAuditEvents([
      {
        audit_event_id: "aud_123",
        event_type: "dashboard.list_connectors",
        actor_type: "human_owner",
        actor_id: "usr_123",
        channel: "dashboard",
        action: "list_connectors",
        resource_type: "connector",
        resource_id: "gmail",
        result: "succeeded",
        reason_code: null,
        correlation_id: "corr_123",
        redaction_state: "redacted",
        metadata_json: { count: 1 },
        occurred_at: "2026-07-22T00:00:00.000Z",
      },
    ]);
    const alerts = toMonitoringAlerts({
      readiness_status: "ready",
      readiness_problem_count: 0,
      agent_count: 1,
      runtime_origin: "atlas-api",
    });

    expect(JSON.stringify({ connectors, runs, audit, alerts })).not.toMatch(
      new RegExp(["secret", "token", "refresh", "access", "grant"].join("|"), "i"),
    );
    expect(connectors[0]).toMatchObject({ id: "gmail", status: "healthy" });
    expect(runs[0]).toMatchObject({
      id: "run_123",
      agent: { name: "Gmail Agent" },
      status: "queued",
    });
    expect(audit[0]).toMatchObject({
      action: "list_connectors",
      result: "succeeded",
    });
    expect(alerts[0]).toMatchObject({
      id: "runtime-readiness",
      status: "resolved",
    });
  });

  it("flattens operation-scoped connector requirements from the hosted API", () => {
    const connectors = toConnectorRecords(
      [
        {
          connector_type: "gmail",
          display_name: "Gmail",
          version: "1.0.0",
          authentication_type: "oauth2",
          status: "active",
          supported_operations: ["gmail.read_metadata", "gmail.create_draft"],
          required_scopes: {
            "gmail.read_metadata": ["gmail.metadata"],
            "gmail.create_draft": ["gmail.metadata", "gmail.modify"],
          },
          supports_health_check: true,
          supports_revocation: true,
          supports_refresh: true,
        },
      ],
      [],
    );

    expect(connectors[0]?.scopes).toEqual(["gmail.metadata", "gmail.modify"]);
  });

  it("maps WO-063 synthetic smoke runtime records into live dashboard state", () => {
    const connectors = toConnectorRecords(
      [
        {
          connector_type: "gmail",
          display_name: "Gmail",
          version: "0.1.0",
          authentication_type: "oauth2",
          status: "active",
          supported_operations: ["gmail.create_draft"],
          required_scopes: {
            "gmail.create_draft": ["https://www.googleapis.com/auth/gmail.modify"],
          },
          supports_health_check: true,
          supports_revocation: true,
          supports_refresh: true,
        },
      ],
      [
        {
          connection_id: "con_smoke",
          connector_type: "gmail",
          display_name: "Synthetic Gmail Smoke Connector",
          account_identifier: "synthetic-smoke+gmail@grafley.invalid",
          status: "connected",
          granted_scopes: ["https://www.googleapis.com/auth/gmail.modify"],
          health_status: "healthy",
          last_success_at: "2026-07-22T00:00:00.000Z",
          last_failure_at: null,
          last_health_checked_at: "2026-07-22T00:00:00.000Z",
          last_error_code: null,
        },
      ],
    );
    const runs = toRunRecords(
      [
        {
          run_id: "run_smoke",
          agent_id: "agt_smoke",
          status: "succeeded",
          trigger_source: "manual",
          correlation_id: "corr_smoke",
          timeout_seconds: 300,
          retry_count: 0,
          failure_reason_code: null,
          started_at: "2026-07-22T00:00:00.000Z",
          completed_at: "2026-07-22T00:00:05.000Z",
          cancelled_at: null,
          created_at: "2026-07-22T00:00:00.000Z",
          updated_at: "2026-07-22T00:00:05.000Z",
        },
      ],
      [
        {
          agent_id: "agt_smoke",
          slug: "hosted-runtime-smoke-agent",
          display_name: "Hosted Runtime Smoke Agent",
          description: "Synthetic smoke agent",
          status: "active",
          risk_level: "medium",
          supports_manual_run: true,
        },
      ],
    );

    expect(connectors[0]).toMatchObject({
      id: "gmail",
      status: "healthy",
      accountLabel: "synthetic-smoke+gmail@grafley.invalid",
    });
    expect(runs[0]).toMatchObject({
      id: "run_smoke",
      status: "succeeded",
      trigger: "Manual",
      agent: { name: "Hosted Runtime Smoke Agent" },
    });
  });
});
