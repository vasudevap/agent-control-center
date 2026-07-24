import { redirect } from "next/navigation";
import { CONTROL_CENTER_ROUTES } from "@/lib/control-center-routes";

export default function ControlCenterAuditPage() {
  redirect(CONTROL_CENTER_ROUTES.activity);
}
