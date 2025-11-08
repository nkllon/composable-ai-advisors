# Implementation Plan

- [x] 1. Verify Health and Discovery
  - Confirm `GET /health` returns `{status:"healthy", timestamp}`.
  - Confirm `GET /` includes message, version, and endpoints.
  - _Requirements: 1_

- [x] 2. Validate PoD Listing
  - Ensure `GET /api/pods` reads `guidance.ttl`, restricts to `docs/pod/`, parses PoDs, and returns required fields.
  - Handle invalid paths gracefully (skip).
  - _Requirements: 2_

- [x] 3. Validate PoD Retrieval by ID
  - Confirm `GET /api/pods/{pod_id}` returns PoD or 404 when not found/out-of-scope.
  - _Requirements: 3_

- [x] 4. Validate Spores Listing
  - Confirm `GET /api/spores` returns fields as specified from registry.
  - _Requirements: 4_

- [x] 5. Validate AI Generation
  - With `GEMINI_API_KEY` configured, test `POST /api/pods/generate`.
  - Validate JSON extraction from fenced/unfenced outputs.
  - Confirm 503 when key missing; 500 on model errors.
  - _Requirements: 5_

- [x] 6. Validate CORS and Security
  - Confirm CORS is enabled; document production origin tightening.
  - Confirm file path restriction to `docs/pod/`.
  - _Requirements: 6_

- [x] 7. Validate Optional MCP Exposure
  - With `ENABLE_MCP_API=1`, confirm MCP endpoints available.
  - Confirm graceful behavior if MCP initialization fails.
  - _Requirements: 7_

