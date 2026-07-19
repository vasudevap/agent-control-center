import { notFound } from "next/navigation";
import { Bot } from "lucide-react";
import { findAgentById } from "../agent-data";
import { AgentDetailWorkspace } from "./agent-detail-workspace";
import { AgentOperationalControls } from "./agent-operational-controls";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import Link from "next/link";

import { MOCK_AGENTS } from "../agent-data";

export function generateStaticParams() {
  return MOCK_AGENTS.map((agent) => ({ agentId: agent.id }));
}

export default async function AgentDetailPage({
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
          <>
            <Button asChild variant="ghost" size="sm" className="w-full justify-start sm:w-auto">
              <Link href="/agents">Back to Agents</Link>
            </Button>
            <AgentOperationalControls agentId={agent.id} agentName={agent.name} initialStatus={agent.status} />
          </>
        }
      />

      <AgentDetailWorkspace agent={agent} />
    </div>
  );
}
