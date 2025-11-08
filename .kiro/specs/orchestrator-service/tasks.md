# Implementation Plan

## Current State

**Backend Status**: The backend currently implements a basic FastAPI service for Plans of Day (PoD) and Spore registries. It includes:
- RDF/Turtle file loading and parsing using RDFLib
- Google Gemini AI integration for PoD generation
- Basic API endpoints for PoDs and Spores
- No orchestrator implementation exists yet
- No domain model framework exists yet
- No MCP implementation exists yet

**Directory Structure**:
- `backend/main.py` - Current FastAPI application (PoD/Spore functionality)
- `backend/orchestrator/` - Does not exist yet (needs to be created)
- `backend/domain_model/` - Does not exist yet (prerequisite)
- `backend/mcp/` - Does not exist yet (prerequisite)

---

## Prerequisites

**IMPORTANT**: The Orchestrator Service has critical dependencies that must be implemented first:

1. **Domain Model Framework** (`.kiro/specs/domain-model-framework/`) - REQUIRED
   - The orchestrator uses the Domain Model Framework to load and parse constraint models
   - This enables the bow-tie pattern (general-purpose LLM constrained by models)
   - Status: Not yet implemented

2. **MCP Implementation** (`.kiro/specs/mcp-implementation/`) - REQUIRED
   - The orchestrator uses MCP for service discovery, context exchange, and traceability
   - All reasoning service communication goes through MCP protocol
   - Status: Not yet implemented

**Action Required**: Implement the Domain Model Framework and MCP Implementation specs before starting orchestrator implementation.

---

## Orchestrator Implementation Tasks

- [ ] 1. Set up project structure and core data models
  - Create `backend/orchestrator/` directory structure
  - Implement data models in `backend/orchestrator/models.py` (TaskStatus, SubTask, TaskDecomposition, RoutingDecision, TaskResult, SynthesizedResponse, OrchestratorTask, ConstraintModel)
  - Add Pydantic models with proper type hints and validation
  - _Requirements: 1.1, 2.2, 2.3, 2.4, 2.5, 3.5, 4.5, 5.5, 6.1, 6.5, 8.2, 8.4_

- [ ] 2. Implement Constraint Model Loader
  - [ ] 2.1 Create ConstraintModelLoader class in `backend/orchestrator/constraint_loader.py`
    - Initialize with DomainModelFramework instance (dependency from domain-model-framework spec)
    - Implement `load_constraints()` method using DomainModelFramework to load RDF/Turtle, JSON, and Markdown files
    - Support combining multiple constraint models
    - Implement `reload_constraints()` for hot reload functionality using DomainModelFramework.reload_domain_model()
    - Implement `get_constraint_value()` to extract values from loaded models
    - Implement `get_routing_rules()` to extract routing rules from constraint models
    - Implement `get_confidence_threshold()` with default of 0.9
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.4_
    - _Dependencies: Domain Model Framework must be implemented first_

- [ ] 3. Implement Task Decomposer
  - [ ] 3.1 Create TaskDecomposer class in `backend/orchestrator/decomposer.py`
    - Initialize with ConstraintModelLoader and Gemini LLM
    - Implement `decompose_task()` method to analyze tasks and identify required domains
    - Implement `_build_decomposition_prompt()` to create LLM prompts with constraint context
    - Implement `_parse_llm_response()` to parse LLM output into TaskDecomposition structure
    - Implement `_evaluate_decomposition_confidence()` to assess decomposition quality
    - Create subtasks with domain assignments, dependencies, and execution order
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 5.1_

- [ ] 4. Implement Task Router
  - [ ] 4.1 Create TaskRouter class in `backend/orchestrator/router.py`
    - Initialize with MCPConfigManager, HealthMonitor, and ConstraintModelLoader (dependencies from mcp-implementation spec)
    - Implement `route_subtask()` to select appropriate reasoning service
    - Implement `_get_candidate_services()` to query available services from MCP registry via MCPConfigManager
    - Implement `_filter_by_health()` to exclude unhealthy services using HealthMonitor
    - Implement `_apply_routing_rules()` to apply constraint model routing preferences
    - Implement `_select_optimal_service()` based on health, response time, and load balancing
    - Implement `_evaluate_routing_confidence()` to assess routing decision quality
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.2, 10.3_
    - _Dependencies: MCP Implementation (MCPConfigManager, HealthMonitor) must be implemented first_

