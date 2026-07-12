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
