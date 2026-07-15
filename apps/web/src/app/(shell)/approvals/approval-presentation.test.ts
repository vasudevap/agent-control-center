import { describe, expect, it } from "vitest";
import { getExpiryPresentation, relativeTime } from "./approval-presentation";

const referenceNow = new Date("2026-07-15T12:00:00Z").getTime();

describe("approval presentation timing", () => {
  it("classifies expiry thresholds against an injected reference clock", () => {
    expect(getExpiryPresentation(undefined, undefined, referenceNow).urgency).toBe("none");
    expect(
      getExpiryPresentation(
        "2026-07-15T11:59:00Z",
        "2026-07-15T02:00:00Z",
        referenceNow
      ).urgency
    ).toBe("expired");
    expect(
      getExpiryPresentation(
        "2026-07-15T12:15:00Z",
        "2026-07-15T02:00:00Z",
        referenceNow
      ).urgency
    ).toBe("imminent");
    expect(
      getExpiryPresentation(
        "2026-07-15T13:00:00Z",
        "2026-07-15T02:00:00Z",
        referenceNow
      ).urgency
    ).toBe("nearing");
    expect(
      getExpiryPresentation(
        "2026-07-16T12:00:00Z",
        "2026-07-15T02:00:00Z",
        referenceNow
      ).urgency
    ).toBe("scheduled");
  });

  it("formats relative time against the same controlled clock", () => {
    expect(relativeTime("2026-07-15T09:00:00Z", referenceNow)).toBe("3 hours ago");
    expect(relativeTime("2026-07-16T12:00:00Z", referenceNow)).toBe("tomorrow");
  });
});