- [ ] 5. Implement Execution Coordinator
  - [ ] 5.1 Create ExecutionCoordinator class in `backend/orchestrator/executor.py`
    - Initialize with ContextExchangeService (from mcp-implementation spec) and TaskRouter
    - Implement `execute_task()` to coordinate full task execution pipeline
    - Implement `execute_subtask()` to execute single subtask via MCP protocol using ContextExchangeService
    - Implement `_execute_with_retry()` with exponential backoff (1s, 2s, 4s delays for 3 retries)
    - Implement `_handle_service_failure()` to route to alternative services using TaskRouter
    - Support synchronous and asynchronous execution modes
    - Implement `create_task_id()` to generate unique task identifiers (UUID format)
    - Implement `get_task_status()` to query async task status from Redis/task store
    - Implement `get_task_result()` to retrieve completed task results from Redis/task store
    - Implement `cancel_task()` to cancel async tasks
    - Handle subtask dependencies and execution order
    - Pass TaskContext and Spores via MCP context exchange (ContextPayload with spore field)
    - Track context provenance in context_provenance list
    - _Requirements: 2.4, 3.5, 6.2, 6.3, 6.4, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 10.1, 10.4, 10.5_
    - _Dependencies: MCP Implementation (ContextExchangeService) must be implemented first_

- [ ] 6. Implement Result Synthesizer
  - [ ] 6.1 Create ResultSynthesizer class in `backend/orchestrator/synthesizer.py`
    - Initialize with ConstraintModelLoader and Gemini LLM
    - Implement `synthesize_results()` to combine results from multiple services
    - Implement `_identify_conflicts()` to detect contradictions between results
    - Implement `_resolve_conflicts()` using LLM with constraint guidance
    - Implement `_build_provenance()` to track which services contributed what
    - Implement `_evaluate_synthesis_confidence()` to assess synthesis quality
    - Implement `_handle_partial_results()` for cases where some subtasks failed
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.3, 6.5, 7.5_

- [ ] 7. Implement Confidence Evaluator
  - [ ] 7.1 Create ConfidenceEvaluator class in `backend/orchestrator/confidence.py`
    - Initialize with ConstraintModelLoader and load confidence threshold
    - Implement `evaluate_decomposition_confidence()` based on clarity, completeness, feasibility
    - Implement `evaluate_routing_confidence()` based on candidates, health, match quality
    - Implement `evaluate_synthesis_confidence()` based on conflicts, consistency, completeness
    - Implement `should_escalate()` to check if confidence is below threshold
    - Implement `escalate_to_human()` to package decision context for human review
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 8. Implement Metrics Tracker
  - [ ] 8.1 Create MetricsTracker class in `backend/orchestrator/metrics.py`
    - Define MetricSnapshot dataclass for metrics snapshots
    - Implement `record_task_start()` to track task initiation
    - Implement `record_decomposition()` to track decomposition time
    - Implement `record_routing()` to track routing decisions and service selection
    - Implement `record_synthesis()` to track synthesis time
    - Implement `record_confidence()` to track confidence scores
    - Implement `record_escalation()` to track human escalations
    - Implement `record_error()` to track error occurrences
    - Implement `get_metrics_snapshot()` to retrieve current metrics
    - Implement `reset_metrics()` to clear metrics counters
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 9. Implement Orchestrator Service API
  - [ ] 9.1 Create OrchestratorService class in `backend/orchestrator/service.py`
    - Define TaskRequest and TaskResponse Pydantic models
    - Initialize with all component dependencies (loader, decomposer, router, executor, synthesizer, evaluator, metrics)
    - Implement `process_task()` to execute full orchestration pipeline
    - Implement pipeline: decompose → route → execute → synthesize → evaluate confidence
    - Implement `get_task_status()` for async task status queries
    - Implement `cancel_task()` for async task cancellation
    - Implement `reload_constraints()` for hot reload of constraint models
    - Implement `get_metrics()` to expose metrics endpoint
    - Handle errors and escalations appropriately
    - _Requirements: 1.5, 5.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1_

