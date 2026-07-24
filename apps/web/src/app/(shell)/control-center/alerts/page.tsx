import { ALERT_FIXTURES } from "@/app/(shell)/alerts/alert-data";
import { AlertsWorkspace } from "@/app/(shell)/alerts/alerts-workspace";

export default async function ControlCenterAlertsPage({
  searchParams,
}: {
  searchParams: Promise<{ alert?: string }>;
}) {
  const { alert } = await searchParams;
  return <AlertsWorkspace alerts={ALERT_FIXTURES} initialAlertId={alert} />;
}
