# Work Order 005 — Application Shell — Design Director Review Package

**Work Order:** APP-005
**Status:** Completed
**Design Review:** Approved
**Final Review:** Passed
**Merge:** Completed
**Scope:** Application shell infrastructure only — no business functionality
**Note on numbering:** this package was requested as "Work Order 006"; no such work order exists in `work-orders/` (only 001–005). Confirmed with the requester that this refers to Work Order 005 (App Shell), the most recently completed implementation.

---

## 0. Final Disposition

Design Director reviewed this package and **approved for merge with three minor changes**, all implemented and re-verified before merge:

1. `NotificationsMenu unreadCount` changed from `2` to `0` in `src/components/layout/top-bar.tsx` — the placeholder must not imply activity that isn't real.
2. `src/app/(shell)/agents/[agentId]/page.tsx` and `src/app/(shell)/runs/[runId]/page.tsx` — titles changed from raw-ID interpolations (`` `Agent ${agentId}` `` / `` `Run ${runId}` ``) to stable strings (`"Agent Details"` / `"Run Details"`); the ID moved into each page's description, and remains visible in the breadcrumb.
3. Search Field placeholder copy in `top-bar.tsx` changed from `"Search Atlas..."` to `"Search agents, runs, artifacts..."`.

Post-change verification: `tsc --noEmit` clean, `eslint` clean (0 warnings), `next build` succeeded (same 11 static + 2 dynamic routes), responsive visual sanity check passed, no unintended changes introduced. This project has no git repository, so "merge" is recorded here as: these changes are the final, accepted state of the working tree.

The file contents in §5 below reflect the **pre-refinement** state (as submitted for review). The three post-review edits are documented above rather than backfilled into §5, to preserve this package as an accurate record of what was actually reviewed.

---

## 1. Summary of Everything Implemented

Work Order 005 asked for the permanent Atlas application shell — the foundation every future screen sits inside — with placeholder routes for every destination in the sidebar, and explicitly no business logic.

Delivered:

- **Page Container** — extracted the shell's content-width/padding wrapper into its own component
- **Breadcrumb** — full implementation per `component-library.md` §3 (mobile back-collapse, desktop trail, dropdown-based truncation for paths >4 levels)
- **Global Search Placeholder** — a real `SearchField` component (per spec §16) wired into the Top Navigation; controlled locally, not connected to any data source
- **Notifications placeholder panel** — the previously-bare Bell icon is now a functioning dropdown panel showing a placeholder empty state
- **Focus-trap fix** on the mobile navigation drawer — this closed a known accessibility gap that `component-library.md` §1 had flagged during the component-spec pass
- **Global Loading Shell** — a route-segment `loading.tsx` with a generic, content-agnostic skeleton
- **Global Error Layout** — a route-segment `error.tsx` client boundary, reusing the existing `ErrorState` component and wired to Next.js's `reset()`
- **Global Empty State** — formalized as `PlaceholderPage`/`PlaceholderBody`, reusing the existing `EmptyState` component
- **Routing restructure** — everything moved into a `(shell)` route group so the shell (`Sidebar` + `TopBar` + `PageContainer`) wraps every route exactly once, with shared loading/error boundaries
- **12 routes scaffolded**: Overview (existing dashboard, relocated, content untouched), Agents + Agent Detail, Runs + Run Detail, Approvals, Alerts, Connectors, Policies, Artifacts, Audit, Settings — the 10 non-Overview top-level routes and 2 detail routes render `PlaceholderPage`, not mock dashboards

Verified: `tsc --noEmit` clean, `eslint` clean (0 warnings), `next build` succeeds (11 static + 2 dynamic routes), manually exercised every route in the browser in both themes, at desktop/tablet/mobile, including the notifications panel and the mobile drawer's new focus trap.

---

## 2. Every File Created

**Components:**
1. `src/components/layout/page-container.tsx`
2. `src/components/layout/breadcrumb.tsx`
3. `src/components/ui/search-field.tsx`
4. `src/components/layout/notifications-menu.tsx`
5. `src/components/layout/placeholder-page.tsx`
6. `src/components/layout/page-loading-skeleton.tsx`

