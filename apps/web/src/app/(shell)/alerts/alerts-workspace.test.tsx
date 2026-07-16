import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ALERT_FIXTURES } from "./alert-data";
import { AlertsWorkspace } from "./alerts-workspace";

describe("AlertsWorkspace", () => {
  it("filters deterministic local alerts and exposes a semantic sortable inventory", async () => {
    const user = userEvent.setup();
    render(<AlertsWorkspace alerts={ALERT_FIXTURES} />);

    expect(
      screen.getByRole("table", { name: "Alerts inventory" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(`4 of ${ALERT_FIXTURES.length} fictional alerts`),
    ).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Severity"), "critical");
    await user.selectOptions(screen.getByLabelText("Status"), "active");
    expect(
      screen.getByText(`1 of ${ALERT_FIXTURES.length} fictional alerts`),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Raised" }));
    expect(
      screen.getByRole("columnheader", { name: /Raised/i }),
    ).toHaveAttribute("aria-sort", "ascending");
    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(
      screen.getByText(`4 of ${ALERT_FIXTURES.length} fictional alerts`),
    ).toBeInTheDocument();

    await user.type(
      screen.getByRole("searchbox", { name: "Search alerts" }),
      "no matching fixture",
    );
    expect(
      screen.getByText("No alerts match these filters"),
    ).toBeInTheDocument();
  });

  it("labels local simulation explicitly and restores canonical relationships", async () => {
    const user = userEvent.setup();
    const alert = ALERT_FIXTURES[0];
    render(
      <AlertsWorkspace alerts={ALERT_FIXTURES} initialAlertId={alert.id} />,
    );

    expect(screen.getAllByText(alert.evidence)[0]).toBeVisible();
    expect(
      screen.getAllByRole("link", { name: "View run" })[0],
    ).toHaveAttribute("href", `/runs/${alert.relatedRunId}`);
    await user.click(
      screen.getAllByRole("button", { name: "Simulate investigation" })[0],
    );
    expect(
      screen.getByText(
        `Simulated investigation for ${alert.id}. Refreshing the page restores the fixture.`,
      ),
    ).toBeInTheDocument();
    expect(screen.getAllByText("Investigating")[0]).toBeInTheDocument();
  });
});
