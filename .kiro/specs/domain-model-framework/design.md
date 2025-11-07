# Design Document

## Overview

This design document describes the implementation of the Domain Model Framework for the Composable AI Advisors system. The Domain Model Framework is the foundational infrastructure that enables loading, parsing, validating, and managing domain model files. Domain models are static, machine-readable descriptions (in Turtle, JSON, or Markdown format) that LLMs use to assume stakeholder positions for specific domains.

The framework provides a clean abstraction layer between domain model files and the services that consume them (orchestrator, reasoning services, MCP layer). It handles format detection, parsing, validation, caching, and registry management.

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
- Use `aiofiles` for async file I/O
- Support both absolute paths and paths relative to base_dir
- Detect format by extension: `.ttl` → TURTLE, `.json` → JSON, `.md` → MARKDOWN
- Read files as UTF-8
- Raise clear errors for missing files or unsupported formats


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
- **Turtle**: Use RDFLib to parse into Graph, extract metadata from RDF triples
- **JSON**: Parse with `json.loads()`, validate structure, extract metadata from top-level fields
- **Markdown**: Extract YAML frontmatter for metadata, parse markdown sections for content
- All parsers extract consistent metadata structure


### 4. Model Validator

**Location**: `backend/domain_model/validator.py`

**Key Classes**:
```python
from jsonschema import validate, ValidationError as JSONSchemaError

class ModelValidator:
    """Validates domain model structure and content"""
    
    def __init__(self):
        self.json_schema = self._load_json_schema()
    
    def validate(self, model: DomainModel) -> ValidationResult:
        """
        Validate a parsed domain model
        
        Checks:
        - Required fields present (domain_id, domain_name, description, version)
        - Version format (semantic versioning)
        - Format-specific validation
        """
        pass
    
    def _validate_required_fields(self, metadata: DomainModelMetadata) -> List[ValidationError]:
        """Validate required metadata fields"""
        pass
    
    def _validate_version_format(self, version: str) -> Optional[ValidationError]:
        """Validate semantic versioning format (e.g., 1.0.0)"""
        pass
    
    def _validate_turtle(self, content: Graph) -> List[ValidationError]:
        """Validate Turtle/RDF content"""
        pass
    
    def _validate_json(self, content: dict) -> List[ValidationError]:
        """Validate JSON content against schema"""
        pass
    
    def _validate_markdown(self, content: dict) -> List[ValidationError]:
        """Validate Markdown content structure"""
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
- **Required fields**: domain_id, domain_name, description, version
- **domain_id**: Lowercase alphanumeric with hyphens
- **version**: Semantic versioning (e.g., 1.0.0)
- **Turtle**: Valid RDF triples, no parsing errors
- **JSON**: Conforms to JSON schema
- **Markdown**: Valid YAML frontmatter, structured sections

### 5. Model Registry

**Location**: `backend/domain_model/registry.py`

**Key Classes**:
```python
from typing import Dict, List, Optional
from datetime import datetime

class ModelRegistry:
    """Registry of loaded domain models"""
    
    def __init__(self):
        self.models: Dict[str, DomainModel] = {}
        self.version_history: Dict[str, List[str]] = {}  # domain_id -> [versions]
    
    def register(self, model: DomainModel) -> None:
        """Register a domain model"""
        pass
    
    def get(self, domain_id: str, version: Optional[str] = None) -> Optional[DomainModel]:
        """Get a domain model by ID and optional version"""
        pass
    
    def list_all(self) -> List[DomainModelMetadata]:
        """List all registered domain models"""
        pass
    
    def search(self, query: str) -> List[DomainModelMetadata]:
        """Search domain models by name, description, or keywords"""
        pass
    
    def get_versions(self, domain_id: str) -> List[str]:
        """Get all versions of a domain model"""
        pass
    
    def unregister(self, domain_id: str) -> None:
        """Unregister a domain model"""
        pass
    
    def _build_search_index(self, model: DomainModel) -> str:
        """Build searchable text index for a model"""
        pass
```

**Registry Features**:
- Index models by domain_id
- Track version history per domain
- Support version-specific retrieval
- Full-text search across name, description, keywords
- Thread-safe operations


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
- LRU-style cache with TTL
- Default TTL: 300 seconds (5 minutes)
- Thread-safe with locks
- Track hit/miss statistics
- Periodic cleanup of expired entries
- Invalidation on reload

### 7. Domain Model Framework (Main Interface)

**Location**: `backend/domain_model/framework.py`

**Key Classes**:
```python
from pathlib import Path
from typing import List, Optional
import logging

class DomainModelFramework:
    """Main interface for domain model management"""
    
    def __init__(self, base_dir: Path = Path(".mcp/domain-models")):
        self.loader = ModelLoader(base_dir)
        self.parser = ModelParser()
        self.validator = ModelValidator()
        self.registry = ModelRegistry()
        self.cache = ModelCache()
        self.logger = logging.getLogger(__name__)
    
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
        """
        pass
    
    async def load_multiple_domain_models(self, file_paths: List[str]) -> List[DomainModel]:
        """Load multiple domain models concurrently"""
        pass
    
    async def reload_domain_model(self, domain_id: str) -> DomainModel:
        """Reload a domain model (invalidate cache and reload)"""
        pass
    
    async def reload_all_domain_models(self) -> List[DomainModel]:
        """Reload all registered domain models"""
        pass
    
    def get_domain_model(self, domain_id: str, version: Optional[str] = None) -> Optional[DomainModel]:
        """Get a domain model from registry (uses cache)"""
        pass
    
    def list_domain_models(self) -> List[DomainModelMetadata]:
        """List all registered domain models"""
        pass
    
    def search_domain_models(self, query: str) -> List[DomainModelMetadata]:
        """Search domain models"""
        pass
    
    def get_cache_statistics(self) -> CacheStatistics:
        """Get cache statistics"""
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
   - File path doesn't exist
   - **Handling**: Raise `FileNotFoundError` with path

2. **Unsupported Format**
   - File extension not .ttl, .json, or .md
   - **Handling**: Raise `ValueError` with supported formats

3. **Parse Error**
   - Invalid Turtle/JSON/Markdown syntax
   - **Handling**: Raise `ParseError` with details

4. **Validation Error**
   - Missing required fields
   - Invalid field values
   - **Handling**: Return `ValidationResult` with errors

5. **Cache Error**
   - Cache corruption
   - **Handling**: Log error, invalidate cache, reload

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
