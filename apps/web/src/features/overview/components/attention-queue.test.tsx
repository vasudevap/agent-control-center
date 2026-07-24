import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AttentionQueue } from "./attention-queue";
import { ALERT_FIXTURES } from "@/app/(shell)/alerts/alert-data";

describe("AttentionQueue", () => {
  it("does not expose deferred approval records in the active Overview queue", () => {
    render(<AttentionQueue agents={[]} alerts={[]} />);

    expect(screen.getByText("Nothing needs attention")).toBeInTheDocument();
    expect(screen.queryByText(/approval/i)).not.toBeInTheDocument();
  });

  it("routes every alert to its canonical Alerts fixture destination", () => {
    render(<AttentionQueue agents={[]} alerts={ALERT_FIXTURES} />);

    ALERT_FIXTURES.forEach((alert) => {
      expect(
        screen.getByRole("link", { name: new RegExp(alert.title, "i") }),
      ).toHaveAttribute("href", `/control-center/alerts?alert=${alert.id}`);
    });
  });
});
