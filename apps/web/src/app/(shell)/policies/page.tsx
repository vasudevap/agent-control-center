import { POLICY_FIXTURES } from "./policy-data";
import { PoliciesWorkspace } from "./policies-workspace";

export default function PoliciesPage() {
  return <PoliciesWorkspace policies={POLICY_FIXTURES} />;
}
