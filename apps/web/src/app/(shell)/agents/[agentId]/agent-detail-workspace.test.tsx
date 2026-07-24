import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MOCK_AGENTS } from "../agent-data";
import { AgentDetailWorkspace } from "./agent-detail-workspace";

const agent = (id: string) => MOCK_AGENTS.find((item) => item.id === id)!;
const API_BASE_URL = "https://api.atlas.grafley.com";

const dashboardAgent = (overrides: Record<string, unknown> = {}) => ({
  agent_id: "agt_123",
  slug: "agent-one",
  display_name: "Agent One",
  description: "Lifecycle test agent",
  status: "active",
  risk_level: "low",
  capabilities: ["telemetry.report"],
  allowed_tools: ["atlas.telemetry.write"],
  required_connectors: [],
  supports_manual_run: false,
  supports_scheduled_run: false,
  lifecycle_status: "connected",
  active_surface_visible: true,
  monitoring_mode: "heartbeat",
  heartbeat_interval_seconds: 60,
  observed_health: "online",
  reported_health: "healthy",
  ...overrides,
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

describe("AgentDetailWorkspace active surface", () => {
  it("omits deferred approval controls and links from the active detail tabs", () => {
    render(<AgentDetailWorkspace agent={agent("agent-policy-digest")} />);

    expect(screen.queryByRole("button", { name: /Human Approvals/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /approval/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve|reject/i })).not.toBeInTheDocument();
  });

  it("keeps activity and governance as the active detail tabs", () => {
    render(<AgentDetailWorkspace agent={agent("agent-calendar-briefing")} />);

    expect(screen.getByRole("button", { name: "Activity" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Governance" })).toBeInTheDocument();
  });

  it("rotates live credentials from the control-center detail page", async () => {
    const user = userEvent.setup();
    const lifecycleUuid = "00000000-0000-4000-8000-000000000000" as ReturnType<
      typeof crypto.randomUUID
    >;
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", API_BASE_URL);
    vi.spyOn(crypto, "randomUUID").mockReturnValue(lifecycleUuid);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            data: {
              authenticated: true,
              csrf_token: "csrf-token",
              user: {
                user_id: "usr_owner",
                email: "owner@example.test",
                display_name: "Owner",
                identity_provider: "google",
                status: "active",
              },
            },
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ data: [dashboardAgent()] }), { status: 200 }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ data: [] }), { status: 200 }),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            data: {
              agent: dashboardAgent(),
              credential: {
                credential_id: "cred_new",
                credential_lookup_id: "cred_lookup",
                plaintext_token: "atl_agent_cred_lookup.secret",
                scope: "telemetry_write",
              },
            },
          }),
          { status: 200 },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<AgentDetailWorkspace requestedId="agt_123" runtimeRequired />);

    expect(await screen.findByText(/Live runtime/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Rotate credential" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenLastCalledWith(
        `${API_BASE_URL}/api/v1/dashboard/agents/agt_123/credentials/rotate`,
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({
            "X-Atlas-CSRF-Token": "csrf-token",
            "Idempotency-Key": `agent-lifecycle-${lifecycleUuid}`,
          }),
        }),
      ),
    );
    expect(
      screen.getByRole("textbox", { name: "One-time agent credential" }),
    ).toHaveValue("atl_agent_cred_lookup.secret");
    expect(screen.getByText(/Atlas only displays it once/i)).toBeInTheDocument();
  });
});
