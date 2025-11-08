# Design Document

## Overview

Two primary registries support discovery:

- `guidance.ttl` — PoD registry linking each PoD URI to its content file (`plan:filePath`) under `docs/pod/`.
- `spore_registry.ttl` — Spore registry with provenance fields and status.

The Backend API loads these registries to enumerate PoDs and Spores, and then loads individual PoD Turtle files for detailed fields.

## Namespaces

- `plan:` `https://ontology.beastmost.com/plan#`
- `spore:` `https://ontology.beastmost.com/spore#`
- `prov:` `http://www.w3.org/ns/prov#`
- `time:` `http://www.w3.org/2006/time#`
- `rdf:`, `rdfs:`, `xsd:` — standard vocabularies

## File Layout

- Root-level registry files:
  - `guidance.ttl`
  - `spore_registry.ttl`
- PoD content files:
  - `docs/pod/YYYY/PoD_YYYY-MM-DD.ttl`
  - Optional `docs/pod/YYYY/README_PoD_YYYY-MM-DD.md`


