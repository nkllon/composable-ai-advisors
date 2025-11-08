# Design Document

## Overview

This design document describes the implementation of the Domain Model Framework for the Composable AI Advisors system. The Domain Model Framework is the foundational infrastructure that enables loading, parsing, validating, and managing domain model files. Domain models are static, machine-readable descriptions (in Turtle, JSON, or Markdown format) that LLMs use to assume stakeholder positions for specific domains.

The framework provides a clean abstraction layer between domain model files and the services that consume them (orchestrator, reasoning services, MCP layer). It handles format detection, parsing, validation, caching, and registry management.

### Design Rationale

**Multi-Format Support**: The framework supports three formats (Turtle, JSON, Markdown) to provide flexibility for different use cases. Turtle is preferred for semantic web integration, JSON for API compatibility, and Markdown for human readability. This addresses Requirement 1.

**Layered Architecture**: The design uses a layered approach (Loader → Parser → Validator → Registry → Cache) to separate concerns and enable independent testing and evolution of each component. Each layer has a single responsibility and clear interfaces.

**Version Management**: The framework tracks version history per domain model and supports version-specific retrieval (Requirements 9.2, 9.3, 9.5). This enables backward compatibility and allows multiple versions of a domain model to coexist. Version compatibility checking (Requirement 9.4) ensures that domain models are compatible with the framework version.

**Caching Strategy**: An in-memory cache with TTL (Requirement 6.4) balances performance with freshness. The cache uses domain_id as the key (Requirement 6.2) and tracks statistics (Requirement 6.5) for monitoring. Invalidation on reload (Requirements 6.3, 7.3) ensures consistency.

**Async Operations**: The framework uses async/await patterns for file I/O (Requirement 2.5) to enable concurrent loading of multiple models without blocking. This improves performance when loading many domain models at startup.

**Comprehensive Monitoring**: The framework logs all operations (Requirements 10.1, 10.2, 10.3) and exposes metrics (Requirements 10.4, 10.5) to support troubleshooting and operational visibility. This is critical for production deployments.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Domain Model Framework                          │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Model Loader                                  │    │
│  │  - File system access                          │    │
│  │  - Format detection                            │    │
│  │  - UTF-8 reading                               │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Model Parser                                  │    │
│  │  - Turtle parser (RDFLib)                      │    │
│  │  - JSON parser                                 │    │
│  │  - Markdown parser                             │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Model Validator                               │    │
│  │  - Structure validation                        │    │
│  │  - Schema validation                           │    │
│  │  - Required fields check                       │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Model Registry                                │    │
│  │  - Domain model index                          │    │
│  │  - Metadata storage                            │    │
│  │  - Version tracking                            │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Model Cache                                   │    │
│  │  - In-memory cache                             │    │
│  │  - TTL management                              │    │
│  │  - Cache statistics                            │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Orchestrator │ │  Reasoning   │ │  MCP Layer   │
│   Service    │ │   Services   │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Components and Interfaces

### 1. Domain Model Data Structures

**Location**: `backend/domain_model/models.py`


**Key Classes**:
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DomainModelFormat(str, Enum):
    """Supported domain model formats"""
    TURTLE = "turtle"
    JSON = "json"
    MARKDOWN = "markdown"

class DomainModelMetadata(BaseModel):
    """Metadata for a domain model"""
    domain_id: str
    domain_name: str
    description: str
    version: str
    format: DomainModelFormat
    file_path: str
    loaded_at: datetime
    capabilities: List[str] = []
    tools: List[str] = []
    rule_sets: List[str] = []
    expertise_keywords: List[str] = []

class DomainModel(BaseModel):
    """Parsed domain model"""
    metadata: DomainModelMetadata
    content: Any  # RDF Graph, dict, or structured text
    raw_content: str  # Original file content
    
    class Config:
        arbitrary_types_allowed = True

class ValidationError(BaseModel):
    """Domain model validation error"""
    field: str
    message: str
    severity: str  # "error", "warning"

