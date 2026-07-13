import Link from "next/link";
import { notFound } from "next/navigation";
import { Bot } from "lucide-react";
import { findAgentById } from "../agent-data";
import { AgentDetailWorkspace } from "./agent-detail-workspace";
import { AgentOperationalControls } from "./agent-operational-controls";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";

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
    <div className="flex flex-col gap-8">
      <PageHeader
        title={agent.name}
        icon={Bot}
        actions={
          <>
            <Button asChild variant="ghost">
              <Link href="/agents">Back to Agents</Link>
            </Button>
            <AgentOperationalControls
              agentId={agent.id}
              agentName={agent.name}
              initialStatus={agent.status}
            />
          </>
        }
      />

      <AgentDetailWorkspace agent={agent} />
    </div>
  );
}
