import { APPROVAL_FIXTURES, getApprovalById } from "../approval-data";
import { ApprovalDetailWorkspace } from "./approval-detail-workspace";

export function generateStaticParams() {
  return APPROVAL_FIXTURES.map((approval) => ({ approvalId: approval.id }));
}

export default async function ApprovalDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ approvalId: string }>;
  searchParams: Promise<{ from?: string | string[] }>;
}) {
  const { approvalId } = await params;
  const { from } = await searchParams;
  const returnTo = typeof from === "string" && from.startsWith("/approvals")
    ? from
    : "/approvals?view=queue";

  return <ApprovalDetailWorkspace approval={getApprovalById(approvalId)} requestedId={approvalId} returnTo={returnTo} />;
}
