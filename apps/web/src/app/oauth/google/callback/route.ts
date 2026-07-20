import { NextResponse } from "next/server";

import {
  atlasApiSigningConfigFromEnv,
  signedAtlasJsonRequest,
} from "@/lib/atlas-api-signing";

const GOOGLE_CALLBACK_PATH = "/api/v1/connectors/oauth/google/callback";

export async function GET(request: Request): Promise<NextResponse> {
  const requestUrl = new URL(request.url);
  const redirectUrl = new URL("/connectors", requestUrl.origin);
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
