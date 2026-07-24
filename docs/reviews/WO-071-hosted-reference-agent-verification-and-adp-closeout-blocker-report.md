# WO-071 Hosted Reference-Agent Verification and ADP Closeout Blocker Report

**Work Order:** [WO-071](../work-orders/071-hosted-reference-agent-verification-and-adp-closeout.md)
**Status:** Blocked - Hosted credential configuration missing
**Prepared:** 2026-07-24
**Commit:** This commit

## Summary

WO-071 can proceed locally through reference-client preparation, but hosted
acceptance cannot be completed yet.

The production API is live, but hosted readiness reports missing agent
credential configuration. Owner enrollment and one-time credential issuance
fail closed without these settings, so the hosted reference-agent workflow
cannot honestly verify enrollment, heartbeat ingestion, lifecycle rotation,
disconnect, reconnect, or archive.

## Prepared Evidence

Three standalone reference clients were added under
[`docs/references/agent-visibility-reference-clients`](../references/agent-visibility-reference-clients/README.md):

- curl + jq shell client;
- plain Python standard-library client;
- TypeScript fetch client.

The clients import no Atlas server packages. They take owner session material
from environment variables, keep generated agent credentials in memory only,
and print redacted step evidence.

Local client validation completed:

```text
bash -n docs/references/agent-visibility-reference-clients/curl/agent-visibility-reference-client.sh
pass

python3 -m py_compile docs/references/agent-visibility-reference-clients/python/agent_visibility_reference_client.py
pass

npx tsc --noEmit --target ES2022 --module ES2022 --moduleResolution bundler --lib ES2022,DOM docs/references/agent-visibility-reference-clients/typescript/agent-visibility-reference-client.ts
pass

.venv/bin/python -m pytest apps/api/tests/test_wo071_reference_clients.py
2 passed
```

Full local validation completed before publishing the blocker branch:

```text
npm ci
pass

npm run typecheck
pass

npm run lint
pass

npm test
110 passed across 26 web test files

npm run build
pass after rerun outside the sandbox because Turbopack attempted to bind a
local process port and the sandbox returned `Operation not permitted`

.venv/bin/python -m pip install -c apps/api/constraints.txt -e "apps/api[dev]"
pass after rerun with network access for build dependency resolution

.venv/bin/python -m mypy apps/api/src
Success: no issues found in 72 source files

.venv/bin/python -m ruff check apps/api
All checks passed!

.venv/bin/python -m pytest apps/api
210 passed, 1 existing Starlette/httpx deprecation warning

ATLAS_API_DATABASE_URL=sqlite:////private/tmp/wo071-alembic-smoke.sqlite ../../.venv/bin/python -m alembic upgrade head
pass from apps/api

ATLAS_API_DATABASE_URL=sqlite:////private/tmp/wo071-alembic-smoke.sqlite ../../.venv/bin/python -m alembic downgrade base
pass from apps/api

git diff --check
pass

Secret-pattern scan
pass after reviewing matches as the reference-client guard regex and a
redacted environment-variable placeholder; no secret values were added.
```

## Hosted Public Checks

Non-secret hosted checks on 2026-07-24:

```text
curl -s -i https://api.atlas.grafley.com/health/live
HTTP/2 200
{"status":"ok","service":"atlas-api","environment":"production"}

curl -s -i https://api.atlas.grafley.com/health/ready
HTTP/2 200
{"status":"not_ready","service":"atlas-api","checks":{"configuration":"failed"},"problems":["agent_credential_pepper_key_id_missing","agent_credential_pepper_missing"]}

curl -s -i https://atlas-agent-control-center-api.onrender.com/health/ready
HTTP/2 200
{"status":"not_ready","service":"atlas-api","checks":{"configuration":"failed"},"problems":["agent_credential_pepper_key_id_missing","agent_credential_pepper_missing"]}

curl -s -I https://atlas.grafley.com/
HTTP/2 200

curl -s -I https://atlas.grafley.com/control-center
HTTP/2 200
```

## Blocker

The hosted Render API environment is missing:

- `ATLAS_API_AGENT_CREDENTIAL_PEPPER`
- `ATLAS_API_AGENT_CREDENTIAL_PEPPER_KEY_ID`

These are production secret/configuration values. They must be provisioned
outside the repository. Do not commit, paste, screenshot, log, or include the
secret value in PR text or chat.

## Why This Blocks WO-071

The ES-009 hosted reference-agent flow depends on owner enrollment returning a
one-time agent telemetry credential. Enrollment calls the credential service,
which intentionally fails closed when the credential pepper or pepper key ID is
not configured.

Without that hosted credential configuration, the reference clients cannot
complete:

- enrollment;
- first heartbeat;
- failed check alert;
- successful and failed execution reporting;
- repeated-failure alert;
- credential rotation and overlap acceptance;
- disconnect rejection;
- reconnect;
- archive.

## Route-Base Evidence

The public frontend route split remains aligned with ADP-006:

- `/` serves the public Atlas landing page;
- `/control-center` serves the authenticated application shell.

No hosted lifecycle credential evidence was captured through the frontend
because owner-authenticated lifecycle verification is blocked by the API
credential configuration readiness failure.

## Required Remediation

Provision the two missing Render API environment values using a secret-safe
operator process:

1. Generate or provide a high-entropy `ATLAS_API_AGENT_CREDENTIAL_PEPPER`.
2. Set a non-secret rotation label such as `ATLAS_API_AGENT_CREDENTIAL_PEPPER_KEY_ID`.
3. Redeploy or restart the Render API service so the new environment is loaded.
4. Verify `https://api.atlas.grafley.com/health/ready` returns `ready`.
5. Rerun one or more WO-071 reference clients with redacted output.

## Residual Status

ADP-006 remains blocked, not complete. WO-064 through WO-070 are merged. WO-071
must resume after hosted credential configuration is ready.
