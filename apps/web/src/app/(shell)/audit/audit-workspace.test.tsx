import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AUDIT_FIXTURES } from "./audit-data";
import { AuditWorkspace } from "./audit-workspace";

describe("AuditWorkspace", () => {
  it("filters fictional history and sorts by true values", async () => {
    const user = userEvent.setup();
    render(<AuditWorkspace events={AUDIT_FIXTURES} />);

    expect(
      screen.getByRole("table", { name: "Audit event history" }),
    ).toBeInTheDocument();
    await user.selectOptions(
      screen.getByLabelText("Action"),
      "Approval decision",
    );
    await user.selectOptions(screen.getByLabelText("Result"), "rejected");
    expect(
      screen.getByText(`1 of ${AUDIT_FIXTURES.length} fictional events`),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Actor" }));
    expect(
      screen.getByRole("columnheader", { name: /Actor/i }),
    ).toHaveAttribute("aria-sort", "ascending");
  });

  it("is visibly read-only and exposes correlation context without mutation controls", async () => {
    const user = userEvent.setup();
    render(<AuditWorkspace events={AUDIT_FIXTURES} />);

    expect(
      screen.getByText(/not operational audit records or a system of record/i),
    ).toBeInTheDocument();
    await user.click(screen.getAllByText("View event details")[0]);
    expect(
      screen.getAllByText(AUDIT_FIXTURES[0].correlationId)[0],
    ).toBeVisible();
    expect(
      screen.queryByRole("button", { name: /edit|delete|export/i }),
    ).not.toBeInTheDocument();
  });
});
