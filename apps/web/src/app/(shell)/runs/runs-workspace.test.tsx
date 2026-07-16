import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { RUN_FIXTURES } from "./run-data";
import { RunsWorkspace } from "./runs-workspace";
import { RunDetailWorkspace } from "./[runId]/run-detail-workspace";

describe("RunsWorkspace", () => {
  it("filters local fixtures by search, status, and trigger and clears the result", async () => {
    const user = userEvent.setup();
    render(<RunsWorkspace />);

    expect(
      screen.getByText(`6 of ${RUN_FIXTURES.length} fictional runs`),
    ).toBeInTheDocument();
    await user.type(
      screen.getByRole("searchbox", { name: "Search runs" }),
      "connector",
    );
    expect(
      screen.getByText(`2 of ${RUN_FIXTURES.length} fictional runs`),
    ).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Status"), "failed");
    await user.selectOptions(screen.getByLabelText("Trigger"), "Scheduled");
    expect(
      screen.getByText(`1 of ${RUN_FIXTURES.length} fictional runs`),
    ).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", { name: /run-2026-07-05-011/i })[0],
    ).toHaveAttribute("href", "/runs/run-2026-07-05-011");

    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(
      screen.getByText(`6 of ${RUN_FIXTURES.length} fictional runs`),
    ).toBeInTheDocument();
  });

  it("renders semantic sortable inventory and a recoverable controlled error", async () => {
    const user = userEvent.setup();
    const { unmount } = render(<RunsWorkspace />);
    expect(
      screen.getByRole("table", { name: "Runs inventory" }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Agent" }));
    expect(
      screen.getByRole("columnheader", { name: /Agent/i }),
    ).toHaveAttribute("aria-sort", "ascending");

    unmount();
    render(<RunsWorkspace state="error" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Runs unavailable");
    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(
      screen.getByRole("table", { name: "Runs inventory" }),
    ).toBeInTheDocument();
  });
});

describe("RunDetailWorkspace", () => {
  it("separates operational logs from audit and links only canonical fixture records", () => {
    const run = RUN_FIXTURES[0];
    render(<RunDetailWorkspace run={run} requestedId={run.id} />);
    expect(
      screen.getByText(
        /No runtime, retry, cancellation, or persistence behavior exists/i,
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("table", { name: "Execution steps" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Operational log excerpts")).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: `Approval ${run.approvalIds[0]}` }),
    ).toHaveAttribute("href", `/approvals/${run.approvalIds[0]}`);
    expect(
      screen.getByRole("link", { name: `Artifact ${run.artifactIds[0]}` }),
    ).toHaveAttribute("href", `/artifacts/${run.artifactIds[0]}`);
  });

  it("keeps unknown runs visibly unavailable without a service lookup", () => {
    render(<RunDetailWorkspace requestedId="run-missing" />);
    expect(
      screen.getByRole("heading", { name: "Run unavailable" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/No service lookup occurred/i)).toBeInTheDocument();
  });
});
