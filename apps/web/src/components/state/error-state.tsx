import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Something went wrong",
  description = "We couldn't load this data. Try again.",
  onRetry,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-2 rounded-atlas-md px-4 py-10 text-center",
        className
      )}
      role="alert"
    >
      <div className="flex size-10 items-center justify-center rounded-full bg-error-bg text-error">
        <AlertCircle className="size-5" aria-hidden="true" />
      </div>
      <p className="text-sm font-medium text-foreground">{title}</p>
      <p className="max-w-xs text-xs text-foreground-secondary">{description}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} className="mt-2">
          Try again
        </Button>
      )}
    </div>
  );
}
