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

## Artifacts
- `.pre-commit-config.yaml` → CI-REQ-015
- `docs/tooling/pre-commit.md` → CI-REQ-015


