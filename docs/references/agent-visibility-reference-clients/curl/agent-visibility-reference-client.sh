#!/usr/bin/env bash
set -eu

# WO-071 Atlas Agent Visibility curl reference client.
# Requires: bash, curl, and jq. This script imports no Atlas server packages
# and does not print owner cookies or generated agent credentials.

BASE_URL="${ATLAS_API_BASE_URL:-https://api.atlas.grafley.com}"
BASE_URL="${BASE_URL%/}"
COOKIE_VALUE="${ATLAS_OWNER_SESSION_COOKIE:-}"
SLUG_PREFIX="${ATLAS_REFERENCE_SLUG_PREFIX:-wo071-reference}"
ALERT_TIMEOUT_SECONDS="${ATLAS_REFERENCE_ALERT_TIMEOUT_SECONDS:-180}"
VERIFY_HEALTH_LOSS="${ATLAS_REFERENCE_VERIFY_HEALTH_LOSS:-false}"
CONTRACT_VERSION="2026-07-24"

if [ -z "$COOKIE_VALUE" ]; then
  echo '{"step":"failed","error":"ATLAS_OWNER_SESSION_COOKIE must be supplied outside the repo."}' >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo '{"step":"failed","error":"jq is required for the curl reference client."}' >&2
  exit 1
fi

case "$COOKIE_VALUE" in
  *=*) OWNER_COOKIE_HEADER="$COOKIE_VALUE" ;;
  *) OWNER_COOKIE_HEADER="atlas_owner_session=$COOKIE_VALUE" ;;
esac

evidence() {
  printf '{"step":"%s"%s}\n' "$1" "$2"
}

request_json() {
  method="$1"
  path="$2"
  body="${3:-}"
  headers="${4:-}"
  expected="${5:-200 201 202}"
  tmp_body="$(mktemp)"
  args=(-sS -o "$tmp_body" -w '%{http_code}' -X "$method" -H 'Accept: application/json')
  while IFS= read -r header; do
    if [ -n "$header" ]; then
      args+=(-H "$header")
    fi
  done <<< "$headers"
  if [ -n "$body" ]; then
    args+=(-H 'Content-Type: application/json' --data "$body")
  fi
  status="$(curl "${args[@]}" "$BASE_URL$path")"
  if ! printf '%s\n' "$expected" | tr ' ' '\n' | grep -qx "$status"; then
    jq -c --arg status "$status" \
      '{step:"failed", status:($status|tonumber), error:(.error.code // "unknown_error")}' \
      "$tmp_body" >&2
    exit 1
  fi
  cat "$tmp_body"
  rm -f "$tmp_body"
}

owner_get() {
  request_json GET "$1" "" "Cookie: $OWNER_COOKIE_HEADER"
}

owner_post() {
  path="$1"
  csrf="$2"
  key="$3"
  body="${4:-}"
  request_json POST "$path" "$body" "Cookie: $OWNER_COOKIE_HEADER
X-Atlas-CSRF-Token: $csrf
Idempotency-Key: $key"
}

agent_heartbeat() {
  agent_id="$1"
  token="$2"
  event_id="$3"
  status="${4:-healthy}"
  checks="${5:-[{\"name\":\"reference\",\"status\":\"healthy\"}]}"
  expected="${6:-200 201 202}"
  if [ -z "$checks" ]; then
    checks='[{"name":"reference","status":"healthy"}]'
  fi
  body="$(jq -cn \
    --arg event_id "$event_id" \
    --arg contract_version "$CONTRACT_VERSION" \
    --arg sent_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg status "$status" \
    --argjson checks "$checks" \
    '{
      event_id: $event_id,
      contract_version: $contract_version,
      sent_at: $sent_at,
      environment: "wo071-hosted",
      status: $status,
      checks: $checks,
      agent_version: "wo071-reference-curl",
      build_sha: "wo071-reference"
    }')"
  request_json POST "/api/v1/agents/$agent_id/heartbeats" "$body" \
    "Authorization: Bearer $token" "$expected" >/dev/null
}