**Routes:**
7. `src/app/(shell)/layout.tsx`
8. `src/app/(shell)/loading.tsx`
9. `src/app/(shell)/error.tsx`
10. `src/app/(shell)/page.tsx` (Overview — relocated; see §6 for why this counts as "created" rather than "modified")
11. `src/app/(shell)/agents/page.tsx`
12. `src/app/(shell)/agents/[agentId]/page.tsx`
13. `src/app/(shell)/runs/page.tsx`
14. `src/app/(shell)/runs/[runId]/page.tsx`
15. `src/app/(shell)/approvals/page.tsx`
16. `src/app/(shell)/alerts/page.tsx`
17. `src/app/(shell)/connectors/page.tsx`
18. `src/app/(shell)/policies/page.tsx`
19. `src/app/(shell)/artifacts/page.tsx`
20. `src/app/(shell)/audit/page.tsx`
21. `src/app/(shell)/settings/page.tsx`

## 3. Every File Modified

1. `src/components/layout/dashboard-layout.tsx` — now composes `PageContainer` instead of inline width/padding classes
2. `src/components/layout/top-bar.tsx` — wires in `SearchField` and swaps the bare Bell button for `NotificationsMenu`
3. `src/components/layout/mobile-nav-drawer.tsx` — added focus-trap logic (initial focus, Tab/Shift+Tab cycling, focus restoration on close)

## 4. Files Removed / Relocated

