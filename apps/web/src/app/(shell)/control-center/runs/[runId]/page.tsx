import { RunDetailWorkspace } from "@/app/(shell)/runs/[runId]/run-detail-workspace";

export default async function ControlCenterRunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  return <RunDetailWorkspace requestedId={runId} runtimeRequired />;
}
