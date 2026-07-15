import { render, screen, waitFor, within } from "@testing-library/react";
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

  it("keeps tall dialog content inside the viewport with internal scrolling", async () => {
    const user = userEvent.setup();
    render(<Dialog><DialogTrigger asChild><button type="button">Open tall review</button></DialogTrigger><DialogContent><DialogTitle>Tall simulated decision</DialogTitle><DialogDescription>Local-only prototype confirmation.</DialogDescription><div>Long content</div></DialogContent></Dialog>);

    await user.click(screen.getByRole("button", { name: "Open tall review" }));
    expect(screen.getByRole("dialog", { name: "Tall simulated decision" })).toHaveClass(
      "max-h-[calc(100dvh-2rem)]",
      "overflow-y-auto",
      "overscroll-contain"
    );
  });

  it("restores focus to the trigger after closing", async () => {
    const user = userEvent.setup();
    render(<Dialog><DialogTrigger asChild><button type="button">Open review</button></DialogTrigger><DialogContent><DialogTitle>Review simulated decision</DialogTitle><DialogDescription>Local-only prototype confirmation.</DialogDescription></DialogContent></Dialog>);
    const trigger = screen.getByRole("button", { name: "Open review" });

    await user.click(trigger);
    await user.keyboard("{Escape}");

    await waitFor(() => expect(trigger).toHaveFocus());
  });

  it("keeps keyboard focus contained inside the open dialog", async () => {
    const user = userEvent.setup();
    render(
      <>
        <button type="button">Outside</button>
        <Dialog>
          <DialogTrigger asChild><button type="button">Open review</button></DialogTrigger>
          <DialogContent>
            <DialogTitle>Review simulated decision</DialogTitle>
            <DialogDescription>Local-only prototype confirmation.</DialogDescription>
            <button type="button">First action</button>
            <button type="button">Last action</button>
          </DialogContent>
        </Dialog>
      </>
    );

    const outside = screen.getByRole("button", { name: "Outside" });
    await user.click(screen.getByRole("button", { name: "Open review" }));
    const dialog = screen.getByRole("dialog", { name: "Review simulated decision" });
    const first = within(dialog).getByRole("button", { name: "First action" });
    const close = within(dialog).getByRole("button", { name: "Close dialog" });

    close.focus();
    await user.tab();
    expect(first).toHaveFocus();
    await user.tab({ shift: true });
    expect(close).toHaveFocus();
    expect(outside).not.toHaveFocus();
  });
});
