import { describe, expect, it } from "vitest";
import { getExpiryPresentation } from "./approval-presentation";

describe("getExpiryPresentation", () => {
  const requested = "2026-07-14T12:00:00.000Z";
  const now = new Date("2026-07-14T12:56:00.000Z").getTime();

  it("labels an expiry imminent request with text as well as a semantic state", () => {
    const result = getExpiryPresentation("2026-07-14T13:00:00.000Z", requested, now);
    expect(result.urgency).toBe("imminent");
    expect(result.label).toContain("Expiry imminent");
  });

  it("labels expired and unspecified requests without relying on color", () => {
    expect(getExpiryPresentation("2026-07-14T12:00:00.000Z", requested, now).urgency).toBe("expired");
    expect(getExpiryPresentation(undefined, requested, now).label).toBe("No expiry is set");
  });
});
