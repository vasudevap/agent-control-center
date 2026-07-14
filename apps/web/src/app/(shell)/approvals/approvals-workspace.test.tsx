import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { APPROVAL_FIXTURES } from "./approval-data";
import { ApprovalsWorkspace } from "./approvals-workspace";

describe("ApprovalsWorkspace", () => {
  it("searches the queue, filters by risk, and clears local controls", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);
    expect(screen.getByText((_, element) => element?.tagName === "P" && /of \d+ queue records/i.test(element.textContent ?? ""))).toBeInTheDocument();
    await user.type(screen.getByRole("searchbox", { name: /ID, agent, action, target, or policy/i }), "billing");
    expect(screen.getAllByText(/Send a remediation notice/i).length).toBeGreaterThan(0);
    await user.selectOptions(screen.getByLabelText("Risk"), "Critical");
    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(screen.getByRole("searchbox", { name: /ID, agent, action, target, or policy/i })).toHaveValue("");
  });
  it("shows the distinct history view", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);
    const historyTab = screen.getByRole("tab", { name: "History" });
    await user.click(historyTab);
    expect(historyTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getAllByText(/Outcome: Indeterminate/i).length).toBeGreaterThan(0);
  });
});
