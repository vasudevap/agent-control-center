import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { MOCK_AGENTS } from "../agent-data";
import { AgentDetailWorkspace } from "./agent-detail-workspace";

const agent = (id: string) => MOCK_AGENTS.find((item) => item.id === id)!;

describe("AgentDetailWorkspace Human Approvals", () => {
  it("links pending approvals from the shared canonical fixture collection", async () => {
    const user = userEvent.setup();
    render(<AgentDetailWorkspace agent={agent("agent-policy-digest")} />);

    await user.click(screen.getByRole("button", { name: /Human Approvals/i }));
    const approvalLink = screen.getByRole("link", {
      name: /Send a remediation notice to the enterprise billing contact/i,
    });
    expect(approvalLink).toHaveAttribute("href", "/approvals/apr-2026-001");
    expect(screen.queryByRole("button", { name: /approve|reject/i })).not.toBeInTheDocument();
  });

  it("shows an empty state when the agent has no pending approval fixture", async () => {
    const user = userEvent.setup();
    render(<AgentDetailWorkspace agent={agent("agent-calendar-briefing")} />);

    await user.click(screen.getByRole("button", { name: /Human Approvals/i }));
    expect(screen.getByText("No human approvals are pending")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /approval/i })).not.toBeInTheDocument();
  });
});
