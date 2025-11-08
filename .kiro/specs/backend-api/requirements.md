# Requirements Document

## Introduction

This specification defines the requirements for the Backend API implemented with FastAPI. The service exposes health and discovery endpoints, provides read access to Plans of Day (PoDs) and Spores defined in RDF/Turtle files, and supports AI-assisted PoD generation via Google Gemini.

## Glossary

- **BackendAPI**: FastAPI service for PoD and Spore interactions.
- **PoD**: Plan of Day; RDF/Turtle documents modeling PDCA phases.
- **Spore**: Context bundle tracked in a registry.
- **GuidanceRegistry**: `guidance.ttl` listing PoDs and file paths.
- **SporeRegistry**: `spore_registry.ttl` listing Spores.
- **Gemini**: Google Generative AI used to generate PoD structures.

## Requirements

### Requirement 1 — Service Health and Discovery

**User Story:** As an operator, I want to verify service availability and discover basic info.

#### Acceptance Criteria
1. THE BackendAPI SHALL expose `GET /health` returning JSON with `status=healthy` and an ISO UTC `timestamp`.
2. THE BackendAPI SHALL expose `GET /` returning JSON with `message`, `version`, and an object of endpoint paths including `pods`, `spores`, and `health`.

### Requirement 2 — List Plans of Day

**User Story:** As a user, I want to list all available PoDs so I can browse daily plans.

#### Acceptance Criteria
1. THE BackendAPI SHALL expose `GET /api/pods` returning a JSON array of PoDs.
2. THE BackendAPI SHALL read `guidance.ttl` for PoD URIs and file paths.
3. THE BackendAPI SHALL resolve PoD file paths only within an allowed directory rooted at `docs/pod/`.
4. THE BackendAPI SHALL parse each referenced PoD Turtle file and extract:
   - `uri`, `label`, `date`, `status`
   - `workflowPhases[]` with `phaseName`, `description`, `phaseOrder`, optional `hasTime`
   - `references[]` with `referenceType`, `referenceValue`
5. THE BackendAPI SHALL skip invalid or out-of-scope file paths without failing the entire response.

### Requirement 3 — Get Plan of Day by ID

**User Story:** As a user, I want to retrieve a specific PoD by ID to view details.

#### Acceptance Criteria
1. THE BackendAPI SHALL expose `GET /api/pods/{pod_id}` returning a PoD object.
2. THE BackendAPI SHALL construct the PoD URI using `{pod_id}` to locate entries in `guidance.ttl`.
3. WHEN the PoD is not registered or the file path is invalid, THE BackendAPI SHALL return `404 Not Found`.

### Requirement 4 — List Spores

**User Story:** As a user, I want to list all Spores so I can inspect context bundles.

#### Acceptance Criteria
1. THE BackendAPI SHALL expose `GET /api/spores` returning a JSON array of Spores.
2. THE BackendAPI SHALL read `spore_registry.ttl` to enumerate Spores.
3. THE BackendAPI SHALL extract `uri`, `label`, `derivedFrom`, `createdAt`, `status`, and optional `linksTo`.

### Requirement 5 — Generate PoD via AI

**User Story:** As a user, I want to generate a new PoD structure using AI given a natural language prompt.

#### Acceptance Criteria
1. THE BackendAPI SHALL expose `POST /api/pods/generate` accepting JSON `{ "prompt": string }`.
2. WHEN `GEMINI_API_KEY` is not configured, THE BackendAPI SHALL return `503` with a clear error message.
3. THE BackendAPI SHALL use Google Gemini model `gemini-pro` to generate a PoD JSON structure following the PDCA phases.
4. THE BackendAPI SHALL robustly extract the first valid JSON object from model output (including fenced code blocks).
5. ON success, THE BackendAPI SHALL return `{ success: true, pod: <object>, message: "..." }`.
6. ON model or parsing errors, THE BackendAPI SHALL return `500` with error details.

### Requirement 6 — CORS and Security

**User Story:** As a frontend developer, I need the API accessible during development and deployment.

#### Acceptance Criteria
1. THE BackendAPI SHALL enable CORS to allow cross-origin requests (development may allow `*`; production SHOULD restrict origins).
2. THE BackendAPI SHALL restrict PoD file path resolution to `docs/pod/` to prevent path traversal.

### Requirement 7 — Optional MCP Exposure

**User Story:** As a platform engineer, I want MCP endpoints available when explicitly enabled.

#### Acceptance Criteria
1. WHEN environment variable `ENABLE_MCP_API` is truthy, THE BackendAPI SHALL include the MCP router under `/api/mcp`.
2. WHEN MCP cannot initialize, THE BackendAPI SHOULD continue serving core endpoints.