class ValidationResult(BaseModel):
    """Result of domain model validation"""
    is_valid: bool
    errors: List[ValidationError] = []
```

### 2. Model Loader

**Location**: `backend/domain_model/loader.py`

**Key Classes**:
```python
from pathlib import Path
from typing import Optional
import asyncio

class ModelLoader:
    """Loads domain model files from filesystem"""
    
    def __init__(self, base_dir: Path = Path(".mcp/domain-models")):
        self.base_dir = base_dir
    
    async def load_file(self, file_path: str) -> tuple[str, DomainModelFormat]:
        """
        Load a domain model file and detect format
        
        Args:
            file_path: Absolute or relative path to domain model file
            
        Returns:
            Tuple of (file_content, format)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format is unsupported
        """
        pass
    
    async def load_multiple(self, file_paths: List[str]) -> List[tuple[str, DomainModelFormat]]:
        """Load multiple domain model files concurrently"""
        pass
    
    def detect_format(self, file_path: str) -> DomainModelFormat:
        """Detect format based on file extension"""
        pass
    
    def resolve_path(self, file_path: str) -> Path:
        """Resolve absolute or relative path"""
        pass
```

**Implementation Details**:
- Use `aiofiles` for async file I/O (Requirement: 2.5)
- Support both absolute paths and paths relative to base_dir (Requirement: 2.2)
- Detect format by extension: `.ttl` → TURTLE, `.json` → JSON, `.md` → MARKDOWN (Requirement: 1.4)
- Read files as UTF-8 (Requirement: 2.4)
- Raise clear errors for missing files with attempted path (Requirement: 2.3)
- Raise clear errors for unsupported formats listing supported formats (Requirement: 1.5)


### 3. Model Parser

**Location**: `backend/domain_model/parser.py`

**Key Classes**:
```python
from rdflib import Graph, Namespace
from abc import ABC, abstractmethod
import json
import re

class BaseParser(ABC):
    """Base class for domain model parsers"""
    
    @abstractmethod
    def parse(self, content: str, file_path: str) -> tuple[Any, DomainModelMetadata]:
        """Parse domain model content and extract metadata"""
        pass

class TurtleParser(BaseParser):
    """Parser for Turtle/RDF domain models"""
    
    def __init__(self):
        self.caa_ns = Namespace("http://nkllon.com/ontology/caa#")
        self.rdfs_ns = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    
    def parse(self, content: str, file_path: str) -> tuple[Graph, DomainModelMetadata]:
        """
        Parse Turtle content into RDF graph and extract metadata
        
        Extracts:
        - domain_name from rdfs:label
        - description from rdfs:comment
        - version from caa:version
        - capabilities from caa:capability
        - tools from caa:usesTool
        - rule_sets from caa:appliesRules
        """
        pass

class JSONParser(BaseParser):
    """Parser for JSON domain models"""
    
    def parse(self, content: str, file_path: str) -> tuple[dict, DomainModelMetadata]:
        """
        Parse JSON content and extract metadata
        
        Expected JSON structure:
        {
          "domain_id": "...",
          "domain_name": "...",
          "description": "...",
          "version": "...",
          "capabilities": [...],
          "tools": [...],
          "rule_sets": [...],
          "expertise_keywords": [...],
          "content": {...}
        }
        """
        pass

class MarkdownParser(BaseParser):
    """Parser for Markdown domain models"""
    
    def parse(self, content: str, file_path: str) -> tuple[dict, DomainModelMetadata]:
        """
        Parse Markdown content and extract metadata
        
        Extracts metadata from YAML frontmatter:
        ---
        domain_id: ...
        domain_name: ...
        description: ...
        version: ...
        capabilities: [...]
        tools: [...]
        rule_sets: [...]
        expertise_keywords: [...]
        ---
        
        Parses markdown sections into structured content
        """
        pass

class ModelParser:
    """Main parser that delegates to format-specific parsers"""
    
    def __init__(self):
        self.parsers = {
            DomainModelFormat.TURTLE: TurtleParser(),
            DomainModelFormat.JSON: JSONParser(),
            DomainModelFormat.MARKDOWN: MarkdownParser()
        }
    
    def parse(self, content: str, format: DomainModelFormat, file_path: str) -> DomainModel:
        """Parse domain model content using appropriate parser"""
        pass
