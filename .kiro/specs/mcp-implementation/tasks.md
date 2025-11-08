# Implementation Plan

- [ ] 1. Set up MCP infrastructure and configuration
  - Create `.mcp/config.json` schema and initial configuration file
  - Add configuration validation logic
  - [x] Provide Pydantic config models in code (`backend/mcp/config.py`) for runtime validation
  - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [ ] 1a. Config overrides and path resolution
  - [ ] Add env override `MCP_CONFIG_PATH` (MCP-REQ-001)
  - [ ] Add env override `MCP_DOMAIN_MODELS_DIR` (MCP-REQ-002)
  - [ ] Resolve defaults from repo-root, independent of CWD (MCP-REQ-005)

- [ ] 2. Implement MCP Configuration Manager
  - [ ] 2.1 Create backend/mcp/manager.py and backend/mcp/config.py with MCPServerConfig and MCPConfigManager classes
    - [x] Create `backend/mcp/` directory and `__init__.py`
    - [x] Implement minimal `MCPServerConfig` Pydantic model (id, name, type, endpoint, enabled, metadata)
    - [ ] Expand `MCPServerConfig` to include: domain, domain_model_path, capabilities, tools, rules, health_check_url, timeout, command, args, env
    - [x] Implement `MCPConfigManager` with config loading and domain model preloading
    - [ ] Add methods: `register_server()`, `get_server()`, `get_domain_model()`, `list_servers()`, `update_server_status()`, `reload_domain_model()`, `validate_server_config()`, `save_server_definition()`
    - [ ] Support filtering servers by domain and capability
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.5, 3.4_

  - [ ] 2.2 Add domain model file loading and parsing
    - [x] Support loading Turtle (.ttl) files using RDFLib
    - [x] Support loading JSON files
    - [x] Support loading Markdown (.md) files
    - [x] Cache loaded domain models in memory
    - [ ] Implement file system watching for automatic reload on changes using watchdog library
    - [ ] Support manual reload via API
    - _Requirements: 1.3, 2.1, 10.1, 10.4_

  - [ ] 2.3 Implement server definition file management
    - Create server definition files in `.mcp/servers/{server_id}.json`
    - Load and save server definitions
    - Validate server definitions against schema
    - _Requirements: 1.4, 2.1_

  - [ ]* 2.4 Write unit tests for Configuration Manager
    - Create `backend/tests/mcp/test_config_manager.py`
    - Test loading valid configuration
    - Test handling invalid configuration
    - Test domain model file loading (all formats)
    - Test server registration and updates
    - Test server definition file management
    - Test domain model reloading
    - Test filtering by domain and capability
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.4, 10.4_

- [ ] 2a. Test-friendly preload behavior
  - [ ] Allow disabling preload via config/env in tests (MCP-REQ-004)
  - [ ] Remove/guard production fallback sample auto-load; use test fixtures (MCP-REQ-006)

