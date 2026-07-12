"use client";

import { CheckSquare, Check, X } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/state/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import type { PendingApproval } from "../types/overview.types";

export interface PendingApprovalsSectionProps {
  approvals: PendingApproval[];
  state?: "success" | "loading" | "empty";
  onDecision?: (id: string, decision: "approved" | "rejected") => void;
}

const RISK_LABEL: Record<PendingApproval["risk"], { label: string; className: string }> = {
  low: { label: "Low risk", className: "bg-surface-tertiary text-foreground-secondary border-transparent" },
  medium: { label: "Medium risk", className: "bg-warning-bg text-warning border-warning-border" },
  high: { label: "High risk", className: "bg-error-bg text-error border-error-border" },
};

export function PendingApprovalsSection({
  approvals,
  state = "success",
  onDecision,
}: PendingApprovalsSectionProps) {
  return (
    <Card className="bg-surface-secondary">
      <CardHeader>
        <CardTitle>Pending Approvals</CardTitle>
        <CardDescription>Actions awaiting operator sign-off</CardDescription>
      </CardHeader>

      {state === "loading" && (
        <CardContent className="flex flex-col gap-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </CardContent>
      )}

      {state === "empty" && (
        <EmptyState
          icon={CheckSquare}
          title="Nothing pending"
          description="Approval requests will show up here."
        />
      )}

      {state === "success" && (
        <CardContent className="flex flex-col gap-3">
          {approvals.map((approval) => {
            const risk = RISK_LABEL[approval.risk];
            return (
              <div
                key={approval.id}
                className="flex flex-col gap-3 rounded-atlas-md border border-border-default bg-surface p-3"
              >
                <div className="flex min-w-0 flex-col gap-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium text-foreground">
                      {approval.agentName}
                    </span>
                    <Badge className={cn(risk.className)}>{risk.label}</Badge>
                  </div>
                  <p className="text-xs text-foreground-secondary">{approval.action}</p>
                  <span className="font-mono text-[11px] text-foreground-tertiary">
                    Requested {approval.requestedAt}
                  </span>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => onDecision?.(approval.id, "rejected")}
                    aria-label={`Reject request from ${approval.agentName}`}
                  >
                    <X className="size-3.5" />
                    Reject
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => onDecision?.(approval.id, "approved")}
                    aria-label={`Approve request from ${approval.agentName}`}
                  >
                    <Check className="size-3.5" />
                    Approve
                  </Button>
                </div>
              </div>
            );
          })}
        </CardContent>
      )}
    </Card>
  );
}
