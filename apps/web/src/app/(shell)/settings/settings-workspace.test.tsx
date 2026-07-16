import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { SettingsWorkspace } from "./settings-workspace";

describe("SettingsWorkspace", () => {
  it("resets session changes to deterministic fixture defaults", async () => {
    const user = userEvent.setup();
    render(<SettingsWorkspace />);

    const name = screen.getByLabelText("Workspace name");
    await user.clear(name);
    await user.type(name, "Changed locally");
    expect(
      screen.getByText("Unsaved session-only changes"),
    ).toBeInTheDocument();
    await user.click(
      screen.getByRole("button", { name: "Reset session changes" }),
    );
    expect(name).toHaveValue("Atlas Operations");
    expect(screen.getByRole("status")).toHaveTextContent(
      /Session changes reset/i,
    );
  });

  it("labels save as a non-persistent simulation", async () => {
    const user = userEvent.setup();
    render(<SettingsWorkspace />);

    await user.click(
      screen.getByRole("checkbox", { name: "Prefer reduced motion" }),
    );
    await user.click(
      screen.getByRole("button", { name: "Simulate save settings" }),
    );
    expect(screen.getByRole("status")).toHaveTextContent(
      /Simulated settings save.*No configuration was persisted or sent/i,
    );
    expect(
      screen.getByText(/Values exist only in component memory/i),
    ).toBeInTheDocument();
  });
});