agent_execution() {
  agent_id="$1"
  token="$2"
  execution_id="$3"
  status="$4"
  error_code="${5:-null}"
  body="$(jq -cn \
    --arg contract_version "$CONTRACT_VERSION" \
    --arg execution_id "$execution_id" \
    --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg status "$status" \
    --arg error_code "$error_code" \
    '{
      contract_version: $contract_version,
      representation_hash: ("sha256:" + $execution_id),
      status: $status,
      trigger: "wo071_reference",
      started_at: $now,
      finished_at: $now,
      duration_ms: 1000,
      summary: ("WO-071 reference execution " + $status + "."),
      error_code: (if $error_code == "null" then null else $error_code end),
      correlation_id: ("wo071-" + $execution_id),
      agent_version: "wo071-reference-curl",
      build_sha: "wo071-reference"
    }')"
  request_json PUT "/api/v1/agents/$agent_id/executions/$execution_id" "$body" \
    "Authorization: Bearer $token" >/dev/null
}

poll_alert() {
  suffix="$1"
  deadline=$(( $(date +%s) + ALERT_TIMEOUT_SECONDS ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    alerts="$(owner_get /api/v1/alerts)"
    alert_id="$(printf '%s' "$alerts" | jq -r --arg suffix "$suffix" \
      '.data[] | select(.condition_key | endswith($suffix)) | .alert_id' | head -n 1)"
    if [ -n "$alert_id" ]; then
      printf '%s' "$alert_id"
      return 0
    fi
    sleep 10
  done
  echo "{\"step\":\"failed\",\"error\":\"Timed out waiting for alert suffix $suffix.\"}" >&2
  exit 1
}

poll_agent_health() {
  agent_id="$1"
  expected="$2"
  timeout="$3"
  deadline=$(( $(date +%s) + timeout ))
  observed="unknown"
  while [ "$(date +%s)" -lt "$deadline" ]; do
    agent="$(owner_get "/api/v1/dashboard/agents/$agent_id")"
    observed="$(printf '%s' "$agent" | jq -r '.data.observed_health // "unknown"')"
    if printf '%s\n' "$expected" | tr ' ' '\n' | grep -qx "$observed"; then
      printf '%s' "$observed"
      return 0
    fi
    sleep 10
  done
  echo "{\"step\":\"failed\",\"error\":\"Timed out waiting for observed health; last value was $observed.\"}" >&2
  exit 1
}

SESSION="$(owner_get /api/v1/dashboard/session)"
CSRF="$(printf '%s' "$SESSION" | jq -r '.data.csrf_token')"
SLUG="$SLUG_PREFIX-$(date +%s)-$(LC_ALL=C tr -dc a-f0-9 </dev/urandom | head -c 8)"
ENROLL_BODY="$(jq -cn --arg slug "$SLUG" '{
  slug: $slug,
  display_name: ("WO-071 Reference Agent " + ($slug | .[-8:])),
  description: "Hosted WO-071 reference verification agent.",
  environment: "wo071-hosted",
  monitoring_mode: "heartbeat",
  heartbeat_interval_seconds: 30,
  tags: ["wo071", "reference"],
  expected_version: "wo071-reference-curl"
}')"
ENROLLED="$(owner_post /api/v1/dashboard/agents "$CSRF" "wo071-enroll-$(date +%s)" "$ENROLL_BODY")"
AGENT_ID="$(printf '%s' "$ENROLLED" | jq -r '.data.agent.agent_id')"
TOKEN="$(printf '%s' "$ENROLLED" | jq -r '.data.credential.plaintext_token')"
evidence enrolled ",\"agent_id\":\"$AGENT_ID\",\"credential\":\"redacted\""

agent_heartbeat "$AGENT_ID" "$TOKEN" "$SLUG-first"
evidence first_heartbeat_accepted ",\"agent_id\":\"$AGENT_ID\""

FAILED_CHECKS='[{"name":"reference-dependency","status":"unhealthy","error_code":"WO071_REFERENCE_CHECK_FAILED"}]'
agent_heartbeat "$AGENT_ID" "$TOKEN" "$SLUG-failed-check" unhealthy "$FAILED_CHECKS"
CHECK_ALERT_ID="$(poll_alert ':check:reference-dependency')"
evidence failed_check_alert_opened ",\"alert_id\":\"$CHECK_ALERT_ID\""

agent_execution "$AGENT_ID" "$TOKEN" "$SLUG-success" succeeded
agent_execution "$AGENT_ID" "$TOKEN" "$SLUG-failed-0" failed WO071_REFERENCE_EXECUTION_FAILED
agent_execution "$AGENT_ID" "$TOKEN" "$SLUG-failed-1" failed WO071_REFERENCE_EXECUTION_FAILED
agent_execution "$AGENT_ID" "$TOKEN" "$SLUG-failed-2" failed WO071_REFERENCE_EXECUTION_FAILED
REPEATED_ALERT_ID="$(poll_alert ':execution:repeated-failure')"
evidence repeated_failure_alert_opened ",\"alert_id\":\"$REPEATED_ALERT_ID\""

if [ "$VERIFY_HEALTH_LOSS" = "true" ]; then
  LOSS="$(poll_agent_health "$AGENT_ID" 'late offline' 180)"
  evidence heartbeat_loss_observed ",\"observed_health\":\"$LOSS\""
  agent_heartbeat "$AGENT_ID" "$TOKEN" "$SLUG-recovery"
  RECOVERED="$(poll_agent_health "$AGENT_ID" online 90)"
  evidence heartbeat_recovery_observed ",\"observed_health\":\"$RECOVERED\""
fi

ROTATED="$(owner_post "/api/v1/dashboard/agents/$AGENT_ID/credentials/rotate" "$CSRF" "wo071-rotate-$(date +%s)")"
NEW_TOKEN="$(printf '%s' "$ROTATED" | jq -r '.data.credential.plaintext_token')"
evidence credential_rotated ",\"agent_id\":\"$AGENT_ID\",\"credential\":\"redacted\""
agent_heartbeat "$AGENT_ID" "$TOKEN" "$SLUG-overlap-old"
agent_heartbeat "$AGENT_ID" "$NEW_TOKEN" "$SLUG-overlap-new"
evidence rotation_overlap_accepts_old_and_new ",\"agent_id\":\"$AGENT_ID\""

owner_post "/api/v1/dashboard/agents/$AGENT_ID/disconnect" "$CSRF" "wo071-disconnect-$(date +%s)" >/dev/null
agent_heartbeat "$AGENT_ID" "$NEW_TOKEN" "$SLUG-after-disconnect" healthy "" 401
evidence disconnect_rejects_telemetry ',"status":401'

RECONNECTED="$(owner_post "/api/v1/dashboard/agents/$AGENT_ID/reconnect" "$CSRF" "wo071-reconnect-$(date +%s)")"
RECONNECT_TOKEN="$(printf '%s' "$RECONNECTED" | jq -r '.data.credential.plaintext_token')"
agent_heartbeat "$AGENT_ID" "$RECONNECT_TOKEN" "$SLUG-after-reconnect"
evidence reconnect_credential_accepted ",\"agent_id\":\"$AGENT_ID\""

owner_post "/api/v1/dashboard/agents/$AGENT_ID/archive" "$CSRF" "wo071-archive-$(date +%s)" >/dev/null
agent_heartbeat "$AGENT_ID" "$RECONNECT_TOKEN" "$SLUG-after-archive" healthy "" 401
evidence archive_rejects_telemetry ',"status":401'
evidence complete ",\"agent_id\":\"$AGENT_ID\",\"tokens\":\"redacted\""
