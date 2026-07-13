import { APPROVAL_FIXTURES } from "./approval-data";
import { ApprovalsWorkspace } from "./approvals-workspace";

export default function ApprovalsPage() {
  return <ApprovalsWorkspace approvals={APPROVAL_FIXTURES} />;
}
