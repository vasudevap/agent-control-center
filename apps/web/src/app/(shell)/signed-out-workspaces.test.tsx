import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AlertsWorkspace } from "./alerts/alerts-workspace";
import { ALERT_FIXTURES } from "./alerts/alert-data";
import { ApprovalsWorkspace } from "./approvals/approvals-workspace";
import { APPROVAL_FIXTURES } from "./approvals/approval-data";
import { AuditWorkspace } from "./audit/audit-workspace";
import { AUDIT_FIXTURES } from "./audit/audit-data";
import { ConnectorsWorkspace } from "./connectors/connectors-workspace";
import { CONNECTOR_FIXTURES } from "./connectors/connector-data";
import { RunsWorkspace } from "./runs/runs-workspace";

const API_BASE_URL = "https://api.atlas.grafley.com";
const SIGN_IN_URL = `${API_BASE_URL}/auth/owner/google/start`;

function stubOwnerSessionMissing() {
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", API_BASE_URL);
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          error: {
            code: "owner_session_missing",
            message: "Owner session is not authorized.",
          },
        }),
        { status: 401 },
      ),
    ),
  );
}

async function expectSignedOutPage(description: string, hiddenTable: string) {
  expect(await screen.findByText("Owner sign-in required")).toBeInTheDocument();
  expect(screen.getByText(description)).toBeInTheDocument();
  expect(screen.getByRole("link", { name: "Sign in with Google" })).toHaveAttribute(
    "href",
    SIGN_IN_URL,
  );
  expect(screen.queryByRole("table", { name: hiddenTable })).not.toBeInTheDocument();
}

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  window.history.replaceState(null, "", "/");
});

describe("signed-out workspace states", () => {
  it.each([
    {
      name: "Runs",
      ui: <RunsWorkspace />,
      description: "Sign in to load runtime run history from the Atlas API.",
      table: "Executions inventory",
    },
    {
      name: "Alerts",
      ui: <AlertsWorkspace alerts={ALERT_FIXTURES} />,
      description: "Sign in to load runtime alert monitoring from the Atlas API.",
      table: "Alerts inventory",
    },
    {
      name: "Approvals",
      ui: <ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />,
      description: "Sign in to load runtime approval records from the Atlas API.",
      table: "Approval Queue",
    },
    {
      name: "Connectors",
      ui: <ConnectorsWorkspace connectors={CONNECTOR_FIXTURES} />,
      description: "Sign in to load runtime connector data from the Atlas API.",
      table: "Connector inventory",
    },
    {
      name: "Audit",
      ui: <AuditWorkspace events={AUDIT_FIXTURES} />,
      description: "Sign in to load runtime audit events from the Atlas API.",
      table: "Audit event history",
    },
  ])("$name replaces fixture content with the shared sign-in card", async ({ ui, description, table }) => {
    stubOwnerSessionMissing();

    render(ui);

    await expectSignedOutPage(description, table);
  });

});
