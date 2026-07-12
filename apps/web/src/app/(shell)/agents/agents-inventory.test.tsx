import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AgentsInventory, type AgentRecord } from "./agents-inventory";

const testAgents: AgentRecord[] = [
  {
    id: "agent-alpha",
    name: "Alpha Support Agent",
    description: "Drafts support responses.",
    status: "active",
    health: "healthy",
    owner: "Customer Operations",
    lastRun: "10 minutes ago",
    nextRun: "In 20 minutes",
    version: "v1.0.0",
  },
  {
    id: "agent-beta",
    name: "Beta Policy Agent",
    description: "Reviews exception evidence.",
    status: "paused",
    health: "degraded",
    owner: "Governance Office",
    lastRun: "Yesterday",
    nextRun: "Not scheduled",
    version: "v1.1.0",
    currentIssue: "Evidence export failed.",
  },
  {
    id: "agent-gamma",
    name: "Gamma Connector Agent",
    description: "Checks connector health.",
    status: "running",
    health: "offline",
    owner: "Platform Reliability",
    lastRun: "2 minutes ago",
    nextRun: "In 8 minutes",
    version: "v1.2.0",
  },
];

describe("AgentsInventory", () => {
  it("filters by search, status, and health, then clears filters", async () => {
    const user = userEvent.setup();
    render(<AgentsInventory agents={testAgents} />);

    expect(screen.getByText("Showing 3 of 3 agents")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Beta Policy Agent" })[0]).toHaveAttribute(
      "href",
      "/agents/agent-beta"
    );

    await user.type(screen.getByRole("searchbox", { name: /search agents/i }), "policy");
    expect(screen.getByText("Showing 1 of 3 agents")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Beta Policy Agent" }).length).toBeGreaterThan(0);
    expect(screen.queryAllByRole("link", { name: "Alpha Support Agent" })).toHaveLength(0);

    await user.selectOptions(screen.getByLabelText("Status"), "paused");
    await user.selectOptions(screen.getByLabelText("Health"), "degraded");
    expect(screen.getByText("Showing 1 of 3 agents")).toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText("Health"), "healthy");
    expect(screen.getByText("Showing 0 of 3 agents")).toBeInTheDocument();
    expect(screen.getByText("No agents match the current search or filters")).toBeInTheDocument();

    const emptyState = screen.getByText("No agents match the current search or filters").closest("div");
    expect(emptyState).not.toBeNull();
    await user.click(within(emptyState as HTMLElement).getByRole("button", { name: "Clear Filters" }));

    expect(screen.getByText("Showing 3 of 3 agents")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Alpha Support Agent" }).length).toBeGreaterThan(0);
  });
});
