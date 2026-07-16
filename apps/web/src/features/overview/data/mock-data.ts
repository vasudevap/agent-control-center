/**
 * Alerts are the one Overview fixture that isn't already derivable
 * from agent-data.ts or approval-data.ts, so they remain their own
 * small fixture set here. Fleet health, active runs, schedule, and
 * pending-approval summaries are all derived directly from the
 * canonical agent and approval fixtures inside overview-dashboard.tsx
 * instead of being duplicated as separate, independently-authored
 * mock arrays (the baseline's Overview used seven invented agent
 * names that matched none of the real six-agent inventory).
 */
export { ALERT_FIXTURES as mockAlerts } from "@/app/(shell)/alerts/alert-data";