```

**Parsing Strategy**:
- **Turtle**: Use RDFLib to parse into Graph, extract metadata from RDF triples (Requirements: 1.1, 3.1)
- **JSON**: Parse with `json.loads()`, validate structure, extract metadata from top-level fields (Requirements: 1.2, 3.2)
- **Markdown**: Extract YAML frontmatter for metadata, parse markdown sections for content (Requirements: 1.3, 3.3)
- All parsers extract consistent metadata structure including domain name, description, version (Requirement: 3.4)
- All parsers extract capability metadata: capabilities, tools, rule_sets, expertise_keywords (Requirement: 8.5)
- Return structured error on parse failure with file path, format, and details (Requirement: 3.5)


### 4. Model Validator

**Location**: `backend/domain_model/validator.py`

**Key Classes**:
```python
from jsonschema import validate, ValidationError as JSONSchemaError

class ModelValidator:
    """Validates domain model structure and content"""
    
    def __init__(self, framework_version: str = "1.0.0"):
        self.json_schema = self._load_json_schema()
        self.framework_version = framework_version
        self.supported_version_range = self._parse_version_range()
    
    def validate(self, model: DomainModel) -> ValidationResult:
        """
        Validate a parsed domain model
        
        Checks:
        - Required fields present (domain_id, domain_name, description, version)
        - Version format (semantic versioning)
        - Version compatibility with framework
        - Format-specific validation
        
        Requirements: 4.1, 4.2, 4.5, 9.1, 9.4
        """
        pass
    
    def _validate_required_fields(self, metadata: DomainModelMetadata) -> List[ValidationError]:
        """
        Validate required metadata fields
        
        Requirements: 4.1, 4.2
        """
        pass
    
    def _validate_version_format(self, version: str) -> Optional[ValidationError]:
        """
        Validate semantic versioning format (e.g., 1.0.0)
        
        Requirements: 9.1
        """
        pass
    
    def _validate_version_compatibility(self, version: str) -> Optional[ValidationError]:
        """
        Validate domain model version compatibility with framework
        
        Requirements: 9.4
        """
        pass
    
    def _validate_turtle(self, content: Graph) -> List[ValidationError]:
        """
        Validate Turtle/RDF content
        
        Requirements: 4.3
        """
        pass
    
    def _validate_json(self, content: dict) -> List[ValidationError]:
        """
        Validate JSON content against schema
        
        Requirements: 4.4
        """
        pass
    
    def _validate_markdown(self, content: dict) -> List[ValidationError]:
        """
        Validate Markdown content structure
        
        Requirements: 4.4
        """
        pass
    
    def _parse_version_range(self) -> tuple:
        """Parse supported version range from framework version"""
        pass
    
    def _load_json_schema(self) -> dict:
        """Load JSON schema for domain models"""
        return {
            "type": "object",
            "required": ["domain_id", "domain_name", "description", "version"],
            "properties": {
                "domain_id": {"type": "string", "pattern": "^[a-z0-9-]+$"},
                "domain_name": {"type": "string", "minLength": 1},
                "description": {"type": "string", "minLength": 1},
                "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                "capabilities": {"type": "array", "items": {"type": "string"}},
                "tools": {"type": "array", "items": {"type": "string"}},
                "rule_sets": {"type": "array", "items": {"type": "string"}},
                "expertise_keywords": {"type": "array", "items": {"type": "string"}}
            }
        }
