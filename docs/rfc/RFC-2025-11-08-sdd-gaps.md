# RFC: Close SDD Gaps for MCP, CI/CD, and DMF

Date: 2025-11-08
Status: Draft
Owners: SDD (/kiro)

## Summary
This RFC consolidates new and updated requirements identified during CI/test hardening:

### MCP (MCP-REQ-001…006)
- MCP-REQ-001: Env override `MCP_CONFIG_PATH`.
- MCP-REQ-002: Env override `MCP_DOMAIN_MODELS_DIR`.
- MCP-REQ-003: Use FastAPI lifespan instead of `@on_event("startup")`.
- MCP-REQ-004: Test-friendly preload (disable/control via config/env).
- MCP-REQ-005: Resolve defaults from repo-root (no CWD reliance).
- MCP-REQ-006: Avoid hidden prod fallbacks; use explicit fixtures for tests.

### CI/CD (CI-REQ-010…014)
- CI-REQ-010: Single authoritative `.markdownlint.yml`.
- CI-REQ-011: Exclude generator/internal paths from markdown checks.
- CI-REQ-012: Prefer one markdown linter in CI unless rules harmonized.
- CI-REQ-013: Use path filters to scope jobs by file changes.
- CI-REQ-014: Isolate dev deps (e.g., `requirements-dev.txt`) for CI.

### DMF (DMF-REQ-010…012)
- DMF-REQ-010: Resolve default base_dir from repo-root.
- DMF-REQ-011: Support tests via explicit fixtures; no repo-global dependence.
- DMF-REQ-012: Deterministic preload/registry control in tests.

## Acceptance Criteria
- Code implements env overrides and root resolution; lifespan replaces startup hooks.
- Tests can run with explicit fixture configs; CI is green using dev deps.
- Markdown checks are stable and signal only on meaningful doc changes.

## Rollout Plan
1) Land SDD spec updates (done).
2) Implement minimal code support (lifespan + env overrides + dev deps).
3) Update CI to install `requirements-dev.txt` for typecheck/tests.
4) Remove/guard any prod-only fallbacks and rely on test fixtures.


