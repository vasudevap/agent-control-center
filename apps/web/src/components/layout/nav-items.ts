import {
  Activity,
  LayoutDashboard,
  Bot,
  Workflow,
  CheckSquare,
  Bell,
  type LucideIcon,
} from "lucide-react";
import { CONTROL_CENTER_ROUTES } from "@/lib/control-center-routes";

export const APPROVALS_ICON = CheckSquare;

export interface NavItem {
  label: string;
  href: string;
  icon: LucideIcon;
  badge?: number;
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Overview", href: CONTROL_CENTER_ROUTES.overview, icon: LayoutDashboard },
  { label: "Agents", href: CONTROL_CENTER_ROUTES.agents, icon: Bot },
  { label: "Executions", href: CONTROL_CENTER_ROUTES.executions, icon: Workflow },
  { label: "Alerts", href: CONTROL_CENTER_ROUTES.alerts, icon: Bell },
  { label: "Activity", href: CONTROL_CENTER_ROUTES.activity, icon: Activity },
];