```

**Validation Rules**:
- **Required fields**: domain_id, domain_name, description, version (Requirements: 4.1, 4.2)
- **domain_id**: Lowercase alphanumeric with hyphens (pattern: `^[a-z0-9-]+$`), serves as unique identifier for the domain model (Requirement: 5.1)
- **domain_name**: Non-empty string with minimum length of 1 character (Requirement: 4.1)
- **description**: Non-empty string with minimum length of 1 character (Requirement: 4.2)
- **version**: Semantic versioning format (e.g., 1.0.0) matching pattern `^\d+\.\d+\.\d+$` (Requirement: 9.1)
- **version compatibility**: Must be compatible with framework version (Requirement: 9.4)
- **Turtle**: Valid RDF triples, no parsing errors (Requirement: 4.3)
- **JSON**: Conforms to JSON schema (Requirement: 4.4)
- **Markdown**: Valid YAML frontmatter, structured sections (Requirement: 4.4)

### 5. Model Registry

**Location**: `backend/domain_model/registry.py`

**Key Classes**:
```python
from typing import Dict, List, Optional
from datetime import datetime

class ModelRegistry:
    """Registry of loaded domain models"""
    
    def __init__(self):
        self.models: Dict[str, DomainModel] = {}  # domain_id -> latest model
        self.version_history: Dict[str, Dict[str, DomainModel]] = {}  # domain_id -> {version -> model}
    
    def register(self, model: DomainModel) -> None:
        """
        Register a domain model
        
        Stores model indexed by domain_id and tracks version history.
        Requirements: 5.1, 5.2, 9.2
        """
        pass
    
    def get(self, domain_id: str, version: Optional[str] = None) -> Optional[DomainModel]:
        """
        Get a domain model by ID and optional version
        
        If version is None, returns latest version.
        Requirements: 5.4, 9.3
        """
        pass
    
    def list_all(self) -> List[DomainModelMetadata]:
        """
        List all registered domain models
        
        Requirements: 5.3
        """
        pass
    
    def search(self, query: str) -> List[DomainModelMetadata]:
        """
        Search domain models by name, description, or keywords
        
        Requirements: 5.5
        """
        pass
    
    def get_versions(self, domain_id: str) -> List[str]:
        """
        Get all versions of a domain model
        
        Requirements: 9.2, 9.5
        """
        pass
    
    def unregister(self, domain_id: str, version: Optional[str] = None) -> None:
        """
        Unregister a domain model
        
        If version is None, unregisters all versions.
        """
        pass
    
    def _build_search_index(self, model: DomainModel) -> str:
        """Build searchable text index for a model"""
        pass
```

**Registry Features**:
- Index models by domain_id (unique DomainIdentifier) (Requirement: 5.1)
- Store metadata including file path, format type, load timestamp, and version number (Requirement: 5.2)
- Track version history per domain in version_history dictionary (Requirement: 9.2)
- Support version-specific retrieval using version number parameter (Requirement: 9.3)
- List all registered models returning metadata list (Requirement: 5.3)
- Retrieve specific model by DomainIdentifier (Requirement: 5.4)
- Full-text search across domain name text and description text using search criteria (Requirement: 5.5)
- Retrieve all available version numbers for a specific domain model (Requirement: 9.5)
- Thread-safe operations for concurrent access


### 6. Model Cache

**Location**: `backend/domain_model/cache.py`

**Key Classes**:
```python
from typing import Optional, Dict
from datetime import datetime, timedelta
import threading

class CacheEntry:
    """Cache entry with TTL"""
    model: DomainModel
    cached_at: datetime
    ttl: int  # seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.cached_at + timedelta(seconds=self.ttl)

class CacheStatistics:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    size: int = 0
    
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

