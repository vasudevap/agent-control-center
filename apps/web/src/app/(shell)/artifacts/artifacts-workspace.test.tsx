import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ARTIFACT_FIXTURES } from "./artifact-data";
import { ArtifactsWorkspace } from "./artifacts-workspace";
import { ArtifactDetailWorkspace } from "./[artifactId]/artifact-detail-workspace";

describe("ArtifactsWorkspace", () => {
  it("filters typed fixture metadata and clears the catalog", async () => {
    const user = userEvent.setup();
    render(<ArtifactsWorkspace />);
    expect(
      screen.getByText(`5 of ${ARTIFACT_FIXTURES.length} fictional artifacts`),
    ).toBeInTheDocument();
    await user.type(
      screen.getByRole("searchbox", { name: "Search artifacts" }),
      "connector",
    );
    await user.selectOptions(
      screen.getByLabelText("Status"),
      "review-required",
    );
    expect(
      screen.getByText(`1 of ${ARTIFACT_FIXTURES.length} fictional artifacts`),
    ).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", { name: /Connector evidence export/i })[0],
    ).toHaveAttribute("href", "/artifacts/art-2026-0705-011");
    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(
      screen.getByText(`5 of ${ARTIFACT_FIXTURES.length} fictional artifacts`),
    ).toBeInTheDocument();
  });

  it("provides a semantic desktop inventory and mobile-equivalent card links", () => {
    render(<ArtifactsWorkspace />);
    expect(
      screen.getByRole("table", { name: "Artifacts inventory" }),
    ).toBeInTheDocument();
    expect(
      screen.getAllByRole("link", {
        name: /Billing remediation evidence packet/i,
      }),
    ).toHaveLength(2);
  });
});

describe("ArtifactDetailWorkspace", () => {
  it("renders safe metadata and canonical lineage without a download action", () => {
    const artifact = ARTIFACT_FIXTURES[0];
    render(
      <ArtifactDetailWorkspace artifact={artifact} requestedId={artifact.id} />,
    );
    expect(
      screen.getByText(/Unsafe inline rendering is disabled/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: artifact.runId })).toHaveAttribute(
      "href",
      `/runs/${artifact.runId}`,
    );
    expect(
      screen.queryByRole("button", { name: /download/i }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: /download/i }),
    ).not.toBeInTheDocument();
  });

  it("keeps unavailable run lineage non-interactive", () => {
    const artifact = ARTIFACT_FIXTURES.find((item) =>
      item.runId.startsWith("run-unavailable"),
    )!;
    render(
      <ArtifactDetailWorkspace artifact={artifact} requestedId={artifact.id} />,
    );
    expect(
      screen.getByText(
        /run-unavailable-2025-1201 \(unavailable in prototype\)/i,
      ),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: artifact.runId }),
    ).not.toBeInTheDocument();
  });
});
