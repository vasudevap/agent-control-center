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

        <div className="flex-1" />

        <div className="flex items-center justify-end gap-1">
          <div className="hidden w-80 sm:block">
            <SearchField
              value={searchValue}
              onChange={setSearchValue}
              placeholder="Search agents, runs, artifacts..."
              aria-label="Search"
            />
          </div>

          <ThemeToggle />

          <NotificationsMenu unreadCount={0} />

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
