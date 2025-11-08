# MCP Implementation — Design

Relates to: MCP-REQ-001…MCP-REQ-006

1. Config Path Resolution
   - Read `MCP_CONFIG_PATH` env; if set, use that absolute/relative path.
   - Else default to repo-root `/.mcp/config.json` resolved from `backend/mcp/config.py` using `Path(__file__).resolve().parents[2]`.
   - Same pattern for `MCP_DOMAIN_MODELS_DIR` (REQ-002).

2. Lifespan Events
   - Replace `@on_event("startup")` with FastAPI lifespan context.
   - During lifespan: async load config + optional preload.
   - For tests: ensure endpoints lazily trigger `_ensure_loaded()` to avoid reliance on app startup hooks (REQ-003, REQ-004).

3. Preload Behavior
   - Preload only when config `domain_models.preload == true`.
   - Tests provide a temporary config and domain models; avoid hidden sample auto-load in production (REQ-004, REQ-006).

4. Defaults and Root Resolution
   - Defaults computed from repo-root so CI/test working dirs don’t break (REQ-005).
   - Keep sample files for tests only; guard any sample loading path behind test/dev flags (REQ-006).

# Design Document

## Overview

This design document describes the implementation of the Model Context Protocol (MCP) layer for the Composable AI Advisors system. The MCP layer is the critical infrastructure that enables the multi-agent mesh architecture by providing secure context exchange, tool sharing, and traceability between the orchestrator and domain-specific reasoning services.

The design follows the bow-tie pattern where a general-purpose orchestrator LLM is constrained by models (static RDF/Turtle, JSON, or Markdown files) and coordinates independent reasoning services. Each reasoning service uses domain models (static, machine-readable files) to constrain its LLM for domain-specific behavior. The MCP layer sits between these components, managing all inter-agent communication while maintaining service boundaries and audit trails.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Orchestrator Service                       │
│   (General-Purpose LLM + Model Constraints)            │
│   - Task decomposition                                  │
│   - Reasoning service routing                           │
│   - Result synthesis                                    │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              MCP Layer (NEW)                            │
│   ┌─────────────────────────────────────────────────┐  │
│   │  MCP Server Registry                            │  │
│   │  - Reasoning service discovery                  │  │
│   │  - Domain model metadata                        │  │
│   │  - Capability metadata                          │  │
│   │  - Health monitoring                            │  │
│   └─────────────────────────────────────────────────┘  │
│   ┌─────────────────────────────────────────────────┐  │
│   │  Context Exchange Protocol                      │  │
│   │  - Spore transmission                           │  │
│   │  - Task routing                                 │  │
│   │  - Response handling                            │  │
│   └─────────────────────────────────────────────────┘  │
│   ┌─────────────────────────────────────────────────┐  │
│   │  Trace & Audit Layer                            │  │
│   │  - Provenance tracking                          │  │
│   │  - Interaction logging                          │  │
│   │  - RDF/Turtle storage                           │  │
│   └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Reasoning   │ │  Reasoning   │ │  Reasoning   │
│  Service A   │ │  Service B   │ │  Service C   │
│ (MCP Server) │ │ (MCP Server) │ │ (MCP Server) │
│              │ │              │ │              │
│ Domain Model │ │ Domain Model │ │ Domain Model │
│ (static .ttl)│ │ (static .ttl)│ │ (static .ttl)│
│ - Tools      │ │ - Tools      │ │ - Tools      │
│ - Rules      │ │ - Rules      │ │ - Rules      │
│ - LLM        │ │ - LLM        │ │ - LLM        │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Integration with Existing System

The MCP layer integrates with the existing FastAPI backend:

