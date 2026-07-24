import { afterEach, describe, expect, it, vi } from "vitest";
import {
  DashboardApiError,
  archiveDashboardAgent,
  dashboardApiBaseUrl,
  dashboardRequest,
  dashboardSignInUrl,
  disconnectDashboardAgent,
  reconnectDashboardAgent,
  rotateDashboardAgentCredential,
  toAuditEvents,
  toAlertRecords,
  toConnectorRecords,
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

  it("uses the accepted production API origin when the hosted build omits the public variable", () => {
    const originalLocation = window.location;
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { hostname: "atlas.grafley.com" },
    });

    expect(dashboardApiBaseUrl()).toBe("https://api.atlas.grafley.com");

    Object.defineProperty(window, "location", {
      configurable: true,
      value: originalLocation,
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

  it("posts agent lifecycle actions with CSRF and idempotency headers", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.atlas.grafley.com/");
    const lifecycleUuid = "00000000-0000-4000-8000-000000000000" as ReturnType<
      typeof crypto.randomUUID
    >;
    vi.spyOn(crypto, "randomUUID").mockReturnValue(lifecycleUuid);
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          data: {
            agent: {
              agent_id: "agt_123",
              slug: "agent-one",
              display_name: "Agent One",
              description: "Lifecycle test agent",
              status: "active",
              risk_level: "low",
              supports_manual_run: false,
              lifecycle_status: "pending",
              active_surface_visible: true,
            },
          },
        }),
        { status: 200 },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await rotateDashboardAgentCredential("agt_123", "csrf-token");
    await disconnectDashboardAgent("agt_123", "csrf-token");
    await reconnectDashboardAgent("agt_123", "csrf-token");
    await archiveDashboardAgent("agt_123", "csrf-token");

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "https://api.atlas.grafley.com/api/v1/dashboard/agents/agt_123/credentials/rotate",
      expect.objectContaining({
        method: "POST",
        credentials: "include",
        headers: expect.objectContaining({
          "X-Atlas-CSRF-Token": "csrf-token",
          "Idempotency-Key": `agent-lifecycle-${lifecycleUuid}`,
        }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "https://api.atlas.grafley.com/api/v1/dashboard/agents/agt_123/disconnect",
      expect.any(Object),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "https://api.atlas.grafley.com/api/v1/dashboard/agents/agt_123/reconnect",
      expect.any(Object),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      4,
      "https://api.atlas.grafley.com/api/v1/dashboard/agents/agt_123/archive",
      expect.any(Object),
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
          agent_execution_id: "run_123",
          agent_id: "agt_123",
          external_execution_id: "external_run_123",
          status: "accepted",
          trigger: "manual",
          started_at: null,
          finished_at: null,
          duration_ms: null,
          summary: null,
          error_code: null,
          correlation_id: "corr_123",
          agent_version: null,
          build_sha: null,
          first_reported_at: "2026-07-22T00:00:00.000Z",
          last_reported_at: "2026-07-22T00:00:00.000Z",
          terminal_at: null,
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
        activity_event_id: "act_123",
        agent_id: "agt_123",
        source_type: "agent_execution",
        source_id: "run_123",
        event_type: "execution_reported",
        severity: "info",
        summary: "Execution was reported.",
        correlation_id: "corr_123",
        actor_type: "agent_runtime",
        actor_id: "agt_123",
        metadata_json: { count: 1 },
        occurred_at: "2026-07-22T00:00:00.000Z",
      },
    ]);
    const alerts = toAlertRecords([
      {
        alert_id: "alt_123",
        agent_id: "agt_123",
        condition_key: "agent:heartbeat_late",
        status: "resolved",
        severity: "info",
        first_seen_at: "2026-07-22T00:00:00.000Z",
        last_seen_at: "2026-07-22T00:00:00.000Z",
        acknowledged_at: null,
        acknowledged_by_user_id: null,
        resolved_at: "2026-07-22T00:00:00.000Z",
        resolved_reason: "heartbeat recovered",
        evidence_json: { observed_health: "online" },
      },
    ]);

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
      action: "execution_reported",
      result: "succeeded",
    });
    expect(alerts[0]).toMatchObject({
      id: "alt_123",
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
          agent_execution_id: "run_smoke",
          agent_id: "agt_smoke",
          external_execution_id: "external_run_smoke",
          status: "succeeded",
          trigger: "manual",
          started_at: "2026-07-22T00:00:00.000Z",
          finished_at: "2026-07-22T00:00:05.000Z",
          duration_ms: 5000,
          summary: "Smoke execution succeeded.",
          error_code: null,
          correlation_id: "corr_smoke",
          agent_version: null,
          build_sha: null,
          first_reported_at: "2026-07-22T00:00:00.000Z",
          last_reported_at: "2026-07-22T00:00:05.000Z",
          terminal_at: "2026-07-22T00:00:05.000Z",
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
