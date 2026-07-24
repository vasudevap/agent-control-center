import { PoliciesWorkspace } from "./policies-workspace";
import { POLICY_FIXTURES } from "./policy-data";

export default function PoliciesPage() {
  return <PoliciesWorkspace policies={POLICY_FIXTURES} />;
}
