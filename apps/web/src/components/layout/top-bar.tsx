"use client";

import { useEffect, useState } from "react";
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
import {
  dashboardApiBaseUrl,
  dashboardSignInUrl,
  ownerDisplayName,
  ownerInitials,
  readDashboardSession,
  type DashboardSession,
} from "@/lib/dashboard-runtime";

export function TopBar() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [searchValue, setSearchValue] = useState("");
  const [session, setSession] = useState<DashboardSession | null>(null);
  const [sessionState, setSessionState] = useState<
    "fixture" | "loading" | "live" | "unauthenticated" | "unavailable"
  >("fixture");

  useEffect(() => {
    let cancelled = false;
    async function loadSession() {
      if (!dashboardApiBaseUrl()) {
        setSessionState("fixture");
        return;
      }
      setSessionState("loading");
      try {
        const runtimeSession = await readDashboardSession();
        if (!cancelled) {
          setSession(runtimeSession);
          setSessionState("live");
        }
      } catch (error) {
        if (cancelled) return;
        if (
          error instanceof Error &&
          "status" in error &&
          (error as { status: number }).status === 401
        ) {
          setSessionState("unauthenticated");
        } else {
          setSessionState("unavailable");
        }
      }
    }
    void loadSession();
    return () => {
      cancelled = true;
    };
  }, []);

  const displayName = ownerDisplayName(session);
  const initials = ownerInitials(session);
  const accountLabel =
    session?.user.email ??
    (sessionState === "unauthenticated" ? "Owner sign-in required" : displayName);

  return (
    <TooltipProvider delayDuration={200}>
      <header className="sticky top-(--statusbar-height) z-20 flex h-(--topbar-height) items-center gap-3 border-b border-border-default bg-surface/95 px-3 backdrop-blur supports-[backdrop-filter]:bg-surface/80 sm:px-4">
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden"
          aria-label="Open navigation"
          onClick={() => setMobileNavOpen(true)}
        >
          <Menu className="size-5" />
        </Button>

        <div className="flex-1" />

        <div className="flex items-center justify-end gap-1">
          <div className="hidden w-72 sm:block">
            <SearchField
              value={searchValue}
              onChange={setSearchValue}
              placeholder="Search agents, approvals, artifacts..."
              aria-label="Search"
            />
          </div>

          <ThemeToggle />

          <NotificationsMenu unreadCount={0} />

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="ml-1 flex items-center gap-2 rounded-atlas-sm p-1 pr-2 transition-colors hover:bg-surface-hover"
                aria-label="User menu"
              >
                <Avatar className="size-7">
                  <AvatarFallback>{initials}</AvatarFallback>
                </Avatar>
                <span className="hidden text-sm font-medium text-foreground sm:inline">
                  {displayName}
                </span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>{accountLabel}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="size-4" />
                {sessionState === "live" ? "Profile" : "Session unavailable"}
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="size-4" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {sessionState === "unauthenticated" && dashboardSignInUrl() ? (
                <DropdownMenuItem asChild>
                  <a href={dashboardSignInUrl()}>
                    <User className="size-4" />
                    Sign in with Google
                  </a>
                </DropdownMenuItem>
              ) : (
                <DropdownMenuItem>
                  <LogOut className="size-4" />
                  Sign out
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      <MobileNavDrawer open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
    </TooltipProvider>
  );
}
