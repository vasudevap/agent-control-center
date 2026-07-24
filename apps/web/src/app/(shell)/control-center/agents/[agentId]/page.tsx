import { notFound } from "next/navigation";
import { Bot } from "lucide-react";
import Link from "next/link";
import { findAgentById, MOCK_AGENTS } from "@/app/(shell)/agents/agent-data";
import { AgentDetailWorkspace } from "@/app/(shell)/agents/[agentId]/agent-detail-workspace";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { CONTROL_CENTER_ROUTES } from "@/lib/control-center-routes";

export function generateStaticParams() {
  return MOCK_AGENTS.map((agent) => ({ agentId: agent.id }));
}

export default async function ControlCenterAgentDetailPage({
  params,
}: {
  params: Promise<{ agentId: string }>;
}) {
  const { agentId } = await params;
  const agent = findAgentById(agentId);

  if (!agent) {
    notFound();
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Agent"
        title={agent.name}
        identifier={agent.id}
        icon={Bot}
        description={agent.description}
        actions={
          <Button asChild variant="ghost" size="sm" className="w-full justify-start sm:w-auto">
            <Link href={CONTROL_CENTER_ROUTES.agents}>Back to Agents</Link>
          </Button>
        }
      />

      <AgentDetailWorkspace agent={agent} />
    </div>
  );
}
