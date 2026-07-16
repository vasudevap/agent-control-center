import { findRunById } from "../run-data";
import { RunDetailWorkspace } from "./run-detail-workspace";

export default async function RunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  return <RunDetailWorkspace run={findRunById(runId)} requestedId={runId} />;
}
