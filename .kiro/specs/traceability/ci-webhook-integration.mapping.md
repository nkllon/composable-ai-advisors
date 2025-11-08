### cc-sdd Mapping — CI Webhook Integration

| Requirement ID | Spec Section | Planned Artifact |
| --- | --- | --- |
| CIW-REQ-001 | requirements.md | backend/webhooks/github.py (POST /webhooks/github) |
| CIW-REQ-002 | requirements.md | HMAC verification in github webhook router |
| CIW-REQ-003 | requirements.md | Event handlers: workflow_run/check_suite/check_run/pull_request/status |
| CIW-REQ-004 | requirements.md | Slack notifier module + env config |
| CIW-REQ-005 | requirements.md | Routing filter logic (repo/branch/workflow) |
| CIW-REQ-006 | requirements.md | Delivery GUID dedupe (SQLite/file ledger) |
| CIW-REQ-007 | requirements.md | Retry/backoff utility for Slack posts |
| CIW-REQ-008 | requirements.md | SQLite/file ledger implementation |
| CIW-REQ-009 | requirements.md | Settings loader for all env vars |
| CIW-REQ-010 | requirements.md | /webhooks/github/health & /webhooks/github/metrics |
| CIW-REQ-011 | requirements.md | Docs in README/DEPLOYMENT (GitHub webhook setup) |
| CIW-REQ-012 | requirements.md | pytest fixtures + tests for events |
| CIW-REQ-013 | requirements.md | Logging policy and redaction helpers |
| CIW-REQ-014 | requirements.md | Cloud Run manifest/notes |
| CIW-REQ-015 | requirements.md | Body size limit middleware |
| CIW-REQ-016 | requirements.md | Dry-run mode switch |
| CIW-REQ-017 | requirements.md | Local testing guide (ngrok/cloudflared) |


