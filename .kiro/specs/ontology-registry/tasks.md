# Implementation Plan

- [x] 1. Validate Guidance Registry
  - Confirm `guidance.ttl` includes PoD entries with `plan:filePath` under `docs/pod/`.
  - Confirm registry metadata fields are present.
  - _Requirements: 1_

- [x] 2. Validate PoD Files
  - Confirm PoD files provide required fields and PDCA phases.
  - Confirm references are modeled when present.
  - _Requirements: 2_

- [x] 3. Validate Spore Registry
  - Confirm `spore_registry.ttl` entries include required fields and optional links.
  - Confirm registry metadata fields are present.
  - _Requirements: 3_

- [x] 4. Validate Namespaces
  - Confirm all files declare and use required namespaces.
  - _Requirements: 4_

- [ ]* 5. Add SHACL validation
  - Define SHACL shapes for PoD and Spore resources (required properties and datatypes)
  - Add a validation script to check `.ttl` files during CI
  - _Requirements: 2, 3, 4_

- [ ]* 6. TTL linting and consistency checks
  - Add RDF/Turtle linting (ordering, prefixes, base)
  - Ensure URIs and file paths (`plan:filePath`) resolve within `docs/pod/`
  - _Requirements: 1, 4_

- [ ]* 7. Provenance completeness
  - For PoDs: check `prov:wasGeneratedBy` and `prov:generatedAtTime` presence
  - For Spores: check `prov:wasDerivedFrom` alignment with `spore:derivedFrom`
  - _Requirements: 2, 3_

- [ ]* 8. Registry synchronization
  - Verify every PoD file in `docs/pod/` is registered in `guidance.ttl`
  - Verify removed files are unregistered
  - _Requirements: 1, 2_
