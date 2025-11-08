### Branch Protection and Review Governance — Proposal

Target: main

Recommended settings
- Require pull request reviews: min approvals = 1
- Dismiss stale approvals on new commits: enabled
- Require review from Code Owners: enabled
- Require status checks to pass: enabled
  - Required checks: CI (lint, typecheck, test, security), Markdown Syntax Check, Codex status (when available)
- Require branches to be up to date before merging: optional (on for stricter gating)
- Allow rebase merges only (no squash), or allow merge+rebase as org preference
- Restrict who can push to matching branches: enabled (allow only maintainers/automation)

CODEOWNERS
- Use team once org is ready: `@<org>/beast`
- Interim individual owner: `@louspringer`

Org/Team
- Create or move to a GitHub Organization
- Create team: `beast` with Write/Maintain on this repo
- Add members: `@louspringer`, Codex reviewer account (or machine user), any maintainers

API commands (gh)
Note: Requires repo admin/sufficient scopes.

```bash
OWNER=<owner>; REPO=<repo>
gh api -X PUT repos/$OWNER/$REPO/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f required_status_checks.strict=true \
  -f required_status_checks.contexts[]='CI' \
  -f required_status_checks.contexts[]='Markdown Syntax Check' \
  -f enforce_admins=true \
  -F required_pull_request_reviews='{"dismiss_stale_reviews":true,"required_approving_review_count":1,"require_code_owner_reviews":true}' \
  -F restrictions='null'
```

Add required checks precisely (if separate jobs):
```bash
gh api -X PUT repos/$OWNER/$REPO/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  -f required_status_checks.strict=true \
  -f required_status_checks.checks[0].context='CI' \
  -f required_status_checks.checks[0].app_id=0 \
  -f required_status_checks.checks[1].context='Markdown Syntax Check' \
  -f required_status_checks.checks[1].app_id=0
```

CODEOWNERS example
```
.kiro/specs/** @<org>/beast
backend/** @<org>/beast
.github/** @<org>/beast
```

Next steps
1) Create org (if not already), create `beast` team, add members.
2) Replace CODEOWNERS entries with `@<org>/beast`.
3) Apply branch protection with required checks and Code Owners.
4) Optionally enable auto-merge (rebase) once checks+review pass.


