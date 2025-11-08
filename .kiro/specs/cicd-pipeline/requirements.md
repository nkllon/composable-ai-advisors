# Requirements Document

## Introduction

This specification defines the requirements for the Continuous Integration and Continuous Deployment (CI/CD) pipeline implemented in this repository. The pipeline builds and deploys two services (backend FastAPI and frontend React) to Google Cloud Run using Google Cloud Build, Docker, and Container Registry. These requirements are reverse-engineered from the current implementation to capture the expected behaviors and acceptance criteria.

## Glossary

- **CI/CD_Pipeline**: The automated process that builds, tests (if configured), and deploys application artifacts.
- **CloudBuild**: Google Cloud Build service executing build steps defined in YAML.
- **ContainerRegistry**: Google Container Registry (gcr.io) used to store images.
- **CloudRunService**: A serverless service on Google Cloud Run.
- **BackendService**: `ontology-backend` Cloud Run service (FastAPI).
- **FrontendService**: `ontology-frontend` Cloud Run service (React + Nginx).
- **DeploymentScript**: `scripts/deploy.sh` orchestration script for end-to-end deployment.
- **Substitution**: Cloud Build variable (e.g., `_BACKEND_URL`) passed into a build.

## Source of Truth (Reverse-Engineering Inputs)

- `scripts/cloudbuild-backend.yaml`
- `scripts/cloudbuild-frontend.yaml`
- `scripts/deploy.sh`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `backend/service.yaml` (reference; not applied by Cloud Build)
- `frontend/service.yaml` (reference; not applied by Cloud Build)

## Requirements

### Requirement 10a — Markdown Policy and CI Signal (CI-REQ-010…CI-REQ-012)

#### Acceptance Criteria
1. THE repository SHALL include a single authoritative `.markdownlint.yml` tuned for spec documents (CI-REQ-010).
2. THE markdown workflow SHALL exclude generator/internal paths (e.g., `.cursor/commands/**`) from checks (CI-REQ-011).
3. THE pipeline SHALL run one markdown linter (markdownlint) unless secondary linters are explicitly harmonized (CI-REQ-012).

### Requirement 10b — Path Filters for CI Efficiency (CI-REQ-013)

#### Acceptance Criteria
1. THE Python lint/typecheck/test jobs SHALL trigger only when backend Python or workflow files change.
2. THE markdown job SHALL trigger only when `**/*.md` changes (CI-REQ-013).

### Requirement 10c — Developer Dependencies Isolation (CI-REQ-014)

#### Acceptance Criteria
1. THE repository SHALL define a dev dependency manifest (e.g., `requirements-dev.txt`) for CI tooling (pytest, pytest-cov, type stubs).
2. THE runtime images SHALL not include dev-only dependencies (CI-REQ-014).

### Requirement 10d — Local Pre-commit Checks (CI-REQ-015)

#### Acceptance Criteria
1. THE repository SHALL provide a pre-commit configuration to run markdown lint locally before commit (CI-REQ-015).
2. THE documentation SHALL include setup instructions for enabling the hooks and installing markdownlint.
3. THE local pre-commit behavior SHALL mirror CI markdown rules to minimize drift.

### Requirement 10e — Canonical Make Targets (CI-REQ-016)

#### Acceptance Criteria
1. THE repository SHALL provide a `Makefile` with targets aligning local dev to CI:
   - `setup`, `lint`, `typecheck`, `test`, `markdown`, `pre-commit-install`, `ci`, `run-backend`.
2. THE `markdown` target SHALL use the same `.markdownlint.yml` as CI.
3. THE `ci` target SHALL execute lint → typecheck → test → markdown sequentially.

### Requirement 1 — Backend Build, Push, and Deploy

**User Story:** As a developer, I want the backend container to be built, pushed, and deployed automatically, so that I can run the API on Cloud Run.

#### Acceptance Criteria
1. THE CI/CD_Pipeline SHALL build a Docker image for the backend using `backend/Dockerfile` with context at repository root.
2. THE CI/CD_Pipeline SHALL tag the backend image as `gcr.io/$PROJECT_ID/ontology-backend:latest`.
3. THE CI/CD_Pipeline SHALL push the backend image to Google Container Registry.
4. THE CI/CD_Pipeline SHALL deploy the backend image to a Cloud Run service named `ontology-backend`.
5. THE CloudRunService (backend) SHALL be deployed in region `us-central1`, platform `managed`, and allow unauthenticated access.
6. THE CloudRunService (backend) SHALL expose port `8080`, request `2 vCPU` and `2Gi` memory as per deployment flags.
7. THE CloudBuild configuration for the backend SHALL declare the produced image in the `images:` section.

### Requirement 2 — Frontend Build, Push, and Deploy

**User Story:** As a developer, I want the frontend to be built and deployed with the correct backend URL, so that the UI can reach the API.

