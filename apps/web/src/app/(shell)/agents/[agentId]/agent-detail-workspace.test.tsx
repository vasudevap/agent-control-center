import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MOCK_AGENTS } from "../agent-data";
import { AgentDetailWorkspace } from "./agent-detail-workspace";

const agent = (id: string) => MOCK_AGENTS.find((item) => item.id === id)!;

describe("AgentDetailWorkspace active surface", () => {
  it("omits deferred approval controls and links from the active detail tabs", () => {
    render(<AgentDetailWorkspace agent={agent("agent-policy-digest")} />);

    expect(screen.queryByRole("button", { name: /Human Approvals/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /approval/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /approve|reject/i })).not.toBeInTheDocument();
  });

  it("keeps activity and governance as the active detail tabs", () => {
    render(<AgentDetailWorkspace agent={agent("agent-calendar-briefing")} />);

    expect(screen.getByRole("button", { name: "Activity" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Governance" })).toBeInTheDocument();
  });
});
