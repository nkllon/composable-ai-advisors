# cc-sdd Mapping — cicd-pipeline

## Task → Requirement IDs
- 1. Validate Cloud Build Configurations → 1, 2, 4, 6, 9
- 2. Verify Deployment Script Paths → 3, 6, 10
- 3. Secret Management Verification → 7
- 4. Region/Platform Consistency → 9
- 5. Documentation Check → 10
- 6. Optional Enhancements (Future)
  - 6.1 Add backend unit tests to Cloud Build (pre-deploy) → 5.1, 5.3
  - Triggers, promotions, Artifact Registry, manifests/IaC, metrics/alerts, smoke tests, blue/green, build cache → quality and ops (non-functional)

## New Mapping
- Markdown policy and CI signal → CI-REQ-010, CI-REQ-011, CI-REQ-012
- Path filters for CI efficiency → CI-REQ-013
- Dev dependency isolation → CI-REQ-014
- Local pre-commit markdown checks → CI-REQ-015
- Canonical Makefile targets → CI-REQ-016
- Concurrency/cancellation → CI-REQ-017
- Actions pinned to SHAs → CI-REQ-018
- Caching strategy → CI-REQ-019
- Coverage threshold → CI-REQ-020
- Trivy/Syft scans → CI-REQ-021
- Gitleaks secret scanning → CI-REQ-022
- Token permissions hardening → CI-REQ-023
- Labeler/PR hygiene → CI-REQ-024
- Dependabot/Renovate → CI-REQ-025
- Post-deploy smoke tests → CI-REQ-026
- Environment policies → CI-REQ-027
- Provenance/signing → CI-REQ-028

## File-Level Change → Requirement IDs
- .github/workflows/ci.yml (concurrency, permissions, cache, coverage) → CI-REQ-017, CI-REQ-019, CI-REQ-020, CI-REQ-023
- .github/workflows/markdown-syntax.yml (concurrency, permissions) → CI-REQ-017, CI-REQ-023
- .github/workflows/security-scan.yml (Trivy/Syft) → CI-REQ-021
- .github/workflows/secret-scan.yml (gitleaks) → CI-REQ-022
- .github/workflows/labeler.yml + .github/labeler.yml → CI-REQ-024
- .github/dependabot.yml → CI-REQ-025
- docs/tooling/actions-pinning.md → CI-REQ-018
- docs/ops/environments.md → CI-REQ-027
- docs/security/provenance-and-signing.md → CI-REQ-028

## Artifacts
- `.pre-commit-config.yaml` → CI-REQ-015
- `docs/tooling/pre-commit.md` → CI-REQ-015
- `Makefile` → CI-REQ-016
- `.github/workflows/*.yml (concurrency, permissions)` → CI-REQ-017, CI-REQ-023
- `actions pinned SHAs in workflows` → CI-REQ-018
- `actions/cache` blocks in CI → CI-REQ-019
- `pytest-cov config and threshold` → CI-REQ-020
- `Trivy/Syft steps` → CI-REQ-021
- `gitleaks step/config` → CI-REQ-022
- `.github/labeler.yml` + workflow → CI-REQ-024
- `.github/dependabot.yml` → CI-REQ-025
- `Smoke test script/step` → CI-REQ-026
- `Protected environments/approvals` → CI-REQ-027
- `cosign + OIDC configuration` → CI-REQ-028


