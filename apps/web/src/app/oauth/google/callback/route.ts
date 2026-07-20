import { NextResponse } from "next/server";

import {
  atlasApiSigningConfigFromEnv,
  signedAtlasJsonRequest,
} from "@/lib/atlas-api-signing";

const GOOGLE_CALLBACK_PATH = "/api/v1/connectors/oauth/google/callback";
const DASHBOARD_BASE_URL_ENV = "ATLAS_DASHBOARD_BASE_URL";

function dashboardRedirectUrl(requestUrl: URL): URL {
  const configuredBaseUrl = process.env[DASHBOARD_BASE_URL_ENV]?.trim();
  if (configuredBaseUrl) {
    try {
      return new URL("/connectors", new URL(configuredBaseUrl).origin);
    } catch {
      // Fall back to the request origin so malformed environment values do not
      // expose callback query parameters or prevent a clean owner redirect.
    }
  }

  return new URL("/connectors", requestUrl.origin);
}

export async function GET(request: Request): Promise<NextResponse> {
  const requestUrl = new URL(request.url);
  const redirectUrl = dashboardRedirectUrl(requestUrl);
  redirectUrl.searchParams.set("oauth", "google");

  const providerError = requestUrl.searchParams.get("error");
  if (providerError) {
    redirectUrl.searchParams.set("status", "denied");
    return NextResponse.redirect(redirectUrl);
  }

  const state = requestUrl.searchParams.get("state");
  const code = requestUrl.searchParams.get("code");
  if (!state || !code) {
    redirectUrl.searchParams.set("status", "failed");
    return NextResponse.redirect(redirectUrl);
  }

  try {
    const config = atlasApiSigningConfigFromEnv();
    const signedRequest = signedAtlasJsonRequest(config, GOOGLE_CALLBACK_PATH, {
      state,
      authorization_code: code,
    });
    const response = await fetch(signedRequest.url, signedRequest.init);
    redirectUrl.searchParams.set("status", response.ok ? "connected" : "failed");
  } catch {
    redirectUrl.searchParams.set("status", "failed");
  }

  return NextResponse.redirect(redirectUrl);
}
