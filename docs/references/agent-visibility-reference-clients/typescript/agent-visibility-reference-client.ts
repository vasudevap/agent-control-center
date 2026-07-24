/**
 * WO-071 Atlas Agent Visibility reference client.
 *
 * Runtime requirement: a TypeScript-capable runtime with fetch, such as Deno.
 * This file imports no Atlas server or web application packages.
 */

const CONTRACT_VERSION = "2026-07-24";

interface Config {
  baseUrl: string;
  ownerCookieHeader: string;
  slugPrefix: string;
  alertTimeoutSeconds: number;
  verifyHealthLoss: boolean;
}

interface RequestOptions {
  body?: Record<string, unknown>;
  owner?: boolean;
  csrfToken?: string;
  agentToken?: string;
  idempotencyKey?: string;
  expectStatus?: Set<number>;
}

interface AtlasEnvelope<T> {
  data: T;
  error?: { code?: string; message?: string };
}

interface DashboardSession {
  csrf_token: string;
}

interface DashboardAgent {
  agent_id: string;
  observed_health?: string;
}

interface CredentialResponse {
  plaintext_token: string;
}

interface EnrollmentResponse {
  agent: DashboardAgent;
  credential: CredentialResponse;
}

interface LifecycleResponse {
  agent: DashboardAgent;
  credential?: CredentialResponse;
}

interface AlertResponse {
  alert_id: string;
  condition_key: string;
}

type Environment = Record<string, string | undefined>;

function readEnvironment(): Environment {
  const deno = (globalThis as { Deno?: { env: { get(name: string): string | undefined } } })
    .Deno;
  return new Proxy(
    {},
    {
      get: (_target, property) =>
        typeof property === "string" ? deno?.env.get(property) : undefined,
    },
  ) as Environment;
}

function loadConfig(environment = readEnvironment()): Config {
  const ownerCookie = environment.ATLAS_OWNER_SESSION_COOKIE;
  if (!ownerCookie) {
    throw new Error("ATLAS_OWNER_SESSION_COOKIE must be supplied outside the repo.");
  }
  return {
    baseUrl: (
      environment.ATLAS_API_BASE_URL ?? "https://api.atlas.grafley.com"
    ).replace(/\/$/, ""),
    ownerCookieHeader: ownerCookie.includes("=")
      ? ownerCookie
      : `atlas_owner_session=${ownerCookie}`,
    slugPrefix: environment.ATLAS_REFERENCE_SLUG_PREFIX ?? "wo071-reference",
    alertTimeoutSeconds: Number(
      environment.ATLAS_REFERENCE_ALERT_TIMEOUT_SECONDS ?? "180",
    ),
    verifyHealthLoss: ["1", "true", "yes"].includes(
      (environment.ATLAS_REFERENCE_VERIFY_HEALTH_LOSS ?? "false").toLowerCase(),
    ),
  };
}