- [ ] 3. Implement Trace and Audit Service
  - [ ] 3.1 Create backend/mcp/trace_service.py with TraceRecord model and TraceService class
    - Implement `TraceRecord` Pydantic model with trace_id, parent_trace_id, source_agent, target_agent, interaction_type, timestamp, payload_summary, response_summary, status, duration_ms fields
    - Implement `TraceService` class with RDF/Turtle storage using RDFLib
    - Add methods: `record_interaction()`, `query_traces()`, `get_trace_chain()`
    - Define MCP trace ontology in RDF/Turtle with mcp:TraceRecord, mcp:traceId, mcp:sourceAgent, mcp:targetAgent properties
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 3.2 Implement trace storage and querying
    - Store trace records in RDF/Turtle format in `.mcp/traces/` directory
    - Implement SPARQL queries for trace retrieval by agent, time range, trace ID
    - Add trace retention policy (configurable, default 90 days)
    - _Requirements: 5.3, 5.4, 5.5_

  - [ ]* 3.3 Write unit tests for Trace Service
    - Create `backend/tests/mcp/test_trace_service.py`
    - Test recording interactions
    - Test querying traces by agent, time range
    - Test trace chain retrieval
    - Test RDF serialization
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 4. Implement Context Exchange Service
  - [ ] 4.1 Create backend/mcp/context_exchange.py with ContextPayload model and ContextExchangeService class
    - Implement `ContextPayload` Pydantic model with context_id, source_agent, target_agent, spore, task, metadata, timestamp fields
    - Implement `ContextExchangeService` class with config_manager and trace_service dependencies
    - Add methods: `send_context()`, `receive_response()`, `validate_context()`
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 4.2 Implement context transmission with retry logic
    - Use aiohttp for async HTTP POST requests to reasoning service endpoints
    - Implement exponential backoff retry logic (3 retries with 1s, 2s, 4s delays)
    - Add timeout handling (default 30 seconds, configurable per server)
    - Support Spore transmission as context bundles in payload
    - _Requirements: 4.1, 4.2, 4.4, 6.5_

  - [ ] 4.3 Integrate with Trace Service
    - Record all context exchanges in trace layer using TraceService
    - Generate unique trace IDs for each exchange (format: trace_YYYYMMDD_NNN)
    - Link parent and child traces using parent_trace_id field
    - _Requirements: 5.1, 5.2_

  - [ ]* 4.4 Write unit tests for Context Exchange Service
    - Create `backend/tests/mcp/test_context_exchange.py`
    - Test sending context successfully
    - Test handling connection failures
    - Test retry logic
    - Test context validation
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 5. Implement Tool Adapter Registry
  - [ ] 5.1 Create backend/mcp/tool_adapter.py with ToolDefinition model and ToolAdapterRegistry class
    - Implement `ToolDefinition` Pydantic model with tool_id, name, description, reasoning_service_id, domain, input_schema, output_schema, timeout, invocation_method, endpoint fields
    - Implement `ToolAdapterRegistry` class with config_manager dependency
    - Add methods: `register_tool()`, `get_tool()`, `list_tools_for_service()`, `list_tools_for_domain()`, `invoke_tool()`
    - _Requirements: 6.1, 6.2_

  - [ ] 5.2 Implement tools manifest loading
    - Load tools manifest from `.mcp/servers/{server_id}-tools.json`
    - Parse and validate tool definitions against schema
    - Cache tool definitions in memory
    - _Requirements: 2.3, 6.1_

  - [ ] 5.3 Implement tool invocation with validation
    - Validate tool inputs against JSON schema using jsonschema library
    - Invoke tool via HTTP POST to reasoning service endpoint
    - Handle timeouts (default 30 seconds, configurable per tool)
    - Record invocations in trace layer
    - _Requirements: 6.2, 6.3, 6.4, 6.5_

  - [ ]* 5.4 Write unit tests for Tool Adapter Registry
    - Create `backend/tests/mcp/test_tool_adapter.py`
    - Test tool registration
    - Test tools manifest loading
    - Test tool invocation
    - Test schema validation
    - Test timeout handling
    - _Requirements: 2.3, 6.1, 6.2, 6.3, 6.5_

- [ ] 6. Implement Rule Set Manager
  - [ ] 6.1 Create backend/mcp/rule_manager.py with RuleDefinition and RuleSet models
    - Implement `RuleDefinition` Pydantic model with rule_name, condition, action, error_message, priority fields
    - Implement `RuleSet` Pydantic model with rule_id, name, description, type, priority, format, rules fields
    - Support rule types: validation, policy, routing, safety
    - _Requirements: 8.1, 8.2_

  - [ ] 6.2 Create RuleManager class
    - Implement `RuleManager` class with config_manager dependency
    - Add methods: `load_rules_manifest()`, `register_rule_set()`, `get_rule_set()`, `list_rule_sets_for_service()`, `evaluate_rules()`, `resolve_conflicts()`
    - _Requirements: 8.1, 8.3, 8.5_

  - [ ] 6.3 Implement rules manifest loading
    - Load rules manifest from `.mcp/servers/{server_id}-rules.json`
    - Parse and validate rule definitions against schema
    - Cache rule sets in memory
    - _Requirements: 2.4, 8.1_

  - [ ] 6.4 Implement rule evaluation logic
    - Evaluate rules against context dictionary
    - Support multiple rule formats (JSON Schema, declarative)
    - Return structured results with violated rules and error messages
    - _Requirements: 8.3, 8.4_

  - [ ] 6.5 Implement rule conflict resolution
    - Priority-based conflict resolution (higher priority wins)
    - Handle multiple applicable rules
    - Return highest priority result
    - _Requirements: 8.5_

  - [ ]* 6.6 Write unit tests for Rule Manager
    - Create `backend/tests/mcp/test_rule_manager.py`
    - Test rule set registration
    - Test rules manifest loading
    - Test rule evaluation
    - Test conflict resolution
    - Test error handling for violated rules
    - _Requirements: 2.4, 8.1, 8.3, 8.4, 8.5_

