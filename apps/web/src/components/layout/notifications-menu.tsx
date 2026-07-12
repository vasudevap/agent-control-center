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
