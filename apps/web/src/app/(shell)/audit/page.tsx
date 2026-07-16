import { AUDIT_FIXTURES } from "./audit-data";
import { AuditWorkspace } from "./audit-workspace";

export default function AuditPage() {
  return <AuditWorkspace events={AUDIT_FIXTURES} />;
}