- `src/app/page.tsx` — **deleted**. Its content moved to `src/app/(shell)/page.tsx` (the `(shell)` route group doesn't affect the URL, so `/` is unchanged). The `OverviewDashboard` feature component it renders (`src/features/overview/...`) was **not touched** — same mock data, same sections, same behavior.

---

## 5. Full File Contents

### 5.1 Created — Components

#### `src/components/layout/page-container.tsx`
```tsx
import { cn } from "@/lib/utils";

export interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Consistent max-width and padding for content rendered inside the app
 * shell's main region. Every route's content sits inside exactly one of
 * these — never a raw <main> or a bespoke width/padding per screen.
 */
export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <div className={cn("mx-auto max-w-[1600px] px-4 py-6 sm:px-6 sm:py-8", className)}>
      {children}
    </div>
  );
}
```

#### `src/components/layout/breadcrumb.tsx`
```tsx
"use client";

import Link from "next/link";
import { ChevronRight, MoreHorizontal } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

const MAX_VISIBLE_CRUMBS = 4;

function CrumbLink({ item, isCurrent }: { item: BreadcrumbItem; isCurrent: boolean }) {
  if (isCurrent || !item.href) {
    return (
      <span
        aria-current={isCurrent ? "page" : undefined}
        className="text-sm font-medium text-foreground"
      >
        {item.label}
      </span>
    );
  }

  return (
    <Link
      href={item.href}
      className="text-sm font-medium text-foreground-secondary transition-colors hover:text-foreground hover:underline"
    >
      {item.label}
    </Link>
  );
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  if (items.length === 0) return null;

  const lastIndex = items.length - 1;
  const isTruncated = items.length > MAX_VISIBLE_CRUMBS;

  const visible = isTruncated
    ? {
        leading: items.slice(0, 1),
        hidden: items.slice(1, lastIndex),
        trailing: items.slice(lastIndex),
      }
    : null;

  return (
    <nav aria-label="Breadcrumb" className={className}>
      {/* Mobile: collapse to a single "back" affordance */}
      {items.length > 1 && (
        <Link
          href={items[lastIndex - 1].href ?? "#"}
          className="flex items-center gap-1 text-sm font-medium text-foreground-secondary hover:text-foreground sm:hidden"
        >
          <ChevronRight className="size-3.5 rotate-180" aria-hidden="true" />
          {items[lastIndex - 1].label}
        </Link>
      )}

      {/* Desktop: full trail */}
      <ol className="hidden items-center gap-1.5 sm:flex">
        {isTruncated && visible ? (
          <>
            <li className="flex items-center gap-1.5">
              <CrumbLink item={visible.leading[0]} isCurrent={false} />
              <ChevronRight className="size-3.5 text-foreground-tertiary" aria-hidden="true" />
            </li>
            <li className="flex items-center gap-1.5">
              <DropdownMenu>
                <DropdownMenuTrigger
                  className="flex size-6 items-center justify-center rounded-atlas-sm text-foreground-tertiary transition-colors hover:bg-surface-hover hover:text-foreground"
                  aria-label="Show hidden breadcrumb items"
                >
                  <MoreHorizontal className="size-3.5" aria-hidden="true" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start">
                  {visible.hidden.map((item) => (
                    <DropdownMenuItem key={item.label} asChild>
                      <Link href={item.href ?? "#"}>{item.label}</Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
              <ChevronRight className="size-3.5 text-foreground-tertiary" aria-hidden="true" />
            </li>
            <li className="flex items-center gap-1.5">
              <CrumbLink item={visible.trailing[0]} isCurrent />
            </li>
          </>
        ) : (
          items.map((item, index) => (
            <li key={item.label} className="flex items-center gap-1.5">
              <CrumbLink item={item} isCurrent={index === lastIndex} />
              {index !== lastIndex && (
                <ChevronRight className="size-3.5 text-foreground-tertiary" aria-hidden="true" />
              )}
            </li>
          ))
        )}
      </ol>
    </nav>
  );
}
```

#### `src/components/ui/search-field.tsx`
```tsx
"use client";

import * as React from "react";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SearchFieldProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  size?: "sm" | "md";
  onClear?: () => void;
  "aria-label"?: string;
  id?: string;
  className?: string;
  disabled?: boolean;
}

export function SearchField({
  value,
  onChange,
  placeholder,
  size = "md",
  onClear,
  "aria-label": ariaLabel,
  id,
  className,
  disabled,
}: SearchFieldProps) {
  const handleClear = () => {
    onChange("");
    onClear?.();
  };

  return (
    <div
      className={cn(
        "flex items-center gap-2 rounded-atlas-md border border-border-default bg-surface px-3 text-foreground-tertiary transition-colors",
        "focus-within:border-brand focus-within:text-foreground-secondary",
        !disabled && "hover:border-border-strong",
        disabled && "pointer-events-none opacity-50",
        size === "md" ? "h-9" : "h-8",
        className
      )}
    >
      <Search className="size-4 shrink-0" aria-hidden="true" />
      <input
        id={id}
        type="search"
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={ariaLabel ?? placeholder}
        className="w-full min-w-0 bg-transparent text-sm text-foreground outline-none placeholder:text-foreground-tertiary [&::-webkit-search-cancel-button]:appearance-none"
      />
      {value && (
        <button
          type="button"
          onClick={handleClear}
          aria-label="Clear search"
          className="flex shrink-0 items-center justify-center text-foreground-tertiary transition-colors hover:text-foreground"
        >
          <X className="size-3.5" aria-hidden="true" />
        </button>
      )}
    </div>
  );
}
```

#### `src/components/layout/notifications-menu.tsx`
```tsx
"use client";

import { Bell, BellOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { EmptyState } from "@/components/state/empty-state";

export interface NotificationsMenuProps {
  unreadCount?: number;
}

/**
 * Shell-level notification entry point. No notification data source exists
 * yet (per BOUNDARIES.md — Claude does not own data/backend concerns), so
 * this renders the panel infrastructure with a placeholder empty state.
 */
export function NotificationsMenu({ unreadCount = 0 }: NotificationsMenuProps) {
  const hasUnread = unreadCount > 0;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={hasUnread ? `Notifications, ${unreadCount} unread` : "Notifications"}
        >
          <span className="relative">
            <Bell className="size-4" />
            {hasUnread && (
              <span
                className="absolute -right-0.5 -top-0.5 flex size-2 rounded-full bg-error"
                aria-hidden="true"
              />
            )}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notifications</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <EmptyState
          icon={BellOff}
          title="No notifications yet"
          description="You'll see agent and system notifications here once they start coming in."
          className="py-6"
        />
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

#### `src/components/layout/placeholder-page.tsx`
```tsx
import { Construction } from "lucide-react";
import { PageHeader } from "./page-header";
import { Breadcrumb, type BreadcrumbItem } from "./breadcrumb";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/state/empty-state";

export interface PlaceholderBodyProps {
  title: string;
}

/**
 * The "not built yet" content block, reused by both top-level placeholder
 * routes and nested detail routes (which additionally render a Breadcrumb
 * above their own PageHeader).
 */
export function PlaceholderBody({ title }: PlaceholderBodyProps) {
  return (
    <Card>
      <EmptyState
        icon={Construction}
        title="This screen hasn't been built yet"
        description={`${title} will appear here once implemented.`}
        className="py-16"
      />
    </Card>
  );
}

export interface PlaceholderPageProps {
  title: string;
  description?: string;
  breadcrumb?: BreadcrumbItem[];
}

/**
 * Shared shell for every route that exists as routing infrastructure but
 * has no business functionality built yet. Per BOUNDARIES.md / Work Order
 * 005, this is infrastructure only — no mock dashboards.
 */
export function PlaceholderPage({ title, description, breadcrumb }: PlaceholderPageProps) {
  return (
    <div className="flex flex-col gap-8">
      {breadcrumb && <Breadcrumb items={breadcrumb} />}
      <PageHeader title={title} description={description} />
      <PlaceholderBody title={title} />
    </div>
  );
}
```

#### `src/components/layout/page-loading-skeleton.tsx`
```tsx
import { Card, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Generic, content-agnostic loading placeholder shown while a route
 * segment's content is still arriving. Deliberately has no knowledge of
 * any specific screen's layout (that would encode business/page-specific
 * assumptions into shared shell infrastructure).
 */
export function PageLoadingSkeleton() {
  return (
    <div className="flex flex-col gap-8" aria-busy="true" aria-label="Loading page">
      <div className="flex flex-col gap-2 border-b border-border-default pb-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-72" />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="p-6 sm:p-8">
            <div className="flex items-start justify-between">
              <div className="flex flex-col gap-3">
                <Skeleton className="h-3 w-24" />
                <Skeleton className="h-10 w-20" />
              </div>
              <Skeleton className="size-8 rounded-atlas-md" />
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-56" />
        </CardHeader>
        <div className="flex flex-col gap-3 px-4 pb-6 sm:px-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      </Card>
    </div>
  );
}
```

---

### 5.2 Created — Routes

#### `src/app/(shell)/layout.tsx`
```tsx
import { DashboardLayout } from "@/components/layout/dashboard-layout";

export default function ShellLayout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
```

#### `src/app/(shell)/loading.tsx`
```tsx
import { PageLoadingSkeleton } from "@/components/layout/page-loading-skeleton";

export default function Loading() {
  return <PageLoadingSkeleton />;
}
```

#### `src/app/(shell)/error.tsx`
```tsx
"use client";

import { useEffect } from "react";
import { ErrorState } from "@/components/state/error-state";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <ErrorState
        title="Something went wrong"
        description="This page ran into an unexpected error. Try again, or navigate elsewhere from the sidebar."
        onRetry={reset}
      />
    </div>
  );
}
```

#### `src/app/(shell)/page.tsx` (Overview — relocated, content unchanged)
```tsx
import { OverviewDashboard } from "@/features/overview/components/overview-dashboard";

