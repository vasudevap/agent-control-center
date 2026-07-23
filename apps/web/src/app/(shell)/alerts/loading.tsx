import { Skeleton } from "@/components/ui/skeleton";

/**
 * Alert links can transition through this boundary while the selected alert
 * query is being resolved. Keep the placeholder specific to the destination
 * so a generic dashboard mockup never flashes between Overview and Alerts.
 */
export default function AlertsLoading() {
  return (
    <div className="flex flex-col gap-5" aria-busy="true" aria-label="Loading alerts">
      <div className="flex flex-col gap-2">
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-8 w-28" />
        <Skeleton className="h-4 w-80" />
      </div>
      <Skeleton className="h-16 w-full" />
      <div className="rounded-atlas-lg border border-border-default bg-surface p-3">
        <Skeleton className="h-9 w-full sm:w-80" />
      </div>
      <div className="overflow-hidden rounded-atlas-md border border-border-default bg-surface">
        <div className="grid gap-3 p-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
    </div>
  );
}
