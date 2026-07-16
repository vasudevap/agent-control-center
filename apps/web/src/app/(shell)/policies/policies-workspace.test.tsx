import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { POLICY_FIXTURES } from "./policy-data";
import { PoliciesWorkspace } from "./policies-workspace";

describe("PoliciesWorkspace", () => {
  it("filters typed declarations and exposes semantic policy metadata", async () => {
    const user = userEvent.setup();
    render(<PoliciesWorkspace policies={POLICY_FIXTURES} />);

    expect(
      screen.getByRole("table", { name: "Policy inventory" }),
    ).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Status"), "paused");
    await user.selectOptions(screen.getByLabelText("Type"), "Retention");
    expect(
      screen.getByText(`1 of ${POLICY_FIXTURES.length} fictional policies`),
    ).toBeInTheDocument();
    expect(screen.getAllByText("P-118 · v3")[0]).toBeInTheDocument();
  });

  it("uses explicit local simulation language and never claims enforcement", async () => {
    const user = userEvent.setup();
    render(<PoliciesWorkspace policies={POLICY_FIXTURES} />);

    await user.click(
      screen.getAllByRole("button", { name: "Simulate disable" })[0],
    );
    expect(screen.getByRole("status")).toHaveTextContent(
      /Simulated disable.*No policy engine was contacted/i,
    );
    expect(
      screen.getByText(
        /No rule is evaluated, enforced, authorized, or persisted/i,
      ),
    ).toBeInTheDocument();
  });
});