export default function OverviewPage() {
  return <OverviewDashboard />;
}
```

#### `src/app/(shell)/agents/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function AgentsPage() {
  return (
    <PlaceholderPage
      title="Agents"
      description="Manage and monitor every deployed agent in your fleet."
    />
  );
}
```

#### `src/app/(shell)/agents/[agentId]/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default async function AgentDetailPage({
  params,
}: {
  params: Promise<{ agentId: string }>;
}) {
  const { agentId } = await params;

  return (
    <PlaceholderPage
      title={`Agent ${agentId}`}
      description="Configuration, run history, and health for this agent."
      breadcrumb={[{ label: "Agents", href: "/agents" }, { label: agentId }]}
    />
  );
}
```

#### `src/app/(shell)/runs/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function RunsPage() {
  return (
    <PlaceholderPage
      title="Runs"
      description="Track every execution across your agent fleet."
    />
  );
}
```

#### `src/app/(shell)/runs/[runId]/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default async function RunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  return (
    <PlaceholderPage
      title={`Run ${runId}`}
      description="Execution timeline, logs, and output for this run."
      breadcrumb={[{ label: "Runs", href: "/runs" }, { label: runId }]}
    />
  );
}
```

#### `src/app/(shell)/approvals/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function ApprovalsPage() {
  return (
    <PlaceholderPage
      title="Approvals"
      description="Review and act on requests awaiting operator sign-off."
    />
  );
}
```

#### `src/app/(shell)/alerts/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function AlertsPage() {
  return (
    <PlaceholderPage
      title="Alerts"
      description="Critical, warning, and informational events across Atlas."
    />
  );
}
```

#### `src/app/(shell)/connectors/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function ConnectorsPage() {
  return (
    <PlaceholderPage
      title="Connectors"
      description="Manage integrations between Atlas and external systems."
    />
  );
}
```

#### `src/app/(shell)/policies/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function PoliciesPage() {
  return (
    <PlaceholderPage
      title="Policies"
      description="Define the rules that govern agent behavior and approvals."
    />
  );
}
```

#### `src/app/(shell)/artifacts/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function ArtifactsPage() {
  return (
    <PlaceholderPage
      title="Artifacts"
      description="Browse files and outputs produced by agent runs."
    />
  );
}
```

#### `src/app/(shell)/audit/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function AuditPage() {
  return (
    <PlaceholderPage
      title="Audit"
      description="A complete history of actions taken across Atlas."
    />
  );
}
```

#### `src/app/(shell)/settings/page.tsx`
```tsx
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default function SettingsPage() {
  return (
    <PlaceholderPage
      title="Settings"
      description="Configure your workspace and account preferences."
    />
  );
}
```

---

### 5.3 Modified Files (full contents, post-change)

#### `src/components/layout/dashboard-layout.tsx`
```tsx
import { Sidebar } from "./sidebar";
import { TopBar } from "./top-bar";
import { PageContainer } from "./page-container";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div className="lg:pl-(--sidebar-width)">
        <TopBar />
        <main>
          <PageContainer>{children}</PageContainer>
        </main>
      </div>
    </div>
  );
}
```

**What changed:** the inline `<main className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 sm:py-8">` was replaced with `<main><PageContainer>{children}</PageContainer></main>`. Visually identical — `PageContainer` carries the exact same classes.

