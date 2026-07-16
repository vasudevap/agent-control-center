import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AgentOperationalControls } from "./agent-operational-controls";

describe("AgentOperationalControls", () => {
  it("explains the governed manual-run flow before confirmation", async () => {
    const user = userEvent.setup();
    render(
      <AgentOperationalControls
        agentId="agent-recruiting-triage"
        agentName="Recruiting Triage Agent"
        initialStatus="active"
      />
    );

    await user.click(screen.getByRole("button", { name: "Simulate run" }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Simulate a manual run?")).toBeInTheDocument();
    expect(screen.getByText(/duplicate-run validation/i)).toBeInTheDocument();
    expect(screen.getByText(/No runtime request is sent/i)).toBeInTheDocument();
  });

  it("uses pause to stop future schedules without claiming to stop active work", async () => {
    const user = userEvent.setup();
    render(
      <AgentOperationalControls
        agentId="agent-recruiting-triage"
        agentName="Recruiting Triage Agent"
        initialStatus="active"
      />
    );

    await user.click(screen.getByRole("button", { name: "Simulate pause" }));

    expect(screen.getByText(/fictional run already in progress remains unchanged/i)).toBeInTheDocument();
    await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Simulate pause" }));
    expect(screen.getByRole("button", { name: "Simulate resume" })).toBeInTheDocument();
  });

  it("prevents an accidental duplicate manual run", () => {
    render(
      <AgentOperationalControls
        agentId="agent-recruiting-triage"
        agentName="Recruiting Triage Agent"
        initialStatus="running"
      />
    );

    expect(screen.getByRole("button", { name: "Simulate run" })).toBeDisabled();
  });
});
