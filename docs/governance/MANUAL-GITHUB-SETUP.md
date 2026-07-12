# Manual GitHub Main-Branch Protection Setup

## Verified limitation

On 2026-07-12, GitHub returned HTTP 403 for both the classic branch-protection endpoint and repository-rulesets endpoint for `vasudevap/agent-control-center`:

> Upgrade to GitHub Pro or make this repository public to enable this feature.

The repository is private on a plan that does not currently provide these controls. Do not make the repository public solely to enable protection without a separate privacy decision. ES-001 remains implemented; this document is the required equivalent setup record until the repository plan or visibility changes.

## Prerequisite

Choose one through a separate owner decision:

1. Upgrade the repository owner to a GitHub plan that supports protected branches/rulesets for private repositories; or
2. Make the repository public only if its contents and intended portfolio visibility have been reviewed and approved.

## Preferred ruleset

After the prerequisite is satisfied:

1. Open **Repository settings → Rules → Rulesets**.
2. Create a branch ruleset named `Protect main` and set enforcement to **Active**.
3. Target the default branch, `main`.
4. Enable restriction of branch deletion.
5. Enable restriction of force pushes/non-fast-forward updates.
6. Require a pull request before merging.
7. Set required approvals to **0** for this single-maintainer repository.
8. Do not require code-owner approval unless ownership rules are added later.
9. Require status checks to pass and select the GitHub Actions check named **Validate** from workflow **CI**.
10. Require branches to be up to date before merging.
11. Do not add a bypass actor for routine maintainer changes; apply the rules to administrators where the selected GitHub plan supports that control without creating a lockout.
12. Allow merge commits. Squash may remain available for small atomic maintenance changes; do not require rebase merging.
13. Save the ruleset.

## Classic branch-protection fallback

If rulesets remain unavailable but classic protection becomes available, open **Repository settings → Branches → Add branch protection rule**, use pattern `main`, require pull requests, require the **Validate** status check with strict/up-to-date branches, include administrators where safe, and disallow force pushes and deletion. Keep required approvals at zero.

## Verification

Query one of the following after configuration:

```bash
gh api repos/vasudevap/agent-control-center/rulesets
gh api repos/vasudevap/agent-control-center/branches/main/protection
```

Confirm the returned configuration targets `main`, requires `Validate`, requires a pull request, requires current branches, blocks force pushes and deletion, and does not require an impossible reviewer count. Record the result in the next governance review or release report.
