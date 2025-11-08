# Design Document

## Overview

The Frontend App is a React SPA that interacts with the Backend API to display PoDs and Spores and to generate PoDs via AI. It is built using Node 18 and served via Nginx in a Cloud Run service.

## Architecture

- React 18 app (`src/App.js`) with Axios for HTTP.
- Environment variable `REACT_APP_API_URL` defines backend base URL.
- Tabs control which view is visible (PoDs, Spores, Generate).
- Minimal state management via React hooks.

## API Integration

- `GET {API_URL}/api/pods` → Populate PoD list.
- `GET {API_URL}/api/spores` → Populate Spore list.
- `POST {API_URL}/api/pods/generate` → Returns generated PoD structure.

## UI States

- Loading state during initial fetch.
- Generating state during AI generation.
- Error alerts on generation failure.

## Deployment

- Multi-stage Docker build builds static assets.
- Nginx serves assets on port 80.
- Deployed via Cloud Build to Cloud Run.


