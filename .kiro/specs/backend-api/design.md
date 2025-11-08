# Design Document

## Overview

The Backend API is a FastAPI application exposing endpoints to list and retrieve Plans of Day (PoDs) and Spores stored in RDF/Turtle files, plus an AI-assisted PoD generator. It optionally exposes MCP endpoints when enabled by environment configuration.

## Endpoints

- `GET /` — Service info and endpoint discovery
- `GET /health` — Health status with UTC timestamp
- `GET /api/pods` — List PoDs by reading `guidance.ttl` and parsing per-file Turtle
- `GET /api/pods/{pod_id}` — Retrieve individual PoD by URI mapping
- `GET /api/spores` — List Spores from `spore_registry.ttl`
- `POST /api/pods/generate` — Generate PoD structure via Google Gemini
- `GET /api/mcp/*` — MCP endpoints (enabled when `ENABLE_MCP_API` is truthy)

## Data Sources

- `guidance.ttl` — Registry linking PoD URIs to `plan:filePath`
- `docs/pod/YYYY/PoD_YYYY-MM-DD.ttl` — PoD content files
- `spore_registry.ttl` — Spore registry data

## RDF Namespaces

- `plan:` `https://ontology.beastmost.com/plan#`
- `spore:` `https://ontology.beastmost.com/spore#`
- `prov:` `http://www.w3.org/ns/prov#`
- `time:` `http://www.w3.org/2006/time#`

## Security

- CORS enabled (development permissive, production should restrict)
- File path resolution restricted to `docs/pod/` root

## AI Generation

- Model: `gemini-pro`
- Input: user prompt; System prompt instructs PDCA structure
- Output: JSON PoD structure; robust extraction from possibly fenced output


