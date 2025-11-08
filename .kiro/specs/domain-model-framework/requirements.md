# Domain Model Framework — Requirements (Addendum)

DMF-REQ-010: The framework SHALL resolve default base_dir for domain models from repo-root to avoid CWD dependency.

DMF-REQ-011: The loader/parser/validator stack SHALL be usable with test-provided fixtures without relying on repo-global `.mcp/` content.

DMF-REQ-012: Tests SHALL be able to disable preload or provide explicit model lists, ensuring deterministic registry state.

# Requirements Document

## Introduction

This specification defines the requirements for implementing the Domain Model Framework in the Composable AI Advisors system. The Domain Model Framework is the foundational infrastructure that enables the system to load, parse, validate, and manage domain model files (static, machine-readable descriptions in Turtle, JSON, or Markdown format). Domain models are used by LLMs to assume the position of a stakeholder for a specific domain, enabling domain-specific reasoning capabilities. This framework is a prerequisite for the MCP implementation and the multi-agent mesh architecture.

## Glossary

- **DomainModel**: A static, machine-readable file (Turtle, JSON, or Markdown) that describes a domain and is used by an LLM to assume the position of a stakeholder for that domain
- **DomainModelFramework**: The system that loads, parses, validates, and manages domain model files
- **ModelLoader**: Component that loads domain model files from the filesystem
- **ModelParser**: Component that parses domain model files in different formats (Turtle, JSON, Markdown)
- **ModelValidator**: Component that validates domain model structure and content
- **ModelRegistry**: Component that maintains a registry of loaded domain models with metadata
- **ModelCache**: In-memory cache of parsed domain models for performance
- **LLM**: Large Language Model that uses domain models to constrain its behavior
- **ReasoningService**: A service that uses a domain model to provide domain-specific reasoning capabilities
- **CacheEntry**: A cached domain model with associated time-to-live metadata
- **ValidationResult**: The output of validation containing validity status and error list
- **DomainIdentifier**: A unique string identifier for a domain model

## Requirements

### Requirement 1

**User Story:** As a system architect, I want to define domain models in multiple formats, so that I can choose the most appropriate format for each domain

#### Acceptance Criteria

1. THE DomainModelFramework SHALL support loading domain model files in RDF/Turtle format with .ttl file extension
2. THE DomainModelFramework SHALL support loading domain model files in JSON format with .json file extension
3. THE DomainModelFramework SHALL support loading domain model files in Markdown format with .md file extension
4. THE DomainModelFramework SHALL detect the domain model format by examining the file extension
5. WHERE a domain model file has an unsupported file extension, THE DomainModelFramework SHALL return an error message listing Turtle, JSON, and Markdown as supported formats

### Requirement 2

**User Story:** As a developer, I want domain models to be loaded from the filesystem, so that I can manage them as configuration files

#### Acceptance Criteria

1. THE ModelLoader SHALL load domain model files from a configurable base directory path with default value `.mcp/domain-models/`
2. THE ModelLoader SHALL resolve absolute file paths and relative file paths to the base directory
3. WHEN a domain model file does not exist at the specified path, THE ModelLoader SHALL return an error message containing the attempted file path
4. THE ModelLoader SHALL read domain model file contents using UTF-8 character encoding
5. THE ModelLoader SHALL load multiple domain model files using concurrent asynchronous operations

### Requirement 3

**User Story:** As a developer, I want domain models to be parsed into a structured format, so that LLMs can consume them consistently

#### Acceptance Criteria

1. WHEN a Turtle format file is loaded, THE ModelParser SHALL parse the file content using RDFLib library into an RDF graph structure
2. WHEN a JSON format file is loaded, THE ModelParser SHALL parse the file content into a Python dictionary structure
3. WHEN a Markdown format file is loaded, THE ModelParser SHALL parse the file content into structured text sections with YAML frontmatter
4. THE ModelParser SHALL extract domain metadata fields including domain name, description, and version number from the parsed content
5. WHEN parsing fails for any domain model format, THE ModelParser SHALL return a structured error containing the file path, detected format, and specific error details

### Requirement 4

**User Story:** As a system architect, I want domain models to be validated, so that I can ensure they meet structural requirements

#### Acceptance Criteria