```
┌─────────────────────────────────────────────────────────┐
│         Existing FastAPI Backend                        │
│   /api/pods          - Plans of Day                     │
│   /api/spores        - Spore registry                   │
│   /api/pods/generate - AI generation                    │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         NEW: MCP API Endpoints                          │
│   /api/mcp/servers          - Server registry           │
│   /api/mcp/servers/{id}     - Server details            │
│   /api/mcp/servers/{id}/domain-model - Domain model     │
│   /api/mcp/servers/{id}/tools - Tools manifest          │
│   /api/mcp/servers/{id}/rules - Rules manifest          │
│   /api/mcp/health           - Health check              │
│   /api/mcp/context/exchange - Context exchange          │
│   /api/mcp/tools/invoke     - Tool invocation           │
│   /api/mcp/rules/evaluate   - Rule evaluation           │
│   /api/mcp/trace            - Trace query               │
│   /api/mcp/metrics          - Prometheus metrics        │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

The MCP layer uses a structured directory layout in `.mcp/`:

```
.mcp/
├── config.json                          # Main MCP configuration
├── servers/                             # Server definitions
│   ├── reasoning-service-a.json         # Server config
│   ├── reasoning-service-a-tools.json   # Tools manifest
│   ├── reasoning-service-a-rules.json   # Rules manifest
│   └── ...
├── domain-models/                       # Domain model files
│   ├── tools-domain.ttl                 # RDF/Turtle domain model
│   ├── investments-domain.json          # JSON domain model
│   └── cognition-domain.md              # Markdown domain model
├── tools/                               # Tool adapter definitions
│   └── .gitkeep
├── context/                             # Context storage
│   └── .gitkeep
└── traces/                              # Trace storage (optional)
    └── mcp_traces.ttl
```

**Design Rationale**: This structure separates concerns (configuration, domain models, tools, context) and supports multiple reasoning services with their associated artifacts. The `servers/` directory contains per-service configuration files, enabling independent management of each reasoning service.

## Components and Interfaces

### 1. MCP Configuration Manager

**Purpose**: Manages MCP server configurations, domain model references, and registry

**Location**: `backend/mcp/config_manager.py`

**Key Classes**:
```python
class MCPServerConfig(BaseModel):
    """Configuration for an MCP server (reasoning service)"""
    server_id: str
    name: str
    domain: str
    domain_model_path: str  # Path to static domain model file (.ttl, .json, .md)
    endpoint: str
    capabilities: List[str]
    tools: List[str]
    rules: List[str]
    enabled: bool
    health_check_url: str
    timeout: int = 30

class MCPConfigManager:
    """Manages MCP server configurations and domain models"""
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.servers: Dict[str, MCPServerConfig] = {}
        self.domain_models: Dict[str, str] = {}  # server_id -> domain_model_content
    
    def load_config(self) -> None:
        """Load configuration from .mcp/config.json"""
        pass
    
    def load_domain_model(self, model_path: str) -> str:
        """Load domain model file content"""
        pass
    
    def register_server(self, config: MCPServerConfig) -> None:
        """Register a new MCP server with its domain model"""
        pass
    
    def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        """Get server configuration by ID"""
        pass
    
    def get_domain_model(self, server_id: str) -> Optional[str]:
        """Get domain model content for a server"""
        pass
    
    def list_servers(self, 
                     enabled_only: bool = True,
                     domain: Optional[str] = None,
                     capability: Optional[str] = None) -> List[MCPServerConfig]:
        """List all registered servers with optional filtering"""
        pass
    
    def update_server_status(self, server_id: str, enabled: bool) -> None:
        """Enable or disable a server"""
        pass
    
    def reload_domain_model(self, server_id: str) -> None:
        """Reload domain model file for a server without restart"""
        pass
    
    def validate_server_config(self, config: MCPServerConfig) -> bool:
        """Validate server configuration against schema"""
        pass
    
    def save_server_definition(self, config: MCPServerConfig) -> None:
        """Save server definition to .mcp/servers/{server_id}.json"""
        pass
