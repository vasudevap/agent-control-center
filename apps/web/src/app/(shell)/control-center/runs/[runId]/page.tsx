import { RUN_FIXTURES, findRunById } from "@/app/(shell)/runs/run-data";
import { RunDetailWorkspace } from "@/app/(shell)/runs/[runId]/run-detail-workspace";

export function generateStaticParams() {
  return RUN_FIXTURES.map((run) => ({ runId: run.id }));
}

export default async function ControlCenterRunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  return <RunDetailWorkspace run={findRunById(runId)} requestedId={runId} />;
}
