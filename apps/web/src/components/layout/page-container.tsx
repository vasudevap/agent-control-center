import { cn } from "@/lib/utils";

export interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Consistent max-width and padding for content rendered inside the app
 * shell's main region. Every route's content sits inside exactly one of
 * these — never a raw <main> or a bespoke width/padding per screen.
 */
export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <div className={cn("mx-auto max-w-[1600px] px-4 py-6 sm:px-6 sm:py-8", className)}>
      {children}
    </div>
  );
}
