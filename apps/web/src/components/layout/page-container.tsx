import { cn } from "@/lib/utils";

export interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Slightly denser than the baseline's PageContainer (max-w-[1600px],
 * py-6/py-8): this exploration keeps operational content tighter to
 * the viewport edges and reduces vertical breathing room between the
 * shell and content, in line with the "denser for scanning" half of
 * the exploration's density thesis.
 */
export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <div className={cn("mx-auto max-w-[1520px] px-3 py-5 sm:px-5 sm:py-6", className)}>
      {children}
    </div>
  );
}
