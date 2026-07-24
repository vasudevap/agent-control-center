import { redirect } from "next/navigation";
import { CONTROL_CENTER_ROUTES } from "@/lib/control-center-routes";

export default function AgentsPage() {
  redirect(CONTROL_CENTER_ROUTES.agents);
}
