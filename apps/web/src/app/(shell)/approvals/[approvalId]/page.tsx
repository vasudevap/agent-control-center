import { getApprovalById } from "../approval-data";
import { ApprovalDetailWorkspace } from "./approval-detail-workspace";

export default async function ApprovalDetailPage({ params }: { params: Promise<{ approvalId: string }> }) {
  const { approvalId } = await params;
  return <ApprovalDetailWorkspace approval={getApprovalById(approvalId)} />;
}
