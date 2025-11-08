# Requirements Document

## Introduction

This specification defines the requirements for the React frontend application that displays Plans of Day (PoDs) and Spores and supports AI-assisted PoD generation via the Backend API.

## Glossary

- **FrontendApp**: React SPA served by Nginx on Cloud Run.
- **API_URL**: Backend API base URL, set via `REACT_APP_API_URL`.

## Requirements

### Requirement 1 — Configuration

**User Story:** As a developer, I want the app to point to the correct backend.

#### Acceptance Criteria
1. THE FrontendApp SHALL read `REACT_APP_API_URL` at build time to determine the backend base URL.
2. WHEN `REACT_APP_API_URL` is not set, THE FrontendApp SHALL default to `http://localhost:8080` for local development.

### Requirement 2 — Data Fetching and Loading States

**User Story:** As a user, I want the app to load data and indicate progress.

#### Acceptance Criteria
1. THE FrontendApp SHALL fetch `GET {API_URL}/api/pods` and `GET {API_URL}/api/spores` on initial load.
2. THE FrontendApp SHALL display a loading indicator while data is being fetched.
3. THE FrontendApp SHALL handle and log fetch errors to console and clear loading state.

### Requirement 3 — Navigation and Views

**User Story:** As a user, I want to switch between PoDs, Spores, and AI Generation.

#### Acceptance Criteria
1. THE FrontendApp SHALL provide tabs or controls for:
   - PoDs list
   - Spores list
   - Generate PoD (AI)
2. THE FrontendApp SHALL display item counts on the PoDs and Spores tabs.

### Requirement 4 — PoDs View

**User Story:** As a user, I want to see PoD details including phases and references.

#### Acceptance Criteria
1. THE FrontendApp SHALL render each PoD card with `label`, `date`, and `status`.
2. THE FrontendApp SHALL render PoD `workflowPhases[]` with `phaseOrder`, `phaseName`, `description`, and optional `hasTime`.
3. WHEN PoD references are present, THE FrontendApp SHALL render a references list with `referenceType` and `referenceValue`.

### Requirement 5 — Spores View

**User Story:** As a user, I want to see Spores with provenance fields.

#### Acceptance Criteria
1. THE FrontendApp SHALL render each Spore card with `label`, `status`, and `createdAt`.
2. WHEN `linksTo` is present, THE FrontendApp SHALL render a link to the target.
3. THE FrontendApp SHALL render `derivedFrom` as a link to the source URI.

### Requirement 6 — AI Generation View

**User Story:** As a user, I want to generate a PoD via AI and view the result.

#### Acceptance Criteria
1. THE FrontendApp SHALL provide a textarea for entering a prompt and a button to submit.
2. ON submit, THE FrontendApp SHALL call `POST {API_URL}/api/pods/generate` with `{ prompt }`.
3. THE FrontendApp SHALL display a generating state during the request.
4. ON success, THE FrontendApp SHALL render the returned PoD structure (date, label, phases, references).
5. ON error, THE FrontendApp SHALL alert with an error message derived from HTTP response or exception.

### Requirement 7 — Deployment

**User Story:** As an operator, I want the app containerized and deployable.

#### Acceptance Criteria
1. THE FrontendApp SHALL be built with Node 18 and served by Nginx on port 80.
2. THE container image SHALL be deployable to Cloud Run with `--allow-unauthenticated`.


