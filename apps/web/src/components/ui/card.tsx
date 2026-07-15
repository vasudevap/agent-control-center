import * as React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-atlas-lg border border-border-default bg-surface shadow-atlas-sm",
        className
      )}
      {...props}
    />
  );
}

/**
 * `actionable` marks a card whose content is itself clickable/navigable
 * (a queue or roster you drill into), distinct from a card that is
 * read-only status. The shaded band is a second, non-typographic
 * channel for that distinction — plain header stays reserved for
 * cards that are for reading only, not for doing or going somewhere.
 *
 * `divided` is a separate, weaker signal: a hairline rule (no shading)
 * under the header of a read-only card whose content has no bordered
 * structure of its own (a bare fact list, a loose tag wrap) and so
 * would otherwise visually run together with its title. It uses the
 * subtler border token, not the actionable border, so it never reads
 * as the same "you can click this" cue. `actionable` takes precedence
 * if both are somehow passed, since a card cannot be both signals.
 */
export function CardHeader({ className, actionable, divided, ...props }: React.HTMLAttributes<HTMLDivElement> & { actionable?: boolean; divided?: boolean }) {
  return (
    <div
      className={cn(
        "flex flex-col gap-1 p-4 sm:p-6",
        actionable && "bg-surface-secondary border-b border-border-default",
        !actionable && divided && "border-b border-border-subtle",
        className
      )}
      {...props}
    />
  );
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-foreground-secondary", className)}
      {...props}
    />
  );
}

export function CardDescription({
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p
      className={cn("text-xs text-foreground-secondary", className)}
      {...props}
    />
  );
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-4 pt-0 sm:p-6 sm:pt-0", className)} {...props} />;
}

export function CardFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("flex items-center gap-2 p-4 pt-0 sm:p-6 sm:pt-0", className)}
      {...props}
    />
  );
}
