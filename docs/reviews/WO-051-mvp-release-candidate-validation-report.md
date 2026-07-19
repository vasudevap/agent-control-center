# WO-051 MVP Release Candidate Validation Report

**Work Order:** [WO-051](../work-orders/051-mvp-release-candidate-validation.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing ADP:** [ADP-004](../implementation-plans/ADP-004-phase-7-operational-mvp-release.md)

## Summary

WO-051 validates the Operational MVP release candidate across local backend,
frontend, migration, security/privacy, dashboard, fake-provider Gmail, and
authorized controlled Gmail/Drive evidence.

This validation does not approve production release, create a release tag,
deploy production infrastructure, or accept residual risk. Those decisions
remain WO-052 maintainer authority.

## Release Candidate Evidence

| Area | Evidence | Result |
| --- | --- | --- |
| Backend tests | `apps/api/.venv/bin/python -m pytest apps/api` | 136 passed, 1 warning |
| Backend lint | `apps/api/.venv/bin/python -m ruff check apps/api` | Passed |
| Backend typing | `apps/api/.venv/bin/python -m mypy apps/api/src` | Passed |
| Frontend focused dashboard test | `npm test -- runtime-health-indicator` | 1 file passed, 4 tests passed |
| Frontend full tests | `npm test` | 19 files passed, 88 tests passed |
| Frontend typecheck | `npm run typecheck` | Passed |
| Frontend lint | `npm run lint` | Passed |
| Frontend build | `npm run build` | Passed; 13 routes generated |
| Migration head | `ATLAS_API_DATABASE_URL=sqlite:////private/tmp/atlas-wo051-migration.db ./.venv/bin/alembic upgrade head && ... current` from `apps/api` | `0017_gmail_send_outcomes (head)` |
| Whitespace | `git diff --check` | Passed |
| GitHub CI | PR #65 through PR #71 | Required `Validate` checks passed and merged |

## Gmail Fake-Provider Evidence

The full Gmail fake-provider and contract baseline passed as part of the full
backend suite and was also revalidated during WO-045:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_gmail_messages.py apps/api/tests/test_gmail_actions.py apps/api/tests/test_gmail_knowledge.py apps/api/tests/test_gmail_drafts.py apps/api/tests/test_gmail_approvals.py apps/api/tests/test_gmail_operational.py apps/api/tests/test_gmail_mvp_candidate_closeout.py apps/api/tests/test_connectors.py
```

Result:

```text
46 passed, 1 warning
```

This covers fake-provider OAuth boundaries, exact Gmail/Drive scope posture,
message eligibility, suppression, low-risk actions, ask-instead-of-guess,
draft generation, facts-used evidence, approval gates, send outcomes, audit,
webhook minimization, and operational reconciliation.

## Controlled Account Evidence

WO-045 executed authorized controlled Gmail and Google Drive connector evidence
for `grafleyinc@gmail.com` and cleaned up provider artifacts.

Controlled evidence included:

- Gmail and Drive profiles both resolving to `grafleyinc@gmail.com`;
- one synthetic Gmail self-send with marker
  `ATLAS-WO045-20260718T233456Z`;
- synthetic attachment metadata and attachment retrieval through the Gmail
  connector;
- temporary Drive folder creation and synthetic file upload;
- deletion of the synthetic Drive file and folder;
- Gmail seed message moved to Trash;
- active-mail marker search returning no messages outside Trash.

No real mailbox content, production mailbox, production OAuth client, raw
attachment bytes, OAuth tokens, provider secrets, or message bodies were added
to source or fixtures.

## Dashboard Evidence

Local dashboard smoke validation:

```text
npm run dev
Chrome: http://localhost:3000/
```

Result:

- page title rendered as `Atlas - Agent Control Center`;
- shell navigation rendered `Runs`, `Approvals`, and `Connectors`;
- status bar rendered `Runtime not configured`, the expected state for a local
  dashboard build without `NEXT_PUBLIC_API_BASE_URL`;
- local request returned `GET / 200`.

A Chrome extension emitted an unrelated console error while injecting its own
script. The dashboard itself rendered successfully.

## Security and Privacy Scan

Secret-pattern scan:

```text
rg -n "(sk-[A-Za-z0-9]|OPENAI_API_KEY|ANTHROPIC_API_KEY|GOOGLE_CLIENT_SECRET|NOTION_TOKEN|ntn_|BEGIN PRIVATE KEY|password\\s*=|refresh_token|access_token|oauth_token|client_secret|download_url|gho_)" apps docs --glob '!docs/reviews/WO-045-controlled-account-release-verification-report.md'
```

Result:

- no live secret material found;
- matches are documented command examples, source/test configuration field
  names, synthetic placeholders, redaction tests, and the phrase
  `ask-instead-of-guess`.

## Known Issues and Residual Risks

| Item | Disposition | Next authority |
| --- | --- | --- |
| Atlas runtime did not execute a full production Gmail Agent run against live provider credentials | Known residual risk | WO-052 maintainer release decision or a narrow live-runtime Work Order |
| Local dashboard smoke used `Runtime not configured` because no hosted API URL was provided | Expected for local evidence | Deployment authority and hosted environment configuration |
| Controlled Gmail seed remains recoverable in Trash rather than permanently deleted | Accepted cleanup posture | Maintainer may manually empty Trash after review |
| Production deployment, release tag, public launch, and residual-risk acceptance are not performed | Required boundary | WO-052 |

## Recommendation

The Operational MVP release candidate is ready for WO-052 maintainer acceptance
review with the residual risks above disclosed. This report does not authorize
production deployment or release tagging.
