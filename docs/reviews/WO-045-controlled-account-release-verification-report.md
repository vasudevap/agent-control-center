# WO-045 Controlled-Account Release Verification Report

**Work Order:** [WO-045](../work-orders/045-controlled-account-release-verification.md)
**Status:** Completed - Merged
**Date:** 2026-07-18
**Engineering Specification:** [ES-007](../engineering-specifications/ES-007-operational-mvp-release-readiness.md)
**Governing ADP:** [ADP-004](../implementation-plans/ADP-004-phase-7-operational-mvp-release.md)
**Controlled Account Plan:** [WO-044 Controlled Account Test Plan](./WO-044-controlled-account-test-plan.md)

## Summary

WO-045 revalidated the deterministic fake-provider Gmail Agent baseline,
executed the authorized controlled Gmail and Google Drive connector evidence,
and cleaned up the synthetic provider artifacts.

No personal mailbox, production mailbox, production OAuth client, live webhook
receiver, production deployment, unrestricted mailbox scan, real message body,
or non-synthetic provider content was used.

## Scope Completed

- Reviewed the WO-044 controlled-account authorization boundary, seed data, and
  cleanup checklist.
- Reran the Gmail MVP candidate closeout and operational fake-provider tests.
- Reran the broader Gmail backend fake-provider contract suite.
- Confirmed the accepted Gmail and Drive scopes remain bounded to
  `gmail.modify` and `drive.file` evidence.
- Verified Gmail and Google Drive connector profiles both resolved to
  `grafleyinc@gmail.com`.
- Sent one synthetic Gmail self-test message with a small synthetic attachment.
- Retrieved the synthetic attachment through the Gmail connector.
- Created a temporary Google Drive folder and uploaded the synthetic attachment
  artifact.
- Deleted the synthetic Drive file and temporary Drive folder.
- Moved the synthetic Gmail seed message to Trash and verified the marker no
  longer appeared outside Trash.

## Validation Commands

Focused WO-045 baseline:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_gmail_mvp_candidate_closeout.py apps/api/tests/test_gmail_operational.py
```

Result:

```text
8 passed
```

Gmail fake-provider contract baseline:

```text
apps/api/.venv/bin/python -m pytest apps/api/tests/test_gmail_messages.py apps/api/tests/test_gmail_actions.py apps/api/tests/test_gmail_knowledge.py apps/api/tests/test_gmail_drafts.py apps/api/tests/test_gmail_approvals.py apps/api/tests/test_gmail_operational.py apps/api/tests/test_gmail_mvp_candidate_closeout.py apps/api/tests/test_connectors.py
```

Result:

```text
46 passed, 1 warning
```

## Controlled Account Authorization

The Repository Maintainer authorized the controlled test on 2026-07-18:

```text
Authorized: use grafleyinc@gmail.com and its Drive now; synthetic messages/files only; self-send permitted; cleanup verifier is me.
```

## Controlled Provider Evidence

| Evidence item | Result |
| --- | --- |
| Gmail profile | `grafleyinc@gmail.com` |
| Google Drive profile | `grafleyinc@gmail.com` |
| Synthetic marker | `ATLAS-WO045-20260718T233456Z` |
| Gmail self-send | Created message/thread `19f7795bfae4665c` with `INBOX`, `SENT`, and `UNREAD` labels |
| Gmail marker search | Returned only message `19f7795bfae4665c` |
| Gmail attachment metadata | `atlas-wo045-20260718T233456Z.txt`, `text/plain`, 162 bytes |
| Gmail attachment retrieval | Succeeded through the Gmail connector |
| Drive temporary folder | Created `11fAEAYBaY4lKA8ctvdyFp-JJBn6hzJBR` under root |
| Drive synthetic upload | Created file `1fZ36D2MxmhczORbq-tb15ZoiIw77bZgH` in the temporary folder |
| Drive file cleanup | Deleted file `1fZ36D2MxmhczORbq-tb15ZoiIw77bZgH` |
| Drive folder cleanup | Deleted folder `11fAEAYBaY4lKA8ctvdyFp-JJBn6hzJBR` |
| Gmail seed cleanup | Moved message `19f7795bfae4665c` to Trash |
| Gmail active-mail cleanup check | Marker search with `-in:trash` returned no messages |
| Gmail quarantine check | Marker search with `in:trash` returned message `19f7795bfae4665c` |

## Security and Privacy Evidence

- Gmail and Google Drive connectors were used only with the authorized
  `grafleyinc@gmail.com` account.
- No OAuth authorization code, access token, refresh token, provider secret,
  raw attachment bytes, or message body was added to source or fixtures.
- The only live Gmail content accessed was the synthetic marker message created
  during this controlled test window.
- The only live Drive content created was the temporary synthetic folder and
  uploaded synthetic attachment artifact; both were deleted.
- Fake-provider tests continue to cover suppression, ask-instead-of-guess,
  draft generation, approval gates, send outcomes, audit, and minimized
  webhook payloads.
- Controlled-account cleanup requirements remain documented in the WO-044
  controlled-account plan.

## Residual Risks

| Risk / deferred item | Status | Next authority |
| --- | --- | --- |
| Atlas runtime did not execute a full production Gmail Agent run against live provider credentials | Accepted by WO-052 | Narrow live-runtime Work Order before claiming unattended production operation |
| Gmail seed message remains recoverable in Trash rather than permanently deleted | Accepted cleanup posture | Maintainer may manually empty Trash after review if desired |
| Browser/dashboard evidence for this live connector pass was not captured | Covered by WO-051 local dashboard smoke | Future hosted dashboard evidence requires deployment authority |

## Completion State

WO-045 controlled Gmail and Google Drive evidence is complete with provider
cleanup performed. PR #71 passed required CI and was merged.
