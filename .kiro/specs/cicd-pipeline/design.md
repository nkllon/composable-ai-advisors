# CI/CD Pipeline — Design Addendum

Relates to: CI-REQ-010…CI-REQ-014
; CI-REQ-015

1. Markdown Lint
   - Keep `.github/workflows/markdown-syntax.yml` using `markdownlint-cli`.
   - Configure `.markdownlint.yml` in repo-root for spec style.
   - Exclude `.cursor/commands/**` during changed-files evaluation and loop execution.
   - Remove/disable PyMarkdown step unless rule harmonization is completed.

2. Path Filters
   - Use `paths` or `paths-ignore` in GitHub Actions for Python jobs to limit triggers to backend and workflow files.
   - Keep markdown job scoped to `**/*.md`.

3. Dev Dependencies
   - Add `requirements-dev.txt` with pytest, pytest-cov, httpx, and type stubs; install in CI only.
   - Docker images remain minimal, installing only runtime deps.

4. Local Pre-commit
   - Provide `.pre-commit-config.yaml` with a `markdownlint` hook invoking `markdownlint -c .markdownlint.yml` on staged `.md` files.
   - Document setup in `docs/tooling/pre-commit.md` (install pre-commit, install markdownlint-cli, enable hooks).
   - Ensure CI markdown rules and local hook use the same config to prevent drift.

5. Canonical Makefile
   - Provide a `Makefile` wrapping common local dev tasks to align with CI:
     - `setup`, `lint`, `typecheck`, `test`, `markdown`, `pre-commit-install`, `ci`, `run-backend`.
   - Use uv/uvx to match CI runners and ensure parity.
   - Keep `markdown` target using `.markdownlint.yml` to avoid rule drift.

6. Concurrency and Cancellation (CI-REQ-017)
   - Add `concurrency` to workflows:
     ```
     concurrency:
       group: ${{ github.workflow }}-${{ github.ref }}
       cancel-in-progress: true
     ```

7. Actions Pinning (CI-REQ-018)
   - Pin all `uses: actions/...@<SHA>`; document policy for updating SHAs regularly.

8. Caching (CI-REQ-019)
   - Add actions/cache for uv (wheel/cache directories) keyed by OS + Python + lockfile hashes.
   - Consider caching `.pytest_cache` for marginal gains.

9. Coverage (CI-REQ-020)
   - Workflow: extend `ci.yml` test job to run:
     - `pytest --maxfail=1 -q --cov=backend --cov-report=xml:coverage.xml --cov-fail-under=70`
   - Artifacts: upload `coverage.xml` for future consumers (e.g., SonarCloud).
   - Threshold: 70% initial; adjust in spec if quality gates evolve.

10. Security Scans and SBOM (CI-REQ-021)
   - Workflow file: `.github/workflows/security-scan.yml`
   - Steps:
     - Setup Trivy; run `trivy fs --exit-code 1 --severity HIGH,CRITICAL .`
     - Optionally build images and run `trivy image` on `ontology-backend` and `ontology-frontend` tags
     - Setup Syft; run `syft packages dir:. -o spdx-json > sbom.spdx.json`
     - Upload `sbom.spdx.json` as an artifact
   - Failure policy: fail job on HIGH/CRITICAL findings

11. Secret Scanning (CI-REQ-022)
   - Workflow file: `.github/workflows/secret-scan.yml`
   - Steps:
     - Install `gitleaks`
     - Run `gitleaks detect --redact` (PR scope preferred); fail on findings
     - Optional allowlist config at `.gitleaks.toml` for justified exclusions

12. Token Permissions (CI-REQ-023)
   - All workflows:
     - Add top-level `permissions: contents: read`
     - Override per job only when essential (e.g., `id-token: write` for OIDC)

13. PR Hygiene (CI-REQ-024)
   - Files:
     - `.github/labeler.yml` (path-based label rules)
     - `.github/workflows/labeler.yml` using `actions/labeler`
   - Branch protection (out-of-repo): require ≥1 label before merge (optional)

14. Dependency Automation (CI-REQ-025)
   - File: `.github/dependabot.yml`
   - Ecosystems:
     - `github-actions` in `/.github/workflows`
     - `pip` in `/backend`
   - Schedule: weekly
   - PRs: run same CI checks as human PRs

15. Post-Deploy Smoke (CI-REQ-026)
   - Option A (Cloud Build): add post-deploy step to run `curl` checks against `ontology-backend` and basic endpoint(s)
   - Option B (GitHub): workflow job authenticates with `gcloud`, resolves Cloud Run URLs, executes health checks
   - Backend checks: `GET /health` and 1–2 core endpoints; fail on non-2xx

16. Environment Policies (CI-REQ-027)
   - GitHub environments:
     - `production` requires reviewers (org/project admins)
   - Cloud Build:
     - Manual approval step between stages; document promotion path
   - Documentation:
     - `docs/ops/environments.md` outlines stages, approvers, and triggers

