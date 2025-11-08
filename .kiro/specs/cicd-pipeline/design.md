# CI/CD Pipeline — Design Addendum

Relates to: CI-REQ-010…CI-REQ-014

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


