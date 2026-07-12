import { Construction } from "lucide-react";
import { PageHeader } from "./page-header";
import { Breadcrumb, type BreadcrumbItem } from "./breadcrumb";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/state/empty-state";

export interface PlaceholderBodyProps {
  title: string;
}

/**
 * The "not built yet" content block, reused by both top-level placeholder
 * routes and nested detail routes (which additionally render a Breadcrumb
 * above their own PageHeader).
 */
export function PlaceholderBody({ title }: PlaceholderBodyProps) {
  return (
    <Card>
      <EmptyState
        icon={Construction}
        title="This screen hasn't been built yet"
        description={`${title} will appear here once implemented.`}
        className="py-16"
      />
    </Card>
  );
}

export interface PlaceholderPageProps {
  title: string;
  description?: string;
  breadcrumb?: BreadcrumbItem[];
}

/**
 * Shared shell for every route that exists as routing infrastructure but
 * has no business functionality built yet. Per BOUNDARIES.md / Work Order
 * 005, this is infrastructure only — no mock dashboards.
 */
export function PlaceholderPage({ title, description, breadcrumb }: PlaceholderPageProps) {
  return (
    <div className="flex flex-col gap-8">
      {breadcrumb && <Breadcrumb items={breadcrumb} />}
      <PageHeader title={title} description={description} />
      <PlaceholderBody title={title} />
    </div>
  );
}
