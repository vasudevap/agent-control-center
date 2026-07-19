import { RUN_FIXTURES, findRunById } from "../run-data";
import { RunDetailWorkspace } from "./run-detail-workspace";

export function generateStaticParams() {
  return RUN_FIXTURES.map((run) => ({ runId: run.id }));
}

export default async function RunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  return <RunDetailWorkspace run={findRunById(runId)} requestedId={runId} />;
}