- [ ] 7. Implement Health Monitor
  - [ ] 7.1 Create backend/mcp/health_monitor.py with HealthStatus model and HealthMonitor class
    - Implement `HealthStatus` Pydantic model with server_id, status, last_check, response_time_ms, error_message fields
    - Implement `HealthMonitor` class with config_manager dependency
    - Add methods: `check_server_health()`, `check_all_servers()`, `get_metrics()`
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ] 7.2 Implement health checking with caching
    - Check reasoning service health endpoints via HTTP GET
    - Cache health status in memory (TTL: 30 seconds)
    - Implement background refresh task every 15 seconds using asyncio
    - Mark unhealthy services after 3 consecutive failures
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ] 7.3 Add Prometheus metrics support
    - Expose metrics: mcp_context_exchanges_total, mcp_context_exchange_duration_seconds, mcp_server_health_status, mcp_tool_invocations_total, mcp_errors_total
    - Use prometheus_client library (Counter, Histogram, Gauge)
    - Create metrics registry and expose via /api/mcp/metrics endpoint
    - _Requirements: 7.4, 7.5_

  - [ ]* 7.4 Write unit tests for Health Monitor
    - Create `backend/tests/mcp/test_health_monitor.py`
    - Test health check logic
    - Test status caching
    - Test metrics aggregation
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ] 7.5 Implement per-service rate limiting
    - Create rate limiter using token bucket algorithm
    - Enforce request rate per MCP server (default 100 rpm, configurable in server config)
    - Apply to context exchange and tool invocation endpoints
    - Expose current limiter status via metrics
    - _Requirements: Design/Rate Limiting_

- [ ] 8. Implement Orchestrator Integration
  - [ ] 8.1 Create backend/mcp/orchestrator.py with OrchestratorService class
    - Implement `OrchestratorService` class with config_manager, context_exchange, trace_service dependencies
    - Add methods: `load_constraint_models()`, `reload_constraint_models()`, `decompose_task()`, `route_to_reasoning_service()`, `evaluate_rules_before_routing()`, `execute_task()`, `synthesize_results()`, `evaluate_confidence()`
    - Load orchestrator constraint models from RDF/Turtle, JSON, or Markdown files (e.g., caa-glossary.ttl)
    - Set confidence_threshold attribute (default 0.9, configurable)
    - _Requirements: 10.1, 10.4_

  - [ ] 8.2 Implement task decomposition and routing
    - Decompose tasks into subtasks based on domain requirements
    - Route subtasks to appropriate reasoning services based on domain field
    - Use domain model metadata from config_manager for routing decisions
    - _Requirements: 3.1, 3.2, 3.4_

  - [ ] 8.3 Implement service boundary enforcement
    - Validate that all context exchanges originate from orchestrator (check source_agent field)
    - Reject requests from non-orchestrator sources with 403 Forbidden
    - Log unauthorized access attempts to trace layer
    - Enforce trace chain validation (parent_trace_id must be valid)
    - _Requirements: 10.2, 10.3_

  - [ ] 8.4 Implement confidence evaluation and escalation
    - Evaluate confidence in orchestrator decisions (0.0-1.0 scale)
    - Default confidence threshold: 0.9 (90%)
    - Escalate to human agent if confidence < threshold (return escalation flag in response)
    - _Requirements: 10.5_

  - [ ] 8.5 Implement result synthesis
    - Collect results from multiple reasoning services
    - Synthesize into coherent response dictionary
    - Maintain provenance information (which services contributed)
    - _Requirements: 4.5_

  - [ ]* 8.6 Write unit tests for Orchestrator Service
    - Create `backend/tests/mcp/test_orchestrator.py`
    - Test task decomposition
    - Test routing logic
    - Test service boundary enforcement
    - Test confidence evaluation
    - Test result synthesis
    - _Requirements: 3.1, 3.2, 10.2, 10.3, 10.5_

