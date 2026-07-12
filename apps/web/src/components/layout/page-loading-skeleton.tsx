import { Card, CardHeader } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

/**
 * Generic, content-agnostic loading placeholder shown while a route
 * segment's content is still arriving. Deliberately has no knowledge of
 * any specific screen's layout (that would encode business/page-specific
 * assumptions into shared shell infrastructure).
 */
export function PageLoadingSkeleton() {
  return (
    <div className="flex flex-col gap-8" aria-busy="true" aria-label="Loading page">
      <div className="flex flex-col gap-2 border-b border-border-default pb-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-72" />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="p-6 sm:p-8">
            <div className="flex items-start justify-between">
              <div className="flex flex-col gap-3">
                <Skeleton className="h-3 w-24" />
                <Skeleton className="h-10 w-20" />
              </div>
              <Skeleton className="size-8 rounded-atlas-md" />
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-56" />
        </CardHeader>
        <div className="flex flex-col gap-3 px-4 pb-6 sm:px-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      </Card>
    </div>
  );
}