```

**Configuration File Structure** (`.mcp/config.json`):
```json
{
  "version": "1.0.0",
  "servers": [
    {
      "server_id": "reasoning-service-a",
      "name": "Tools Domain Reasoning Service",
      "domain": "tools",
      "domain_model_path": ".mcp/domain-models/tools-domain.ttl",
      "endpoint": "http://localhost:8081",
      "capabilities": ["tool_execution", "validation"],
      "tools": ["tool_adapter_1", "tool_adapter_2"],
      "rules": ["validation_rules", "safety_rules"],
      "enabled": true,
      "health_check_url": "http://localhost:8081/health",
      "timeout": 30,
      "command": "python",
      "args": ["-m", "reasoning_service"],
      "env": {
        "DOMAIN_MODEL": ".mcp/domain-models/tools-domain.ttl"
      }
    }
  ],
  "trace_config": {
    "enabled": true,
    "storage_path": "mcp_traces.ttl",
    "retention_days": 90
  },
  "orchestrator": {
    "confidence_threshold": 0.9,
    "model_constraints_path": "caa-glossary.ttl"
  }
}
```

**Server Definition Files** (`.mcp/servers/{server_id}.json`):

Each registered reasoning service also has a dedicated configuration file in `.mcp/servers/` for detailed server-specific settings:

```json
{
  "server_id": "reasoning-service-a",
  "name": "Tools Domain Reasoning Service",
  "domain": "tools",
  "domain_model_path": ".mcp/domain-models/tools-domain.ttl",
  "endpoint": "http://localhost:8081",
  "capabilities": ["tool_execution", "validation"],
  "tools_manifest": ".mcp/servers/reasoning-service-a-tools.json",
  "rules_manifest": ".mcp/servers/reasoning-service-a-rules.json",
  "enabled": true,
  "health_check_url": "http://localhost:8081/health",
  "timeout": 30,
  "command": "python",
  "args": ["-m", "reasoning_service"],
  "env": {
    "DOMAIN_MODEL": ".mcp/domain-models/tools-domain.ttl"
  },
  "metadata": {
    "version": "1.0.0",
    "description": "Reasoning service for tools domain",
    "maintainer": "team@example.com"
  }
}
```

**Design Rationale**: Separating server definitions into individual files in `.mcp/servers/` allows for easier management of multiple reasoning services, supports dynamic registration, and enables version control of individual service configurations without affecting the main config file.

### 2. Context Exchange Service

**Purpose**: Handles secure context transmission between orchestrator and domain models

**Location**: `backend/mcp/context_exchange.py`

**Key Classes**:
```python
class ContextPayload(BaseModel):
    """Context payload for MCP exchange"""
    context_id: str
    source_agent: str
    target_agent: str
    spore: Optional[Dict[str, Any]] = None
    task: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime

class ContextExchangeService:
    """Manages context exchange via MCP"""
    def __init__(self, config_manager: MCPConfigManager, trace_service: TraceService):
        self.config_manager = config_manager
        self.trace_service = trace_service
    
    async def send_context(self, payload: ContextPayload) -> Dict[str, Any]:
        """Send context to a domain model"""
        pass
    
    async def receive_response(self, context_id: str) -> Dict[str, Any]:
        """Receive response from domain model"""
        pass
    
    def validate_context(self, payload: ContextPayload) -> bool:
        """Validate context structure"""
        pass
```

**Context Exchange Protocol**:
- Uses HTTP POST for synchronous exchanges
- Supports WebSocket for asynchronous/streaming exchanges
- Includes retry logic with exponential backoff
- Validates payloads against JSON schemas

### 3. Trace and Audit Service

**Purpose**: Records all MCP interactions for provenance and audit

**Location**: `backend/mcp/trace_service.py`

**Key Classes**:
```python
class TraceRecord(BaseModel):
    """Record of an MCP interaction"""
    trace_id: str
    parent_trace_id: Optional[str]
    source_agent: str
    target_agent: str
    interaction_type: str  # "context_exchange", "tool_invocation", etc.
    timestamp: datetime
    payload_summary: Dict[str, Any]
    response_summary: Dict[str, Any]
    status: str  # "success", "error", "timeout"
    duration_ms: int

class TraceService:
    """Manages trace and audit records"""
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.graph = Graph()
    
    def record_interaction(self, record: TraceRecord) -> None:
        """Record an interaction in RDF/Turtle"""
        pass
    
    def query_traces(self, 
                     agent: Optional[str] = None,
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None) -> List[TraceRecord]:
        """Query trace records"""
        pass
    
    def get_trace_chain(self, trace_id: str) -> List[TraceRecord]:
        """Get full trace chain for a given trace ID"""
        pass
```

**Trace RDF Schema**:
```turtle
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix caa:  <http://nkllon.com/ontology/caa#> .
@prefix mcp: <http://nkllon.com/ontology/mcp#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

