"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Boxes } from "lucide-react";
import { NAV_ITEMS } from "./nav-items";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { CONTROL_CENTER_ROOT } from "@/lib/control-center-routes";
import { cn } from "@/lib/utils";

/**
 * Active state uses a left accent bar plus weight/color change rather
 * than a filled pill. It reads as a rail indicator (console pattern)
 * instead of a button-like chip, and keeps every row's left edge
 * available for the same accent-bar language used for risk in
 * Approvals, so the whole shell shares one "leading edge = meaning"
 * convention.
 *
 * Labels remain visible at every rendered sidebar width. Tooltips are
 * retained as a fallback for any label that is truncated by the
 * compact middle tier.
 */
function NavLink({
  item,
  active,
  onNavigate,
  expanded = false,
}: {
  item: (typeof NAV_ITEMS)[number];
  active: boolean;
  onNavigate?: () => void;
  expanded?: boolean;
}) {
  const Icon = item.icon;
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Link
          href={item.href}
          onClick={onNavigate}
          aria-label={item.label}
          aria-current={active ? "page" : undefined}
          className={cn(
            "relative flex items-center rounded-atlas-sm font-mono font-medium uppercase leading-none transition-colors",
            expanded
              ? "flex-row gap-2.5 py-1.5 pl-3 pr-2 text-[11px] tracking-[0.03em]"
              : "flex-col gap-1 px-1 py-2 text-[9px] tracking-[-0.01em] lg:flex-row lg:gap-2.5 lg:py-1.5 lg:pl-3 lg:pr-2 lg:text-[11px] lg:tracking-[0.03em]",
            active ? "bg-surface-active text-foreground" : "text-foreground-secondary hover:bg-surface-hover hover:text-foreground"
          )}
        >
          <span
            aria-hidden="true"
            className={cn("absolute inset-y-0.5 left-0 w-[3px] rounded-full", active ? "bg-brand" : "bg-transparent")}
          />
          <Icon className={cn("size-4 shrink-0", active && "text-brand")} aria-hidden="true" />
          <span className={cn(
            expanded
              ? "min-w-0 flex-1 truncate text-left"
              : "w-full whitespace-nowrap text-center lg:min-w-0 lg:flex-1 lg:truncate lg:text-left"
          )}>{item.label}</span>
          {typeof item.badge === "number" && item.badge > 0 ? (
            <span
              className={cn(
                "h-4.5 min-w-4.5 items-center justify-center rounded-atlas-sm px-1 font-mono text-[10px] font-semibold",
                expanded ? "flex" : "hidden lg:flex",
                active ? "bg-brand-solid text-foreground-on-brand" : "bg-surface-tertiary text-foreground-secondary"
              )}
            >
              {item.badge}
            </span>
          ) : null}
        </Link>
      </TooltipTrigger>
      <TooltipContent side="right">{item.label}</TooltipContent>
    </Tooltip>
  );
}

export function SidebarNav({ onNavigate, expanded = false }: { onNavigate?: () => void; expanded?: boolean }) {
  const pathname = usePathname();
  const isActive = (href: string) =>
    pathname === href ||
    (href !== "/" &&
      href !== CONTROL_CENTER_ROOT &&
      pathname.startsWith(`${href}/`));

  return (
    <TooltipProvider delayDuration={300}>
      <nav className="flex h-full flex-col gap-1 overflow-y-auto p-2.5" aria-label="Primary">
        <div className="flex flex-1 flex-col gap-4">
          <div className="flex flex-col gap-0.5">
            <p className={cn("px-3 pb-1 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] text-foreground-tertiary", expanded ? "block" : "hidden lg:block")}>
              Operations
            </p>
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.href} item={item} active={isActive(item.href)} onNavigate={onNavigate} expanded={expanded} />
            ))}
          </div>
        </div>
      </nav>
    </TooltipProvider>
  );
}

/**
 * The rail now extends to the very top of the viewport and owns the
 * logo/app name itself, instead of a separate full-width status strip
 * above it trying to independently match its width. Three tiers:
 * full (lg+, icon + label), compact labeled rail (md–lg), and hidden
 * below md in favor of the existing menu-triggered labeled drawer.
 */
export function Sidebar() {
  return (
    <aside
      className="fixed inset-y-0 left-0 z-20 hidden w-(--sidebar-width-collapsed) flex-col border-r border-border-default bg-surface md:flex lg:w-(--sidebar-width)"
      aria-label="Sidebar"
    >
      <div className="flex h-(--statusbar-height) shrink-0 items-center gap-1 border-b border-border-default px-2 lg:gap-2 lg:px-3">
        <span className="flex size-5 shrink-0 items-center justify-center rounded-atlas-sm bg-brand-solid text-foreground-on-brand">
          <Boxes className="size-3" aria-hidden="true" />
        </span>
        <span className="min-w-0 truncate font-mono text-[9px] font-semibold uppercase tracking-[0.04em] text-foreground lg:text-[11px] lg:tracking-[0.12em]">Atlas</span>
      </div>
      <SidebarNav />
    </aside>
  );
}
