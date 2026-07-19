# WO-054 Netlify Frontend Deployment Implementation Report

**Work Order:** [WO-054](../work-orders/054-netlify-frontend-deployment.md)
**Status:** Blocked - Deploy Fix Pending Review
**Date:** 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-054 implementation has started. The Netlify project target exists, public
frontend environment variables are configured, and production deploy attempts
were performed. The hosted site is not healthy yet: it currently returns 502
because the Netlify Next.js server handler imports
`/var/task/apps/web/.netlify/dist/...` files that were not bundled into the
function package.

The source fix in this branch moves Netlify configuration to
`apps/web/netlify.toml`, keeps the official Next.js runtime explicit, removes
the build-time Google Fonts dependency, and adds deterministic
`generateStaticParams` for fixture-backed detail routes. No further production
deploy should be attempted until this source fix is reviewed and merged.

No secret values were created, displayed, written to Git, or configured in
Netlify during this Work Order.

## Scope Implemented

- Added `apps/web/netlify.toml` for the accepted workspace build command and
  Next publish output:
  - build command: `npm run build`
  - publish directory: `.next`
  - official Next.js runtime: `@netlify/plugin-nextjs`
- Ignored local Netlify link metadata with `.netlify/`.
- Created and linked the Netlify site target:
  - site name: `atlas-agent-control-center`
  - site URL: `https://atlas-agent-control-center.netlify.app`
  - admin URL: `https://app.netlify.com/projects/atlas-agent-control-center`
- Configured the non-secret Netlify production build variable
  `NEXT_PUBLIC_APP_ENV=production`.
- Configured the non-secret Netlify production build variable
  `NEXT_PUBLIC_API_BASE_URL=https://atlas-agent-control-center-api.onrender.com`.
- Configured the non-secret Netlify production build variable
  `NEXT_PUBLIC_RELEASE_VERSION=17b5415`.
- Configured the non-secret Netlify function runtime variable
  `AWS_LAMBDA_JS_RUNTIME=nodejs22.x`.
- Configured the non-secret Netlify build variable `NODE_VERSION=22`.

## Explicitly Not Performed

- No secret variables were configured or inspected.
- No Netlify environment-variable listing was captured because that command can
  reveal provider-side values.
- No public launch, release tag, database migration, Gmail/Drive workflow, or
  production-ready claim was performed.

## Provider Evidence

| Check | Result | Side effect |
| --- | --- | --- |
| `netlify sites:create --name atlas-agent-control-center --account-slug vasudevap --filter @atlas/web` | Site created and linked | Netlify site creation |
| `netlify env:set NEXT_PUBLIC_APP_ENV production --context production --scope builds --filter @atlas/web` | Non-secret production build label configured | Netlify environment variable write |
| `netlify env:set NEXT_PUBLIC_API_BASE_URL ... --context production --scope builds --filter @atlas/web` | Public API base URL configured | Netlify environment variable write |
| `netlify env:set NEXT_PUBLIC_RELEASE_VERSION 17b5415 --context production --scope builds --filter @atlas/web` | Public release label configured | Netlify environment variable write |
| `netlify env:set AWS_LAMBDA_JS_RUNTIME nodejs22.x --context production --scope functions --filter @atlas/web` | Public runtime selector configured | Netlify environment variable write |
| `netlify env:set NODE_VERSION 22 --context production --scope builds --filter @atlas/web` | Public build runtime selector configured | Netlify environment variable write |
| `netlify status` from `apps/web` | Linked site reports `atlas-agent-control-center` and app-local `netlify.toml` | Read-only |
| `curl -s -I https://atlas-agent-control-center.netlify.app` | Current hosted site returns HTTP 502 | Read-only |

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
Next.js 16.2.10 compiled successfully under elevated local execution after
removing the Google Fonts build-time dependency
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

WO-054 requires hosted dashboard render and runtime-health evidence. The
Netlify production URL currently returns 502. Function logs and forced rebuild
output point to a server-handler packaging path issue:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/var/task/apps/web/.netlify/dist/run/handlers/request-context.cjs'
```

The source fix is ready for review in this branch, but it must be merged before
the next production deploy attempt.

## Completion State

WO-054 is not complete. The next dependency-safe implementation action is to
merge the Netlify packaging fix, redeploy the frontend from reviewed `main`,
and then verify hosted dashboard render plus runtime-health evidence.
