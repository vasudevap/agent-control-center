"use client";

import * as React from "react";
import { AlertTriangle, CheckCircle2, CircleDashed, ServerOff } from "lucide-react";

import {
  buildRuntimeReadyUrl,
  runtimeHealthFromReadyPayload,
  type RuntimeHealthPresentation,
} from "@/lib/runtime-health";
import { cn } from "@/lib/utils";

const STATE_CONFIG: Record<
  RuntimeHealthPresentation["state"],
  {
    icon: React.ComponentType<{ className?: string }>;
    className: string;
    spin?: boolean;
  }
> = {
  "not-configured": {
    icon: ServerOff,
    className: "border-border-default bg-surface-tertiary text-foreground-secondary",
  },
  checking: {
    icon: CircleDashed,
    className: "border-border-default bg-surface-tertiary text-foreground-secondary",
    spin: true,
  },
  ready: {
    icon: CheckCircle2,
    className: "border-success-border bg-success-bg text-success",
  },
  "not-ready": {
    icon: AlertTriangle,
    className: "border-warning-border bg-warning-bg text-warning",
  },
  unavailable: {
    icon: ServerOff,
    className: "border-error-border bg-error-bg text-error",
  },
};

const NOT_CONFIGURED: RuntimeHealthPresentation = {
  state: "not-configured",
  label: "Runtime not configured",
  detail: "NEXT_PUBLIC_API_BASE_URL is not configured for this dashboard build.",
  problemCount: 0,
};

const CHECKING: RuntimeHealthPresentation = {
  state: "checking",
  label: "Checking runtime",
  detail: "Checking Atlas API readiness.",
  problemCount: 0,
};

const UNAVAILABLE: RuntimeHealthPresentation = {
  state: "unavailable",
  label: "Runtime unavailable",
  detail: "Atlas API readiness could not be reached.",
  problemCount: 0,
};

export function RuntimeHealthIndicator({
  apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL,
}: {
  apiBaseUrl?: string;
}) {
  const readyUrl = React.useMemo(() => buildRuntimeReadyUrl(apiBaseUrl), [apiBaseUrl]);
  const [result, setResult] = React.useState<{
    readyUrl: string;
    presentation: RuntimeHealthPresentation;
  } | null>(null);

  React.useEffect(() => {
    if (!readyUrl) {
      return;
    }

    const controller = new AbortController();

    fetch(readyUrl, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          setResult({ readyUrl, presentation: UNAVAILABLE });
          return;
        }
        setResult({
          readyUrl,
          presentation: runtimeHealthFromReadyPayload(await response.json()),
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setResult({ readyUrl, presentation: UNAVAILABLE });
      });

    return () => controller.abort();
  }, [readyUrl]);

  const presentation = !readyUrl
    ? NOT_CONFIGURED
    : result?.readyUrl === readyUrl
      ? result.presentation
      : CHECKING;
  const config = STATE_CONFIG[presentation.state];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "hidden shrink-0 items-center gap-1.5 rounded-atlas-sm border px-2 py-1 font-mono text-[10px] uppercase md:inline-flex",
        config.className,
      )}
      role="status"
      aria-live="polite"
      title={presentation.detail}
    >
      <Icon className={cn("size-3", config.spin && "animate-spin")} aria-hidden="true" />
      {presentation.label}
    </span>
  );
}
