### CI Webhook Integration — Requirements

ID prefix: CIW-REQ-###

- CIW-REQ-001: Provide an HTTP endpoint to receive GitHub webhooks.
- CIW-REQ-002: Verify webhook authenticity using HMAC (X-Hub-Signature-256).
- CIW-REQ-003: Support events: workflow_run, check_suite, check_run, pull_request, status.
- CIW-REQ-004: Emit real-time notifications to a configured sink (Slack webhook URL).
- CIW-REQ-005: Allow filtering by repo, branch patterns, PR number, and workflows.
- CIW-REQ-006: Provide idempotency and safe reprocessing (dedupe by delivery GUID).
- CIW-REQ-007: Provide retry/backoff on downstream notification failures.
- CIW-REQ-008: Persist a minimal event ledger for the last N deliveries (configurable).
- CIW-REQ-009: Config via environment: GITHUB_WEBHOOK_SECRET, SLACK_WEBHOOK_URL, ALLOWED_BRANCHES, ALLOWED_REPOS, ENABLE_WEBHOOKS.
- CIW-REQ-010: Expose a health endpoint and a basic metrics endpoint for deliveries and failures.
- CIW-REQ-011: Document GitHub-side configuration (events enabled, secret, content type).
- CIW-REQ-012: Provide unit tests with recorded payload fixtures for each supported event.
- CIW-REQ-013: Respect privacy: do not log entire payloads; log event IDs and safe fields only.
- CIW-REQ-014: Support Cloud Run deployment behind HTTPS; tolerate Cloudflare forwarding headers.
- CIW-REQ-015: Enforce request size limits and reject over-sized payloads gracefully.
- CIW-REQ-016: Provide dry-run mode to validate signature and routing without posting notifications.
- CIW-REQ-017: Provide minimal docs for local testing with `ngrok` or `cloudflared`.


