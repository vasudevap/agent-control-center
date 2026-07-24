import { redirect } from "next/navigation";
import { MOCK_AGENTS } from "../agent-data";
import { controlCenterAgentHref } from "@/lib/control-center-routes";

export function generateStaticParams() {
  return MOCK_AGENTS.map((agent) => ({ agentId: agent.id }));
}

export default async function AgentDetailPage({
  params,
}: {
  params: Promise<{ agentId: string }>;
}) {
  const { agentId } = await params;
  redirect(controlCenterAgentHref(agentId));
}
