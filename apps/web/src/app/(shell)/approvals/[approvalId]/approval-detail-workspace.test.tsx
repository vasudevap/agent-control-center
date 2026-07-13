import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { APPROVAL_FIXTURES } from "../approval-data";
import { ApprovalDetailWorkspace } from "./approval-detail-workspace";

describe("ApprovalDetailWorkspace", () => {
  it("requires a reason before simulating rejection", async () => {
    const user = userEvent.setup();
    render(<ApprovalDetailWorkspace approval={APPROVAL_FIXTURES[0]} />);
    await user.click(screen.getByRole("button", { name: "Simulate rejection" }));
    await user.click(screen.getByRole("checkbox", { name: /simulated step-up confirmation/i }));
    await user.click(screen.getByRole("button", { name: /confirm simulated rejection/i }));
    expect(screen.getByRole("alert")).toHaveTextContent("A reason is required");
    await user.type(screen.getByLabelText(/Reason \(required\)/i), "The contact needs revised evidence.");
    await user.click(screen.getByRole("button", { name: /confirm simulated rejection/i }));
    expect(screen.getAllByText("Rejected").length).toBeGreaterThan(0);
    expect(screen.getByText(/Simulated rejected this local fixture/i)).toBeInTheDocument();
  });
  it("explains why approval is unavailable when evidence is incomplete", () => {
    render(<ApprovalDetailWorkspace approval={APPROVAL_FIXTURES[2]} />);
    expect(screen.getByText("Approval unavailable")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Simulate approval" })).toBeDisabled();
  });
});
