# WO-054 Netlify Frontend Deployment Implementation Report

**Work Order:** [WO-054](../work-orders/054-netlify-frontend-deployment.md)
**Status:** Blocked - Netlify Deploy Packaging and CI Linkage
**Date:** 2026-07-19
**Engineering Specification:** [ES-008](../engineering-specifications/ES-008-hosted-mvp-production-cutover.md)
**Governing ADP:** [ADP-005](../implementation-plans/ADP-005-hosted-mvp-production-cutover.md)

## Summary

WO-054 implementation has started. The Netlify project target exists, public
frontend environment variables are configured, and production deploy attempts
were performed. The hosted site is not healthy yet. The first failing
production deploy returned 502 because the Netlify Next.js server handler
imported `/var/task/apps/web/.netlify/dist/...` files that were not bundled into
the function package. A later manual deploy of adapter artifacts went live but
returned Netlify's default 404 because the OpenNext output uses generated route
metadata and blob-backed content, not only flat static files.

The merged source fix uses a root `netlify.toml` with `base = "apps/web"` and
`publish = ".next"` because the linked Netlify CI build resolves `publish`
relative to the configured base directory. It also keeps the official Next.js
runtime explicit, removes the build-time Google Fonts dependency, and adds
deterministic `generateStaticParams` for fixture-backed detail routes.

No secret values were created, displayed, written to Git, or configured in
Netlify during this Work Order.

## Scope Implemented

- Added root `netlify.toml` for the accepted monorepo build command and Next
  publish output:
  - base directory: `apps/web`
  - build command: `npm run build`
  - publish directory: `.next` relative to `apps/web`
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
| `netlify build --dry --filter @atlas/web --debug` | Resolved current directory `apps/web`, config `netlify.toml`, publish `apps/web/.next`, and Next runtime bundling stages | Read-only |
| `netlify build --filter @atlas/web --debug` | Completed successfully and bundled the Next.js server handler plus edge functions | Local build output generated |
| `netlify deploy --prod --build --filter @atlas/web ...` | Failed during function bundling because the local CLI doubled the generated internal function path to `apps/web/apps/web/.netlify/...` | No production deploy |
| `netlify deploy --prod --build --context production ...` from `apps/web` | Failed during post-build publish because the local CLI doubled the publish path to `apps/web/apps/web/.next` | No production deploy |
| `netlify deploy --trigger ...` and `netlify api createSiteBuild ...` | Remote provider build could not be triggered because the manually created Netlify site is not connected to CI build settings | No production deploy |
| Netlify CI deploy from linked Git repository at `main@9dcae7e` | Failed because the checked-in publish path resolved to `/opt/build/repo/apps/web/apps/web/.next`; provider CI treats `publish` as relative to `base = apps/web` | No production deploy |
| `curl -s -i https://atlas-agent-control-center.netlify.app` | Current hosted site returns HTTP 404 after the manual artifact deploy | Read-only |

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
Netlify production URL currently returns 404 after a manual artifact deploy.
The first failing deploy returned 502, and function logs plus forced rebuild
output pointed to a server-handler packaging path issue:

```text
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '/var/task/apps/web/.netlify/dist/run/handlers/request-context.cjs'
```

PR #78 merged the initial base/publish source fix and local `netlify build`
completed, but the first linked Netlify CI deploy showed that provider CI
resolves `publish` relative to `base = apps/web`. The source configuration now
sets `publish = ".next"` to match that provider behavior.

## Completion State

WO-054 is not complete. The next dependency-safe implementation action is to
merge the corrected Netlify publish path, redeploy the frontend from reviewed
`main`, and then verify hosted dashboard render plus runtime-health evidence.

## Verification - 2026-07-19 (repository-side readiness re-check)

An independent repository-side re-check captured the current deploy
configuration and the subsequent linked CI deploy proved one source change is
required:

- `apps/web/next.config.ts` uses the default Next.js server build and pins the
  Turbopack workspace root to the repository root. `@netlify/plugin-nextjs`
  (`^5.15.12`) is declared and referenced by the root `netlify.toml`.
- The root `netlify.toml` keeps `base = apps/web`, `command = npm run build`,
  and the official Next runtime plugin, but `publish` must be `.next` because
  the provider CI build resolves it relative to `apps/web`.
- Live check: the production URL still returns HTTP 404 (site exists; no healthy
  deploy yet), matching the recorded blocker.

Re-link note for the CI step: this working copy is not linked to the Netlify
site (link metadata is gitignored), so the GitHub/CI linkage step must be
performed against the Netlify account/team that owns the
`atlas-agent-control-center` site (created under account slug `vasudevap`).
