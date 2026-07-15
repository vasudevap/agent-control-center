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

    await user.click(screen.getByRole("button", { name: "Run now" }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Start a manual run?")).toBeInTheDocument();
    expect(screen.getByText(/duplicate-run safeguards/i)).toBeInTheDocument();
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

    await user.click(screen.getByRole("button", { name: "Pause agent" }));

    expect(screen.getByText(/run already in progress will be allowed to finish/i)).toBeInTheDocument();
    await user.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Pause agent" }));
    expect(screen.getByRole("button", { name: "Resume agent" })).toBeInTheDocument();
  });

  it("prevents an accidental duplicate manual run", () => {
    render(
      <AgentOperationalControls
        agentId="agent-recruiting-triage"
        agentName="Recruiting Triage Agent"
        initialStatus="running"
      />
    );

    expect(screen.getByRole("button", { name: "Run now" })).toBeDisabled();
  });
});