17. Provenance and Signing (CI-REQ-028)
   - OIDC:
     - Configure GitHub→GCP workload identity federation
     - Grant minimal roles for signing/push
   - Cosign:
     - Use keyless or managed key; sign images pre-deploy
     - Verify via `cosign verify` in CI
   - Documentation:
     - `docs/security/provenance-and-signing.md` with step-by-step verification

# Design Document

## Overview

The CI/CD pipeline builds and deploys two services (backend FastAPI and frontend React) to Google Cloud Run using Google Cloud Build and Docker. Container images are stored in Google Container Registry (gcr.io). The pipeline is driven by two Cloud Build YAML files and a deployment script that orchestrates end-to-end deployment and environment substitutions.

## Components

1. Cloud Build (Backend)
   - Config: `scripts/cloudbuild-backend.yaml`
   - Steps:
     - Docker build using `backend/Dockerfile` with tag `gcr.io/$PROJECT_ID/ontology-backend:latest`
     - Docker push to Container Registry
     - `gcloud run deploy ontology-backend` with region `us-central1`, `--allow-unauthenticated`, port `8080`, 2Gi memory, 2 vCPU
   - Declares produced image in `images:` section

2. Cloud Build (Frontend)
   - Config: `scripts/cloudbuild-frontend.yaml`
   - Steps:
     - Node 18 builder to run `npm install` and build React app with `REACT_APP_API_URL=${_BACKEND_URL}`
     - Docker build using `frontend/Dockerfile` with tag `gcr.io/$PROJECT_ID/ontology-frontend:latest`
     - Docker push to Container Registry
     - `gcloud run deploy ontology-frontend` with region `us-central1`, `--allow-unauthenticated`, port `80`, 512Mi memory, 1 vCPU
   - Substitution `_BACKEND_URL` provided by caller/script
   - Declares produced image in `images:` section

3. Deployment Script
   - Script: `scripts/deploy.sh`
   - Responsibilities:
     - Accept `PROJECT_ID` or read `GOOGLE_CLOUD_PROJECT`
     - Enable required APIs: Cloud Build, Cloud Run, Container Registry
     - Submit backend Cloud Build, deploy backend to Cloud Run
     - Read backend service URL
     - Submit frontend Cloud Build with `_BACKEND_URL` substitution set to backend URL
     - Output both service URLs
     - Provide operator guidance for configuring `GEMINI_API_KEY` via Secret Manager

4. GitHub Workflows (CI Quality Gates)
   - `ci.yml`:
     - Add concurrency group and permissions
     - Add caching and coverage enforcement
   - `markdown-syntax.yml`:
     - Ensure concurrency and least-privilege permissions
   - `security-scan.yml`:
     - Trivy fs/image scans; Syft SBOM artifact
   - `secret-scan.yml`:
     - gitleaks detection with redaction
   - `labeler.yml`:
     - Auto-apply labels based on changed paths
   - `.github/dependabot.yml`:
     - Weekly dependency PRs for actions and Python

4. Dockerfiles
   - Backend: `backend/Dockerfile`
     - Base: `python:3.11-slim`
     - Installs `backend/requirements.txt`
     - Copies `backend/main.py`, `guidance.ttl`, `spore_registry.ttl`, and `docs/`
     - Exposes port `8080`
     - Entrypoint: `python main.py`
   - Frontend: `frontend/Dockerfile` (multi-stage)
     - Build stage: `node:18-alpine`, `npm install`, `npm run build`
     - Runtime: `nginx:alpine`, serve static files on port `80`

5. Service Manifests (Reference)
   - `backend/service.yaml` and `frontend/service.yaml` provide Cloud Run service definitions (scaling annotations, env vars), but current Cloud Build steps deploy via flags and do not apply these manifests directly.

## Flow

1. Operator runs `scripts/deploy.sh PROJECT_ID`
2. Backend Cloud Build executes: build → push → Cloud Run deploy
3. Script captures backend URL
4. Frontend Cloud Build executes with `_BACKEND_URL` → build → push → Cloud Run deploy
5. Script prints URLs and hints for secret configuration

## Configuration and Secrets

- `REACT_APP_API_URL` is injected at frontend build time via `_BACKEND_URL`.
- `GEMINI_API_KEY` is supplied at runtime via Secret Manager (not baked into images). Script prints `gcloud` commands to configure secrets post-deploy.

## Observations and Known Gaps

- The deploy script references Cloud Build config paths relative to `backend/` and `frontend/`; ensure the paths point to `scripts/cloudbuild-*.yaml` when invoked.
- Container Registry (gcr.io) is used instead of Artifact Registry; acceptable for current design but can be upgraded.
- Service YAMLs are not applied by the pipeline; scaling annotations/env var differences may exist between manifests and actual deployed flags.


