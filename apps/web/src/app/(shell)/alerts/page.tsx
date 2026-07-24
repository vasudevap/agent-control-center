import { redirect } from "next/navigation";
import { CONTROL_CENTER_ROUTES, controlCenterAlertHref } from "@/lib/control-center-routes";

export default async function AlertsPage({
  searchParams,
}: {
  searchParams: Promise<{ alert?: string }>;
}) {
  const { alert } = await searchParams;
  redirect(alert ? controlCenterAlertHref(alert) : CONTROL_CENTER_ROUTES.alerts);
}
