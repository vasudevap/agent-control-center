import { Bot } from "lucide-react";
import { PlaceholderPage } from "@/components/layout/placeholder-page";

export default async function AgentDetailPage({
  params,
}: {
  params: Promise<{ agentId: string }>;
}) {
  const { agentId } = await params;

  return (
    <PlaceholderPage
      title="Agent Details"
      description={`Configuration, run history, and health for agent ${agentId}.`}
      breadcrumb={[{ label: "Agents", href: "/agents" }, { label: agentId }]}
      icon={Bot}
    />
  );
}
