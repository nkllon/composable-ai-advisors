# Implementation Plan

- [x] 1. Validate Cloud Build Configurations
  - Confirm `scripts/cloudbuild-backend.yaml` builds/pushes/deploys backend as specified.
  - Confirm `scripts/cloudbuild-frontend.yaml` builds with `_BACKEND_URL` substitution and deploys frontend.
  - _Requirements: 1, 2, 4, 6, 9_

- [x] 2. Verify Deployment Script Paths
  - Ensure `scripts/deploy.sh` references Cloud Build configs in `scripts/` directory when called from subdirs.
  - Validate retrieval of backend URL and propagation to `_BACKEND_URL`.
  - _Requirements: 3, 6, 10_

- [x] 3. Secret Management Verification
  - Verify `GEMINI_API_KEY` is not built into images.
  - Validate secret configuration steps via Secret Manager and Cloud Run update commands.
  - _Requirements: 7_

- [x] 4. Region/Platform Consistency
  - Check both services deploy to `us-central1` and `managed` platform.
  - _Requirements: 9_

- [x] 5. Documentation Check
  - Ensure DEPLOYMENT.md steps match implemented pipeline and include substitution note for `_BACKEND_URL`.
  - _Requirements: 10_

- [ ]* 6. Optional Enhancements (Future)
  - [ ] 6.1 Add backend unit tests to Cloud Build (pre-deploy)
    - Insert a pytest step before Docker build/push in `scripts/cloudbuild-backend.yaml`
    - Gate deploy on green tests; surface junit output in build logs
    - _Requirements: 5.1, 5.3 (determinism), quality gate_
  - Add Cloud Build triggers (on branch/tag) and environment promotions.
    - Configure GitHub trigger for pushes to `main` (deploy to dev)
    - Configure tag-based trigger `v*` (deploy to prod)
    - Add manual approval step between stages
  - Migrate to Artifact Registry.
    - Create AR repositories for backend and frontend
    - Update image names and permissions in Cloud Build configs
  - Use service manifests or infra-as-code to unify scaling/env vars across environments.
    - Author Cloud Run service YAMLs for backend/frontend with consistent env, secrets, scaling
    - Optionally manage via Terraform
  - Integrate Prometheus metrics/alerts for build and deploy events.
    - Export build/deploy metrics to Cloud Monitoring
    - Add alerts for build failures and error rates
  - Add smoke tests post-deploy (health checks and basic API calls).
    - Hit `/health`, `/api/pods` and assert 200 in a post-deploy step
    - Fail pipeline on non-2xx responses
  - Implement blue/green or traffic-splitting deployments.
    - Use `--traffic` flags to gradually shift traffic on successful health checks
  - Optimize Docker builds and cache usage.
    - Pin base image digests and leverage build cache for `npm install`/`pip install`
  - _Requirements: Design/Enhancements_

7. Local Pre-commit Checks
- [x] Add `.pre-commit-config.yaml` with `markdownlint` hook mirroring CI config
- [x] Add setup guide `docs/tooling/pre-commit.md` for developer workflow
- _Requirements: CI-REQ-015_

8. Canonical Makefile
- [x] Add `Makefile` with targets: setup, lint, typecheck, test, markdown, pre-commit-install, ci, run-backend
- [x] Ensure markdown target uses `.markdownlint.yml`
- _Requirements: CI-REQ-016_

9. Concurrency and Cancellation
 - [ ] Add `concurrency` blocks to CI and markdown workflows
   - Edit `.github/workflows/ci.yml` and `.github/workflows/markdown-syntax.yml`
   - Use `group: ${{ github.workflow }}-${{ github.ref }}` and `cancel-in-progress: true`
 - _Requirements: CI-REQ-017_

10. Actions Pinning
 - [ ] Pin all Actions to commit SHAs and document policy
   - Replace `@vX` tags with commit SHAs across all `uses:` steps
   - Add `docs/tooling/actions-pinning.md` with refresh policy
 - _Requirements: CI-REQ-018_

11. Caching
 - [ ] Add actions/cache for uv/python dependencies and test caches (if useful)
   - Cache key: `${{ runner.os }}-py-${{ matrix.python-version }}-uv-${{ hashFiles('**/requirements*.txt') }}`
   - Add restore-keys for partial matches
 - _Requirements: CI-REQ-019_

12. Coverage
 - [ ] Enable pytest-cov, produce coverage.xml, enforce `--cov-fail-under=70`
   - Command: `pytest --maxfail=1 -q --cov=backend --cov-report=xml:coverage.xml --cov-fail-under=70`
   - Upload `coverage.xml` artifact
 - _Requirements: CI-REQ-020_

13. Security and SBOM
 - [ ] Add Trivy scanning (fs/image) with fail on high/critical
   - File: `.github/workflows/security-scan.yml`
   - Step: `trivy fs --exit-code 1 --severity HIGH,CRITICAL .`
 - [ ] Generate SBOM via Syft and upload
   - Step: `syft packages dir:. -o spdx-json > sbom.spdx.json`
   - Upload artifact
 - _Requirements: CI-REQ-021_

14. Secret Scanning
 - [ ] Add gitleaks step with repo allowlist where necessary
   - File: `.github/workflows/secret-scan.yml`
   - Optional config: `.gitleaks.toml` (curated allowlist)
 - _Requirements: CI-REQ-022_

15. Token Permissions
 - [ ] Add job-level `permissions` blocks (least privilege)
   - Top-level `permissions: contents: read` and job-level overrides only as needed
 - _Requirements: CI-REQ-023_

16. PR Hygiene
 - [ ] Add `.github/labeler.yml` and auto-label workflow
   - Workflow: `.github/workflows/labeler.yml`
   - Patterns: `backend/**`, `frontend/**`, `docs/**`, `.github/**`, `scripts/**`
 - _Requirements: CI-REQ-024_

17. Dependency Automation
 - [ ] Add `.github/dependabot.yml` (or Renovate) for Actions/Python
   - Ecosystems: `github-actions` (/.github/workflows), `pip` (/backend)
   - Schedule: `weekly`
 - _Requirements: CI-REQ-025_

18. Post-Deploy Smoke
 - [ ] Add smoke test step after deploy with clear assertions
   - Option A: Cloud Build post-deploy curl checks
   - Option B: GitHub job with `gcloud` resolving Cloud Run URLs and hitting `/health` + one core endpoint
 - _Requirements: CI-REQ-026_

19. Environment Policies
 - [ ] Document/configure protected environments or Cloud Build approvals
   - Docs: `docs/ops/environments.md` with approvers and promotion rules
   - Configure GitHub protected environments or Cloud Build approval step
 - _Requirements: CI-REQ-027_

20. Provenance and Signing
 - [ ] Configure OIDC to GCP and cosign; document verification policy
   - Configure GitHub→GCP OIDC; add `id-token: write` where needed
   - Sign images via `cosign`; verify before deploy
   - Docs: `docs/security/provenance-and-signing.md`
 - _Requirements: CI-REQ-028_


