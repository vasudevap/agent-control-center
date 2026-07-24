import { AUDIT_FIXTURES } from "@/app/(shell)/audit/audit-data";
import { AuditWorkspace } from "@/app/(shell)/audit/audit-workspace";

export default function ControlCenterActivityPage() {
  return <AuditWorkspace events={AUDIT_FIXTURES} runtimeRequired />;
}