mcp:TraceRecord a owl:Class ;
  rdfs:label "MCP Trace Record" ;
  rdfs:comment "Record of an MCP interaction" .

mcp:traceId a owl:DatatypeProperty ;
  rdfs:domain mcp:TraceRecord ;
  rdfs:range xsd:string .

mcp:sourceAgent a owl:ObjectProperty ;
  rdfs:domain mcp:TraceRecord ;
  rdfs:range caa:Orchestrator, caa:DomainModel .

mcp:targetAgent a owl:ObjectProperty ;
  rdfs:domain mcp:TraceRecord ;
  rdfs:range caa:DomainModel .
```

### 4. Tool Adapter Registry

**Purpose**: Manages tool adapters exposed by reasoning services

**Location**: `backend/mcp/tool_adapter.py`

**Tools Manifest Structure** (`.mcp/servers/{server_id}-tools.json`):

Each reasoning service declares its available tools in a manifest file:

```json
{
  "server_id": "reasoning-service-a",
  "tools": [
    {
      "tool_id": "tool_adapter_1",
      "name": "Data Validator",
      "description": "Validates data against domain-specific rules",
      "input_schema": {
        "type": "object",
        "properties": {
          "data": {"type": "object"},
          "rules": {"type": "array"}
        },
        "required": ["data"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "valid": {"type": "boolean"},
          "errors": {"type": "array"}
        }
      },
      "timeout": 30,
      "invocation_method": "POST",
      "endpoint": "/tools/validate"
    }
  ]
}
```

**Design Rationale**: Separating tool definitions into manifest files allows reasoning services to declare their capabilities independently, supports dynamic tool registration, and enables validation of tool schemas before invocation.

**Key Classes**:
```python
class ToolDefinition(BaseModel):
    """Definition of a tool adapter"""
    tool_id: str
    name: str
    description: str
    reasoning_service_id: str
    domain: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    timeout: int = 30

