### Composable AI Advisors — Backlog

Status buckets: Now / Next / Later / Icebox

#### Now
- Governance: Create `nkllon/beast` team; update CODEOWNERS to `@nkllon/beast`; apply branch protection (require 1 approval, Code Owners, CI checks).
- CI Webhook: Implement webhook listener per spec (CIW-REQ-001..017) with Slack notifications.

#### Next
- MCP: Backlog adapter design and implementation (expose backlog via MCP; add read/write endpoints and shapes).
- Ops: Add CODEOWNERS coverage for frontend and ontology paths after team creation.
- Observability: Slack routing by repo/branch, and minimal delivery ledger persistence.

#### Later
- Projects: Optional GitHub Project board mirroring docs/backlog; automation to sync closed items.
- Security: Optional IP allowlist for GitHub webhook source ranges.
- Analytics: Prometheus metrics export and Grafana dashboard for CI events.

#### Icebox
- Multi-org strategy: separate private org for non-public work; migration guide and scripts.
- Bot reviewers: evaluate machine user policy; keep human approval required.

Notes
- Source of truth for backlog is this file; open an issue per item when work begins.
- Keep items atomic and reference requirement IDs where applicable (e.g., CIW-REQ-###).