class ModelCache:
    """In-memory cache for domain models"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, CacheEntry] = {}
        self.default_ttl = default_ttl
        self.stats = CacheStatistics()
        self.lock = threading.Lock()
    
    def get(self, domain_id: str) -> Optional[DomainModel]:
        """Get a domain model from cache"""
        pass
    
    def put(self, domain_id: str, model: DomainModel, ttl: Optional[int] = None) -> None:
        """Put a domain model in cache"""
        pass
    
    def invalidate(self, domain_id: str) -> None:
        """Invalidate a cache entry"""
        pass
    
    def invalidate_all(self) -> None:
        """Invalidate all cache entries"""
        pass
    
    def get_statistics(self) -> CacheStatistics:
        """Get cache statistics"""
        pass
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        pass
```

**Caching Strategy**:
- Store parsed models in memory after first successful load operation completes (Requirement: 6.1)
- Use domain_id (DomainIdentifier) as unique cache key for storage and retrieval operations (Requirement: 6.2)
- LRU-style cache with configurable time-to-live duration
- Default TTL: 300 seconds (5 minutes) (Requirement: 6.4)
- Thread-safe with locks for concurrent access
- Track and maintain cache hit count and cache miss count as performance statistics (Requirement: 6.5)
- Periodic cleanup of expired entries
- Provide invalidation method to remove cached entries when domain model file is modified (Requirements: 6.3, 7.3)

### 7. Domain Model Framework (Main Interface)

**Location**: `backend/domain_model/framework.py`

**Key Classes**:
```python
from pathlib import Path
from typing import List, Optional
import logging

class DomainModelFramework:
    """Main interface for domain model management"""
    
    def __init__(self, base_dir: Path = Path(".mcp/domain-models"), framework_version: str = "1.0.0"):
        self.loader = ModelLoader(base_dir)
        self.parser = ModelParser()
        self.validator = ModelValidator(framework_version)
        self.registry = ModelRegistry()
        self.cache = ModelCache()
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "load_count": 0,
            "parse_error_count": 0,
            "validation_error_count": 0
        }
    
    async def load_domain_model(self, file_path: str) -> DomainModel:
        """
        Load, parse, validate, and register a domain model
        
        Steps:
        1. Check cache
        2. Load file
        3. Parse content
        4. Validate model
        5. Register model
        6. Cache model
        7. Return model
        
        Logs all operations and tracks metrics.
        Requirements: 10.1, 10.2, 10.3, 10.4
        """
        pass
    
    async def load_multiple_domain_models(self, file_paths: List[str]) -> List[DomainModel]:
        """
        Load multiple domain models concurrently
        
        Requirements: 2.5
        """
        pass
    
    async def reload_domain_model(self, domain_id: str, version: Optional[str] = None) -> DomainModel:
        """
        Reload a domain model (invalidate cache and reload)
        
        Requirements: 7.1, 7.3, 7.4, 7.5
        """
        pass
    
    async def reload_all_domain_models(self) -> List[DomainModel]:
        """
        Reload all registered domain models
        
        Requirements: 7.2, 7.3, 7.4, 7.5
        """
        pass
    
    def get_domain_model(self, domain_id: str, version: Optional[str] = None) -> Optional[DomainModel]:
        """
        Get a domain model from registry (uses cache)
        
        Requirements: 5.4, 9.3
        """
        pass
    
    def list_domain_models(self) -> List[DomainModelMetadata]:
        """
        List all registered domain models
        
        Requirements: 5.3
        """
        pass
    
    def search_domain_models(self, query: str) -> List[DomainModelMetadata]:
        """
        Search domain models
        
        Requirements: 5.5
        """
        pass
    
    def get_versions(self, domain_id: str) -> List[str]:
        """
        Get all available versions for a specific domain model
        
        Requirements: 9.5
        """
        pass
    
    def get_cache_statistics(self) -> CacheStatistics:
        """
        Get cache statistics
        
        Requirements: 6.5, 10.5
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get framework metrics for monitoring
        
        Returns metrics including:
        - domain_model_load_count: Total successful loads
        - parse_error_count: Total parse errors
        - validation_error_count: Total validation errors
        - cache_hit_rate: Cache hit rate percentage
        - cache_size: Current cache size
        - registered_models_count: Number of registered models
        
        Requirements: 10.4, 10.5
        """
        pass
```

**Framework Workflow**:
```
load_domain_model(file_path)
    │
    ├─> Check cache
    │   └─> If hit: return cached model
    │
    ├─> Load file (ModelLoader)
    │   └─> Detect format
    │   └─> Read content
    │
    ├─> Parse content (ModelParser)
    │   └─> Format-specific parsing
    │   └─> Extract metadata
    │
    ├─> Validate model (ModelValidator)
    │   └─> Check required fields
    │   └─> Format-specific validation
    │   └─> If invalid: raise error
    │
    ├─> Register model (ModelRegistry)
    │   └─> Index by domain_id
    │   └─> Track version
    │
    ├─> Cache model (ModelCache)
    │   └─> Store with TTL
    │
    └─> Return model
```


## Data Models

### Example Turtle Domain Model

```turtle
@prefix caa: <http://nkllon.com/ontology/caa#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dct: <http://purl.org/dc/terms/> .

caa:tools-domain a caa:DomainModel ;
  rdfs:label "Tools Domain" ;
  rdfs:comment "Domain model for tool execution and validation" ;
  caa:version "1.0.0" ;
  caa:capability "tool_execution", "validation" ;
  caa:usesTool "tool_adapter_1", "tool_adapter_2" ;
  caa:appliesRules "validation_rules", "safety_rules" ;
  caa:expertiseKeyword "tools", "execution", "validation" .
```

### Example JSON Domain Model

```json
{
  "domain_id": "tools-domain",
  "domain_name": "Tools Domain",
  "description": "Domain model for tool execution and validation",
  "version": "1.0.0",
  "capabilities": ["tool_execution", "validation"],
  "tools": ["tool_adapter_1", "tool_adapter_2"],
  "rule_sets": ["validation_rules", "safety_rules"],
  "expertise_keywords": ["tools", "execution", "validation"],
  "content": {
    "stakeholder_perspective": "Tool execution specialist",
    "domain_constraints": {
      "max_execution_time": 30,
      "allowed_operations": ["read", "execute", "validate"]
    }
  }
}
```

### Example Markdown Domain Model

```markdown
---
domain_id: tools-domain
domain_name: Tools Domain
description: Domain model for tool execution and validation
version: 1.0.0
capabilities:
  - tool_execution
  - validation
tools:
  - tool_adapter_1
  - tool_adapter_2
rule_sets:
  - validation_rules
  - safety_rules
expertise_keywords:
  - tools
  - execution
  - validation
---

# Tools Domain Model

## Stakeholder Perspective

As a tool execution specialist, I focus on...

## Domain Constraints

- Maximum execution time: 30 seconds
- Allowed operations: read, execute, validate

## Capabilities

### Tool Execution
...

### Validation
...
```

## Error Handling

### Error Categories

1. **File Not Found**
   - File path doesn't exist at specified location
   - **Handling**: Raise `FileNotFoundError` with error message containing the attempted file path
   - **Requirements**: 2.3

2. **Unsupported Format**
   - File extension not .ttl, .json, or .md
   - **Handling**: Raise `ValueError` with error message listing Turtle, JSON, and Markdown as supported formats
   - **Requirements**: 1.5

3. **Parse Error**
   - Invalid Turtle/JSON/Markdown syntax
   - **Handling**: Raise `ParseError` with structured error containing file path, detected format, and specific error details
   - **Requirements**: 3.5

4. **Validation Error**
   - Missing required fields (domain_id, domain_name, description, version)
   - Invalid field values or format violations
   - **Handling**: Return `ValidationResult` containing field names and specific error messages
   - **Requirements**: 4.1, 4.2, 4.5

5. **Version Incompatibility Error**
   - Domain model version incompatible with framework version
   - **Handling**: Raise `VersionIncompatibilityError` with error message containing domain model version and framework version details
   - **Requirements**: 9.4

6. **Cache Error**
   - Cache corruption or inconsistency
   - **Handling**: Log error, invalidate cache, reload from source

### Error Response Format

```python
class DomainModelError(Exception):
    """Base exception for domain model errors"""
    def __init__(self, message: str, details: Dict[str, Any]):
        self.message = message
        self.details = details
        super().__init__(message)

class FileLoadError(DomainModelError):
    """Error loading domain model file"""
    pass

class ParseError(DomainModelError):
    """Error parsing domain model content"""
    pass

class ValidationError(DomainModelError):
    """Error validating domain model"""
    pass

class VersionIncompatibilityError(DomainModelError):
    """Error when domain model version is incompatible with framework"""
    pass
```

## Testing Strategy

### Unit Tests

**Location**: `backend/tests/domain_model/`

**Coverage**:
1. **Loader Tests** (`test_loader.py`)
   - Load valid files (all formats)
   - Handle missing files
   - Detect formats correctly
   - Resolve paths correctly

2. **Parser Tests** (`test_parser.py`)
   - Parse Turtle correctly
   - Parse JSON correctly
   - Parse Markdown correctly
   - Extract metadata correctly
   - Handle parse errors

3. **Validator Tests** (`test_validator.py`)
   - Validate required fields
   - Validate version format
   - Format-specific validation
   - Return validation errors

4. **Registry Tests** (`test_registry.py`)
   - Register models
   - Retrieve models
   - List models
   - Search models
   - Version tracking

5. **Cache Tests** (`test_cache.py`)
   - Cache hit/miss
   - TTL expiration
   - Invalidation
   - Statistics

6. **Framework Tests** (`test_framework.py`)
   - End-to-end load
   - Reload models
   - Concurrent loading
   - Error handling

### Test Fixtures

**Location**: `backend/tests/fixtures/domain_models/`

- `valid_turtle.ttl` - Valid Turtle domain model
- `valid_json.json` - Valid JSON domain model
- `valid_markdown.md` - Valid Markdown domain model
- `invalid_turtle.ttl` - Invalid Turtle syntax
- `invalid_json.json` - Invalid JSON structure
- `missing_fields.json` - Missing required fields

## Metrics and Monitoring

### Metrics Collection

The framework tracks the following metrics for monitoring and troubleshooting:

**Load Metrics** (Requirement: 10.4):
- `domain_model_load_count`: Total number of successful domain model load operations
- `parse_error_count`: Total number of parsing errors encountered
- `validation_error_count`: Total number of validation errors encountered

**Cache Metrics** (Requirement: 10.5):
- `cache_hit_rate`: Cache hit rate percentage (hits / total requests)
- `cache_size`: Current cache size count (number of models in cache)

**Registry Metrics**:
- `registered_models_count`: Total number of registered domain models in the registry

### Logging Strategy

The framework logs all significant operations (Requirements: 10.1, 10.2, 10.3):

**Load Operations** (Requirement: 10.1):
- Log level: INFO
- Message: "Loading domain model from {file_path}" / "Successfully loaded domain model {domain_id}"
- Include: file path and completion status

**Parse Errors** (Requirement: 10.2):
- Log level: ERROR
- Message: "Parse error for {file_path}"
- Include: file path and specific error details

**Validation Errors** (Requirement: 10.3):
- Log level: ERROR
- Message: "Validation error for {domain_id}"
- Include: DomainIdentifier and specific error details

**Cache Operations**:
- Log level: DEBUG
- Message: "Cache hit for {domain_id}" / "Cache miss for {domain_id}"
- Include: domain_id

**Reload Operations** (Requirements: 7.1, 7.2):
- Log level: INFO
- Message: "Reloading domain model {domain_id}" / "Reloading all domain models"
- Include: domain_id (if specific), completion status

### Metrics Export

The `get_metrics()` method returns a dictionary with all operational and performance metrics (Requirements: 10.4, 10.5):

```python
{
    "domain_model_load_count": 42,      # Total successful loads
    "parse_error_count": 2,              # Total parse errors
    "validation_error_count": 1,         # Total validation errors
    "cache_hit_rate": 0.85,              # Cache hit rate (85%)
    "cache_size": 15,                    # Current models in cache
    "registered_models_count": 20        # Total registered models
}
```

## Performance Considerations

### Caching Strategy
- Cache parsed models in memory after first successful load
- Default TTL: 300 seconds (configurable)
- Invalidate on reload to ensure consistency
- Track hit rate for monitoring cache effectiveness

### Async Operations
- Use `asyncio` for file I/O operations (Requirement: 2.5)
- Concurrent loading of multiple domain models
- Non-blocking operations to improve throughput

### Memory Management
- Limit cache size (configurable maximum entries)
- Periodic cleanup of expired entries
- Weak references for large RDF graphs to allow garbage collection

## Security Considerations

### File Access
- Restrict file loading to configured base directory
- Validate and sanitize file paths (prevent directory traversal attacks)
- Read-only access to domain model files
- Resolve both absolute and relative paths safely (Requirement: 2.2)

### Content Validation
- Validate all inputs before processing
- Sanitize file paths and domain identifiers
- Limit file size to prevent resource exhaustion (default: 10MB)
- Validate UTF-8 encoding (Requirement: 2.4)

## Deployment Strategy

### Phase 1: Standalone Implementation
- Implement framework as independent module in `backend/domain_model/`
- Unit tests with comprehensive fixtures
- No external service dependencies

### Phase 2: Integration with Backend
- Add to FastAPI backend application
- Expose via API endpoints (optional for external access)
- Integration tests with backend services

### Phase 3: MCP Integration
- Use in MCP configuration manager for domain model registration
- Use in reasoning services for domain-specific capabilities
- End-to-end tests with orchestrator and domain models

## Future Enhancements

### Remote Loading
- Load domain models from URLs (HTTP/HTTPS)
- Support for Git repositories (clone and load)
- Version control integration for automatic updates

### Hot Reload
- Watch file system for changes using file system events
- Auto-reload on modification without manual trigger
- Notify dependent services of model updates

### Schema Evolution
- Support schema migrations for domain model format changes
- Backward compatibility with older versions
- Version negotiation between framework and models

### Advanced Validation
- SHACL validation for Turtle format (semantic validation)
- Custom validation rules per domain
- Semantic validation beyond structural checks

### Performance Optimization
- Lazy loading of domain model content
- Streaming parser for large files
- Distributed caching for multi-instance deploymentsading domain model from {file_path}"
- Include: file_path, completion status

**Parse Errors** (Requirement: 10.2):
- Log level: ERROR
- Message: "Parse error for {file_path}"
- Include: file_path, format, specific error details

**Validation Errors** (Requirement: 10.3):
- Log level: ERROR
- Message: "Validation error for {domain_id}"
- Include: domain_id, specific error details

**Cache Operations**:
- Log level: DEBUG
- Message: "Cache hit/miss for {domain_id}"

### Metrics Export

The `get_metrics()` method returns a dictionary with all metrics:

```python
{
    "domain_model_load_count": 42,
    "parse_error_count": 2,
    "validation_error_count": 1,
    "cache_hit_rate": 0.85,
    "cache_size": 15,
    "registered_models_count": 20
}
```

## Performance Considerations

### Caching Strategy
- Cache parsed models in memory
- Default TTL: 300 seconds
- Invalidate on reload
- Track hit rate

### Async Operations
- Use `asyncio` for file I/O
- Concurrent loading of multiple models
- Non-blocking operations

### Memory Management
- Limit cache size (configurable)
- Periodic cleanup of expired entries
- Weak references for large graphs

## Security Considerations

### File Access
- Restrict to configured base directory
- Validate file paths (no directory traversal)
- Read-only access

### Content Validation
- Validate all inputs
- Sanitize file paths
- Limit file size (default: 10MB)

## Deployment Strategy

### Phase 1: Standalone Implementation
- Implement framework as independent module
- Unit tests with fixtures
- No external dependencies

### Phase 2: Integration with Backend
- Add to FastAPI backend
- Expose via API endpoints (optional)
- Integration tests

### Phase 3: MCP Integration
- Use in MCP configuration manager
- Use in reasoning services
- End-to-end tests

## Future Enhancements

### Remote Loading
- Load domain models from URLs
- Support for Git repositories
- Version control integration

### Hot Reload
- Watch file system for changes
- Auto-reload on modification
- Notify dependent services

### Schema Evolution
- Support schema migrations
- Backward compatibility
- Version negotiation

### Advanced Validation
- SHACL validation for Turtle
- Custom validation rules
- Semantic validation
