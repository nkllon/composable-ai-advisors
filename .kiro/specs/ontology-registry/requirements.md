# Requirements Document

## Introduction

This specification defines the requirements for the ontology registry artifacts used by the system: the Guidance Registry for PoDs and the Spore Registry. These define how PoDs and Spores are referenced and discovered by the Backend API and clients.

## Glossary

- **GuidanceRegistry**: RDF/Turtle file `guidance.ttl` listing PoDs and their file paths.
- **SporeRegistry**: RDF/Turtle file `spore_registry.ttl` listing Spores and provenance fields.
- **PoDFile**: RDF/Turtle document containing a single PoD instance with PDCA phases.

## Requirements

### Requirement 1 — Guidance Registry Structure

**User Story:** As a backend, I need a registry of PoDs and file paths to load PoD details.

#### Acceptance Criteria
1. THE GuidanceRegistry SHALL be a Turtle file named `guidance.ttl` at repository root.
2. THE GuidanceRegistry SHALL declare PoD resources of type `plan:PlanOfDay`.
3. EACH PoD entry SHALL include:
   - `plan:filePath` with a relative path to the PoD Turtle file (under `docs/pod/`).
   - OPTIONAL `plan:readmePath` for a Markdown summary.
4. THE GuidanceRegistry SHALL include registry metadata with label, `plan:lastUpdated` (xsd:dateTime), and `plan:registryVersion`.

### Requirement 2 — PoD File Structure (Minimum for Parsing)

**User Story:** As a backend, I need predictable PoD content to extract fields.

#### Acceptance Criteria
1. EACH PoDFile SHALL define the same PoD URI present in GuidanceRegistry.
2. EACH PoDFile SHALL provide:
   - `rdfs:label` (string)
   - `plan:date` (string or xsd:date)
   - `plan:status` (string)
3. EACH PoDFile SHOULD define PDCA phases as blank nodes linked via `plan:workflowPhase` with:
   - `plan:phaseName` (string)
   - `plan:description` (string)
   - `plan:phaseOrder` (integer)
   - OPTIONAL `time:hasTime` (xsd:dateTime)
4. A PoDFile MAY include references as blank nodes linked via `plan:references` with:
   - `plan:referenceType` (string)
   - `plan:referenceValue` (string)

### Requirement 3 — Spore Registry Structure

**User Story:** As a backend, I need a registry of Spores to present provenance.

#### Acceptance Criteria
1. THE SporeRegistry SHALL be a Turtle file named `spore_registry.ttl` at repository root.
2. THE SporeRegistry SHALL declare Spore resources of type `spore:Spore`.
3. EACH Spore entry SHALL include:
   - `rdfs:label` (string)
   - `spore:derivedFrom` (URI) and/or `prov:wasDerivedFrom` (URI)
   - `spore:createdAt` (xsd:dateTime)
   - `spore:status` (string)
   - OPTIONAL `spore:linksTo` (URI)
4. THE SporeRegistry SHALL include registry metadata with label, `spore:lastUpdated` (xsd:dateTime), and `spore:registryVersion`.

### Requirement 4 — Namespaces

**User Story:** As an ontology author, I want predictable prefixes.

#### Acceptance Criteria
1. THE registries and PoD files SHALL use standard prefixes for `rdf:`, `rdfs:`, `xsd:`, and domain-specific `plan:`, `spore:`, `prov:`, `time:`.
2. THE registries SHOULD set `@base` to `https://ontology.beastmost.com/` for stable URIs.


