import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { APPROVAL_FIXTURES, type ApprovalRecord } from "./approval-data";
import { ApprovalsWorkspace } from "./approvals-workspace";

const queueSummary = () =>
  screen.getByText(
    (_, element) =>
      element?.tagName === "P" && /of \d+ queue records/i.test(element.textContent ?? "")
  );

const historySummary = () =>
  screen.getByText(
    (_, element) =>
      element?.tagName === "P" && /of \d+ history records/i.test(element.textContent ?? "")
  );

describe("ApprovalsWorkspace", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/approvals");
  });

  it("searches across core approval metadata", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);
    const search = screen.getByRole("searchbox", {
      name: /ID, agent, action, target, evidence source, or policy/i,
    });

    for (const term of ["Policy Digest", "apr-2026-003", "P-071", "connector"]) {
      await user.clear(search);
      await user.type(search, term);
      expect(queueSummary()).toHaveTextContent(/Showing [1-9]\d* of 5 queue records/i);
      expect(screen.queryByText(/No approvals match/i)).not.toBeInTheDocument();
    }
  });

  it("combines Risk and Review filters and clears all local controls", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    await user.selectOptions(screen.getByLabelText("Risk"), "High");
    await user.selectOptions(screen.getByLabelText("Review"), "Blocked");
    expect(queueSummary()).toHaveTextContent("Showing 1 of 5 queue records");
    expect(screen.getAllByText(/Re-run the failed connector evidence export/i)).not.toHaveLength(0);

    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(screen.getByLabelText("Risk")).toHaveValue("all");
    expect(screen.getByLabelText("Review")).toHaveValue("all");
    expect(screen.getByRole("searchbox")).toHaveValue("");
    expect(queueSummary()).toHaveTextContent("Showing 5 of 5 queue records");
  });

  it("uses the owner-approved concise Queue filter set", () => {
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    expect(screen.getByLabelText("Risk")).toBeInTheDocument();
    expect(screen.getByLabelText("Review")).toBeInTheDocument();
    expect(screen.queryByLabelText("State")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Agent")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Policy")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Expiry")).not.toBeInTheDocument();
  });

  it("replaces Review with State on History and filters terminal records", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    await user.click(screen.getByRole("tab", { name: "History" }));
    expect(screen.queryByLabelText("Review")).not.toBeInTheDocument();
    expect(screen.getByLabelText("State")).toHaveValue("all");

    await user.selectOptions(screen.getByLabelText("State"), "Rejected");
    expect(historySummary()).toHaveTextContent("Showing 1 of 4 history records");
    expect(screen.getAllByText(/Send a vendor follow-up/i)).not.toHaveLength(0);
    expect(new URLSearchParams(window.location.search).get("state")).toBe("Rejected");
    expect(new URLSearchParams(window.location.search).has("review")).toBe(false);

    await user.click(screen.getByRole("button", { name: "Clear filters" }));
    expect(screen.getByLabelText("State")).toHaveValue("all");
    expect(historySummary()).toHaveTextContent("Showing 4 of 4 history records");
  });

  it("reports matching, total, and nearing-expiry counts", async () => {
    const user = userEvent.setup();
    const nearExpiry = APPROVAL_FIXTURES.map((approval) =>
      approval.id === "apr-2026-001"
        ? {
            ...approval,
            requestedAt: new Date(Date.now() - 60 * 60_000).toISOString(),
            expiresAt: new Date(Date.now() + 4 * 60_000).toISOString(),
          }
        : approval
    );
    render(<ApprovalsWorkspace approvals={nearExpiry} />);

    expect(queueSummary()).toHaveTextContent("Showing 5 of 5 queue records");
    expect(queueSummary()).toHaveTextContent("1 nearing expiry");

    await user.type(screen.getByRole("searchbox"), "billing");
    expect(queueSummary()).toHaveTextContent("Showing 1 of 5 queue records");

    await user.click(screen.getByRole("tab", { name: "History" }));
    expect(
      screen.getByText(
        (_, element) =>
          element?.tagName === "P" && /Showing \d+ of \d+ history records/i.test(element.textContent ?? "")
      )
    ).toHaveTextContent("Showing 0 of 4 history records");
  });

  it("ships an approaching-expiry representative fixture", () => {
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    expect(queueSummary()).toHaveTextContent("1 nearing expiry");
    expect(screen.getAllByText("Nearing")).not.toHaveLength(0);
  });

  it("restores supported collection controls from the URL", () => {
    window.history.replaceState(
      null,
      "",
      "/approvals?view=history&q=vendor&risk=High&state=Rejected&sort=agent&dir=desc&page=1"
    );

    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    expect(screen.getByRole("tab", { name: "History" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("searchbox")).toHaveValue("vendor");
    expect(screen.getByLabelText("Risk")).toHaveValue("High");
    expect(screen.queryByLabelText("Review")).not.toBeInTheDocument();
    expect(screen.getByLabelText("State")).toHaveValue("Rejected");
    expect(screen.getByRole("columnheader", { name: "Agent" })).toHaveAttribute("aria-sort", "descending");
  });

  it("writes supported search and filter state to the URL", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    await user.type(screen.getByRole("searchbox"), "connector");
    await user.selectOptions(screen.getByLabelText("Risk"), "High");
    await user.selectOptions(screen.getByLabelText("Review"), "Blocked");
    await user.click(screen.getByRole("button", { name: "Agent" }));
    await user.click(screen.getByRole("button", { name: "Agent" }));

    await waitFor(() => {
      const params = new URLSearchParams(window.location.search);
      expect(params.get("q")).toBe("connector");
      expect(params.get("risk")).toBe("High");
      expect(params.get("review")).toBe("Blocked");
      expect(params.get("sort")).toBe("agent");
      expect(params.get("dir")).toBe("desc");
    });
  });

  it("sorts Queue records by risk, agent, requested time, and review progress", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);
    const table = screen.getByRole("table");

    await user.click(within(table).getByRole("button", { name: "Risk" }));
    expect(within(table).getAllByRole("link")[0]).toHaveTextContent(
      /Send a remediation notice/i
    );

    await user.click(within(table).getByRole("button", { name: "Agent" }));
    expect(within(table).getAllByRole("link")[0]).toHaveTextContent(
      /Re-run the failed connector evidence export/i
    );

    await user.click(within(table).getByRole("button", { name: "Requested" }));
    expect(within(table).getAllByRole("link")[0]).toHaveTextContent(
      /Tag a completed intake batch/i
    );

    await user.click(within(table).getByRole("button", { name: "Review" }));
    expect(within(table).getAllByRole("link")[0]).toHaveTextContent(
      /Send a remediation notice/i
    );
  });

  it("sorts expiry in the announced direction and changes attention ordering", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);
    const table = screen.getByRole("table", { name: "Approval Queue" });
    const firstAction = () => within(table).getAllByRole("link")[0];

    const approvalHeader = within(table).getByRole("columnheader", { name: "Approval" });
    expect(approvalHeader).toHaveAttribute("aria-sort", "ascending");
    expect(firstAction()).toHaveTextContent(/Send a remediation notice/i);
    await user.click(within(approvalHeader).getByRole("button", { name: "Approval" }));
    expect(approvalHeader).toHaveAttribute("aria-sort", "descending");
    expect(firstAction()).toHaveTextContent(/Tag a completed intake batch/i);

    const expiryHeader = within(table).getByRole("columnheader", { name: "Expiry" });
    await user.click(within(expiryHeader).getByRole("button", { name: "Expiry" }));
    expect(expiryHeader).toHaveAttribute("aria-sort", "ascending");
    expect(firstAction()).toHaveTextContent(/Send a remediation notice/i);
    await user.click(within(expiryHeader).getByRole("button", { name: "Expiry" }));
    expect(expiryHeader).toHaveAttribute("aria-sort", "descending");
    expect(firstAction()).toHaveTextContent(/Re-run the failed connector evidence export/i);
  });

  it("gives the table an accessible name and exposes sort state on headers", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);
    const table = screen.getByRole("table", { name: "Approval Queue" });
    const riskHeader = within(table).getByRole("columnheader", { name: "Risk" });

    expect(riskHeader).toHaveAttribute("aria-sort", "none");
    await user.click(within(riskHeader).getByRole("button", { name: "Risk" }));
    expect(riskHeader).toHaveAttribute("aria-sort", "descending");
  });

  it("preserves key approval context in the mobile card list", () => {
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);
    const list = screen.getByRole("list", { name: "Approval Queue mobile list" });
    const card = within(list).getByRole("link", {
      name: /Send a remediation notice to the enterprise billing contact/i,
    });

    expect(within(card).getByText("Pending")).toBeInTheDocument();
    expect(within(card).getByText(/billing-operations@northstar\.example/i)).toBeInTheDocument();
    expect(within(card).getByText(/Policy Digest Agent/i)).toBeInTheDocument();
    expect(within(card).getByText(/apr-2026-001/i)).toBeInTheDocument();
    expect(within(card).getByText("Requested")).toBeInTheDocument();
    expect(within(card).getByText("Expires")).toBeInTheDocument();
    expect(within(card).getByText("Review")).toBeInTheDocument();
  });

  it("keeps deliberately long action, agent, policy, and identifier values breakable", () => {
    const longToken = "governedcontent".repeat(18);
    const approval: ApprovalRecord = {
      ...APPROVAL_FIXTURES.find((item) => item.id === "apr-2026-008")!,
      id: `apr-${longToken}`,
      action: `Review ${longToken}`,
      agent: { id: `agent-${longToken}`, name: `Agent ${longToken}` },
      policy: `Policy ${longToken}`,
    };
    render(<ApprovalsWorkspace approvals={[approval]} />);

    const table = screen.getByRole("table", { name: "Approval Queue" });
    expect(within(table).getByRole("link", { name: approval.action })).toHaveClass("break-words");
    expect(within(table).getByRole("cell", { name: approval.agent.name })).toHaveClass("break-words");
    expect(within(table).getByText((_, element) => element?.tagName === "P" && element.textContent?.includes(approval.policy) === true)).toHaveClass("break-words");

    const mobileCard = within(screen.getByRole("list", { name: "Approval Queue mobile list" })).getByRole("link");
    expect(within(mobileCard).getByText(approval.action)).toHaveClass("break-words");
    expect(within(mobileCard).getByText((_, element) => element?.tagName === "P" && element.textContent?.includes(approval.agent.name) === true)).toHaveClass("break-words");
  });

  it("paginates a finite local fixture collection", async () => {
    const user = userEvent.setup();
    const template = APPROVAL_FIXTURES.find((approval) => approval.id === "apr-2026-008")!;
    const approvals: ApprovalRecord[] = Array.from({ length: 9 }, (_, index) => ({
      ...template,
      id: `apr-page-${index + 1}`,
      action: `Review paginated fixture ${index + 1}`,
    }));

    render(<ApprovalsWorkspace approvals={approvals} />);
    expect(screen.getByText("Page 1 of 2")).toBeInTheDocument();
    expect(screen.queryByText("Review paginated fixture 9")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByText("Page 2 of 2")).toBeInTheDocument();
    expect(screen.getAllByText("Review paginated fixture 9")).not.toHaveLength(0);
  });

  it("renders loading, error, initial-empty, and filtered-empty states", async () => {
    const { rerender } = render(
      <ApprovalsWorkspace approvals={APPROVAL_FIXTURES} presentationState="error" />
    );
    expect(screen.getByText("Approval data is unavailable")).toBeInTheDocument();

    rerender(<ApprovalsWorkspace approvals={[]} presentationState="empty" />);
    expect(screen.getByText("No actions currently require authorization")).toBeInTheDocument();

    rerender(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} presentationState="ready" />);
    const user = userEvent.setup();
    await user.type(screen.getByRole("searchbox"), "no-matching-approval");
    expect(screen.getByText("No approvals match the current search or filters")).toBeInTheDocument();

    rerender(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} presentationState="loading" />);
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows a distinct History view with terminal and indeterminate records", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    const historyTab = screen.getByRole("tab", { name: "History" });
    await user.click(historyTab);
    expect(historyTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getAllByText(/Outcome: Indeterminate/i)).not.toHaveLength(0);
    expect(screen.getAllByText("Approved")).not.toHaveLength(0);
    expect(screen.getAllByText("Rejected")).not.toHaveLength(0);
  });

  it("defaults History to newest decision time and presents decision context", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    await user.click(screen.getByRole("tab", { name: "History" }));
    const table = screen.getByRole("table", { name: "Approval History" });
    const decidedHeader = within(table).getByRole("columnheader", { name: "Decided" });
    expect(decidedHeader).toHaveAttribute("aria-sort", "descending");
    expect(within(table).getAllByRole("link")[0]).toHaveTextContent(/Add a reviewed categorization note/i);
    expect(within(table).getAllByText(/Reviewer: Prototype reviewer/i)).not.toHaveLength(0);
    expect(within(table).getByText(/Reason: The note is consistent/i)).toBeInTheDocument();
    expect(within(table).getByText("corr-apr-2026-005")).toBeInTheDocument();

    await user.click(within(decidedHeader).getByRole("button", { name: "Decided" }));
    expect(decidedHeader).toHaveAttribute("aria-sort", "ascending");
    expect(within(table).getAllByRole("link")[0]).toHaveTextContent(/Export a reviewed evidence bundle/i);
  });

  it("searches evidence-source labels", async () => {
    const user = userEvent.setup();
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    await user.type(screen.getByRole("searchbox"), "Billing remediation evidence packet");

    expect(queueSummary()).toHaveTextContent("Showing 1 of 5 queue records");
    expect(screen.getAllByText(/Send a remediation notice/i)).not.toHaveLength(0);
  });

  it("preserves search, filters, sort, direction, and page in detail return links", () => {
    const template = APPROVAL_FIXTURES.find((approval) => approval.id === "apr-2026-003")!;
    const approvals: ApprovalRecord[] = Array.from({ length: 9 }, (_, index) => ({
      ...template,
      id: `apr-context-${index + 1}`,
      action: `Context fixture ${index + 1}`,
    }));
    window.history.replaceState(
      null,
      "",
      "/approvals?view=queue&q=Context&risk=High&review=Blocked&sort=agent&dir=desc&page=2"
    );

    render(<ApprovalsWorkspace approvals={approvals} />);

    const list = screen.getByRole("list", { name: "Approval Queue mobile list" });
    const link = within(list).getByRole("link", { name: /Context fixture/i });
    const href = new URL(link.getAttribute("href")!, "http://localhost");
    expect(href.searchParams.get("from")).toBe(
      "/approvals?view=queue&q=Context&risk=High&review=Blocked&sort=agent&dir=desc&page=2"
    );
  });

  it("replays collection state when browser Back or Forward emits popstate", () => {
    render(<ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />);

    act(() => {
      window.history.pushState(null, "", "/approvals?view=history&state=Expired&sort=decided&dir=asc");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    expect(screen.getByRole("tab", { name: "History" })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByLabelText("State")).toHaveValue("Expired");
    expect(screen.getByRole("columnheader", { name: "Decided" })).toHaveAttribute("aria-sort", "ascending");

    act(() => {
      window.history.pushState(null, "", "/approvals?view=queue&risk=High&review=Blocked");
      window.dispatchEvent(new PopStateEvent("popstate"));
    });
    expect(screen.getByRole("tab", { name: /Queue/i })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByLabelText("Risk")).toHaveValue("High");
    expect(screen.getByLabelText("Review")).toHaveValue("Blocked");
  });
});
