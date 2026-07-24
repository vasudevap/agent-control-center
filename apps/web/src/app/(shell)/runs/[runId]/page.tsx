import { redirect } from "next/navigation";
import { RUN_FIXTURES } from "../run-data";
import { controlCenterExecutionHref } from "@/lib/control-center-routes";

export function generateStaticParams() {
  return RUN_FIXTURES.map((run) => ({ runId: run.id }));
}

export default async function RunDetailPage({
  params,
}: {
  params: Promise<{ runId: string }>;
}) {
  const { runId } = await params;

  redirect(controlCenterExecutionHref(runId));
}
