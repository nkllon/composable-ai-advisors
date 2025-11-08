# Implementation Plan

- [x] 1. Set up domain model framework structure
  - Create `backend/domain_model/` directory
  - Create `__init__.py` with package exports
  - Create subdirectories for tests and fixtures
  - _Requirements: All_

- [x] 2. Update backend dependencies
  - Add `aiofiles` for async file I/O
  - Add `pyyaml` for Markdown frontmatter parsing
  - Note: `jsonschema` and `rdflib` already present in requirements.txt
  - Update `requirements.txt`
  - _Requirements: 2.4, 3.3, 4.4_

- [x] 3. Implement domain model data structures
  - [x] 3.1 Create models.py with Pydantic models
    - Implement `DomainModelFormat` enum
    - Implement `DomainModelMetadata` model
    - Implement `DomainModel` model
    - Implement `ValidationIssue` and `ValidationResult` models
    - _Requirements: 1.1, 1.2, 1.3, 3.4, 4.5, 9.4_

- [x] 4. Implement Model Loader
  - [x] 4.1 Create loader.py with ModelLoader class
    - Implement `__init__` with configurable base directory (default: `.mcp/domain-models/`)
    - Implement `load_file` method with async file I/O
    - Implement `detect_format` method for extension-based detection
    - Implement `resolve_path` method for absolute/relative paths
    - Implement `load_multiple` method for concurrent loading
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 4.2 Add error handling for file operations
    - Handle FileNotFoundError with clear messages including attempted path
    - Handle unsupported format errors with list of supported formats
    - Handle UTF-8 encoding errors
    - _Requirements: 1.5, 2.3_

  - [ ]* 4.3 Write unit tests for Model Loader
    - Test loading valid files (all formats)
    - Test handling missing files
    - Test format detection
    - Test path resolution
    - Test concurrent loading
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 5. Implement Model Parser
  - [x] 5.1 Create parser.py with ModelParser class
    - Implement `ModelParser` main class with format-specific parser delegation
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 5.2 Implement TurtleParser
    - Parse Turtle content using RDFLib
    - Extract metadata from RDF triples (domain_id, domain_name, description, version)
    - Extract capability metadata (capabilities, tools, rule_sets, expertise_keywords)
    - Return Graph and DomainModelMetadata
    - _Requirements: 1.1, 3.1, 3.4, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 5.3 Implement JSONParser
    - Parse JSON content
    - Extract metadata from top-level fields
    - Extract capability metadata
    - Return dict and DomainModelMetadata
    - _Requirements: 1.2, 3.2, 3.4, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 5.4 Implement MarkdownParser
    - Extract YAML frontmatter for metadata
    - Parse markdown sections for content
    - Extract capability metadata from frontmatter
    - Return structured dict and DomainModelMetadata
    - _Requirements: 1.3, 3.3, 3.4, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 5.5 Add error handling for parsing
    - Handle RDF parsing errors with file path and format
    - Handle JSON parsing errors with specific details
    - Handle YAML/Markdown parsing errors
    - Return structured ParseError with details
    - _Requirements: 3.5_

  - [ ]* 5.6 Write unit tests for Model Parser
    - Test parsing valid Turtle files
    - Test parsing valid JSON files
    - Test parsing valid Markdown files
    - Test metadata extraction for all formats
    - Test error handling for invalid content
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6. Implement Model Validator
  - [x] 6.1 Create validator.py with ModelValidator class
    - Implement `__init__` with framework_version parameter
    - Implement `validate` method
    - Implement `_validate_required_fields` method (domain_id, domain_name, description, version)
    - Implement `_validate_version_format` method (semantic versioning)
    - Implement `_validate_version_compatibility` method
    - _Requirements: 4.1, 4.2, 9.1, 9.4_

  - [ ] 6.2 Implement format-specific validation
    - Implement `_validate_turtle` for RDF validation
    - Implement `_validate_json` for JSON schema validation
    - Implement `_validate_markdown` for Markdown structure validation
    - _Requirements: 4.3, 4.4_

  - [x] 6.3 Add validation error reporting
    - Return ValidationResult with list of errors
    - Include field names and error messages
    - Support error severity levels
    - _Requirements: 4.5_

  - [ ]* 6.4 Write unit tests for Model Validator
    - Test required field validation
    - Test version format validation
    - Test version compatibility validation
    - Test format-specific validation
    - Test validation error reporting
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 9.1, 9.4_

