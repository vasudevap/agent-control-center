import { createHash, createHmac, randomUUID } from "node:crypto";

export interface AtlasApiSigningConfig {
  apiBaseUrl: string;
  clientId: string;
  keyId: string;
  secret: string;
}

export interface SignedAtlasJsonRequest {
  url: string;
  init: RequestInit;
}

export function atlasApiSigningConfigFromEnv(): AtlasApiSigningConfig {
  const apiBaseUrl = requiredEnv(
    "NEXT_PUBLIC_API_BASE_URL",
    process.env.NEXT_PUBLIC_API_BASE_URL,
  );
  return {
    apiBaseUrl,
    clientId: requiredEnv(
      "ATLAS_DASHBOARD_EXTERNAL_CLIENT_ID",
      process.env.ATLAS_DASHBOARD_EXTERNAL_CLIENT_ID,
    ),
    keyId: requiredEnv(
      "ATLAS_DASHBOARD_EXTERNAL_CLIENT_KEY_ID",
      process.env.ATLAS_DASHBOARD_EXTERNAL_CLIENT_KEY_ID,
    ),
    secret: requiredEnv(
      "ATLAS_DASHBOARD_EXTERNAL_CLIENT_SECRET",
      process.env.ATLAS_DASHBOARD_EXTERNAL_CLIENT_SECRET,
    ),
  };
}

export function signedAtlasJsonRequest(
  config: AtlasApiSigningConfig,
  path: string,
  payload: unknown,
  options: { nonce?: string; timestamp?: number } = {},
): SignedAtlasJsonRequest {
  const body = JSON.stringify(payload);
  const timestamp = options.timestamp ?? Math.floor(Date.now() / 1000);
  const nonce = options.nonce ?? randomUUID();
  const pathQuery = normalizePathQuery(path);
  const signature = signAtlasRequest({
    method: "POST",
    pathQuery,
    timestamp,
    nonce,
    body,
    secret: config.secret,
  });
  return {
    url: `${config.apiBaseUrl.replace(/\/+$/, "")}${pathQuery}`,
    init: {
      method: "POST",
      cache: "no-store",
      body,
      headers: {
        "Content-Type": "application/json",
        "X-Atlas-Client-Id": config.clientId,
        "X-Atlas-Key-Id": config.keyId,
        "X-Atlas-Timestamp": String(timestamp),
        "X-Atlas-Nonce": nonce,
        "X-Atlas-Signature": signature,
      },
    },
  };
}

export function signAtlasRequest(input: {
  method: string;
  pathQuery: string;
  timestamp: number;
  nonce: string;
  body: string;
  secret: string;
}): string {
  const bodyDigest = createHash("sha256").update(input.body).digest("hex");
  const canonical = [
    input.method.toUpperCase(),
    normalizePathQuery(input.pathQuery),
    String(input.timestamp),
    input.nonce,
    bodyDigest,
  ].join("\n");
  return createHmac("sha256", input.secret).update(canonical).digest("hex");
}

function normalizePathQuery(pathQuery: string): string {
  if (!pathQuery.startsWith("/")) {
    throw new Error("Atlas API path must be absolute.");
  }
  return pathQuery;
}

function requiredEnv(name: string, value: string | undefined): string {
  const trimmed = value?.trim();
  if (!trimmed) {
    throw new Error(`${name} is not configured.`);
  }
  return trimmed;
}
