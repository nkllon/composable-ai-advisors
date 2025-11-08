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


