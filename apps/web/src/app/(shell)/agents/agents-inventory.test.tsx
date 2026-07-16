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
    lastRunAt: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    nextRun: "In 20 minutes",
    nextRunAt: new Date(Date.now() + 20 * 60 * 1000).toISOString(),
    version: "v1.0.0",
    responsibilities: ["Draft support responses for review."],
    capabilities: ["Response drafting"],
    connectors: ["Support queue"],
    permissions: ["Draft responses"],
    recentActivity: ["Prepared one draft response."],
  },
  {
    id: "agent-beta",
    name: "Beta Policy Agent",
    description: "Reviews exception evidence.",
    status: "paused",
    health: "degraded",
    owner: "Governance Office",
    lastRun: "Yesterday",
    lastRunAt: new Date(Date.now() - 20 * 60 * 60 * 1000).toISOString(),
    nextRun: "Not scheduled",
    version: "v1.1.0",
    currentIssue: "Evidence export failed.",
    responsibilities: ["Review exception evidence."],
    capabilities: ["Evidence review"],
    connectors: ["Policy queue"],
    permissions: ["Read evidence metadata"],
    recentActivity: ["Detected one failed evidence export."],
  },
  {
    id: "agent-gamma",
    name: "Gamma Connector Agent",
    description: "Checks connector health.",
    status: "running",
    health: "offline",
    owner: "Platform Reliability",
    lastRun: "2 minutes ago",
    lastRunAt: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    nextRun: "In 8 minutes",
    nextRunAt: new Date(Date.now() + 8 * 60 * 1000).toISOString(),
    version: "v1.2.0",
    responsibilities: ["Check connector health."],
    capabilities: ["Connector polling"],
    connectors: ["Connector registry"],
    permissions: ["Read connector status"],
    recentActivity: ["Checked connector health signals."],
  },
];

describe("AgentsInventory", () => {
  it("filters by search, status, and health, then clears filters", async () => {
    const user = userEvent.setup();
    render(<AgentsInventory agents={testAgents} />);

    expect(screen.getByText("Showing 3 of 3")).toBeInTheDocument();
    expect(screen.queryByText("3 registered")).not.toBeInTheDocument();
    const table = screen.getByRole("table", { name: "Agents inventory" });
    expect(within(table).getAllByText("Healthy")[0]).not.toHaveClass("sr-only");
    expect(within(table).getAllByText("Healthy")[0]).not.toHaveClass("rounded-full");
    expect(within(table).getAllByText("Active")[0]).not.toHaveClass("sr-only");
    expect(within(table).getAllByText("Active")[0]).not.toHaveClass("rounded-full");
    expect(screen.getAllByRole("link", { name: "Beta Policy Agent" })[0]).toHaveAttribute("href", "/agents/agent-beta");

    await user.type(screen.getByRole("searchbox", { name: /search agents/i }), "policy");
    expect(screen.getByText("Showing 1 of 3")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Beta Policy Agent" }).length).toBeGreaterThan(0);
    expect(screen.queryAllByRole("link", { name: "Alpha Support Agent" })).toHaveLength(0);

    await user.selectOptions(screen.getByLabelText("Filter by status"), "paused");
    await user.selectOptions(screen.getByLabelText("Filter by health"), "degraded");
    expect(screen.getByText("Showing 1 of 3")).toBeInTheDocument();

    await user.selectOptions(screen.getByLabelText("Filter by health"), "healthy");
    expect(screen.getByText("Showing 0 of 3")).toBeInTheDocument();
    expect(screen.getByText("No agents match the current search or filters")).toBeInTheDocument();

    const emptyState = screen.getByText("No agents match the current search or filters").closest("div");
    expect(emptyState).not.toBeNull();
    await user.click(within(emptyState as HTMLElement).getByRole("button", { name: "Clear filters" }));

    expect(screen.getByText("Showing 3 of 3")).toBeInTheDocument();
    expect(screen.getAllByRole("link", { name: "Alpha Support Agent" }).length).toBeGreaterThan(0);
  });

  it("shares accessible sortable-header behavior with Approvals", async () => {
    const user = userEvent.setup();
    render(<AgentsInventory agents={testAgents} />);
    const table = screen.getByRole("table", { name: "Agents inventory" });
    const agentHeader = within(table).getByRole("columnheader", { name: "Agent" });

    expect(agentHeader).toHaveAttribute("aria-sort", "none");
    await user.click(within(agentHeader).getByRole("button", { name: "Agent" }));
    expect(agentHeader).toHaveAttribute("aria-sort", "ascending");
    expect(within(table).getAllByRole("link")[0]).toHaveTextContent("Alpha Support Agent");
  });
});