- [ ] 9. Add MCP API endpoints to FastAPI backend
  - [ ] 9.1 Create backend/mcp/router.py with MCP router and endpoints
    - Create FastAPI APIRouter for MCP endpoints
    - [x] Add `/api/mcp/servers` endpoint (GET) - list all reasoning services
    - [ ] Add `/api/mcp/servers/{id}` endpoint (GET) - get reasoning service details
    - [ ] Add `/api/mcp/servers/{id}/domain-model` endpoint (GET) - get domain model content
    - Add `/api/mcp/servers/{id}/tools` endpoint (GET) - get tools manifest
    - Add `/api/mcp/servers/{id}/rules` endpoint (GET) - get rules manifest
    - [x] Add `/api/mcp/health` endpoint (GET) - health check all services
    - Add `/api/mcp/context/exchange` endpoint (POST) - exchange context
    - Add `/api/mcp/tools/invoke` endpoint (POST) - invoke tool
    - Add `/api/mcp/rules/evaluate` endpoint (POST) - evaluate rules
    - Add `/api/mcp/trace` endpoint (GET) - query traces
    - [ ] Add `/api/mcp/metrics` endpoint (GET) - Prometheus metrics
    - [x] Add `/api/mcp/metrics` endpoint (GET) - JSON metrics (interim)
    - [x] Add `/api/mcp/domain-models` endpoint (GET) - list registered domain models
    - [x] Add `/api/mcp/reload` endpoint (POST) - reload config and preload models
    - _Requirements: 2.2, 2.3, 2.4, 3.1, 3.5, 4.1, 6.1, 7.1, 7.5, 8.1_

  - [ ] 9.1a Replace startup hooks with lifespan handlers (MCP-REQ-003)

  - [ ] 9.2 Add request/response models for API
    - Create Pydantic models for all API requests and responses in router.py
    - Add OpenAPI documentation with descriptions and examples
    - Include error response models
    - _Requirements: 2.2, 3.1, 4.1_

  - [ ] 9.3 Integrate MCP services with API endpoints and update main.py
    - [ ] Initialize MCP services (ConfigManager, ContextExchange, TraceService, ToolAdapter, RuleManager, HealthMonitor, Orchestrator) in main.py
    - [x] Include MCP router in FastAPI app (behind `ENABLE_MCP_API` flag)
    - [ ] Add error handling and structured error responses (HTTPException with code, message, details, trace_id)
    - [x] Add startup event to load MCP configuration (in router)
    - _Requirements: 2.2, 3.1, 4.1, 7.1, 8.1_

  - [x] 9.4 Add unit tests for MCP router endpoints (basic)
    - Tests: `/api/mcp/servers`, `/api/mcp/health`, `/api/mcp/metrics` (JSON), `/api/mcp/domain-models`, `/api/mcp/reload`
    - Location: `backend/tests/mcp/test_router.py`
    - _Requirements: 2.2, 7.1_

- [ ] 10. Integrate MCP with existing PoD and Spore infrastructure
  - [ ] 10.1 Update PoD execution to use MCP
    - Modify existing PoD endpoints in main.py to optionally route phases to reasoning services via MCP
    - Use MCP context exchange for PoD phase execution
    - Track reasoning service participation in PoD RDF/Turtle files (add mcp:executedBy, mcp:hasTrace properties)
    - _Requirements: 9.1, 9.3, 9.4_

  - [ ] 10.2 Enable Spore transmission via MCP
    - Support Spores as context bundles in ContextPayload (spore field)
    - Link Spores to MCP trace records in trace storage
    - Update spore_registry.ttl with MCP trace references (add mcp:hasTrace property)
    - _Requirements: 9.2, 9.5_

  - [ ]* 10.3 Write integration tests for PoD/Spore MCP integration
    - Create `backend/tests/integration/test_pod_mcp_integration.py`
    - Test PoD execution via MCP
    - Test Spore transmission
    - Test provenance tracking
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 11. Create example domain model and reasoning service
  - [ ] 11.1 Create example domain model file
    - Create `.mcp/domain-models/example-tools-domain.ttl` in RDF/Turtle format
    - Define domain description and stakeholder perspective using caa: namespace
    - Make it machine-readable for LLM consumption (include rdfs:label, rdfs:comment)
    - Follow ontology conventions from caa-glossary.ttl
    - _Requirements: 2.1, 10.1_

  - [ ] 11.2 Create example tools and rules manifests
    - Create `.mcp/servers/example-service-tools.json` with sample tool definitions (at least 2 tools)
    - Create `.mcp/servers/example-service-rules.json` with sample rule sets (validation and safety rules)
    - _Requirements: 2.3, 2.4_

  - [ ] 11.3 Create mock reasoning service for testing
    - Create `backend/tests/mocks/mock_reasoning_service.py`
    - Implement FastAPI service that loads and uses domain model from file
    - Implement health endpoint (GET /health)
    - Implement domain-model endpoint (GET /domain-model)
    - Implement context endpoint (POST /mcp/context)
    - Add example tool adapters (POST /tools/{tool_id})
    - _Requirements: 2.1, 2.3, 2.4, 6.1_

  - [ ] 11.4 Register example service in MCP configuration
    - Add example service to `.mcp/config.json` with all required fields
    - Create server definition file in `.mcp/servers/example-service.json`
    - Test service discovery via /api/mcp/servers endpoint
    - Test health checking via /api/mcp/health endpoint
    - _Requirements: 1.4, 2.1, 2.2, 7.1_

