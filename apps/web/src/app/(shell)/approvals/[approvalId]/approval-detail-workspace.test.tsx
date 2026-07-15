import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { APPROVAL_FIXTURES } from "../approval-data";
import { ApprovalDetailWorkspace } from "./approval-detail-workspace";

const fixture = (id: string) =>
  APPROVAL_FIXTURES.find((approval) => approval.id === id)!;

const firstButton = (name: string | RegExp) =>
  screen.getAllByRole("button", { name })[0];

describe("ApprovalDetailWorkspace", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/approvals/apr-2026-001");
  });

  it("presents exact action, policy, evidence, context, and prototype boundaries", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-001")} />);

    expect(screen.getByText(/Frontend prototype/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Send a remediation notice/i)).not.toHaveLength(0);
    expect(screen.getByText("External Communications P-214")).toBeInTheDocument();
    expect(screen.getByText("Untrusted evidence preview")).toBeInTheDocument();
    expect(screen.getAllByText(/run-2026-07-12-001 \(unavailable in prototype\)/i)).not.toHaveLength(0);
    expect(screen.getAllByRole("link", { name: "Policy Digest Agent" })[0]).toHaveAttribute(
      "href",
      "/agents/agent-policy-digest"
    );
  });

  it("simulates a low-risk approval without requiring a reason or step-up", async () => {
    const user = userEvent.setup();
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-008")} />);

    await user.click(firstButton("Simulate approval"));
    expect(screen.queryByRole("checkbox", { name: /step-up/i })).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Confirm simulated approval/i }));

    expect(screen.getAllByText("Approved")).not.toHaveLength(0);
    expect(screen.getByText(/Simulated approved this local fixture/i)).toBeInTheDocument();
  });

  it("requires explanatory text and simulated step-up for a high-risk approval", async () => {
    const user = userEvent.setup();
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-002")} />);

    await user.click(firstButton("Simulate approval"));
    const stepUp = screen.getByRole("checkbox", { name: /simulated step-up confirmation/i });
    expect(stepUp).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Confirm simulated approval/i })).toBeDisabled();

    await user.click(stepUp);
    await user.click(screen.getByRole("button", { name: /Confirm simulated approval/i }));
    expect(screen.getByRole("alert")).toHaveTextContent(/Explanatory text is required/i);

    await user.type(screen.getByLabelText(/Reason \(required\)/i), "Evidence supports the exception.");
    await user.click(screen.getByRole("button", { name: /Confirm simulated approval/i }));
    expect(screen.getAllByText("Approved")).not.toHaveLength(0);
  });

  it("requires a reason before simulating rejection", async () => {
    const user = userEvent.setup();
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-001")} />);

    await user.click(firstButton("Simulate rejection"));
    await user.click(screen.getByRole("checkbox", { name: /simulated step-up confirmation/i }));
    await user.click(screen.getByRole("button", { name: /confirm simulated rejection/i }));
    expect(screen.getByRole("alert")).toHaveTextContent("A reason is required");

    await user.type(screen.getByLabelText(/Reason \(required\)/i), "The contact needs revised evidence.");
    await user.click(screen.getByRole("button", { name: /confirm simulated rejection/i }));
    expect(screen.getAllByText("Rejected")).not.toHaveLength(0);
    expect(screen.getByText(/Simulated rejected this local fixture/i)).toBeInTheDocument();
  });

  it("keeps clarification Pending and does not alter expiry", async () => {
    const user = userEvent.setup();
    const approval = fixture("apr-2026-004");
    render(<ApprovalDetailWorkspace approval={approval} />);

    await user.click(firstButton("Simulate clarification request"));
    await user.type(screen.getByLabelText(/Clarification question \(required\)/i), "Which catalog owner reviewed this?");
    await user.click(screen.getByRole("button", { name: /Confirm simulated clarification request/i }));

    expect(screen.getAllByText("Pending")).not.toHaveLength(0);
    expect(screen.getAllByText("Awaiting information")).not.toHaveLength(0);
    expect(screen.getByText(/Which catalog owner reviewed this/i)).toBeInTheDocument();
    expect(approval.expiresAt).toBe(fixture("apr-2026-004").expiresAt);
  });

  it("explains why approval is unavailable when evidence is incomplete", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-003")} />);
    expect(screen.getAllByText("Approval unavailable")).not.toHaveLength(0);
    expect(screen.getByText(/Source checksum, Original connector export/i)).toBeInTheDocument();

    for (const button of screen.getAllByRole("button", { name: "Simulate approval" })) {
      expect(button).toBeDisabled();
    }
  });

  it("renders terminal approvals as read-only", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-005")} />);

    expect(screen.getAllByText("Approved")).not.toHaveLength(0);
    expect(screen.getAllByText(/historical or no longer actionable/i)).not.toHaveLength(0);
    for (const button of screen.getAllByRole("button", { name: /Simulate/i })) {
      expect(button).toBeDisabled();
    }
  });

  it("presents terminal decision time, reviewer, reason, and correlation context", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-005")} />);

    expect(screen.getAllByText("Prototype reviewer")).not.toHaveLength(0);
    expect(screen.getAllByText("The note is consistent with the supplied evidence.")).not.toHaveLength(0);
    expect(screen.getAllByText("corr-apr-2026-005")).not.toHaveLength(0);
    expect(screen.getAllByText("Decision time")).not.toHaveLength(0);
  });

  it("renders a clear unavailable state for an unknown approval", () => {
    render(<ApprovalDetailWorkspace approval={undefined} />);

    expect(screen.getByRole("heading", { name: "Approval unavailable" })).toBeInTheDocument();
    expect(screen.getByText(/No real approval service was contacted/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Return to Queue" })).toHaveAttribute(
      "href",
      "/approvals?view=queue"
    );
  });

  it("keeps Indeterminate distinct from Failed and states that Retry is blocked", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-007")} />);

    expect(screen.getAllByText("Indeterminate outcome")).not.toHaveLength(0);
    expect(screen.getAllByText(/Retry is blocked pending investigation/i)).not.toHaveLength(0);
    expect(screen.queryByText(/^Failed$/)).not.toBeInTheDocument();
  });

  it("restores the canonical fixture when the detail component is remounted", async () => {
    const user = userEvent.setup();
    const approval = fixture("apr-2026-008");
    const firstRender = render(<ApprovalDetailWorkspace approval={approval} />);

    await user.click(firstButton("Simulate approval"));
    await user.click(screen.getByRole("button", { name: /Confirm simulated approval/i }));
    expect(screen.getByText(/Simulated approved this local fixture/i)).toBeInTheDocument();

    firstRender.unmount();
    render(<ApprovalDetailWorkspace approval={approval} />);
    expect(screen.getAllByText("Pending")).not.toHaveLength(0);
    expect(screen.queryByText(/Simulated approved this local fixture/i)).not.toBeInTheDocument();
  });

  it("requires a non-empty clarification question", async () => {
    const user = userEvent.setup();
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-004")} />);

    await user.click(firstButton("Simulate clarification request"));
    await user.click(screen.getByRole("button", { name: /Confirm simulated clarification request/i }));
    expect(screen.getByRole("alert")).toHaveTextContent("A clarification question is required");

    await user.type(screen.getByLabelText(/Clarification question \(required\)/i), "Who verified the catalog owner?");
    await user.click(screen.getByRole("button", { name: /Confirm simulated clarification request/i }));
    expect(screen.getByText(/Who verified the catalog owner/i)).toBeInTheDocument();
  });

  it("associates the decision region semantically with Approval unavailable", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-003")} />);

    for (const region of screen.getAllByRole("region", { name: "Decision controls" })) {
      const descriptionId = region.getAttribute("aria-describedby");
      expect(descriptionId).toBeTruthy();
      expect(document.getElementById(descriptionId!)).toHaveTextContent(/Missing fictional evidence/i);
    }
  });

  it("models and presents related Artifact metadata", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-001")} />);

    expect(screen.getAllByText(/Billing remediation evidence packet \(art-2026-0712-001; unavailable in prototype\)/i)).not.toHaveLength(0);
  });

  it("presents Indeterminate investigation guidance in the mobile reading flow", () => {
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-007")} />);

    const guidance = screen.getByRole("note", { name: "Mobile indeterminate guidance" });
    expect(guidance).toHaveTextContent("Indeterminate outcome");
    expect(guidance).toHaveTextContent(/Retry is blocked pending investigation/i);
  });

  it("announces the post-decision state change through a live region", async () => {
    const user = userEvent.setup();
    render(<ApprovalDetailWorkspace approval={fixture("apr-2026-008")} />);

    await user.click(firstButton("Simulate approval"));
    await user.click(screen.getByRole("button", { name: /Confirm simulated approval/i }));

    const announcement = screen.getByText(/Prototype state updated: simulated approval/i);
    expect(announcement).toHaveAttribute("role", "status");
    expect(announcement).toHaveAttribute("aria-live", "polite");
    expect(announcement).toHaveTextContent(/No real action was recorded or executed/i);
  });

  it("tests expired-during-review behavior with a controlled reference clock", async () => {
    const user = userEvent.setup();
    let referenceTime = new Date("2026-07-15T12:00:00Z").getTime();
    const expiring = {
      ...fixture("apr-2026-008"),
      expiresAt: new Date(referenceTime + 1_000).toISOString(),
    };
    render(<ApprovalDetailWorkspace approval={expiring} now={() => referenceTime} />);

    await user.click(firstButton("Simulate approval"));
    referenceTime += 2_000;
    await user.click(screen.getByRole("button", { name: /Confirm simulated approval/i }));

    expect(screen.getAllByText("Expired")).not.toHaveLength(0);
    expect(screen.getByText(/Detected expiry before simulated decision confirmation/i)).toBeInTheDocument();
    expect(screen.getByText(/expired before confirmation/i)).toHaveAttribute("role", "status");
    expect(screen.queryByText(/Simulated approved this local fixture/i)).not.toBeInTheDocument();
  });
});
