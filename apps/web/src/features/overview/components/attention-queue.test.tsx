import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { APPROVAL_FIXTURES } from "@/app/(shell)/approvals/approval-data";
import { AttentionQueue } from "./attention-queue";

describe("AttentionQueue", () => {
  it("renders only the approval fixtures serialized through its server-owned prop", () => {
    const approval = {
      ...APPROVAL_FIXTURES[0],
      id: "apr-server-serialized",
      action: "Review the server-serialized approval fixture.",
    };

    render(<AttentionQueue approvals={[approval]} />);

    expect(screen.getByText("Review the server-serialized approval fixture.")).toBeInTheDocument();
    expect(screen.queryByText(APPROVAL_FIXTURES[1].action)).not.toBeInTheDocument();
  });
});