#### `src/components/layout/top-bar.tsx`
```tsx
"use client";

import { useState } from "react";
import { Menu, LogOut, Settings, User } from "lucide-react";
import { ThemeToggle } from "./theme-toggle";
import { MobileNavDrawer } from "./mobile-nav-drawer";
import { NotificationsMenu } from "./notifications-menu";
import { SearchField } from "@/components/ui/search-field";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { TooltipProvider } from "@/components/ui/tooltip";

export function TopBar() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [searchValue, setSearchValue] = useState("");

  return (
    <TooltipProvider delayDuration={200}>
      <header className="sticky top-0 z-20 flex h-(--topbar-height) items-center gap-3 border-b border-border-default bg-surface/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-surface/80 sm:px-6">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          aria-label="Open navigation"
          onClick={() => setMobileNavOpen(true)}
        >
          <Menu className="size-5" />
        </Button>

        <div className="hidden max-w-xs flex-1 sm:block">
          <SearchField
            value={searchValue}
            onChange={setSearchValue}
            placeholder="Search Atlas..."
            aria-label="Search"
          />
        </div>

        <div className="flex-1 sm:hidden" />

        <div className="flex items-center gap-1">
          <ThemeToggle />

          <NotificationsMenu unreadCount={2} />

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="ml-1 flex items-center gap-2 rounded-atlas-md p-1 pr-2 transition-colors hover:bg-surface-hover"
                aria-label="User menu"
              >
                <Avatar className="size-7">
                  <AvatarFallback>OP</AvatarFallback>
                </Avatar>
                <span className="hidden text-sm font-medium text-foreground sm:inline">
                  Operator
                </span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>operator@atlas.dev</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="size-4" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="size-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <LogOut className="size-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <MobileNavDrawer open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
    </TooltipProvider>
  );
}
```

**What changed:** removed the inline `Bell` icon button (with its own unread-dot markup) and replaced it with `<NotificationsMenu unreadCount={2} />`; added the `searchValue` state and the `SearchField` block (hidden below `sm`); removed the now-unused `Bell` import.

