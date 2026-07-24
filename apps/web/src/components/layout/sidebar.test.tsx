import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SidebarNav } from "./sidebar";

vi.mock("next/navigation", () => ({
  usePathname: () => "/control-center/runs/run-2026-07-12-001",
}));

describe("SidebarNav", () => {
  it("keeps the parent workspace focused when its detail route is open", () => {
    render(<SidebarNav expanded />);

    expect(screen.getByRole("link", { name: "Executions" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "Overview" })).not.toHaveAttribute(
      "aria-current",
    );
    expect(screen.getByRole("link", { name: "Executions" })).toHaveAttribute(
      "href",
      "/control-center/runs",
    );
  });

  it("exposes only the Agent Visibility MVP destinations", () => {
    render(<SidebarNav expanded />);

    expect(screen.getAllByRole("link").map((link) => link.textContent)).toEqual([
      "Overview",
      "Agents",
      "Executions",
      "Alerts",
      "Activity",
    ]);
  });
});
