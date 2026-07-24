import { redirect } from "next/navigation";
import { CONTROL_CENTER_ROUTES } from "@/lib/control-center-routes";

export default function AuditPage() {
  redirect(CONTROL_CENTER_ROUTES.activity);
}