#### Acceptance Criteria
1. THE CI/CD_Pipeline SHALL build the React app with `node:18` by running `npm install` and `npm run build` in `frontend/`.
2. THE CI/CD_Pipeline SHALL set `REACT_APP_API_URL` at build time using the `_BACKEND_URL` substitution.
3. THE CI/CD_Pipeline SHALL build a Docker image for the frontend using `frontend/Dockerfile` with context `frontend/`.
4. THE CI/CD_Pipeline SHALL tag the frontend image as `gcr.io/$PROJECT_ID/ontology-frontend:latest`.
5. THE CI/CD_Pipeline SHALL push the frontend image to Google Container Registry.
6. THE CI/CD_Pipeline SHALL deploy the frontend image to a Cloud Run service named `ontology-frontend`.
7. THE CloudRunService (frontend) SHALL be deployed in region `us-central1`, platform `managed`, allow unauthenticated access, and expose port `80`.
8. THE CloudBuild configuration for the frontend SHALL declare the produced image in the `images:` section.

### Requirement 3 — End-to-End Deployment Orchestration

**User Story:** As an operator, I want a single script to orchestrate backend and frontend deployment, so that I can deploy both services end-to-end with one command.

#### Acceptance Criteria
1. THE DeploymentScript SHALL accept a `PROJECT_ID` as an argument or from `GOOGLE_CLOUD_PROJECT`.
2. THE DeploymentScript SHALL enable required APIs: `cloudbuild.googleapis.com`, `run.googleapis.com`, `containerregistry.googleapis.com`.
3. THE DeploymentScript SHALL submit the backend Cloud Build using the repository’s backend Cloud Build configuration.
4. AFTER the backend deploys, THE DeploymentScript SHALL retrieve the backend service URL and use it to configure the frontend build (via Cloud Build substitution `_BACKEND_URL`).
5. THE DeploymentScript SHALL submit the frontend Cloud Build with `_BACKEND_URL` set to the deployed backend URL.
6. THE DeploymentScript SHALL output both backend and frontend Cloud Run service URLs upon completion.
7. THE DeploymentScript SHALL print instructions for configuring the `GEMINI_API_KEY` secret for the backend service.

### Requirement 4 — Image Registry and Tagging

**User Story:** As a release engineer, I want consistent image tagging and storage, so that deployments are predictable.

#### Acceptance Criteria
1. THE CI/CD_Pipeline SHALL push images to Google Container Registry at `gcr.io/$PROJECT_ID/*`.
2. THE CI/CD_Pipeline SHALL tag deployable images with `:latest`.
3. THE CI/CD_Pipeline MAY optionally retain build-specific digests as produced by Cloud Build (implicit).

### Requirement 5 — Build Isolation and Determinism

**User Story:** As an engineer, I want deterministic builds, so that results are reproducible.

#### Acceptance Criteria
1. THE backend build SHALL use `python:3.11-slim` as the base image as defined in `backend/Dockerfile`.
2. THE frontend build SHALL use a multi-stage Dockerfile with `node:18-alpine` for build and `nginx:alpine` for runtime as defined in `frontend/Dockerfile`.
3. THE CI/CD_Pipeline SHALL not rely on local developer environment state; all build steps run inside Cloud Build provided images.

### Requirement 6 — Configuration and Substitutions

**User Story:** As an operator, I want the pipeline to inject environment-specific values, so that the build outputs are correctly configured.

#### Acceptance Criteria
1. THE frontend Cloud Build configuration SHALL define a substitution `_BACKEND_URL` to set `REACT_APP_API_URL` at build time.
2. THE DeploymentScript SHALL update or pass `_BACKEND_URL` using the actual backend Cloud Run URL.
3. THE backend Cloud Run deployment SHALL set `PORT=8080` and may enable additional environment variables per service requirements (e.g., `ENABLE_MCP_API`) as part of deployment flags or subsequent updates.

### Requirement 7 — Security and Secrets (Execution-Time)

**User Story:** As a security engineer, I want sensitive values managed as secrets, so that they are not baked into images.

#### Acceptance Criteria
1. THE pipeline SHALL NOT bake sensitive secrets (e.g., `GEMINI_API_KEY`) into container images.
2. THE pipeline SHALL document (via DeploymentScript output) how to configure `GEMINI_API_KEY` through Google Secret Manager and `gcloud run services update`.
3. THE backend service SHALL obtain `GEMINI_API_KEY` from environment or secrets at runtime (not at build time).

### Requirement 8 — Access and IAM

**User Story:** As an operator, I want public endpoints for testing, so that services are accessible without authentication during demos.

#### Acceptance Criteria
1. THE backend and frontend Cloud Run deployments SHALL include `--allow-unauthenticated`.
2. THE services SHALL be addressable via HTTPS URLs provided by Cloud Run after deployment.

### Requirement 9 — Region and Platform Consistency

**User Story:** As a platform engineer, I want consistent regional deployments, so that services co-locate for performance.

#### Acceptance Criteria
1. THE backend and frontend services SHALL be deployed to region `us-central1`.
2. THE Cloud Run platform SHALL be `managed` for both services.

### Requirement 10 — Documentation and Operator Feedback

**User Story:** As an operator, I want clear output and docs, so that I can verify deployment success.

#### Acceptance Criteria
1. THE DeploymentScript SHALL print backend and frontend Cloud Run URLs after successful deployment.
2. THE repository docs (DEPLOYMENT.md) SHALL include instructions matching the implemented pipeline steps for both Cloud Build methods and manual Docker builds.
3. THE frontend Cloud Build config SHALL comment or document that `_BACKEND_URL` must be updated after backend deployment if not provided by a script.


