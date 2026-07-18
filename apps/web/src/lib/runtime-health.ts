export type RuntimeHealthState =
  | "not-configured"
  | "checking"
  | "ready"
  | "not-ready"
  | "unavailable";

export interface RuntimeHealthPresentation {
  state: RuntimeHealthState;
  label: string;
  detail: string;
  problemCount: number;
}

interface RuntimeReadyPayload {
  status?: unknown;
  problems?: unknown;
}

export function buildRuntimeReadyUrl(apiBaseUrl: string | undefined): string | null {
  const trimmed = apiBaseUrl?.trim();
  if (!trimmed) return null;
  return `${trimmed.replace(/\/+$/, "")}/health/ready`;
}

export function runtimeHealthFromReadyPayload(
  payload: RuntimeReadyPayload,
): RuntimeHealthPresentation {
  const problemCount = Array.isArray(payload.problems) ? payload.problems.length : 0;

  if (payload.status === "ready") {
    return {
      state: "ready",
      label: "Runtime ready",
      detail: "Atlas API readiness is healthy.",
      problemCount: 0,
    };
  }

  if (payload.status === "not_ready") {
    return {
      state: "not-ready",
      label: problemCount > 0 ? `Runtime not ready (${problemCount})` : "Runtime not ready",
      detail: "Atlas API returned release-readiness problem codes.",
      problemCount,
    };
  }

  return {
    state: "unavailable",
    label: "Runtime unavailable",
    detail: "Atlas API readiness returned an unexpected response.",
    problemCount: 0,
  };
}
