import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SidebarNav } from "./sidebar";

vi.mock("next/navigation", () => ({
  usePathname: () => "/approvals/apr-2026-001",
}));

describe("SidebarNav", () => {
  it("keeps the parent workspace focused when its detail route is open", () => {
    render(<SidebarNav expanded />);

    expect(screen.getByRole("link", { name: "Approvals" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "Overview" })).not.toHaveAttribute(
      "aria-current",
    );
  });
});