class ToolAdapterRegistry:
    """Registry of available tool adapters"""
    def __init__(self, config_manager: MCPConfigManager):
        self.config_manager = config_manager
        self.tools: Dict[str, ToolDefinition] = {}
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool adapter for a reasoning service"""
        pass
    
    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition"""
        pass
    
    def list_tools_for_service(self, service_id: str) -> List[ToolDefinition]:
        """List tools for a specific reasoning service"""
        pass
    
    def list_tools_for_domain(self, domain: str) -> List[ToolDefinition]:
        """List tools for a specific domain"""
        pass
    
    async def invoke_tool(self, tool_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a tool adapter"""
        pass
```

### 5. Rule Set Manager

**Purpose**: Manages rule sets for domain-specific constraints and policies

**Location**: `backend/mcp/rule_manager.py`

**Rules Manifest Structure** (`.mcp/servers/{server_id}-rules.json`):

Each reasoning service declares its rule sets in a manifest file:

```json
{
  "server_id": "reasoning-service-a",
  "rule_sets": [
    {
      "rule_id": "validation_rules",
      "name": "Data Validation Rules",
      "description": "Rules for validating input data",
      "type": "validation",
      "priority": 100,
      "format": "json_schema",
      "rules": [
        {
          "rule_name": "required_fields",
          "condition": "data must contain required fields",
          "action": "reject",
          "error_message": "Missing required fields: {fields}"
        }
      ]
    },
    {
      "rule_id": "safety_rules",
      "name": "Safety Rules",
      "description": "Rules for ensuring safe operations",
      "type": "safety",
      "priority": 200,
      "format": "declarative",
      "rules": [
        {
          "rule_name": "no_destructive_ops",
          "condition": "operation.type != 'delete'",
          "action": "require_confirmation",
          "error_message": "Destructive operation requires confirmation"
        }
      ]
    }
  ]
}
```

**Design Rationale**: Rule sets enable domain-specific constraints to be enforced before task execution. The priority-based system allows for conflict resolution when multiple rules apply. Supporting multiple rule formats (JSON Schema, declarative, SHACL) provides flexibility for different use cases.

**Key Classes**:
```python
class RuleDefinition(BaseModel):
    """Definition of a single rule"""
    rule_name: str
    condition: str
    action: str  # "reject", "require_confirmation", "warn", "allow"
    error_message: str
    priority: int = 100

class RuleSet(BaseModel):
    """Collection of related rules"""
    rule_id: str
    name: str
    description: str
    type: str  # "validation", "policy", "routing", "safety"
    priority: int
    format: str  # "json_schema", "declarative", "shacl"
    rules: List[RuleDefinition]

class RuleManager:
    """Manages rule sets for reasoning services"""
    def __init__(self, config_manager: MCPConfigManager):
        self.config_manager = config_manager
        self.rule_sets: Dict[str, RuleSet] = {}
    
    def load_rules_manifest(self, server_id: str) -> None:
        """Load rules manifest for a reasoning service"""
        pass
    
    def register_rule_set(self, rule_set: RuleSet) -> None:
        """Register a rule set"""
        pass
    
    def get_rule_set(self, rule_id: str) -> Optional[RuleSet]:
        """Get rule set by ID"""
        pass
    
    def list_rule_sets_for_service(self, service_id: str) -> List[RuleSet]:
        """List rule sets for a specific reasoning service"""
        pass
    
    def evaluate_rules(self, rule_ids: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate applicable rules against context"""
        pass
    
    def resolve_conflicts(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts when multiple rules apply (priority-based)"""
        pass
```

### 6. Health Monitor

**Purpose**: Monitors health and performance of MCP servers

**Location**: `backend/mcp/health_monitor.py`

**Key Classes**:
```python
class HealthStatus(BaseModel):
    """Health status of an MCP server"""
    server_id: str
    status: str  # "healthy", "unhealthy", "unknown"
    last_check: datetime
    response_time_ms: int
    error_message: Optional[str] = None

class HealthMonitor:
    """Monitors MCP server health"""
    def __init__(self, config_manager: MCPConfigManager):
        self.config_manager = config_manager
        self.status_cache: Dict[str, HealthStatus] = {}
    
    async def check_server_health(self, server_id: str) -> HealthStatus:
        """Check health of a specific server"""
        pass
    
    async def check_all_servers(self) -> Dict[str, HealthStatus]:
        """Check health of all servers"""
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics"""
        pass
```

### 7. Orchestrator Integration

**Purpose**: Integrates MCP with orchestrator logic

**Location**: `backend/mcp/orchestrator.py`

**Key Classes**:
```python
class OrchestratorService:
    """Orchestrator with MCP integration"""
    def __init__(self, 
                 config_manager: MCPConfigManager,
                 context_exchange: ContextExchangeService,
                 trace_service: TraceService):
        self.config_manager = config_manager
        self.context_exchange = context_exchange
        self.trace_service = trace_service
        self.confidence_threshold = 0.9
        self.constraint_models = {}  # Loaded model constraints
    
    def load_constraint_models(self) -> None:
        """Load model constraints for orchestrator (RDF/Turtle, JSON, or Markdown)"""
        pass
    
    def reload_constraint_models(self) -> None:
        """Reload constraint models without restarting orchestrator"""
        pass
    
    async def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose task into subtasks for reasoning services"""
        pass
    
    async def route_to_reasoning_service(self, subtask: Dict[str, Any]) -> str:
        """Determine which reasoning service should handle a subtask based on domain"""
        pass
    
    async def evaluate_rules_before_routing(self, subtask: Dict[str, Any], server_id: str) -> bool:
        """Evaluate rule sets before routing task to reasoning service"""
        pass
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task via MCP"""
        pass
    
    async def synthesize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesize results from multiple reasoning services"""
        pass
    
    def evaluate_confidence(self, result: Dict[str, Any]) -> float:
        """Evaluate confidence in orchestrator decision"""
        pass
```

## Data Models

### MCP Server Configuration
```python
{
  "server_id": "reasoning-service-a",
  "name": "Tools Domain Reasoning Service",
  "domain": "tools",
  "domain_model_path": ".mcp/domain-models/tools-domain.ttl",
  "endpoint": "http://localhost:8081",
  "capabilities": ["tool_execution", "validation"],
  "tools": ["tool_adapter_1", "tool_adapter_2"],
  "rules": ["validation_rules", "safety_rules"],
  "enabled": true,
  "health_check_url": "http://localhost:8081/health",
  "timeout": 30
}
```

### Context Payload
```python
{
  "context_id": "ctx_20251107_001",
  "source_agent": "orchestrator",
  "target_agent": "domain-model-a",
  "spore": {
    "uri": "https://ontology.beastmost.com/spore/2025/ctx_001",
    "label": "Context for task execution",
    "context_data": {...}
  },
  "task": {
    "task_id": "task_001",
    "description": "Execute validation",
    "parameters": {...}
  },
  "metadata": {
    "priority": "high",
    "timeout": 30
  },
  "timestamp": "2025-11-07T10:00:00Z"
}
```

### Trace Record (RDF/Turtle)
```turtle
@prefix mcp: <http://nkllon.com/ontology/mcp#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix caa: <http://nkllon.com/ontology/caa#> .

mcp:trace_20251107_001 a mcp:TraceRecord ;
  mcp:traceId "trace_20251107_001" ;
  mcp:sourceAgent caa:orchestrator ;
  mcp:targetAgent caa:domain-model-a ;
  mcp:interactionType "context_exchange" ;
  prov:generatedAtTime "2025-11-07T10:00:00Z"^^xsd:dateTime ;
  mcp:status "success" ;
  mcp:durationMs 150 .
```

### PoD with MCP Provenance (RDF/Turtle)
```turtle
@prefix caa: <http://nkllon.com/ontology/caa#> .
@prefix mcp: <http://nkllon.com/ontology/mcp#> .
@prefix prov: <http://www.w3.org/ns/prov#> .

caa:pod_20251107 a caa:PlanOfDay ;
  rdfs:label "Plan of Day - 2025-11-07" ;
  caa:hasPhase caa:pod_20251107_plan_phase .

caa:pod_20251107_plan_phase a caa:PlanPhase ;
  rdfs:label "Planning Phase" ;
  mcp:executedBy caa:reasoning-service-a ;
  mcp:hasTrace mcp:trace_20251107_001 ;
  prov:generatedAtTime "2025-11-07T10:00:00Z"^^xsd:dateTime .
```

**Design Rationale**: Linking PoD phases to MCP traces provides full provenance tracking, showing which reasoning services participated in each workflow phase. This supports audit requirements and enables analysis of multi-agent collaboration patterns.

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Invalid server configuration
   - Missing required fields
   - Duplicate server IDs
   - **Handling**: Validate on load, return 400 Bad Request

2. **Connection Errors**
   - Server unreachable
   - Timeout
   - Network failure
   - **Handling**: Retry with exponential backoff, mark server unhealthy after 3 failures

3. **Validation Errors**
   - Invalid context payload
   - Schema mismatch
   - Missing required fields
   - **Handling**: Return 422 Unprocessable Entity with detailed error

4. **Execution Errors**
   - Tool invocation failure
   - Rule violation
   - Domain model error
   - **Handling**: Record in trace, return structured error to orchestrator

5. **Trace Errors**
   - Storage failure
   - RDF parsing error
   - **Handling**: Log error, continue operation (non-blocking)

### Error Response Format
```python
{
  "error": {
    "code": "MCP_CONNECTION_ERROR",
    "message": "Failed to connect to domain model",
    "details": {
      "server_id": "domain-model-a",
      "endpoint": "http://localhost:8081",
      "reason": "Connection timeout after 30s"
    },
    "trace_id": "trace_20251107_001",
    "timestamp": "2025-11-07T10:00:00Z"
  }
}
```

## Testing Strategy

### Unit Tests

**Location**: `backend/tests/mcp/`

**Coverage**:
1. **Config Manager Tests** (`test_config_manager.py`)
   - Load valid configuration
   - Handle invalid configuration
   - Register/update servers
   - List servers with filters

2. **Context Exchange Tests** (`test_context_exchange.py`)
   - Send context successfully
   - Handle connection failures
   - Validate context payloads
   - Retry logic

3. **Trace Service Tests** (`test_trace_service.py`)
   - Record interactions
   - Query traces
   - RDF serialization
   - Trace chain retrieval

4. **Tool Adapter Tests** (`test_tool_adapter.py`)
   - Register tools
   - Invoke tools
   - Schema validation
   - Timeout handling

5. **Health Monitor Tests** (`test_health_monitor.py`)
   - Check server health
   - Update status cache
   - Aggregate metrics

6. **Rule Manager Tests** (`test_rule_manager.py`)
   - Load rules manifest
   - Register rule sets
   - Evaluate rules
   - Resolve rule conflicts
   - Priority-based resolution

### Integration Tests

**Location**: `backend/tests/integration/`

**Coverage**:
1. **End-to-End MCP Flow** (`test_mcp_e2e.py`)
   - Orchestrator → MCP → Domain Model → Response
   - Multi-domain model coordination
   - Trace generation

2. **PoD Integration** (`test_pod_mcp_integration.py`)
   - Execute PoD workflow via MCP
   - Spore transmission
   - Provenance tracking

3. **API Integration** (`test_mcp_api.py`)
   - All MCP API endpoints
   - Error handling
   - Authentication (if added)

### Mock Reasoning Services

**Location**: `backend/tests/mocks/`

Create mock reasoning service servers for testing:
```python
# mock_reasoning_service.py
from fastapi import FastAPI
from pathlib import Path

app = FastAPI()

# Mock domain model (static content)
DOMAIN_MODEL = """
@prefix caa: <http://nkllon.com/ontology/caa#> .
caa:mockDomain a caa:DomainModel ;
  rdfs:label "Mock Domain for Testing" .
"""

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/domain-model")
async def get_domain_model():
    return {"content": DOMAIN_MODEL, "format": "turtle"}

@app.post("/mcp/context")
async def receive_context(payload: dict):
    # Mock processing with domain model constraints
    return {"result": "success", "data": {...}}
```

### Test Data

**Location**: `backend/tests/fixtures/`

- Sample MCP configurations
- Sample context payloads
- Sample trace records
- Sample tool definitions

## Performance Considerations

### Caching Strategy

1. **Server Configuration Cache**
   - Cache loaded configurations in memory
   - Reload on file change (watch for modifications)
   - TTL: Until file modification

2. **Domain Model Cache**
   - Cache loaded domain model files in memory
   - Watch for file modifications using file system events
   - Reload automatically when domain model files change
   - Invalidate cache on manual reload request
   - TTL: Until file modification or manual reload

3. **Health Status Cache**
   - Cache health check results
   - TTL: 30 seconds
   - Background refresh every 15 seconds

4. **Tool Definition Cache**
   - Cache tool schemas
   - TTL: 5 minutes
   - Invalidate on server update

5. **Rule Set Cache**
   - Cache loaded rule sets
   - Reload when rules manifest changes
   - TTL: Until file modification

**Design Rationale**: Dynamic reloading of domain models and configurations enables updates without service restarts, supporting the bow-tie pattern where models constrain LLM behavior. File system watching ensures changes are detected automatically while caching maintains performance.

### Async Operations

- Use `asyncio` for all I/O operations
- Parallel health checks for multiple servers
- Concurrent context exchanges when possible
- Non-blocking trace recording

### Connection Pooling

- Maintain HTTP connection pools for each domain model
- Reuse connections for multiple requests
- Configure appropriate pool sizes (default: 10 per server)

### Monitoring Metrics

Expose Prometheus-compatible metrics:
- `mcp_context_exchanges_total` - Counter of context exchanges
- `mcp_context_exchange_duration_seconds` - Histogram of exchange durations
- `mcp_server_health_status` - Gauge of server health (1=healthy, 0=unhealthy)
- `mcp_tool_invocations_total` - Counter of tool invocations
- `mcp_errors_total` - Counter of errors by type

## Service Boundary Enforcement

The MCP layer enforces the bow-tie pattern by ensuring all inter-agent communication flows through the orchestrator:

### Architectural Constraints

1. **No Direct Service-to-Service Communication**
   - Reasoning services cannot directly call other reasoning services
   - All communication must go through the orchestrator via MCP
   - Network policies can enforce this at infrastructure level

2. **Orchestrator as Central Hub**
   - Orchestrator receives all task requests
   - Orchestrator decomposes tasks and routes to appropriate services
   - Orchestrator synthesizes results from multiple services
   - Orchestrator maintains the coordination context

3. **Service Independence**
   - Each reasoning service operates independently
   - Services are unaware of other services
   - Services only respond to orchestrator requests
   - Services maintain their own domain models

### Implementation Mechanisms

1. **Request Validation**
   - MCP layer validates that all context exchanges originate from orchestrator
   - Reject requests from non-orchestrator sources
   - Log unauthorized access attempts

2. **Trace Enforcement**
   - All interactions must have valid trace IDs
   - Trace chains must originate from orchestrator
   - Orphaned traces are flagged for investigation

3. **Configuration Enforcement**
   - Server configurations specify allowed communication patterns
   - Orchestrator endpoint is the only valid source for reasoning service requests
   - Health checks and administrative operations are exceptions

**Design Rationale**: Enforcing service boundaries at the MCP layer ensures the bow-tie pattern is maintained, prevents tight coupling between services, and provides a single point for governance and audit. This architectural constraint is critical for maintaining the composability and independence of reasoning services.

## Security Considerations

### Authentication & Authorization

**Phase 1 (Current)**: No authentication (development)
- All endpoints publicly accessible
- Suitable for local development only

**Phase 2 (Future)**: API Key Authentication
- Each domain model has an API key
- Keys stored in environment variables or Secret Manager
- Validated on each request

**Phase 3 (Future)**: Mutual TLS
- Certificate-based authentication
- Encrypted communication
- Certificate rotation

### Data Privacy

- Sensitive data in context payloads should be encrypted
- Trace records should not include sensitive payload data (only summaries)
- Support for PII redaction in logs

### Rate Limiting

- Implement rate limiting per domain model
- Default: 100 requests per minute per server
- Configurable per server

## Deployment Strategy

### Phase 1: Local Development
- Run MCP layer in same process as FastAPI backend
- Mock domain models for testing
- File-based configuration

### Phase 2: Single Cloud Run Service
- Deploy MCP layer with existing backend
- Reasoning services as separate Cloud Run services
- Domain model files stored in container or Cloud Storage
- Configuration via environment variables

### Phase 3: Separate MCP Service
- Deploy MCP layer as dedicated Cloud Run service
- Orchestrator and reasoning services connect to MCP service
- Centralized trace storage
- Domain model files managed centrally

### Configuration Management

**Development**:
- `.mcp/config.json` in repository
- Local file system

**Production**:
- Configuration in Google Secret Manager
- Environment variables for endpoints
- Dynamic service discovery (future)

## Migration Path

### Step 1: Infrastructure Setup
1. Create `.mcp/` directory structure
2. Add MCP configuration file
3. Update backend dependencies

### Step 2: Core Implementation
1. Implement Config Manager
2. Implement Trace Service
3. Implement Context Exchange Service

### Step 3: API Integration
1. Add MCP API endpoints to FastAPI
2. Update existing PoD/Spore endpoints to use MCP
3. Add health monitoring endpoints

### Step 4: Testing
1. Unit tests for all components
2. Integration tests with mock domain models
3. End-to-end tests

### Step 5: Documentation
1. API documentation (OpenAPI/Swagger)
2. Developer guide for creating domain models (static files)
3. Developer guide for creating reasoning services
4. Deployment guide updates

### Step 6: Deployment
1. Deploy to development environment
2. Create first domain model file (static .ttl)
3. Create first reasoning service using the domain model
4. Test orchestration flow
5. Deploy to production

## Future Enhancements

### Dynamic Service Discovery
- Integrate with service mesh (Istio, Linkerd)
- Automatic reasoning service registration
- Load balancing across multiple instances

### Advanced Orchestration
- Machine learning for optimal routing
- Adaptive confidence thresholds
- Multi-stage reasoning chains

### Enhanced Tracing
- Distributed tracing integration (Jaeger, Zipkin)
- Real-time trace visualization
- Anomaly detection

### Rule Engine
- Declarative rule language (SHACL, SWRL)
- Rule conflict resolution
- Dynamic rule updates

### Spore Evolution
- Spore versioning
- Spore merging and splitting
- Spore lifecycle management