#### `src/components/layout/mobile-nav-drawer.tsx`
```tsx
"use client";

import { useEffect, useRef } from "react";
import { X } from "lucide-react";
import { SidebarNav } from "./sidebar";
import { Button } from "@/components/ui/button";

const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function MobileNavDrawer({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const dialogRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!open) return;

    triggerRef.current = document.activeElement as HTMLElement;
    dialogRef.current?.querySelector<HTMLElement>(FOCUSABLE_SELECTOR)?.focus();

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        onClose();
        return;
      }

      if (e.key !== "Tab" || !dialogRef.current) return;

      const focusable = Array.from(
        dialogRef.current.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)
      );
      if (focusable.length === 0) return;

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      triggerRef.current?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-40 lg:hidden">
      <div
        className="absolute inset-0 bg-neutral-950/50"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-label="Navigation"
        className="absolute inset-y-0 left-0 flex w-(--sidebar-width) flex-col border-r border-border-default bg-surface shadow-atlas-md"
      >
        <div className="flex items-center justify-end px-2 pt-2">
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close navigation">
            <X className="size-4" />
          </Button>
        </div>
        <SidebarNav onNavigate={onClose} />
      </div>
    </div>
  );
}
```

**What changed:** added `dialogRef`/`triggerRef`; on open, captures the previously-focused element and moves focus into the dialog; the keydown handler now also intercepts `Tab`/`Shift+Tab` to cycle focus within the dialog's focusable elements; on close/unmount, restores focus to whatever triggered the drawer. Previously: only handled `Escape`, with no focus management at all.

---

## 6. Design Decisions Made During Implementation

1. **Route-group shell instead of per-page wrapping.** Rather than importing `DashboardLayout` into every `page.tsx` (as the original Overview page did), all routes live under a `(shell)` route group with one `layout.tsx`. This means `loading.tsx`/`error.tsx` render *inside* the persisting shell chrome (sidebar/top bar stay mounted, only the content area shows the skeleton or error) rather than replacing the whole page — a materially better UX than a full-page loading/error screen, and it's why Overview's `page.tsx` counts as "created" in this package rather than "modified": the file is new, but the component it renders (`OverviewDashboard`) is byte-for-byte unchanged.

2. **Icon Button pattern, not a new component.** Per the already-approved `component-library.md` §15, "Icon Button" was formalized as a usage pattern of `Button size="icon"`, not a new component. The mobile-menu toggle, notifications trigger, and theme toggle all follow this.

3. **Notifications reuses `EmptyState` directly**, sized down via `className="py-6"` and a `w-80` dropdown content width, rather than inventing a separate compact empty-state variant. Consistent with "reuse components" in CLAUDE.md.

4. **Search Field is genuinely non-functional.** It holds local `useState` and nothing else — no filtering, no keyboard shortcut, no results dropdown. This was a deliberate reading of "Global Search Placeholder": build the real, spec-compliant component (infrastructure), but do not wire it to any behavior (business logic), since there is no data to search per BOUNDARIES.md.

5. **Fixed the mobile drawer's focus trap now, not deferred.** `component-library.md` §1 flagged this as "a defect to fix in the same pass this component library is implemented" — since App Shell is that implementation pass for the Sidebar/drawer, and WCAG 2.2 AA is a hard, standing requirement (not a new one), this was treated as in-scope rather than a separate change request.

6. **Agent/Run Detail pages use `async` Server Components** (`params: Promise<{...}>`) per Next.js 16's async dynamic-params API — no client-side fetching, no data layer, just reading the route param and echoing it into the placeholder title/breadcrumb.

---

## 7. Deviations from Work Order / Design System / Component Library / Screen Specs

- **None substantive.** One interpretive call was made and should be explicitly confirmed: the work order's placeholder-routes list includes "Overview," which was read as *"make sure Overview participates in the new shared shell,"* not *"replace Overview's built content with a placeholder."* Rebuilding Overview as a placeholder would have discarded previously-reviewed, approved work (Work Orders 001 and the subsequent refinement pass) and would contradict BOUNDARIES.md's "do not redesign the product." This was flagged at the time and no objection was raised — restating it here for the design-review record.
- Two small additions to the icon set (`Construction` for placeholder screens, `MoreHorizontal` for breadcrumb truncation) are used but **not yet reflected** in `icon-system.md`'s concept→icon mapping table — see Known Limitations.

## 8. Assumptions

