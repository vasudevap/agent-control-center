"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Boxes } from "lucide-react";
import { NAV_ITEMS, SETTINGS_NAV_ITEM } from "./nav-items";
import { Separator } from "@/components/ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

const OPERATIONS_NAV_ITEMS = NAV_ITEMS.slice(0, 5);
const GOVERNANCE_NAV_ITEMS = NAV_ITEMS.slice(5);

/**
 * Active state uses a left accent bar plus weight/color change rather
 * than a filled pill. It reads as a rail indicator (console pattern)
 * instead of a button-like chip, and keeps every row's left edge
 * available for the same accent-bar language used for risk in
 * Approvals, so the whole shell shares one "leading edge = meaning"
 * convention.
 *
 * The label is wrapped in a tooltip unconditionally rather than only
 * at the collapsed width: harmless when the label is already visible
 * inline at the full width, and it is the only way to know what an
 * icon means once the rail narrows to icon-only.
 */
function NavLink({
  item,
  active,
  onNavigate,
}: {
  item: (typeof NAV_ITEMS)[number];
  active: boolean;
  onNavigate?: () => void;
}) {
  const Icon = item.icon;
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <Link
          href={item.href}
          onClick={onNavigate}
          aria-current={active ? "page" : undefined}
          className={cn(
            "relative flex items-center gap-2.5 rounded-atlas-sm py-1.5 pl-3 pr-2 font-mono text-[11px] font-medium uppercase tracking-[0.03em] leading-none transition-colors",
            active ? "bg-surface-active text-foreground" : "text-foreground-secondary hover:bg-surface-hover hover:text-foreground"
          )}
        >
          <span
            aria-hidden="true"
            className={cn("absolute inset-y-0.5 left-0 w-[3px] rounded-full", active ? "bg-brand" : "bg-transparent")}
          />
          <Icon className={cn("size-4 shrink-0", active && "text-brand")} aria-hidden="true" />
          <span className="hidden flex-1 truncate lg:inline">{item.label}</span>
          {typeof item.badge === "number" && item.badge > 0 ? (
            <span
              className={cn(
                "hidden h-4.5 min-w-4.5 items-center justify-center rounded-atlas-sm px-1 font-mono text-[10px] font-semibold lg:flex",
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

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <TooltipProvider delayDuration={300}>
      <nav className="flex h-full flex-col gap-1 overflow-y-auto p-2.5" aria-label="Primary">
        <div className="flex flex-1 flex-col gap-4">
          <div className="flex flex-col gap-0.5">
            <p className="hidden px-3 pb-1 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] text-foreground-tertiary lg:block">
              Operations
            </p>
            {OPERATIONS_NAV_ITEMS.map((item) => (
              <NavLink key={item.href} item={item} active={pathname === item.href} onNavigate={onNavigate} />
            ))}
          </div>

          <div className="flex flex-col gap-0.5 border-t border-border-subtle pt-3">
            <p className="hidden px-3 pb-1 font-mono text-[9px] font-semibold uppercase tracking-[0.14em] text-foreground-tertiary lg:block">
              Governance
            </p>
            {GOVERNANCE_NAV_ITEMS.map((item) => (
              <NavLink key={item.href} item={item} active={pathname === item.href} onNavigate={onNavigate} />
            ))}
          </div>
        </div>

        <Separator className="my-1.5" />
        <NavLink item={SETTINGS_NAV_ITEM} active={pathname === SETTINGS_NAV_ITEM.href} onNavigate={onNavigate} />
      </nav>
    </TooltipProvider>
  );
}

/**
 * The rail now extends to the very top of the viewport and owns the
 * logo/app name itself, instead of a separate full-width status strip
 * above it trying to independently match its width. Three tiers:
 * full (lg+, icon + label), collapsed-to-icons (md–lg), and hidden
 * below md in favor of the existing menu-triggered drawer.
 */
export function Sidebar() {
  return (
    <aside
      className="fixed inset-y-0 left-0 z-20 hidden w-(--sidebar-width-collapsed) flex-col border-r border-border-default bg-surface md:flex lg:w-(--sidebar-width)"
      aria-label="Sidebar"
    >
      <div className="flex h-(--statusbar-height) shrink-0 items-center gap-2 border-b border-border-default px-3">
        <span className="flex size-5 shrink-0 items-center justify-center rounded-atlas-sm bg-brand-solid text-foreground-on-brand">
          <Boxes className="size-3" aria-hidden="true" />
        </span>
        <span className="hidden font-mono text-[11px] font-semibold uppercase tracking-[0.12em] text-foreground lg:inline">Atlas</span>
      </div>
      <SidebarNav />
    </aside>
  );
}
