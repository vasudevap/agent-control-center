# WO-054 Netlify Frontend Deployment Implementation Report

**Work Order:** [WO-054](../work-orders/054-netlify-frontend-deployment.md)
**Status:** Blocked - Hosted API URL Pending
**Date:** 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-054 implementation has started. The Netlify project target now exists and
the source-level Netlify build configuration is added, but the frontend cannot
be honestly completed or production-deployed until WO-055 provides the hosted
Atlas API URL for `NEXT_PUBLIC_API_BASE_URL`.

No secret values were created, displayed, written to Git, or configured in
Netlify during this Work Order.

## Scope Implemented

- Added root `netlify.toml` for the accepted workspace build command and Next
  publish output:
  - build command: `npm run build`
  - publish directory: `apps/web/.next`
- Ignored local Netlify link metadata with `.netlify/`.
- Created and linked the Netlify site target:
  - site name: `atlas-agent-control-center`
  - site URL: `https://atlas-agent-control-center.netlify.app`
  - admin URL: `https://app.netlify.com/projects/atlas-agent-control-center`
- Configured the non-secret Netlify production build variable
  `NEXT_PUBLIC_APP_ENV=production`.

## Explicitly Not Performed

- No production deploy was performed.
- No `NEXT_PUBLIC_API_BASE_URL` value was set because the hosted API URL does
  not exist yet.
- No secret variables were configured or inspected.
- No Netlify environment-variable listing was captured because that command can
  reveal provider-side values.
- No public launch, release tag, backend deploy, or database migration was
  performed.

## Provider Evidence

| Check | Result | Side effect |
| --- | --- | --- |
| `netlify sites:create --name atlas-agent-control-center --account-slug vasudevap --filter @atlas/web` | Site created and linked | Netlify site creation |
| `netlify env:set NEXT_PUBLIC_APP_ENV production --context production --scope builds --filter @atlas/web` | Non-secret production build label configured | Netlify environment variable write |
| `netlify status` from `apps/web` | Linked site reports `atlas-agent-control-center` and root `netlify.toml` | Read-only |

The `netlify env:list --json` verifier was intentionally not used after the
safety reviewer rejected it as too risky for provider-side environment values.

## Validation Commands

Frontend tests:

```text
npm test
```

Result:

```text
19 test files passed, 88 tests passed
```

Frontend lint:

```text
npm run lint
```

Result:

```text
Passed
```

Frontend typecheck:

```text
npm run typecheck
```

Result:

```text
Passed
```

Production build:

```text
npm run build
```

Result:

```text
Next.js 16.2.10 compiled successfully; 13 static pages generated
```

Release-readiness provider file guard:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_release_readiness.py
```

Result:

```text
2 passed
```

## Blocker

WO-054 requires `NEXT_PUBLIC_API_BASE_URL` to point to the accepted hosted API
and requires runtime-health evidence. That cannot be completed until WO-055
creates or identifies the Render API service URL.

Deploying before that URL exists would produce a hosted dashboard with
`Runtime not configured`, which is useful as a local readiness state but does
not satisfy the WO-054 completion criteria.

## Completion State

WO-054 is not complete. The next dependency-safe implementation action is
WO-055 Render API and PostgreSQL deployment so the frontend can receive the
hosted API URL and complete Netlify deployment verification from a reviewed
source state.
