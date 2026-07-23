import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TopBar } from "./top-bar";

vi.mock("@/lib/dashboard-runtime", () => ({
  dashboardApiBaseUrl: () => "https://api.atlas.example.test",
  dashboardSignInUrl: () => "https://api.atlas.example.test/auth/owner/google/start",
  ownerDisplayName: () => "Owner",
  ownerInitials: () => "O",
  readDashboardSession: () =>
    Promise.reject(Object.assign(new Error("Owner session missing"), { status: 401 })),
}));

describe("TopBar", () => {
  it("offers sign-in rather than sign-out when there is no owner session", async () => {
    const user = userEvent.setup();
    render(<TopBar />);

    await user.click(screen.getByRole("button", { name: "User menu" }));

    expect(await screen.findByRole("menuitem", { name: "Sign in with Google" })).toHaveAttribute(
      "href",
      "https://api.atlas.example.test/auth/owner/google/start",
    );
    expect(screen.getByTestId("google-logo")).toBeInTheDocument();
    expect(screen.queryByRole("menuitem", { name: "Sign out" })).not.toBeInTheDocument();
  });
});