async function requestJson<T>(
  config: Config,
  method: string,
  path: string,
  options: RequestOptions = {},
): Promise<{ status: number; body: AtlasEnvelope<T> }> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body) headers["Content-Type"] = "application/json";
  if (options.owner) headers.Cookie = config.ownerCookieHeader;
  if (options.csrfToken) headers["X-Atlas-CSRF-Token"] = options.csrfToken;
  if (options.idempotencyKey) headers["Idempotency-Key"] = options.idempotencyKey;
  if (options.agentToken) headers.Authorization = `Bearer ${options.agentToken}`;
  const response = await fetch(`${config.baseUrl}${path}`, {
    method,
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const body = (await response.json().catch(() => ({}))) as AtlasEnvelope<T>;
  const allowed = options.expectStatus ?? new Set([200, 201, 202]);
  if (!allowed.has(response.status)) {
    throw new Error(
      `Atlas request failed with HTTP ${response.status}: ${
        body.error?.code ?? "unknown_error"
      }`,
    );
  }
  return { status: response.status, body };
}

function nowIso(): string {
  return new Date().toISOString();
}

function evidence(step: string, details: Record<string, unknown> = {}): void {
  console.log(JSON.stringify({ step, ...details }));
}

async function heartbeat(
  config: Config,
  agentId: string,
  token: string,
  eventId: string,
  options: {
    status?: "healthy" | "degraded" | "unhealthy";
    checks?: Array<Record<string, string>>;
    expectStatus?: Set<number>;
  } = {},
) {
  return requestJson(config, "POST", `/api/v1/agents/${agentId}/heartbeats`, {
    agentToken: token,
    expectStatus: options.expectStatus,
    body: {
      event_id: eventId,
      contract_version: CONTRACT_VERSION,
      sent_at: nowIso(),
      environment: "wo071-hosted",
      status: options.status ?? "healthy",
      checks: options.checks ?? [{ name: "reference", status: "healthy" }],
      agent_version: "wo071-reference-typescript",
      build_sha: "wo071-reference",
    },
  });
}

async function execution(
  config: Config,
  agentId: string,
  token: string,
  executionId: string,
  status: "succeeded" | "failed",
) {
  return requestJson(
    config,
    "PUT",
    `/api/v1/agents/${agentId}/executions/${executionId}`,
    {
      agentToken: token,
      body: {
        contract_version: CONTRACT_VERSION,
        representation_hash: `sha256:${executionId}`,
        status,
        trigger: "wo071_reference",
        started_at: nowIso(),
        finished_at: nowIso(),
        duration_ms: 1000,
        summary: `WO-071 reference execution ${status}.`,
        error_code: status === "failed" ? "WO071_REFERENCE_EXECUTION_FAILED" : null,
        correlation_id: `wo071-${executionId}`,
        agent_version: "wo071-reference-typescript",
        build_sha: "wo071-reference",
      },
    },
  );
}

async function lifecycle(
  config: Config,
  csrfToken: string,
  agentId: string,
  suffix: string,
): Promise<LifecycleResponse> {
  return (
    await requestJson<LifecycleResponse>(
      config,
      "POST",
      `/api/v1/dashboard/agents/${agentId}${suffix}`,
      {
        owner: true,
        csrfToken,
        idempotencyKey: `wo071-${suffix.replace(/\W+/g, "-")}-${crypto.randomUUID()}`,
      },
    )
  ).body.data;
}

async function pollAlert(
  config: Config,
  conditionSuffix: string,
  timeoutSeconds: number,
): Promise<AlertResponse> {
  const deadline = Date.now() + timeoutSeconds * 1000;
  while (Date.now() < deadline) {
    const alerts = (
      await requestJson<AlertResponse[]>(config, "GET", "/api/v1/alerts", {
        owner: true,
      })
    ).body.data;
    const found = alerts.find((alert) =>
      alert.condition_key.endsWith(conditionSuffix),
    );
    if (found) return found;
    await new Promise((resolve) => setTimeout(resolve, 10_000));
  }
  throw new Error(`Timed out waiting for alert suffix ${conditionSuffix}.`);
}

async function pollAgentObservedHealth(
  config: Config,
  agentId: string,
  expected: Set<string>,
  timeoutSeconds: number,
): Promise<string> {
  const deadline = Date.now() + timeoutSeconds * 1000;
  let observed = "unknown";
  while (Date.now() < deadline) {
    const agent = (
      await requestJson<DashboardAgent>(
        config,
        "GET",
        `/api/v1/dashboard/agents/${agentId}`,
        { owner: true },
      )
    ).body.data;
    observed = agent.observed_health ?? "unknown";
    if (expected.has(observed)) return observed;
    await new Promise((resolve) => setTimeout(resolve, 10_000));
  }
  throw new Error(`Timed out waiting for health; last value was ${observed}.`);
}

export async function runAgentVisibilityReferenceClient(
  config = loadConfig(),
): Promise<void> {
  const session = (
    await requestJson<DashboardSession>(
      config,
      "GET",
      "/api/v1/dashboard/session",
      { owner: true },
    )
  ).body.data;
  const slug = `${config.slugPrefix}-${Date.now()}-${crypto.randomUUID().slice(0, 8)}`;
  const enrolled = (
    await requestJson<EnrollmentResponse>(
      config,
      "POST",
      "/api/v1/dashboard/agents",
      {
        owner: true,
        csrfToken: session.csrf_token,
        idempotencyKey: `wo071-enroll-${crypto.randomUUID()}`,
        body: {
          slug,
          display_name: `WO-071 Reference Agent ${slug.slice(-8)}`,
          description: "Hosted WO-071 reference verification agent.",
          environment: "wo071-hosted",
          monitoring_mode: "heartbeat",
          heartbeat_interval_seconds: 30,
          tags: ["wo071", "reference"],
          expected_version: "wo071-reference-typescript",
        },
      },
    )
  ).body.data;
  const agentId = enrolled.agent.agent_id;
  let token = enrolled.credential.plaintext_token;
  evidence("enrolled", { agent_id: agentId, credential: "redacted" });

  await heartbeat(config, agentId, token, `${slug}-first`);
  evidence("first_heartbeat_accepted", { agent_id: agentId });

  await heartbeat(config, agentId, token, `${slug}-failed-check`, {
    status: "unhealthy",
    checks: [
      {
        name: "reference-dependency",
        status: "unhealthy",
        error_code: "WO071_REFERENCE_CHECK_FAILED",
      },
    ],
  });
  const checkAlert = await pollAlert(
    config,
    ":check:reference-dependency",
    config.alertTimeoutSeconds,
  );
  evidence("failed_check_alert_opened", { alert_id: checkAlert.alert_id });

  await execution(config, agentId, token, `${slug}-success`, "succeeded");
  for (const index of [0, 1, 2]) {
    await execution(config, agentId, token, `${slug}-failed-${index}`, "failed");
  }
  const repeatedAlert = await pollAlert(
    config,
    ":execution:repeated-failure",
    config.alertTimeoutSeconds,
  );
  evidence("repeated_failure_alert_opened", { alert_id: repeatedAlert.alert_id });

  if (config.verifyHealthLoss) {
    const late = await pollAgentObservedHealth(
      config,
      agentId,
      new Set(["late", "offline"]),
      180,
    );
    evidence("heartbeat_loss_observed", { observed_health: late });
    await heartbeat(config, agentId, token, `${slug}-recovery`);
    const recovered = await pollAgentObservedHealth(
      config,
      agentId,
      new Set(["online"]),
      90,
    );
    evidence("heartbeat_recovery_observed", { observed_health: recovered });
  }

  const rotated = await lifecycle(
    config,
    session.csrf_token,
    agentId,
    "/credentials/rotate",
  );
  const previousToken = token;
  token = rotated.credential?.plaintext_token ?? "";
  evidence("credential_rotated", { agent_id: agentId, credential: "redacted" });

  await heartbeat(config, agentId, previousToken, `${slug}-overlap-old`);
  await heartbeat(config, agentId, token, `${slug}-overlap-new`);
  evidence("rotation_overlap_accepts_old_and_new", { agent_id: agentId });

  await lifecycle(config, session.csrf_token, agentId, "/disconnect");
  const rejected = await heartbeat(
    config,
    agentId,
    token,
    `${slug}-after-disconnect`,
    { expectStatus: new Set([401]) },
  );
  evidence("disconnect_rejects_telemetry", { status: rejected.status });

  const reconnected = await lifecycle(
    config,
    session.csrf_token,
    agentId,
    "/reconnect",
  );
  token = reconnected.credential?.plaintext_token ?? "";
  await heartbeat(config, agentId, token, `${slug}-after-reconnect`);
  evidence("reconnect_credential_accepted", { agent_id: agentId });

  await lifecycle(config, session.csrf_token, agentId, "/archive");
  const archived = await heartbeat(config, agentId, token, `${slug}-after-archive`, {
    expectStatus: new Set([401]),
  });
  evidence("archive_rejects_telemetry", { status: archived.status });
  evidence("complete", { agent_id: agentId, tokens: "redacted" });
}

if (
  typeof (globalThis as { Deno?: unknown }).Deno !== "undefined" &&
  (import.meta as ImportMeta & { main?: boolean }).main
) {
  await runAgentVisibilityReferenceClient();
}
