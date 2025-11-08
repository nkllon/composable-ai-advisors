### CI Webhook Integration — Design

Covers: CIW-REQ-001…017

#### Overview
- Component: Webhook listener inside existing FastAPI backend (`/webhooks/github`).
- Verifies GitHub signatures (HMAC SHA-256), routes by event name, posts summarized statuses to Slack.
- Stores minimal ledger (delivery GUID, event name, timestamp, outcome) in a lightweight file or SQLite.

#### Architecture
- FastAPI router `backend/webhooks/github.py`:
  - POST `/webhooks/github`:
    - Read headers: `X-GitHub-Event`, `X-Hub-Signature-256`, `X-GitHub-Delivery`.
    - Bound by body size limit (e.g., 1–2 MB).
    - Verify signature using `GITHUB_WEBHOOK_SECRET`.
    - Deduplicate by delivery GUID (SQLite table `deliveries` keyed by guid).
    - Route to handlers per event type.
  - GET `/webhooks/github/health`: return status, last delivery time, ledger size.
  - GET `/webhooks/github/metrics`: counters for deliveries, failures, dedup hits, Slack posts, retries.

- Event handlers
  - `workflow_run`: summarize workflow name, status/conclusion, URL.
  - `check_suite`, `check_run`: aggregate to key status updates.
  - `pull_request`: for opened, synchronize, closed; include PR number/title/author.
  - `status`: map sha + context to pending/success/failure.

- Filtering and routing
  - Filters via env: `ALLOWED_BRANCHES` (comma-separated globs), `ALLOWED_REPOS` (owner/repo strings).
  - Only deliver Slack messages for matching filters; still record ledger entry.

- Slack integration
  - Post to `SLACK_WEBHOOK_URL` with compact JSON blocks (title, repo/branch, status, URL).
  - Backoff retries (e.g., 3 attempts, exponential backoff starting at 1s).
  - Redact secrets and avoid sending raw payloads.

- Configuration
  - `ENABLE_WEBHOOKS` gate for entire feature.
  - `GITHUB_WEBHOOK_SECRET` required when enabled.
  - `SLACK_WEBHOOK_URL` recommended; when absent, log-only mode.
  - `LEDGER_BACKEND` (file|sqlite), `LEDGER_LIMIT` (default 1000 entries).

- Security and privacy
  - HMAC verification mandatory; reject if missing/invalid signature.
  - Size limit middleware.
  - Log correlation: use delivery GUID + summarized context.
  - Optional IP allowlist (future).

- Deployment
  - Cloud Run: expose `/webhooks/github`; configure GitHub webhook to point to public URL (via Cloudflare tunnel if needed).
  - Content type `application/json` on GitHub side.

#### Data Model (SQLite)
```sql
CREATE TABLE IF NOT EXISTS deliveries (
  guid TEXT PRIMARY KEY,
  event TEXT NOT NULL,
  received_at TEXT NOT NULL,
  repo TEXT,
  ref TEXT,
  workflow TEXT,
  status TEXT,
  conclusion TEXT,
  url TEXT,
  delivered INTEGER NOT NULL DEFAULT 0,
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT
);
```

#### Testing
- Pytest fixtures: sample payloads for each supported event in `backend/tests/webhooks/fixtures/`.
- Unit tests:
  - Signature verification (valid/invalid/missing).
  - Event routing per type.
  - Slack posting success/failure and retry behavior (mock httpx).
  - Deduplication by delivery GUID.
  - Filters applied correctly.

#### Observability
- Metrics counters (in-memory) exported via `/webhooks/github/metrics`.
- Basic histograms (processing time) optional.


