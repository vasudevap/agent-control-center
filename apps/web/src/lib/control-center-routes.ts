export const CONTROL_CENTER_ROOT = "/control-center";

export const CONTROL_CENTER_ROUTES = {
  overview: CONTROL_CENTER_ROOT,
  agents: `${CONTROL_CENTER_ROOT}/agents`,
  executions: `${CONTROL_CENTER_ROOT}/runs`,
  alerts: `${CONTROL_CENTER_ROOT}/alerts`,
  activity: `${CONTROL_CENTER_ROOT}/activity`,
  legacyAudit: `${CONTROL_CENTER_ROOT}/audit`,
} as const;

export const controlCenterAgentHref = (agentId: string) =>
  `${CONTROL_CENTER_ROUTES.agents}/${encodeURIComponent(agentId)}`;

export const controlCenterExecutionHref = (runId: string) =>
  `${CONTROL_CENTER_ROUTES.executions}/${encodeURIComponent(runId)}`;

export const controlCenterAlertHref = (alertId: string) =>
  `${CONTROL_CENTER_ROUTES.alerts}?alert=${encodeURIComponent(alertId)}`;
