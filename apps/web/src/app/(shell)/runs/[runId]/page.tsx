import { Workflow } from "lucide-react";
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default async function RunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  return (
    <PlaceholderPage
      title="Run Details"
      description={`Execution timeline, logs, and output for run ${runId}.`}
      breadcrumb={[{ label: "Runs", href: "/runs" }, { label: runId }]}
      icon={Workflow}
    />
  );
}
