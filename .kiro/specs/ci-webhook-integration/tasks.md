### CI Webhook Integration — Tasks

Status legend: [ ] pending, [x] complete

1. Webhook endpoint and verification
   - [ ] Add router `backend/webhooks/github.py` with POST `/webhooks/github`
   - [ ] Implement HMAC SHA-256 verification (CIW-REQ-002)
   - [ ] Enforce body size limit middleware (CIW-REQ-015)
   - [ ] Deduplicate by `X-GitHub-Delivery` GUID (CIW-REQ-006)

2. Event routing and filtering
   - [ ] Handlers for `workflow_run`, `check_suite`, `check_run`, `pull_request`, `status` (CIW-REQ-003)
   - [ ] Filter by repo/branch/workflow via env (CIW-REQ-005, CIW-REQ-009)
   - [ ] Dry-run mode (no Slack send) (CIW-REQ-016)

3. Notifications
   - [ ] Slack integration via `SLACK_WEBHOOK_URL` (CIW-REQ-004)
   - [ ] Retry with backoff on failures (CIW-REQ-007)
   - [ ] Redact sensitive fields in logs (CIW-REQ-013)

4. Persistence and metrics
   - [ ] SQLite/file ledger for deliveries (CIW-REQ-008)
   - [ ] `/webhooks/github/health` and `/webhooks/github/metrics` (CIW-REQ-010)

5. Configuration and docs
   - [ ] Env vars: `ENABLE_WEBHOOKS`, `GITHUB_WEBHOOK_SECRET`, `SLACK_WEBHOOK_URL`, `ALLOWED_BRANCHES`, `ALLOWED_REPOS`, `LEDGER_BACKEND`, `LEDGER_LIMIT` (CIW-REQ-009)
   - [ ] GitHub configuration docs (events, secret, content type) (CIW-REQ-011)
   - [ ] Local testing docs with `ngrok`/`cloudflared` (CIW-REQ-017)

6. Tests
   - [ ] Fixtures for each event type (CIW-REQ-012)
   - [ ] Unit tests: signature, routing, filters, retry, dedupe, metrics (CIW-REQ-012)

7. Deployment
   - [ ] Cloud Run path exposure confirmation and secret configuration (CIW-REQ-014)


