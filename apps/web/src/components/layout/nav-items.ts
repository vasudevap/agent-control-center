import {
  LayoutDashboard,
  Bot,
  Workflow,
  CheckSquare,
  Bell,
  Plug,
  ShieldCheck,
  Package,
  ScrollText,
  Settings,
  type LucideIcon,
} from "lucide-react";
import { MOCK_AGENTS } from "@/app/(shell)/agents/agent-data";
import { APPROVAL_FIXTURES, isQueueApproval } from "@/app/(shell)/approvals/approval-data";
import { mockAlerts } from "@/features/overview/data/mock-data";

export const APPROVALS_ICON = CheckSquare;

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: number;
}

/**
 * Badge counts are derived from the same fixture data every screen
 * reads, instead of separately hardcoded numbers. This is a small but
 * deliberate correction carried into the exploration: nav badges can
 * never silently disagree with what Queue or Overview actually show.
 */
const pendingApprovalsCount = APPROVAL_FIXTURES.filter(isQueueApproval).length;
const activeAlertsCount = mockAlerts.length;

export const NAV_ITEMS: NavItem[] = [
  { label: "Overview", href: "/", icon: LayoutDashboard },
  { label: "Agents", href: "/agents", icon: Bot },
  { label: "Runs", href: "/runs", icon: Workflow },
  { label: "Approvals", href: "/approvals", icon: APPROVALS_ICON, badge: pendingApprovalsCount },
  { label: "Alerts", href: "/alerts", icon: Bell, badge: activeAlertsCount },
  { label: "Connectors", href: "/connectors", icon: Plug },
  { label: "Policies", href: "/policies", icon: ShieldCheck },
  { label: "Artifacts", href: "/artifacts", icon: Package },
  { label: "Audit", href: "/audit", icon: ScrollText },
];

export const SETTINGS_NAV_ITEM: NavItem = {
  label: "Settings",
  href: "/settings",
  icon: Settings,
};

export const FLEET_PULSE = {
  totalAgents: MOCK_AGENTS.length,
  healthyAgents: MOCK_AGENTS.filter((agent) => agent.health === "healthy").length,
  degradedAgents: MOCK_AGENTS.filter((agent) => agent.health === "degraded").length,
  offlineAgents: MOCK_AGENTS.filter((agent) => agent.health === "offline").length,
  runningAgents: MOCK_AGENTS.filter((agent) => agent.status === "running" || agent.status === "active").length,
  pendingApprovals: pendingApprovalsCount,
  activeAlerts: activeAlertsCount,
};
