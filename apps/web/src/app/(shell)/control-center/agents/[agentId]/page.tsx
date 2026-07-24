import { AgentDetailWorkspace } from "@/app/(shell)/agents/[agentId]/agent-detail-workspace";

export default async function ControlCenterAgentDetailPage({
  params,
}: {
  params: Promise<{ agentId: string }>;
}) {
  const { agentId } = await params;
  return <AgentDetailWorkspace requestedId={agentId} runtimeRequired />;
}
