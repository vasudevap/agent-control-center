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

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: number;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Overview", href: "/", icon: LayoutDashboard },
  { label: "Agents", href: "/agents", icon: Bot },
  { label: "Runs", href: "/runs", icon: Workflow },
  { label: "Approvals", href: "/approvals", icon: CheckSquare, badge: 3 },
  { label: "Alerts", href: "/alerts", icon: Bell, badge: 2 },
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
