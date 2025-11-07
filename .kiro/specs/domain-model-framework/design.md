# Design Document

## Overview

The Domain Model Framework provides the runtime that loads, parses, validates, and registers static domain model files so that LLM-backed components can assume stakeholder perspectives consistently. It is format‑agnostic (RDF/Turtle, JSON, Markdown) and produces a normalized in‑memory representation used by MCP and the orchestrator.

## Components

1. ModelLoader
   - Loads files from a configurable base directory (default `.mcp/domain-models/`)
   - Supports absolute/relative paths; UTF‑8 text
   - Concurrent I/O where safe

2. ModelParser
   - Turtle: parse with RDFLib → `rdflib.Graph`
   - JSON: parse to `dict`; validate with JSON Schema (`.mcp/schemas/domain_model.schema.json`)
   - Markdown: parse sections to a dict using a fixed heading schema (see `docs/domain-model-markdown-spec.md`)
   - Extract metadata: `domain`, `description`, `version`, `capabilities`, `tools`, `rules`, `expertise`

3. ModelValidator
   - JSON/Markdown: JSON Schema validation
   - Turtle: RDF parse + optional SHACL validation (`.mcp/shapes/domain-model-shapes.ttl`)
   - Produces structured error list

4. ModelRegistry
   - Registry keyed by `domainId`
   - Stores metadata: file path, format, load timestamp, version
   - Query: list, get by id, search by name/description/keywords
   - Version history tracking (simple array of versions)

5. ModelCache
   - In‑memory cache of normalized models
   - TTL default 300s; explicit invalidation on file change or reload
   - Hit/miss statistics

## Data Flow

`path → ModelLoader → ModelParser(format) → ModelValidator(format) → normalize → ModelRegistry + ModelCache`

## Normalized Representation

```python
class NormalizedDomainModel(TypedDict):
    domain: str
    description: str
    version: str   # semver
    capabilities: List[str]
    tools: List[str]
    rules: List[str]
    expertise: List[str]
    raw_format: Literal["turtle","json","markdown"]
    raw_content: str
```

## Operations

- load(domainId|path) → NormalizedDomainModel
- reload(domainId|path) → refresh cache and registry
- list()/get()/search()
- versions(domainId)

## Errors

- `ModelNotFoundError(path)`
- `UnsupportedFormatError(extension)`
- `ParseError(details)`
- `ValidationError(list[Violation])`

## Security and Governance

- No execution—static file ingestion only
- Log file loads, parse/validation failures
- Provenance: record loader, timestamp, checksum

## Interfaces/Locations

- Implementation (planned): `backend/domain_models/`
- Schemas: `.mcp/schemas/domain_model.schema.json`
- SHACL: `.mcp/shapes/domain-model-shapes.ttl`
- Default base dir: `.mcp/domain-models/`