- [x] 7. Implement Model Registry
  - [x] 7.1 Create registry.py with ModelRegistry class
    - Implement `register` method
    - Implement `get` method with optional version parameter
    - Implement `list_all` method
    - Implement `get_versions` method
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 9.2, 9.3_

  - [x] 7.2 Implement version tracking
    - Track version history per domain_id in version_history dict
    - Support version-specific retrieval
    - Handle version conflicts
    - _Requirements: 9.2, 9.3, 9.5_

  - [ ] 7.3 Add search functionality to registry
    - Implement `search` method with full-text search across domain name and description
    - Implement `_build_search_index` helper method
    - _Requirements: 5.5_

  - [ ]* 7.4 Write unit tests for Model Registry
    - Test model registration
    - Test model retrieval
    - Test listing all models
    - Test search functionality
    - Test version tracking
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 9.2, 9.3_

- [x] 8. Implement Model Cache
  - [x] 8.1 Create cache.py with ModelCache class
    - Implement `CacheEntry` class with TTL
    - Implement `CacheStatistics` class with hit_rate calculation
    - Implement `get` method
    - Implement `put` method with TTL (default: 300 seconds)
    - Implement `invalidate` method
    - Implement `invalidate_all` method
    - Implement `get_statistics` method
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 8.2 Add thread safety
    - Use threading.Lock for cache operations
    - Ensure atomic operations
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 8.3 Write unit tests for Model Cache
    - Test cache hit/miss
    - Test TTL expiration
    - Test invalidation
    - Test statistics tracking
    - Test thread safety
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 9. Complete Domain Model Framework main interface
  - [x] 9.1 Create framework.py with DomainModelFramework class (partial)
    - Implement `__init__` to initialize all components (Loader, Parser, Validator, Registry, Cache)
    - Initialize framework_version and metrics tracking
    - Implement `load_domain_model` method with full workflow (check cache → load → parse → validate → register → cache)
    - Implement `get_domain_model` method with optional version parameter
    - Implement `get_cache_statistics` method
    - Implement `get_metrics` method
    - _Requirements: 5.3, 5.4, 7.1, 9.3, 10.4, 10.5_

  - [ ] 9.2 Add missing framework methods
    - Implement `load_multiple_domain_models` method for concurrent loading
    - Implement `reload_domain_model` method with cache invalidation
    - Implement `reload_all_domain_models` method
    - Implement `list_domain_models` method
    - Implement `search_domain_models` method
    - Implement `get_versions` method
    - _Requirements: 5.3, 5.4, 5.5, 7.2, 7.3, 7.4, 7.5, 9.5_

  - [ ] 9.3 Add logging and metrics tracking
    - Configure logger for domain_model module
    - Log all load operations with file path and status (INFO level)
    - Log parsing errors with file path and details (ERROR level)
    - Log validation errors with domain_id and details (ERROR level)
    - Log cache operations (DEBUG level)
    - Track load_count, parse_error_count, validation_error_count metrics
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ]* 9.4 Write unit tests for DomainModelFramework
    - Test end-to-end load workflow
    - Test reload functionality
    - Test concurrent loading
    - Test error handling at each stage
    - Test cache integration
    - Test metrics collection
    - Test version-specific retrieval
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 9.3, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 10. Update package exports
  - [ ] 10.1 Update __init__.py with proper exports
    - Export main classes: DomainModelFramework, DomainModel, DomainModelMetadata
    - Export enums: DomainModelFormat
    - Export validation classes: ValidationResult, ValidationIssue
    - _Requirements: All_

- [ ]* 11. Create test fixtures
  - [ ]* 11.1 Create fixture domain model files in backend/tests/fixtures/domain_models/
    - Create `valid_turtle.ttl` with complete metadata (domain_id, name, description, version, capabilities, tools, rule_sets, keywords)
    - Create `valid_json.json` with complete metadata
    - Create `valid_markdown.md` with complete metadata and YAML frontmatter
    - Create `invalid_turtle.ttl` with syntax errors
    - Create `invalid_json.json` with structure errors
    - Create `missing_fields.json` with missing required fields
    - _Requirements: All_

- [ ]* 12. Create integration tests
  - [ ]* 12.1 Write end-to-end integration tests in backend/tests/integration/
    - Test loading all fixture formats
    - Test reload workflow
    - Test concurrent loading
    - Test error scenarios
    - Test cache behavior
    - _Requirements: All_

- [ ]* 13. Create documentation
  - [ ]* 13.1 Write developer guide
    - Document how to create domain model files
    - Provide examples for each format (Turtle, JSON, Markdown)
    - Document metadata fields (domain_id, domain_name, description, version, capabilities, tools, rule_sets, expertise_keywords)
    - Document validation rules
    - _Requirements: All_

  - [ ]* 13.2 Write API documentation
    - Document DomainModelFramework API
    - Document all public methods
    - Provide usage examples
    - _Requirements: All_
