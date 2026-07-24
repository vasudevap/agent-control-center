import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AUDIT_FIXTURES } from "./audit-data";
import { AuditWorkspace } from "./audit-workspace";

describe("AuditWorkspace", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("filters fictional history and sorts by true values", async () => {
    const user = userEvent.setup();
    render(<AuditWorkspace events={AUDIT_FIXTURES} />);

    expect(
      screen.getByRole("table", { name: "Activity event history" }),
    ).toBeInTheDocument();
    await user.selectOptions(
      screen.getByLabelText("Action"),
      "Approval decision",
    );
    await user.selectOptions(screen.getByLabelText("Result"), "rejected");
    expect(
      screen.getByText(`1 of ${AUDIT_FIXTURES.length} fictional events`),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Actor" }));
    expect(
      screen.getByRole("columnheader", { name: /Actor/i }),
    ).toHaveAttribute("aria-sort", "ascending");
  });

  it("is visibly read-only and exposes correlation context without mutation controls", async () => {
    const user = userEvent.setup();
    render(<AuditWorkspace events={AUDIT_FIXTURES} />);

    expect(
      screen.getByText(/not operational activity records or a system of record/i),
    ).toBeInTheDocument();
    await user.click(screen.getAllByText("View event details")[0]);
    expect(
      screen.getAllByText(AUDIT_FIXTURES[0].correlationId)[0],
    ).toBeVisible();
    expect(
      screen.queryByRole("button", { name: /edit|delete|export/i }),
    ).not.toBeInTheDocument();
  });

  it("shows an intentional empty state for a live account with no activity", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.atlas.grafley.com");
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              data: {
                authenticated: true,
                csrf_token: "csrf-token",
                user: {
                  user_id: "owner-1",
                  email: "owner@example.com",
                  display_name: "Owner",
                  identity_provider: "google",
                  status: "active",
                },
              },
            }),
          ),
        )
        .mockResolvedValueOnce(new Response(JSON.stringify({ data: [] }))),
    );

    render(<AuditWorkspace events={AUDIT_FIXTURES} runtimeRequired />);

    expect(
      await screen.findByText("Nothing to display yet"),
    ).toBeInTheDocument();
    expect(screen.getByText("No activity has been recorded.")).toBeInTheDocument();
    expect(screen.queryByText(AUDIT_FIXTURES[0].summary)).not.toBeInTheDocument();
  });
});
