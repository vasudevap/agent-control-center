import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Button } from "./button";

describe("Button", () => {
  it("is accessible by name and handles a user click", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(<Button onClick={handleClick}>Review agent</Button>);

    const button = screen.getByRole("button", { name: "Review agent" });
    expect(button).toBeEnabled();

    await user.click(button);

    expect(handleClick).toHaveBeenCalledOnce();
  });
});
