import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { Dialog, DialogContent, DialogDescription, DialogTitle, DialogTrigger } from "./dialog";

describe("Dialog", () => {
  it("opens with an accessible name and closes with Escape", async () => {
    const user = userEvent.setup();
    render(<Dialog><DialogTrigger asChild><button type="button">Open review</button></DialogTrigger><DialogContent><DialogTitle>Review simulated decision</DialogTitle><DialogDescription>Local-only prototype confirmation.</DialogDescription></DialogContent></Dialog>);
    await user.click(screen.getByRole("button", { name: "Open review" }));
    expect(screen.getByRole("dialog", { name: "Review simulated decision" })).toBeInTheDocument();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
