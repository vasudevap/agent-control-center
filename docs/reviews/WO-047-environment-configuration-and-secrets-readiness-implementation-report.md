# WO-047 Environment Configuration and Secrets Readiness Implementation Report

**Work Order:** [WO-047](../work-orders/047-environment-configuration-and-secrets-readiness.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing ADP:** [ADP-004](../implementation-plans/ADP-004-phase-7-operational-mvp-release.md)

## Summary

WO-047 adds the release-critical configuration and secrets readiness boundary
for Phase 7 without creating live credentials, provisioning provider resources,
or changing the accepted OAuth scope posture.

## Scope Implemented

- Added typed backend settings for Google OAuth client readiness:
  `ATLAS_API_GOOGLE_OAUTH_CLIENT_ID`,
  `ATLAS_API_GOOGLE_OAUTH_CLIENT_SECRET`, and
  `ATLAS_API_GOOGLE_OAUTH_REDIRECT_URI`.
- Expanded production-like readiness checks for `staging` and `production` to
  fail closed until database, owner identity, external-client signing, webhook
  signing, and Google OAuth readiness values are configured.
- Expanded redacted settings evidence to report configured/not-configured
  status for non-secret identifiers and redact all secret values.
- Added a Phase 7 environment configuration and secrets readiness inventory.
- Updated backend documentation with the release-critical configuration link.

## Security and Privacy Evidence

- No real secret values, OAuth tokens, provider credentials, `.env` files, or
  production configuration files were added.
- Readiness problems use stable reason codes only.
- Secret values remain represented as `SecretStr` and redact to `***`.
- Browser-visible `NEXT_PUBLIC_` values are documented as non-secret only.
- Accepted Gmail and Drive scopes remain `gmail.modify` and `drive.file`.

## Validation Commands

Focused configuration validation:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_config.py
```

Result:

```text
10 passed
```

Full backend validation:

```text
apps/api/.venv/bin/python -m pytest apps/api
```

Result:

```text
133 passed, 1 warning
```

Static validation:

```text
apps/api/.venv/bin/python -m ruff check apps/api
apps/api/.venv/bin/python -m mypy apps/api/src
git diff --check
```

Result:

```text
All checks passed
Success: no issues found in 61 source files
git diff --check passed
```

Secret scan:

```text
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\\s*=|refresh_token|access_token|oauth_token|client_secret)" apps/api/src apps/api/tests docs/implementation-plans/phase-7-environment-configuration-and-secrets-readiness.md docs/reviews/WO-047-environment-configuration-and-secrets-readiness-implementation-report.md
```

Result:

```text
Matches are limited to configuration field names, readiness reason codes,
synthetic test placeholder strings, redacted output assertions, and the
pre-existing phrase ask-instead-of-guess. No live credential material was
introduced.
```

## Residual Risks

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Google OAuth settings are readiness fields only | Expected | Later provider cutover Work Order must wire real OAuth exchange behavior |
| No live credentials were created or verified | Expected | Controlled-account or production credential use requires explicit authorization |
| Provider-native secret stores are documented, not provisioned | Expected | WO-048 and WO-050 own deployment/runbook readiness without unauthorized provisioning |

## Completion State

WO-047 is complete. Local validation passed, PR #65 passed required CI, and the
work was merged into `main`.