- [ ] 10. Create FastAPI endpoints
  - [ ] 10.1 Add orchestrator endpoints to `backend/main.py`
    - Create POST `/orchestrator/task` endpoint for task submission
    - Create GET `/orchestrator/task/{task_id}` endpoint for task status
    - Create DELETE `/orchestrator/task/{task_id}` endpoint for task cancellation
    - Create POST `/orchestrator/reload` endpoint for constraint reload
    - Create GET `/orchestrator/metrics` endpoint for metrics
    - Wire up OrchestratorService with proper dependency injection
    - Add error handling and HTTP status codes
    - _Requirements: 1.5, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1_

- [ ] 11. Integrate with MCP layer
  - [ ] 11.1 Set up MCP client integration
    - Use MCPConfigManager for service discovery via MCP server registry
    - Use ContextExchangeService for context exchange via MCP protocol for all reasoning service communication
    - Use ToolAdapterRegistry for tool invocation via MCP for reasoning services
    - Use TraceService for trace layer recording for all MCP interactions
    - Register orchestrator as MCP client in MCP configuration
    - Verify all orchestrator components use MCP services (no direct HTTP calls to reasoning services)
    - _Requirements: 3.5, 6.2, 10.1, 10.2, 10.3, 10.4, 10.5_
    - _Dependencies: MCP Implementation (all MCP services) must be implemented first_

