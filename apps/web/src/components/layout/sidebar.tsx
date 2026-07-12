"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Boxes } from "lucide-react";
import { NAV_ITEMS, SETTINGS_NAV_ITEM } from "./nav-items";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

function NavLink({
  item,
  active,
  onNavigate,
  className,
}: {
  item: (typeof NAV_ITEMS)[number];
  active: boolean;
  onNavigate?: () => void;
  className?: string;
}) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      className={cn(
        "group relative flex items-center gap-2 rounded-atlas-md px-2 py-2 text-sm font-medium leading-none transition-colors",
        active
          ? "bg-brand-subtle text-brand"
          : "text-foreground-secondary hover:bg-surface-hover hover:text-foreground",
        className
      )}
    >
      {active && (
        <span
          aria-hidden="true"
          className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-brand"
        />
      )}
      <Icon className="size-4 shrink-0" aria-hidden="true" />
      <span className="flex-1 truncate">{item.label}</span>
      {item.badge ? (
        <span
          className={cn(
            "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 font-mono text-[11px] font-semibold",
            active
              ? "bg-brand-solid text-foreground-on-brand"
              : "bg-surface-tertiary text-foreground-secondary"
          )}
        >
          {item.badge}
        </span>
      ) : null}
    </Link>
  );
}

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex h-full flex-col gap-1 overflow-y-auto p-2" aria-label="Primary">
      <div className="flex items-center gap-2 px-2 py-2">
        <div className="flex size-8 items-center justify-center rounded-atlas-md bg-brand-solid text-foreground-on-brand">
          <Boxes className="size-4" aria-hidden="true" />
        </div>
        <span className="text-sm font-semibold tracking-tight text-foreground">Atlas</span>
      </div>

      <div className="mt-1 flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.href}
            item={item}
            active={pathname === item.href}
            onNavigate={onNavigate}
            className={item.label === "Connectors" ? "mt-4" : undefined}
          />
        ))}
      </div>

      <Separator className="my-2" />
      <NavLink
        item={SETTINGS_NAV_ITEM}
        active={pathname === SETTINGS_NAV_ITEM.href}
        onNavigate={onNavigate}
      />
    </nav>
  );
}

export function Sidebar() {
  return (
    <aside
      className="fixed inset-y-0 left-0 z-30 hidden w-(--sidebar-width) border-r border-border-default bg-surface lg:block"
      aria-label="Sidebar"
    >
      <SidebarNav />
    </aside>
  );
}
