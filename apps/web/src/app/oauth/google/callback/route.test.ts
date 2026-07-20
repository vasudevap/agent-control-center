import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "./route";

describe("Google OAuth callback route", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllEnvs();
  });

  it("completes through the signed Atlas API callback and redirects cleanly", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.atlas.grafley.com");
    vi.stubEnv("ATLAS_DASHBOARD_EXTERNAL_CLIENT_ID", "client-1");
    vi.stubEnv("ATLAS_DASHBOARD_EXTERNAL_CLIENT_KEY_ID", "key-1");
    vi.stubEnv("ATLAS_DASHBOARD_EXTERNAL_CLIENT_SECRET", "secret-1");
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await GET(
      new Request(
        "https://atlas.grafley.com/oauth/google/callback?state=state-1&code=code-1",
      ),
    );

    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.atlas.grafley.com/api/v1/connectors/oauth/google/callback",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          state: "state-1",
          authorization_code: "code-1",
        }),
      }),
    );
    const location = response.headers.get("location");
    expect(location).toBe(
      "https://atlas.grafley.com/connectors?oauth=google&status=connected",
    );
    expect(location).not.toContain("code-1");
  });

  it("redirects with denied status for provider-denied callbacks", async () => {
    const response = await GET(
      new Request(
        "https://atlas.grafley.com/oauth/google/callback?error=access_denied",
      ),
    );

    expect(response.headers.get("location")).toBe(
      "https://atlas.grafley.com/connectors?oauth=google&status=denied",
    );
  });

  it("fails closed without exposing callback query values", async () => {
    const response = await GET(
      new Request(
        "https://atlas.grafley.com/oauth/google/callback?state=state-1&code=code-1",
      ),
    );

    const location = response.headers.get("location");
    expect(location).toBe(
      "https://atlas.grafley.com/connectors?oauth=google&status=failed",
    );
    expect(location).not.toContain("state-1");
    expect(location).not.toContain("code-1");
  });
});
