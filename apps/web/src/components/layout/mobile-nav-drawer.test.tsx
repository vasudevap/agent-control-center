import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MobileNavDrawer } from "./mobile-nav-drawer";

vi.mock("next/navigation", () => ({
  usePathname: () => "/control-center/agents",
}));

describe("MobileNavDrawer", () => {
  it("shows readable labels and gives every navigation link an accessible name", () => {
    render(<MobileNavDrawer open onClose={vi.fn()} />);

    expect(screen.getByRole("dialog", { name: "Navigation" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Overview" })).toHaveAttribute("aria-label", "Overview");
    expect(screen.getByRole("link", { name: "Overview" })).toHaveAttribute("href", "/control-center");
    expect(screen.getByRole("link", { name: "Agents" })).toHaveAttribute("href", "/control-center/agents");
    expect(screen.getByText("Overview")).not.toHaveClass("hidden");
    expect(screen.getByRole("link", { name: "Agents" })).toHaveAttribute("aria-current", "page");
    expect(screen.getAllByRole("link").map((link) => link.textContent)).toEqual([
      "Overview",
      "Agents",
      "Executions",
      "Alerts",
      "Activity",
    ]);
    expect(screen.queryByRole("link", { name: "Settings" })).not.toBeInTheDocument();
  });
});
