import { createHash, createHmac } from "node:crypto";

import { describe, expect, it } from "vitest";

import { signAtlasRequest, signedAtlasJsonRequest } from "./atlas-api-signing";

describe("Atlas API request signing", () => {
  it("matches the backend external-client HMAC canonical request", () => {
    const body = JSON.stringify({
      state: "oauth-state",
      authorization_code: "provider-code",
    });
    const bodyDigest = createHash("sha256").update(body).digest("hex");
    const canonical = [
      "POST",
      "/api/v1/connectors/oauth/google/callback",
      "1770000000",
      "nonce-1",
      bodyDigest,
    ].join("\n");
    const expected = createHmac("sha256", "secret-1")
      .update(canonical)
      .digest("hex");

    const signature = signAtlasRequest({
      method: "POST",
      pathQuery: "/api/v1/connectors/oauth/google/callback",
      timestamp: 1770000000,
      nonce: "nonce-1",
      body,
      secret: "secret-1",
    });

    expect(signature).toBe(expected);
  });

  it("builds a signed JSON request without exposing the signing secret", () => {
    const request = signedAtlasJsonRequest(
      {
        apiBaseUrl: "https://api.atlas.grafley.com/",
        clientId: "client-1",
        keyId: "key-1",
        secret: "secret-1",
      },
      "/api/v1/connectors/oauth/google/callback",
      { state: "oauth-state", authorization_code: "provider-code" },
      { timestamp: 1770000000, nonce: "nonce-1" },
    );

    expect(request.url).toBe(
      "https://api.atlas.grafley.com/api/v1/connectors/oauth/google/callback",
    );
    expect(request.init.method).toBe("POST");
    expect(request.init.body).toBe(
      JSON.stringify({
        state: "oauth-state",
        authorization_code: "provider-code",
      }),
    );
    expect(request.init.headers).toMatchObject({
      "Content-Type": "application/json",
      "X-Atlas-Client-Id": "client-1",
      "X-Atlas-Key-Id": "key-1",
      "X-Atlas-Timestamp": "1770000000",
      "X-Atlas-Nonce": "nonce-1",
    });
    expect(JSON.stringify(request.init.headers)).not.toContain("secret-1");
  });
});