- [ ] 12. Add error handling and validation
  - [ ] 12.1 Implement structured error responses
    - Create error response Pydantic models with code, message, details, trace_id fields
    - Handle configuration errors (400 Bad Request) in config_manager
    - Handle connection errors with retry logic in context_exchange
    - Handle validation errors (422 Unprocessable Entity) in tool_adapter and rule_manager
    - Handle execution errors with trace recording in orchestrator
    - _Requirements: 4.3, 6.3, 8.4_

  - [ ] 12.2 Add comprehensive logging
    - Configure Python logging in main.py
    - Log all MCP operations (INFO level) with operation type and parameters
    - Log errors with full context (ERROR level) including stack traces
    - Log trace IDs for correlation in all log messages
    - _Requirements: 5.1, 5.2_

- [ ]* 13. Create integration tests
  - [ ]* 13.1 Write end-to-end MCP flow tests
    - Create `backend/tests/integration/test_mcp_e2e.py`
    - Test orchestrator → MCP → reasoning service → response flow
    - Test multi-service coordination
    - Test trace generation
    - _Requirements: 4.1, 4.5, 5.1, 5.2_

  - [ ]* 13.2 Write API integration tests
    - Create `backend/tests/integration/test_mcp_api.py`
    - Test all MCP API endpoints
    - Test error handling
    - Test concurrent requests
    - _Requirements: 2.2, 3.1, 4.1, 7.1_

- [ ]* 14. Create documentation
  - [ ]* 14.1 Write developer guide for domain models
    - Create `docs/mcp/domain-model-guide.md`
    - Document how to create domain model files (Turtle, JSON, Markdown)
    - Provide examples and best practices
    - Explain machine-readable format requirements for LLM consumption
    - _Requirements: 2.1, 10.1_

  - [ ]* 14.2 Write developer guide for reasoning services
    - Create `docs/mcp/reasoning-service-guide.md`
    - Document how to create reasoning services
    - Explain how to load and use domain models
    - Document tool adapter implementation
    - Document MCP server registration
    - _Requirements: 2.1, 2.3, 2.4, 6.1_

  - [ ]* 14.3 Update API documentation
    - Generate OpenAPI/Swagger documentation (automatic via FastAPI)
    - Document all MCP endpoints in docstrings
    - Add examples for each endpoint
    - _Requirements: 2.2, 3.1, 4.1, 7.1_

  - [ ]* 14.4 Update deployment guide
    - Update `DEPLOYMENT.md` with MCP deployment steps
    - Document configuration management (.mcp/config.json)
    - Document monitoring and metrics (Prometheus)
    - _Requirements: 7.5_

- [ ]* 15. Deploy and validate
  - [ ]* 15.1 Deploy to development environment
    - Deploy updated backend with MCP layer to local or dev environment
    - Deploy example reasoning service (mock_reasoning_service.py)
    - Verify configuration loading from .mcp/config.json
    - _Requirements: 1.1, 1.2, 2.2_

  - [ ]* 15.2 Test orchestration flow
    - Test task decomposition and routing via /api/mcp/context/exchange
    - Test context exchange with example service
    - Test trace recording and retrieval via /api/mcp/trace
    - Verify confidence evaluation in orchestrator responses
    - _Requirements: 3.1, 4.1, 5.1, 10.5_

  - [ ]* 15.3 Validate monitoring and metrics
    - Verify health checks working via /api/mcp/health
    - Verify Prometheus metrics exposed via /api/mcp/metrics
    - Test alerting on service failures (mark service unhealthy)
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
