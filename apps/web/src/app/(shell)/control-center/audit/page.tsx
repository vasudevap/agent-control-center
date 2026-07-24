import { AUDIT_FIXTURES } from "@/app/(shell)/audit/audit-data";
import { AuditWorkspace } from "@/app/(shell)/audit/audit-workspace";

export default function ControlCenterAuditPage() {
  return <AuditWorkspace events={AUDIT_FIXTURES} />;
}
