import { redirect } from "next/navigation";
import { CONTROL_CENTER_ROUTES } from "@/lib/control-center-routes";

export default function RunsPage() {
  redirect(CONTROL_CENTER_ROUTES.executions);
}
