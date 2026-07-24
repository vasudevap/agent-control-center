# Agent Visibility Reference Clients

These WO-071 clients prove that external agents can integrate with the Atlas
Agent Visibility MVP without importing Atlas server packages.

Each client is intentionally standalone:

- `curl/agent-visibility-reference-client.sh`
- `python/agent_visibility_reference_client.py`
- `typescript/agent-visibility-reference-client.ts`

## Required runtime inputs

Set these values outside the repository before running a hosted verification:

```bash
export ATLAS_API_BASE_URL="https://api.atlas.grafley.com"
export ATLAS_OWNER_SESSION_COOKIE="<redacted owner-session cookie value or Cookie header>"
```

Do not paste either value into documentation, logs, screenshots, pull request
text, or chat. The scripts keep generated agent credentials in memory and print
only redacted evidence.

## Optional inputs

```bash
export ATLAS_REFERENCE_SLUG_PREFIX="wo071-reference"
export ATLAS_REFERENCE_VERIFY_HEALTH_LOSS="false"
export ATLAS_REFERENCE_ALERT_TIMEOUT_SECONDS="180"
```

Set `ATLAS_REFERENCE_VERIFY_HEALTH_LOSS=true` for the long hosted run that waits
for heartbeat loss and recovery evidence. With the accepted ES-009 thresholds,
this can take more than five minutes because Atlas marks a heartbeat-monitored
agent late after at least 120 seconds and offline after at least 300 seconds.

## Evidence boundary

Hosted runs can prove enrollment, first heartbeat, failed check alert,
successful execution, repeated failed execution alert, credential rotation,
overlap acceptance, disconnect rejection, reconnect, and archive.

The exact 24-hour rejection after overlap expiry is covered by deterministic
local tests. Hosted verification should not mutate provider-managed database
time/state or wait 24 hours merely to observe expiry. The rotate response and
local tests together prove the expiry contract without exposing credentials.

## Curl client

```bash
docs/references/agent-visibility-reference-clients/curl/agent-visibility-reference-client.sh
```

Requirements: `curl`, `jq`, POSIX shell.

## Python client

```bash
python3 docs/references/agent-visibility-reference-clients/python/agent_visibility_reference_client.py
```

Requirements: Python 3.12+ standard library only.

## TypeScript client

The TypeScript client is runtime-neutral and depends only on `fetch`.

```bash
deno run --allow-net --allow-env docs/references/agent-visibility-reference-clients/typescript/agent-visibility-reference-client.ts
```

It can also be compiled with the repository TypeScript compiler:

```bash
npx tsc --noEmit --target ES2022 --module ES2022 --moduleResolution bundler \
  --lib ES2022,DOM docs/references/agent-visibility-reference-clients/typescript/agent-visibility-reference-client.ts
```