1. Overview's existing mock-data-driven content was in scope to relocate but not to modify.
2. "Global Search Placeholder" meant a real, spec-built `SearchField` with no wired behavior — not a disabled-looking decorative element, and not a fully wired (but fake) search experience.
3. "Notification Placeholder" meant a functioning panel shell with a placeholder empty state, not just a static bell icon.
4. Detail routes (`/agents/[agentId]`, `/runs/[runId]`) should exist and be reachable by direct URL as routing infrastructure, even though nothing currently links to them (no list data exists yet to link from).

## 9. Known Limitations / Technical Debt

1. **Icon-system documentation lag.** `Construction` and `MoreHorizontal` are used in shipped code but not yet added to `icon-system.md`'s mapping table. Low risk, easy follow-up.
2. **TopBar's user identity and unread count are still hardcoded** (`"Operator"` / `2`), exactly as flagged in `component-library.md` §2 — this work order didn't require fixing it, so it wasn't, but it's the same pre-existing debt, now also true of `NotificationsMenu`'s `unreadCount` prop, which `TopBar` still passes a hardcoded literal into.
3. **Breadcrumb truncation logic is implemented but unexercised** — no current route hierarchy is deep enough to trigger `MAX_VISIBLE_CRUMBS` (4). It's been reviewed by inspection, not by a live example, since one doesn't exist yet.
4. **No route currently throws**, so `(shell)/error.tsx` has been verified by code review and Next.js's documented error-boundary contract, not by triggering a live error in the browser during this pass.
5. **Search Field has no keyboard shortcut (e.g. ⌘K)** — common in comparable enterprise products (Linear, Vercel) but not requested by the work order; not added, to avoid scope creep beyond "placeholder."

---

## 10. Directory Tree — New Components and Routes

```
src/
├── app/
│   ├── layout.tsx                          (existing, unchanged)
│   ├── globals.css                         (existing, unchanged)
│   └── (shell)/                            ◄ NEW route group
│       ├── layout.tsx                      ◄ NEW
│       ├── loading.tsx                     ◄ NEW
│       ├── error.tsx                       ◄ NEW
│       ├── page.tsx                        ◄ NEW (Overview — relocated from src/app/page.tsx)
│       ├── agents/
│       │   ├── page.tsx                    ◄ NEW
│       │   └── [agentId]/
│       │       └── page.tsx                ◄ NEW
│       ├── runs/
│       │   ├── page.tsx                    ◄ NEW
│       │   └── [runId]/
│       │       └── page.tsx                ◄ NEW
│       ├── approvals/page.tsx              ◄ NEW
│       ├── alerts/page.tsx                 ◄ NEW
│       ├── connectors/page.tsx             ◄ NEW
│       ├── policies/page.tsx               ◄ NEW
│       ├── artifacts/page.tsx              ◄ NEW
│       ├── audit/page.tsx                  ◄ NEW
│       └── settings/page.tsx               ◄ NEW
│
└── components/
    ├── layout/
    │   ├── dashboard-layout.tsx            ● MODIFIED
    │   ├── top-bar.tsx                     ● MODIFIED
    │   ├── mobile-nav-drawer.tsx           ● MODIFIED
    │   ├── page-container.tsx              ◄ NEW
    │   ├── breadcrumb.tsx                  ◄ NEW
    │   ├── notifications-menu.tsx          ◄ NEW
    │   ├── placeholder-page.tsx            ◄ NEW
    │   ├── page-loading-skeleton.tsx       ◄ NEW
    │   ├── sidebar.tsx                     (existing, unchanged)
    │   ├── nav-items.ts                    (existing, unchanged)
    │   ├── page-header.tsx                 (existing, unchanged)
    │   └── theme-toggle.tsx                (existing, unchanged)
    │
    └── ui/
        ├── search-field.tsx                ◄ NEW
        └── (all other ui/ primitives unchanged)
```

**Removed:** `src/app/page.tsx` (superseded by `src/app/(shell)/page.tsx`).

---

## 11. Screenshots

Provided directly in the conversation accompanying this document (desktop 1440px, tablet 768px, mobile 375px — Overview Dashboard, dark theme, current build). Responsive behavior confirmed: 4-column metric grid → 2-column (tablet) → 1-column (mobile); `SearchField` hides below `sm` in the Top Navigation to preserve space on mobile, consistent with the dashboard's "monitoring + approvals" mobile scope from the original Work Order 001 clarifications.

**Status: Completed. Design Review: Approved. Final Review: Passed. Merge: Completed.**
