import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";

export type SortDirection = "asc" | "desc";

export function getAriaSort(active: boolean, direction: SortDirection) {
  if (!active) return "none" as const;
  return direction === "asc" ? "ascending" as const : "descending" as const;
}

export function SortHeader<SortKey extends string>({
  label,
  sortKey,
  active,
  direction,
  onSort,
}: {
  label: string;
  sortKey: SortKey;
  active: boolean;
  direction: SortDirection;
  onSort: (key: SortKey) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSort(sortKey)}
      className="inline-flex items-center gap-1 font-mono text-[11px] font-medium uppercase tracking-wider text-foreground-tertiary hover:text-foreground"
    >
      {label}
      {active ? (
        direction === "asc" ? (
          <ArrowUp className="size-3" aria-hidden="true" />
        ) : (
          <ArrowDown className="size-3" aria-hidden="true" />
        )
      ) : (
        <ArrowUpDown className="size-3 opacity-40" aria-hidden="true" />
      )}
    </button>
  );
}
