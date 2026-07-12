"use client";

import { useEffect } from "react";
import { ErrorState } from "@/components/state/error-state";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <ErrorState
        title="Something went wrong"
        description="This page ran into an unexpected error. Try again, or navigate elsewhere from the sidebar."
        onRetry={reset}
      />
    </div>
  );
}
