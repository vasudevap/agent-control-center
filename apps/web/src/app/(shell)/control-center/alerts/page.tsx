import { AlertsWorkspace } from "@/app/(shell)/alerts/alerts-workspace";

export default async function ControlCenterAlertsPage({
  searchParams,
}: {
  searchParams: Promise<{ alert?: string }>;
}) {
  const { alert } = await searchParams;
  return (
    <AlertsWorkspace
      alerts={[]}
      initialAlertId={alert}
      runtimeRequired
    />
  );
}
