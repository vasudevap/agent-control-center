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
