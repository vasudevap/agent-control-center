import { ALERT_FIXTURES } from "./alert-data";
import { AlertsWorkspace } from "./alerts-workspace";

export default async function AlertsPage({
  searchParams,
}: {
  searchParams: Promise<{ alert?: string }>;
}) {
  const { alert } = await searchParams;
  return <AlertsWorkspace alerts={ALERT_FIXTURES} initialAlertId={alert} />;
}
