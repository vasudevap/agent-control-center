/**
 * Alerts are the one Overview fixture that isn't already derivable
 * from agent-data.ts or approval-data.ts, so they remain their own
 * small fixture set here. Fleet health, active runs, schedule, and
 * pending-approval summaries are all derived directly from the
 * canonical agent and approval fixtures inside overview-dashboard.tsx
 * instead of being duplicated as separate, independently-authored
 * mock arrays (the baseline's Overview used seven invented agent
 * names that matched none of the real six-agent inventory).
 */
import type { AlertItem } from "../types/overview.types";

export const mockAlerts: AlertItem[] = [
  {
    id: "alt-901",
    severity: "critical",
    title: "Connector authentication expired",
    description: "Policy Digest Agent lost access to its evidence-export connector. Runs are paused.",
    timestamp: "6 hours ago",
    source: "Policy Digest Agent",
    sourceAgentId: "agent-policy-digest",
  },
  {
    id: "alt-902",
    severity: "warning",
    title: "Elevated policy-review backlog",
    description: "Invoice Reconciliation Agent has three invoices waiting on policy review.",
    timestamp: "12 minutes ago",
    source: "Invoice Reconciliation Agent",
    sourceAgentId: "agent-invoice-reconcile",
  },
  {
    id: "alt-903",
    severity: "information",
    title: "Policy updated",
    description: "\"External Communications P-214\" now requires step-up confirmation for Critical requests.",
    timestamp: "2 hours ago",
    source: "Policies",
  },
];
