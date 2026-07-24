import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { OverviewDashboard } from "./overview-dashboard";

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("OverviewDashboard runtime states", () => {
  it("uses a neutral empty state when live overview data is not configured", () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "");

    render(<OverviewDashboard runtimeRequired />);

    expect(screen.getByText("Nothing to display yet")).toBeInTheDocument();
    expect(
      screen.getByText("Runtime overview will appear once the Atlas API is configured for this build."),
    ).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
