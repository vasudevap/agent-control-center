import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

export interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  identifier?: string;
  description?: string;
  icon?: LucideIcon;
  actions?: React.ReactNode;
  meta?: React.ReactNode;
  className?: string;
}

/**
 * Compact, identity-first header. The baseline direction uses a large
 * display-scale title with a description paragraph beneath it on every
 * screen, including object-detail pages. That costs vertical space an
 * operator triaging many objects per session does not want to keep
 * scrolling past.
 *
 * Here the title sits at a single, moderate size; a mono-set eyebrow
 * carries section context; an optional mono identifier (an approval or
 * agent ID) sits inline next to the title instead of buried in body
 * text; and description becomes a single trailing line only where it
 * adds information the title/meta row does not already carry.
 *
 * The icon sits in its own column, outside the text stack, so eyebrow,
 * title, and description all share one left edge instead of the icon
 * pushing only the title line rightward while eyebrow/description stay
 * flush with the icon above and below it.
 */
export function PageHeader({ eyebrow, title, identifier, description, icon: Icon, actions, meta, className }: PageHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-3 border-b border-border-default pb-4", className)}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex flex-col gap-1">
          {eyebrow && (
            <p className={cn("font-mono text-[10px] font-semibold uppercase tracking-[0.14em] text-foreground-tertiary", Icon && "pl-[2.375rem]")}>
              {eyebrow}
            </p>
          )}
          <div className="flex min-w-0 flex-wrap items-center gap-2.5">
            {Icon && (
              <span className="flex size-7 shrink-0 items-center justify-center rounded-atlas-sm border border-border-default bg-surface-secondary text-brand">
                <Icon className="size-4" aria-hidden="true" />
              </span>
            )}
            <h1 className="min-w-0 break-words font-mono text-lg font-semibold uppercase tracking-[0.03em] text-foreground sm:text-xl">
              {title}
            </h1>
            {identifier && (
              <span className="rounded-atlas-sm border border-border-default bg-surface-secondary px-1.5 py-0.5 font-mono text-[11px] text-foreground-tertiary">
                {identifier}
              </span>
            )}
          </div>
        </div>
        {actions && <div className="flex min-w-0 flex-wrap items-center gap-2">{actions}</div>}
      </div>
      {(description || meta) && (
        <div className={cn("flex flex-wrap items-center justify-between gap-2", Icon && "pl-[2.375rem]")}>
          {description && <p className="text-sm leading-relaxed text-foreground-secondary">{description}</p>}
          {meta && <div className="flex flex-wrap items-center gap-2">{meta}</div>}
        </div>
      )}
    </div>
  );
}
