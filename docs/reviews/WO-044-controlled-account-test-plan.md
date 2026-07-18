# WO-044 Controlled Account Test Plan

**Status:** Not Executed - Separate Repository Maintainer Authorization Required
**Date:** 2026-07-18
**Work Order:** [WO-044](../work-orders/044-controlled-account-verification-and-mvp-candidate-closeout.md)
**Engineering Specification:** [ES-006](../engineering-specifications/ES-006-gmail-agent-mvp-candidate.md)

## Purpose

This plan defines the only acceptable boundary for a future live controlled
Gmail/Drive verification pass. It was prepared as WO-044 evidence, but no live
controlled-account execution was performed because this session did not receive
separate authorization to use real Google credentials or a live mailbox.

## Authorization Required Before Execution

Before any live controlled-account test begins, the Repository Maintainer must
explicitly authorize:

- the controlled Gmail account identifier;
- the controlled Google Drive account or folder boundary;
- the OAuth client/configuration source;
- the exact test window;
- the person responsible for cleanup verification;
- whether sending a controlled test message is permitted.

Personal mailbox, production mailbox, private beta, production OAuth, and
unbounded live-provider testing remain prohibited.

## Seed Data Set

The controlled account should contain only synthetic messages created for the
test window:

| Message | Purpose | Expected result |
| --- | --- | --- |
| Recruiter-style scheduling message | Ask-instead-of-guess, draft, approval, send continuation | Questions when facts missing; draft after facts; approval required; controlled send only if separately authorized |
| Receipt with one small synthetic attachment | Low-risk label, archive, attachment save | Label/archive/save only if configured policy allows |
| Appointment reminder with no real personal details | Suppression guardrail | Held for manual handling; no question, draft, approval, send, action, or learned fact |

No real medical, financial, employment, personal, or confidential content
should be used.

## Execution Checklist

1. Confirm repository branch and commit SHA under test.
2. Confirm exact Gmail and Drive OAuth scopes:
   - `https://www.googleapis.com/auth/gmail.modify`
   - `https://www.googleapis.com/auth/drive.file`
3. Confirm no `https://mail.google.com/` scope is requested or granted.
4. Run the deterministic fake-provider closeout test suite first.
5. Connect only the authorized controlled Gmail and Drive accounts.
6. Run one manual Gmail Agent pass against the controlled seed data.
7. Verify run status, run steps, pending approvals, manual holds, send outcome,
   webhook payload summaries, and audit metadata through governed API records.
8. Verify no token values, message bodies, attachment bytes, restricted
   content, or uncontrolled provider references appear in logs, webhooks, audit
   metadata, test fixtures, or repository files.
9. Export only minimized evidence: ids, statuses, timestamps, reason codes, and
   hashes where needed.
10. Complete cleanup checklist before closing the evidence record.

## Cleanup Checklist

- Revoke the controlled Gmail connector.
- Revoke the controlled Google Drive connector.
- Remove or quarantine all controlled seed messages.
- Remove controlled Drive artifacts created during the test.
- Confirm webhook attempts contain only minimized payload summaries.
- Confirm no live OAuth tokens or authorization codes were written to the
  repository or local fixtures.
- Record cleanup timestamp and responsible reviewer in the evidence report.

## Current Evidence State

No live controlled-account execution evidence exists for WO-044. The accepted
WO-044 closeout evidence is deterministic fake-provider automation plus this
future controlled-account plan.