1. THE ModelValidator SHALL verify that each domain model contains a non-empty domain name field value
2. THE ModelValidator SHALL verify that each domain model contains a non-empty description field value
3. WHERE a domain model is in Turtle format, THE ModelValidator SHALL verify the parsed content contains valid RDF triples
4. WHERE a domain model is in JSON format, THE ModelValidator SHALL verify the parsed content conforms to the defined JSON schema structure
5. WHEN validation fails for any domain model, THE ModelValidator SHALL return a ValidationResult containing field names and specific error messages

### Requirement 5

**User Story:** As a developer, I want domain models to be registered with metadata, so that I can discover and query available models

#### Acceptance Criteria

1. THE ModelRegistry SHALL maintain an in-memory registry of loaded domain models indexed by unique DomainIdentifier
2. THE ModelRegistry SHALL store metadata for each domain model including file path, format type, load timestamp, and version number
3. THE ModelRegistry SHALL provide a retrieval method to return a list of all registered domain model metadata
4. THE ModelRegistry SHALL provide a retrieval method to return a specific domain model using its DomainIdentifier
5. THE ModelRegistry SHALL provide a search method to return domain models matching domain name text or description text as search criteria

### Requirement 6

**User Story:** As a developer, I want domain models to be cached in memory, so that repeated access is performant

#### Acceptance Criteria

1. THE ModelCache SHALL store parsed domain models in memory after the first successful load operation completes
2. THE ModelCache SHALL use the DomainIdentifier as the unique cache key for storage and retrieval operations
3. THE ModelCache SHALL provide an invalidation method to remove cached entries when a domain model file is modified
4. THE ModelCache SHALL support configurable cache time-to-live duration with a default value of 300 seconds
5. THE ModelCache SHALL track and maintain cache hit count and cache miss count as performance statistics

### Requirement 7

**User Story:** As a developer, I want to reload domain models without restarting the service, so that I can update models dynamically

#### Acceptance Criteria

1. THE DomainModelFramework SHALL provide a reload method to refresh a specific domain model using its DomainIdentifier
2. THE DomainModelFramework SHALL provide a reload method to refresh all registered domain models
3. WHEN a domain model is reloaded, THE DomainModelFramework SHALL invalidate the corresponding ModelCache entry before reloading the file
4. WHEN a domain model is reloaded, THE DomainModelFramework SHALL re-parse the file content and re-validate the parsed domain model
5. WHEN a domain model reload operation succeeds, THE DomainModelFramework SHALL return the updated domain model to the calling component

### Requirement 8

**User Story:** As a developer, I want domain models to include capability metadata, so that the orchestrator can route tasks appropriately

#### Acceptance Criteria

1. THE DomainModel SHALL include a list of capability names that the domain model provides
2. THE DomainModel SHALL include a list of tool identifiers that the domain model supports for execution
3. THE DomainModel SHALL include a list of rule set identifiers that the domain model applies during reasoning operations
4. THE DomainModel SHALL include a list of domain expertise keywords for orchestrator routing decisions
5. THE ModelParser SHALL extract capability metadata fields from Turtle, JSON, and Markdown format domain models

### Requirement 9

**User Story:** As a developer, I want domain models to be versioned, so that I can track changes and maintain compatibility

#### Acceptance Criteria

1. THE DomainModel SHALL include a version field value using semantic versioning format MAJOR.MINOR.PATCH
2. THE ModelRegistry SHALL track and store version history entries for each registered domain model
3. THE DomainModelFramework SHALL support loading a specific version of a domain model using the version number parameter
4. WHEN a domain model version is incompatible with the DomainModelFramework version, THE DomainModelFramework SHALL return an error message containing the domain model version and framework version details
5. THE DomainModelFramework SHALL provide a retrieval method to return a list of all available version numbers for a specific domain model

### Requirement 10

**User Story:** As a system operator, I want to monitor domain model loading and usage, so that I can troubleshoot issues

#### Acceptance Criteria

1. THE DomainModelFramework SHALL log all domain model load operations including file path and completion status at INFO level
2. THE DomainModelFramework SHALL log all parsing errors including file path and specific error details at ERROR level
3. THE DomainModelFramework SHALL log all validation errors including DomainIdentifier and specific error details at ERROR level
4. THE DomainModelFramework SHALL expose operational metrics including domain model load count, parse error count, and validation error count
5. THE DomainModelFramework SHALL expose performance metrics including cache hit rate percentage and current cache size count
