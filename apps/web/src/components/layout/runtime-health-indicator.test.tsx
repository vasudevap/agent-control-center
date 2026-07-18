import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RuntimeHealthIndicator } from "./runtime-health-indicator";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("RuntimeHealthIndicator", () => {
  it("does not call the runtime when the API base URL is not configured", () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);

    render(<RuntimeHealthIndicator apiBaseUrl="" />);

    expect(screen.getByRole("status")).toHaveTextContent("Runtime not configured");
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("reports ready when the runtime readiness endpoint is healthy", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ready", problems: [] }),
    });
    vi.stubGlobal("fetch", fetchSpy);

    render(<RuntimeHealthIndicator apiBaseUrl="https://api.example.test/" />);

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent("Runtime ready");
    });
    expect(fetchSpy).toHaveBeenCalledWith(
      "https://api.example.test/health/ready",
      expect.objectContaining({
        cache: "no-store",
        headers: { Accept: "application/json" },
      }),
    );
  });

  it("reports readiness problem counts without exposing problem values", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        status: "not_ready",
        problems: ["database_url_missing", "webhook_signing_secret_missing"],
      }),
    });
    vi.stubGlobal("fetch", fetchSpy);

    render(<RuntimeHealthIndicator apiBaseUrl="https://api.example.test" />);

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent("Runtime not ready (2)");
    });
    expect(screen.getByRole("status")).not.toHaveTextContent("database_url_missing");
  });

  it("reports unavailable when the readiness check fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network failed")));

    render(<RuntimeHealthIndicator apiBaseUrl="https://api.example.test" />);

    await waitFor(() => {
      expect(screen.getByRole("status")).toHaveTextContent("Runtime unavailable");
    });
  });
});
