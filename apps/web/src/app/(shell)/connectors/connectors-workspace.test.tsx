import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { CONNECTOR_FIXTURES } from "./connector-data";
import { ConnectorsWorkspace } from "./connectors-workspace";

describe("ConnectorsWorkspace", () => {
  it("filters fictional connector descriptors without requesting credentials", async () => {
    const user = userEvent.setup();
    render(<ConnectorsWorkspace connectors={CONNECTOR_FIXTURES} />);

    expect(
      screen.getByRole("table", { name: "Connector inventory" }),
    ).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Status"), "expired");
    await user.selectOptions(
      screen.getByLabelText("Authentication type"),
      "Service identity",
    );
    expect(
      screen.getByText(
        `1 of ${CONNECTOR_FIXTURES.length} fictional connectors`,
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByLabelText(/secret|token|credential/i),
    ).not.toBeInTheDocument();
  });

  it("confirms and labels revocation as a refresh-reset local simulation", async () => {
    const user = userEvent.setup();
    render(<ConnectorsWorkspace connectors={CONNECTOR_FIXTURES} />);

    await user.click(
      screen.getAllByRole("button", { name: "Simulate revoke" })[0],
    );
    expect(
      screen.getByRole("dialog", { name: "Simulate connector revocation?" }),
    ).toBeInTheDocument();
    await user.click(
      screen.getByRole("button", { name: "Confirm simulated revocation" }),
    );
    expect(screen.getByRole("status")).toHaveTextContent(
      /Simulated revocation.*Refresh restores/i,
    );
    expect(screen.getAllByText("Revoked")[0]).toBeInTheDocument();
  });
});
