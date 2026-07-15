import { Ban, Eye, Inbox, MessageCircleQuestion } from "lucide-react";
import { StatusBadge, type AtlasStatus } from "@/components/badge/status-badge";
import { cn } from "@/lib/utils";
import type { ApprovalRecord, ApprovalState, ReviewProgress } from "./approval-data";
import { getExpiryPresentation } from "./approval-presentation";

const STATE_TO_ATLAS_STATUS: Record<ApprovalState, AtlasStatus> = {
  Pending: "pending",
  Approved: "approved",
  Rejected: "rejected",
  Expired: "expired",
  Cancelled: "cancelled",
};

export const REVIEW_CONFIG: Record<ReviewProgress, { icon: React.ComponentType<{ className?: string }>; label: string; className: string }> = {
  Unopened: { icon: Inbox, label: "Unopened", className: "text-foreground-tertiary" },
  "In review": { icon: Eye, label: "In review", className: "text-brand" },
  "Awaiting information": { icon: MessageCircleQuestion, label: "Awaiting information", className: "text-warning" },
  Blocked: { icon: Ban, label: "Blocked", className: "text-warning" },
};

const REVIEW_RANK: Record<ReviewProgress, number> = { Unopened: 0, "In review": 1, "Awaiting information": 2, Blocked: 3 };

export function reviewRank(progress: ReviewProgress) {
  return REVIEW_RANK[progress];
}

export function ReviewProgressTag({ progress }: { progress: ReviewProgress }) {
  const config = REVIEW_CONFIG[progress];
  const Icon = config.icon;
  return (
    <span className={cn("inline-flex items-center gap-1 text-xs font-medium", config.className)}>
      <Icon className="size-3.5" aria-hidden="true" />
      {config.label}
    </span>
  );
}

export function ExpiryLabel({ approval }: { approval: ApprovalRecord }) {
  const expiry = getExpiryPresentation(approval.expiresAt, approval.requestedAt);
  return (
    <span className={cn("text-xs", expiry.urgency === "imminent" ? "font-semibold text-error" : expiry.urgency === "nearing" ? "font-semibold text-warning" : "text-foreground-secondary")}>
      {expiry.urgency === "none" ? expiry.label : expiry.shortLabel}
    </span>
  );
}

export function StateChip({ state, className }: { state: ApprovalState; className?: string }) {
  return <StatusBadge status={STATE_TO_ATLAS_STATUS[state]} plain className={className} />;
}