- [ ] 12. Create example constraint models
  - [ ] 12.1 Create sample constraint model files
    - Create example RDF/Turtle constraint model at `.mcp/domain-models/orchestrator-constraints.ttl`
      - Use caa: namespace from caa-glossary.ttl
      - Define orch: namespace for orchestrator-specific properties
      - Include confidence threshold (orch:confidenceThreshold 0.9)
      - Include max retries (orch:maxRetries 3)
      - Include routing rules (orch:RoutingRule with domain, preferredService, priority)
      - Include escalation policies
      - Follow ontology conventions from ontology.mdc steering rules
    - Create example JSON constraint model at `.mcp/domain-models/orchestrator-constraints.json`
      - Include same configuration as Turtle format
      - Use JSON schema structure
    - Create example Markdown constraint model at `.mcp/domain-models/orchestrator-constraints.md`
      - Include same configuration as Turtle/JSON formats
      - Use structured markdown with clear sections
    - Document constraint model structure and usage in comments/documentation
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 13. Add error handling and logging
  - [ ] 13.1 Implement comprehensive error handling
    - Add error handling for service unavailable scenarios
    - Add error handling for service failure scenarios
    - Add error handling for decomposition failures
    - Add error handling for synthesis failures
    - Implement structured logging for all errors with context
    - Create error response format with escalation options
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 14. Write unit tests
  - [ ] 14.1 Write tests for Constraint Model Loader
    - Test loading RDF/Turtle models
    - Test loading JSON models
    - Test loading Markdown models
    - Test combining multiple models
    - Test hot reload functionality
    - Test extracting constraint values
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ] 14.2 Write tests for Task Decomposer
    - Test decomposing simple tasks
    - Test decomposing complex tasks
    - Test handling ambiguous tasks
    - Test confidence evaluation
    - Test LLM response parsing
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 5.1_

  - [ ] 14.3 Write tests for Task Router
    - Test matching services to requirements
    - Test filtering by health status
    - Test applying routing rules
    - Test selecting optimal service
    - Test routing confidence evaluation
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 5.2_

  - [ ] 14.4 Write tests for Execution Coordinator
    - Test executing single subtask
    - Test executing multiple subtasks with dependencies
    - Test handling service failures
    - Test retry logic with exponential backoff
    - Test async execution
    - _Requirements: 7.1, 7.2, 7.3, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ] 14.5 Write tests for Result Synthesizer
    - Test combining consistent results
    - Test resolving conflicts
    - Test building provenance
    - Test handling partial results
    - Test synthesis confidence evaluation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.3, 7.5_

  - [ ] 14.6 Write tests for Confidence Evaluator
    - Test decomposition confidence evaluation
    - Test routing confidence evaluation
    - Test synthesis confidence evaluation
    - Test escalation logic
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 14.7 Write tests for Metrics Tracker
    - Test recording all metric types
    - Test calculating averages and rates
    - Test metrics snapshot generation
    - Test metrics reset
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 15. Write integration tests
  - [ ] 15.1 Create mock reasoning services for testing
    - Create mock legal reasoning service
    - Create mock investment reasoning service
    - Create mock cognition reasoning service
    - Add configurable response times and failure rates
    - _Requirements: 3.1, 3.2, 3.3, 7.1, 7.2_

  - [ ] 15.2 Write end-to-end pipeline tests
    - Test complete task processing through pipeline
    - Test decomposition → routing → execution → synthesis flow
    - Test confidence evaluation at each stage
    - Test metrics tracking throughout pipeline
    - _Requirements: All requirements_

  - [ ] 15.3 Write MCP integration tests
    - Test service discovery via MCP
    - Test context exchange via MCP
    - Test tool invocation via MCP
    - Test trace layer recording
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 15.4 Write error handling tests
    - Test service failure scenarios
    - Test retry and fallback logic
    - Test partial result handling
    - Test escalation workflows
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 16. Update dependencies and configuration
  - [ ] 16.1 Update backend dependencies
    - Verify google-generativeai is in requirements.txt for Gemini LLM (already present)
    - Verify rdflib is in requirements.txt for RDF/Turtle processing (already present)
    - Add redis or aioredis to requirements.txt for async task state storage
    - Ensure FastAPI and Pydantic are up to date (already present)
    - Verify all MCP dependencies are included from mcp-implementation spec
    - _Requirements: 1.1, 2.1, 4.2, 8.1, 8.2, 10.1_

  - [ ] 16.2 Add environment configuration
    - Add ORCHESTRATOR_CONSTRAINT_MODELS environment variable (comma-separated paths to constraint model files)
    - Add ORCHESTRATOR_CONFIDENCE_THRESHOLD environment variable (default: 0.9)
    - Add ORCHESTRATOR_MAX_RETRIES environment variable (default: 3)
    - Add REDIS_URL environment variable for async task storage (default: redis://localhost:6379)
    - Verify GEMINI_API_KEY environment variable (already documented)
    - Document configuration in DEPLOYMENT.md
    - _Requirements: 1.1, 5.4, 7.1, 8.1, 8.2_

- [ ] 17. Add documentation
  - [ ] 17.1 Document orchestrator API
    - Document POST `/orchestrator/task` endpoint with request/response examples
    - Document GET `/orchestrator/task/{task_id}` endpoint
    - Document DELETE `/orchestrator/task/{task_id}` endpoint
    - Document POST `/orchestrator/reload` endpoint
    - Document GET `/orchestrator/metrics` endpoint
    - Add API documentation to ARCHITECTURE.md or create separate API docs
    - _Requirements: All requirements_

  - [ ] 17.2 Document constraint model format
    - Document RDF/Turtle constraint model structure
    - Document JSON constraint model structure
    - Document Markdown constraint model structure
    - Provide examples for each format
    - Document how to create custom constraint models
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

---

## Implementation Order Summary

**Phase 1: Prerequisites (MUST BE COMPLETED FIRST)**
1. Implement Domain Model Framework spec (`.kiro/specs/domain-model-framework/`)
2. Implement MCP Implementation spec (`.kiro/specs/mcp-implementation/`)

**Phase 2: Orchestrator Core (AFTER PREREQUISITES)**
1. Tasks 1-3: Project structure, data models, task decomposer
2. Tasks 4-5: Task router and execution coordinator (uses MCP services)
3. Tasks 6-8: Result synthesizer, confidence evaluator, metrics tracker

**Phase 3: Integration and API**
1. Tasks 9-11: Orchestrator service API, FastAPI endpoints, MCP integration
2. Task 12: Example constraint models

**Phase 4: Error Handling and Testing**
1. Task 13: Error handling and logging
2. Tasks 14-15: Unit and integration tests

**Phase 5: Configuration and Documentation**
1. Task 16: Dependencies and configuration
2. Task 17: Documentation

**Critical Dependencies**:
- ConstraintModelLoader requires DomainModelFramework
- TaskRouter requires MCPConfigManager and HealthMonitor
- ExecutionCoordinator requires ContextExchangeService
- All components require MCP layer for service communication

**Recommendation**: Complete the Domain Model Framework and MCP Implementation specs before starting any orchestrator tasks.
