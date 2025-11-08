# Design Document

## Overview

This design document describes the implementation of the Orchestrator Service for the Composable AI Advisors system. The Orchestrator is a general-purpose LLM constrained by models (bow-tie pattern) that serves as the central coordination point in the multi-agent mesh architecture. It decomposes complex tasks, routes them to domain-specific reasoning services, and synthesizes results into coherent responses.

### Bow-Tie Pattern Implementation

The Orchestrator follows the bow-tie pattern: it starts as a general-purpose LLM (Google Gemini) and is constrained by models (static RDF/Turtle, JSON, or Markdown files) to exhibit model-driven behavior. This allows the orchestrator's behavior to be updated by changing model files without code changes.

**Three Bow-Tie Patterns in the System**:

1. **Architectural Bow-Tie**: Many domain models → Constrained orchestrator → Many client applications
   - This is the overall system architecture pattern
   
2. **Orchestrator Internal Bow-Tie**: General-purpose LLM (Gemini) → Constrained by models → Model-driven orchestration behavior
   - This design document focuses on implementing this pattern
   - Constraint models define: confidence thresholds, routing rules, domain mappings, escalation policies
   
3. **Domain Model Internal Bow-Tie**: Each domain model's LLM → Constrained by domain models → Domain-specific behavior
   - Implemented by individual reasoning services (not part of this design)

**Design Rationale**: The bow-tie pattern enables behavior modification through model updates rather than code changes. This provides flexibility, maintainability, and allows domain experts to influence orchestrator behavior by updating constraint models without requiring software development expertise.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Orchestrator Service                            │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Constraint Model Loader                       │    │
│  │  - Load RDF/Turtle, JSON, Markdown             │    │
│  │  - Combine multiple models                     │    │
│  │  - Hot reload support                          │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Task Decomposer                               │    │
│  │  - Analyze task requirements                   │    │
│  │  - Identify domain expertise needed            │    │
│  │  - Create subtask plan                         │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Task Router                                   │    │
│  │  - Query available reasoning services          │    │
│  │  - Match capabilities to requirements          │    │
│  │  - Select optimal service                      │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Execution Coordinator                         │    │
│  │  - Execute subtasks via MCP                    │    │
│  │  - Handle dependencies                         │    │
│  │  - Manage async execution                      │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Result Synthesizer                            │    │
│  │  - Collect results                             │    │
│  │  - Resolve conflicts                           │    │
│  │  - Combine into coherent response              │    │
│  └────────────────────────────────────────────────┘    │
│                        │                                │
│                        ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │  Confidence Evaluator                          │    │
│  │  - Evaluate decision confidence                │    │
│  │  - Apply threshold                             │    │
│  │  - Escalate when needed                        │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Reasoning   │ │  Reasoning   │ │  Reasoning   │
│  Service A   │ │  Service B   │ │  Service C   │
│  (via MCP)   │ │  (via MCP)   │ │  (via MCP)   │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Integration with MCP Layer

```
┌─────────────────────────────────────────────────────────┐
│         Orchestrator Service                            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         MCP Layer                                       │
│  - Context Exchange                                     │
│  - Server Registry                                      │
│  - Trace Layer                                          │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Reasoning   │ │  Reasoning   │ │  Reasoning   │
│  Services    │ │  Services    │ │  Services    │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Components and Interfaces

### 1. Data Structures

**Location**: `backend/orchestrator/models.py`


**Key Classes**:
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    DECOMPOSING = "decomposing"
    ROUTING = "routing"
    EXECUTING = "executing"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"

class SubTask(BaseModel):
    """A subtask created by task decomposition"""
    subtask_id: str
    description: str
    required_domain: str
    required_capabilities: List[str]
    dependencies: List[str] = []  # Other subtask IDs
    context: Dict[str, Any] = {}
    assigned_service: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    status: TaskStatus = TaskStatus.PENDING

class TaskDecomposition(BaseModel):
    """Result of task decomposition"""
    task_id: str
    original_task: str
    subtasks: List[SubTask]
    execution_order: List[str]  # Subtask IDs in execution order
    confidence: float

class RoutingDecision(BaseModel):
    """Decision about which service to route to"""
    subtask_id: str
    selected_service_id: str
    reasoning: str
    confidence: float
    alternatives: List[str] = []  # Alternative service IDs

class TaskResult(BaseModel):
    """Result from a reasoning service"""
    subtask_id: str
    service_id: str
    result: Dict[str, Any]
    provenance: Dict[str, Any]
    execution_time_ms: int

class SynthesizedResponse(BaseModel):
    """Final synthesized response"""
    task_id: str
    response: Dict[str, Any]
    provenance: List[Dict[str, Any]]  # Which services contributed
    confidence: float
    subtask_results: List[TaskResult]

class OrchestratorTask(BaseModel):
    """Complete orchestrator task"""
    task_id: str
    original_request: str
    user_context: Dict[str, Any]
    spore: Optional[Dict[str, Any]] = None  # Spore as context bundle for task execution
    status: TaskStatus
    decomposition: Optional[TaskDecomposition] = None
    routing_decisions: List[RoutingDecision] = []
    results: List[TaskResult] = []
    final_response: Optional[SynthesizedResponse] = None
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None
    context_provenance: List[str] = []  # Track context flow through pipeline

class ConstraintModel(BaseModel):
    """Loaded constraint model"""
    model_id: str
    content: Any  # RDF Graph, dict, or structured text
    format: str  # "turtle", "json", "markdown"
    loaded_at: datetime
```

### 2. Constraint Model Loader

**Location**: `backend/orchestrator/constraint_loader.py`

**Key Classes**:
```python
from pathlib import Path
from domain_model.framework import DomainModelFramework

class ConstraintModelLoader:
    """Loads and manages orchestrator constraint models"""
    
    def __init__(self, model_paths: List[str]):
        self.model_paths = model_paths
        self.domain_model_framework = DomainModelFramework()
        self.constraint_models: List[ConstraintModel] = []
    
    async def load_constraints(self) -> List[ConstraintModel]:
        """
        Load all constraint models
        
        Uses DomainModelFramework to load and parse models
        Combines multiple models if specified
        """
        pass
    
    async def reload_constraints(self) -> List[ConstraintModel]:
        """Reload constraint models (hot reload)"""
        pass
    
    def get_constraint_value(self, key: str, default: Any = None) -> Any:
        """
        Get a constraint value from loaded models
        
        Searches across all loaded models
        Returns first match or default
        """
        pass
    
    def get_routing_rules(self) -> Dict[str, Any]:
        """Extract routing rules from constraint models"""
        pass
    
    def get_confidence_threshold(self) -> float:
        """Get confidence threshold from constraints (default 0.9)"""
        pass
```

**Constraint Model Structure**:
Constraint models define orchestrator behavior including:
- Confidence thresholds
- Routing preferences
- Domain expertise mappings
- Escalation policies
- Task decomposition strategies

**Design Rationale**: Using the Domain Model Framework for constraint loading provides consistency with the overall architecture pattern. The framework already handles RDF/Turtle, JSON, and Markdown parsing, reducing code duplication and ensuring consistent model handling across the system. This dependency is explicit and required for the orchestrator to function.


### 3. Task Decomposer

**Location**: `backend/orchestrator/decomposer.py`

**Key Classes**:
```python
import google.generativeai as genai
from typing import List

class TaskDecomposer:
    """Decomposes complex tasks into subtasks"""
    
    def __init__(self, constraint_loader: ConstraintModelLoader):
        self.constraint_loader = constraint_loader
        self.llm = genai.GenerativeModel('gemini-pro')
    
    async def decompose_task(self, task: str, context: Dict[str, Any]) -> TaskDecomposition:
        """
        Decompose a task into subtasks
        
        Process:
        1. Analyze task using LLM constrained by models
        2. Identify required domain expertise
        3. Create subtasks with domain assignments
        4. Determine execution order and dependencies
        5. Evaluate confidence in decomposition
        
        Returns TaskDecomposition with subtasks and confidence
        """
        pass
    
    def _build_decomposition_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """
        Build prompt for LLM task decomposition
        
        Includes:
        - Task description
        - Available domains from constraint models
        - Context information
        - Decomposition guidelines
        """
        pass
    
    def _parse_llm_response(self, response: str) -> TaskDecomposition:
        """Parse LLM response into TaskDecomposition structure"""
        pass
    
    def _evaluate_decomposition_confidence(self, decomposition: TaskDecomposition) -> float:
        """
        Evaluate confidence in task decomposition
        
        Factors:
        - Clarity of domain assignments
        - Completeness of subtask coverage
        - Feasibility of execution order
        """
        pass
```

**Decomposition Strategy**:
- Use general-purpose LLM (Gemini) constrained by loaded models
- Prompt includes available domains and their capabilities
- LLM identifies which domains are needed for each aspect of the task
- Creates subtasks with clear domain assignments
- Determines dependencies and execution order

### 4. Task Router

**Location**: `backend/orchestrator/router.py`

**Key Classes**:
```python
from mcp.config_manager import MCPConfigManager
from mcp.health_monitor import HealthMonitor

class TaskRouter:
    """Routes subtasks to appropriate reasoning services"""
    
    def __init__(self, 
                 mcp_config: MCPConfigManager,
                 health_monitor: HealthMonitor,
                 constraint_loader: ConstraintModelLoader):
        self.mcp_config = mcp_config
        self.health_monitor = health_monitor
        self.constraint_loader = constraint_loader
    
    async def route_subtask(self, subtask: SubTask) -> RoutingDecision:
        """
        Route a subtask to a reasoning service
        
        Process:
        1. Query available reasoning services from MCP registry
        2. Filter by required domain and capabilities
        3. Check health status
        4. Apply routing rules from constraint models
        5. Select optimal service
        6. Evaluate confidence in routing decision
        
        Returns RoutingDecision with selected service and confidence
        """
        pass
    
    def _get_candidate_services(self, subtask: SubTask) -> List[str]:
        """Get reasoning services that match subtask requirements"""
        pass
    
    def _filter_by_health(self, service_ids: List[str]) -> List[str]:
        """Filter services by health status"""
        pass
    
    def _apply_routing_rules(self, 
                            service_ids: List[str], 
                            subtask: SubTask) -> List[str]:
        """Apply routing rules from constraint models"""
        pass
    
    def _select_optimal_service(self, service_ids: List[str]) -> str:
        """
        Select optimal service from candidates
        
        Criteria:
        - Health status
        - Response time
        - Load balancing
        - Routing preferences from constraints
        """
        pass
    
    def _evaluate_routing_confidence(self, 
                                     decision: RoutingDecision,
                                     candidates: List[str]) -> float:
        """
        Evaluate confidence in routing decision
        
        Factors:
        - Number of candidate services
        - Health status of selected service
        - Match quality with requirements
        """
        pass
```

**Routing Strategy**:
- Query MCP server registry for available services
- Match subtask requirements (domain, capabilities) to service metadata
- Filter by health status (exclude unhealthy services)
- Apply routing rules from constraint models (preferences, policies)
- Select based on health, response time, and load balancing
- Evaluate confidence in routing decision


### 5. Execution Coordinator

**Location**: `backend/orchestrator/executor.py`

**Key Classes**:
```python
from mcp.client import MCPClient
import asyncio

class ExecutionCoordinator:
    """Coordinates execution of subtasks via MCP"""
    
    def __init__(self, 
                 mcp_client: MCPClient,
                 router: TaskRouter,
                 task_store: Optional[Any] = None):  # Redis or similar for async task state
        self.mcp_client = mcp_client
        self.router = router
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_store = task_store  # Shared storage for async task state
    
    async def execute_task(self, 
                          task: OrchestratorTask,
                          async_mode: bool = False) -> OrchestratorTask:
        """
        Execute a complete orchestrator task
        
        Process:
        1. Execute subtasks according to execution order
        2. Respect dependencies between subtasks
        3. Pass context via MCP protocol
        4. Collect results
        5. Handle errors with retry logic
        
        Returns updated OrchestratorTask with results
        """
        pass
    
    async def execute_subtask(self, 
                             subtask: SubTask,
                             service_id: str,
                             context: Dict[str, Any]) -> TaskResult:
        """
        Execute a single subtask via MCP
        
        Process:
        1. Prepare context bundle (Spore) - supports both ContextSpore and PromptSpore
        2. Invoke reasoning service via MCP tool call
        3. Collect result and provenance
        4. Track context flow for provenance
        5. Handle errors with retry logic
        
        Returns TaskResult with service response
        
        Design Rationale: Spore support enables portable context bundles that maintain
        continuity across agent sessions and multi-agent workflows, as per Requirement 6.
        """
        pass
    
    async def _execute_with_retry(self,
                                  subtask: SubTask,
                                  service_id: str,
                                  context: Dict[str, Any],
                                  max_retries: int = 3) -> TaskResult:
        """
        Execute subtask with exponential backoff retry
        
        Retry logic:
        - Attempt 1: immediate
        - Attempt 2: 1 second delay
        - Attempt 3: 2 second delay
        - Attempt 4: 4 second delay
        """
        pass
    
    async def _handle_service_failure(self,
                                      subtask: SubTask,
                                      failed_service_id: str) -> Optional[str]:
        """
        Handle service failure by routing to alternative
        
        Returns alternative service ID or None if no alternatives
        """
        pass
    
    def create_task_id(self) -> str:
        """Generate unique task identifier"""
        pass
    
    async def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Query status of asynchronous task
        
        Checks both in-memory active_tasks and task_store (Redis) for task state.
        Returns current TaskStatus enum value.
        """
        pass
    
    async def get_task_result(self, task_id: str) -> Optional[OrchestratorTask]:
        """
        Retrieve result of completed task
        
        Fetches complete OrchestratorTask from task_store.
        Returns None if task not found or not yet completed.
        """
        pass
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel an asynchronous task
        
        Cancels asyncio.Task if still running and updates task_store.
        Returns True if successfully cancelled, False otherwise.
        """
        pass
```

**Execution Strategy**:
- Execute subtasks in order respecting dependencies
- Use MCP protocol for all service communication
- Support both synchronous and asynchronous execution
- Implement retry logic with exponential backoff
- Route to alternative services on failure
- Maintain task state for async queries

### 6. Result Synthesizer

**Location**: `backend/orchestrator/synthesizer.py`

**Key Classes**:
```python
class ResultSynthesizer:
    """Synthesizes results from multiple reasoning services"""
    
    def __init__(self, 
                 constraint_loader: ConstraintModelLoader,
                 llm: genai.GenerativeModel):
        self.constraint_loader = constraint_loader
        self.llm = llm
    
    async def synthesize_results(self,
                                task: OrchestratorTask,
                                results: List[TaskResult]) -> SynthesizedResponse:
        """
        Synthesize results into coherent response
        
        Process:
        1. Collect all subtask results
        2. Identify conflicts between results
        3. Use LLM to resolve conflicts and combine
        4. Build provenance metadata
        5. Evaluate synthesis confidence
        
        Returns SynthesizedResponse with combined result
        """
        pass
    
    def _identify_conflicts(self, results: List[TaskResult]) -> List[Dict[str, Any]]:
        """
        Identify conflicts between reasoning service results
        
        Conflicts occur when:
        - Results contradict each other
        - Results provide different answers to same question
        - Results have overlapping but inconsistent information
        """
        pass
    
    async def _resolve_conflicts(self,
                                conflicts: List[Dict[str, Any]],
                                results: List[TaskResult]) -> Dict[str, Any]:
        """
        Resolve conflicts using LLM
        
        Strategy:
        - Present conflicts to LLM with context
        - Apply conflict resolution rules from constraints
        - Select most authoritative source
        - Combine complementary information
        """
        pass
    
    def _build_provenance(self, results: List[TaskResult]) -> List[Dict[str, Any]]:
        """
        Build provenance metadata
        
        Includes:
        - Which services contributed
        - What each service provided
        - Confidence of each contribution
        - Timestamps and execution times
        """
        pass
    
    def _evaluate_synthesis_confidence(self,
                                      response: SynthesizedResponse,
                                      conflicts: List[Dict[str, Any]]) -> float:
        """
        Evaluate confidence in synthesized response
        
        Factors:
        - Number and severity of conflicts
        - Consistency of results
        - Completeness of response
        - Individual result confidences
        """
        pass
    
    async def _handle_partial_results(self,
                                      task: OrchestratorTask,
                                      successful_results: List[TaskResult],
                                      failed_subtasks: List[SubTask]) -> SynthesizedResponse:
        """
        Handle case where some subtasks failed
        
        Strategy:
        - Synthesize available results
        - Note missing information
        - Provide partial response with caveats
        - Include error information in provenance
        """
        pass
```

**Synthesis Strategy**:
- Use LLM to combine results intelligently
- Identify and resolve conflicts between services
- Maintain complete provenance information
- Handle partial results when some subtasks fail
- Evaluate confidence in final synthesis

### 7. Confidence Evaluator

**Location**: `backend/orchestrator/confidence.py`

**Key Classes**:
```python
class ConfidenceEvaluator:
    """Evaluates confidence in orchestrator decisions"""
    
    def __init__(self, constraint_loader: ConstraintModelLoader):
        self.constraint_loader = constraint_loader
        self.confidence_threshold = constraint_loader.get_confidence_threshold()
    
    def evaluate_decomposition_confidence(self,
                                         decomposition: TaskDecomposition) -> float:
        """
        Evaluate confidence in task decomposition
        
        Factors:
        - Clarity of domain assignments (0-1)
        - Completeness of subtask coverage (0-1)
        - Feasibility of execution order (0-1)
        - Complexity of dependencies (0-1)
        
        Returns confidence score 0-1
        """
        pass
    
    def evaluate_routing_confidence(self,
                                   decision: RoutingDecision,
                                   candidates: List[str]) -> float:
        """
        Evaluate confidence in routing decision
        
        Factors:
        - Number of candidate services (more = higher confidence)
        - Health status of selected service (0-1)
        - Match quality with requirements (0-1)
        - Availability of alternatives (0-1)
        
        Returns confidence score 0-1
        """
        pass
    
    def evaluate_synthesis_confidence(self,
                                     response: SynthesizedResponse,
                                     conflicts: List[Dict[str, Any]]) -> float:
        """
        Evaluate confidence in result synthesis
        
        Factors:
        - Number and severity of conflicts (fewer = higher)
        - Consistency of results (0-1)
        - Completeness of response (0-1)
        - Individual result confidences (average)
        
        Returns confidence score 0-1
        """
        pass
    
    def should_escalate(self, confidence: float) -> bool:
        """
        Determine if decision should be escalated to human
        
        Returns True if confidence < threshold
        """
        return confidence < self.confidence_threshold
    
    async def escalate_to_human(self,
                               task: OrchestratorTask,
                               decision_type: str,
                               confidence: float,
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escalate decision to human agent
        
        Process:
        1. Package decision context (full task details, confidence scores, reasoning)
        2. Include confidence score and reasoning for escalation
        3. Provide options for human review (approve, modify, reject)
        4. Log escalation event with timestamp and decision type
        5. Update task status to ESCALATED
        6. Notify human agent via configured channel (API callback, queue, etc.)
        
        Returns escalation record with escalation_id for tracking
        
        Design Rationale: Escalation to human agents (Requirement 5) ensures that
        uncertain decisions receive human oversight. The configurable confidence
        threshold (default 90%) balances automation with quality control.
        """
        pass
```

**Confidence Evaluation Strategy**:
- Evaluate confidence at each decision point
- Use multiple factors for each evaluation
- Compare against configurable threshold (default 90%)
- Escalate to human when below threshold
- Provide full context for human review

### 8. Metrics Tracker

**Location**: `backend/orchestrator/metrics.py`

**Key Classes**:
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class MetricSnapshot:
    """Snapshot of orchestrator metrics"""
    timestamp: datetime
    tasks_processed: int
    avg_decomposition_time_ms: float
    avg_routing_time_ms: float
    avg_synthesis_time_ms: float
    avg_total_time_ms: float
    avg_confidence_score: float
    escalation_rate: float
    service_selection_counts: Dict[str, int]
    error_rate: float

class MetricsTracker:
    """Tracks orchestrator performance metrics"""
    
    def __init__(self):
        self.tasks_processed = 0
        self.decomposition_times: List[float] = []
        self.routing_times: List[float] = []
        self.synthesis_times: List[float] = []
        self.total_times: List[float] = []
        self.confidence_scores: List[float] = []
        self.escalations = 0
        self.service_selections: Dict[str, int] = {}
        self.errors = 0
    
    def record_task_start(self, task_id: str) -> None:
        """Record start of task processing"""
        pass
    
    def record_decomposition(self, task_id: str, time_ms: float) -> None:
        """Record task decomposition metrics"""
        pass
    
    def record_routing(self, 
                      task_id: str,
                      service_id: str,
                      time_ms: float) -> None:
        """Record routing decision metrics"""
        pass
    
    def record_synthesis(self, task_id: str, time_ms: float) -> None:
        """Record result synthesis metrics"""
        pass
    
    def record_confidence(self, task_id: str, confidence: float) -> None:
        """Record confidence score"""
        pass
    
    def record_escalation(self, task_id: str) -> None:
        """Record human escalation"""
        pass
    
    def record_error(self, task_id: str, error: str) -> None:
        """Record error occurrence"""
        pass
    
    def get_metrics_snapshot(self) -> MetricSnapshot:
        """Get current metrics snapshot"""
        pass
    
    def reset_metrics(self) -> None:
        """Reset all metrics counters"""
        pass
```

**Metrics Strategy**:
- Track all key performance indicators
- Calculate averages and rates
- Monitor service selection patterns
- Track escalation and error rates
- Provide metrics snapshots for monitoring

### 9. Orchestrator Service API

**Location**: `backend/orchestrator/service.py`

**Key Classes**:
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class TaskRequest(BaseModel):
    """Request to orchestrator"""
    task: str
    user_context: Dict[str, Any] = {}
    spore: Optional[Dict[str, Any]] = None
    async_mode: bool = False

class TaskResponse(BaseModel):
    """Response from orchestrator"""
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    provenance: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    error: Optional[str] = None

class OrchestratorService:
    """Main orchestrator service"""
    
    def __init__(self,
                 constraint_loader: ConstraintModelLoader,
                 decomposer: TaskDecomposer,
                 router: TaskRouter,
                 executor: ExecutionCoordinator,
                 synthesizer: ResultSynthesizer,
                 confidence_evaluator: ConfidenceEvaluator,
                 metrics_tracker: MetricsTracker):
        self.constraint_loader = constraint_loader
        self.decomposer = decomposer
        self.router = router
        self.executor = executor
        self.synthesizer = synthesizer
        self.confidence_evaluator = confidence_evaluator
        self.metrics_tracker = metrics_tracker
    
    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """
        Process a task through the orchestration pipeline
        
        Pipeline:
        1. Create orchestrator task
        2. Decompose into subtasks
        3. Route subtasks to services
        4. Execute subtasks
        5. Synthesize results
        6. Evaluate confidence
        7. Return response or escalate
        
        Returns TaskResponse with result or task ID for async
        """
        pass
    
    async def get_task_status(self, task_id: str) -> TaskResponse:
        """Get status of asynchronous task"""
        pass
    
    async def cancel_task(self, task_id: str) -> TaskResponse:
        """Cancel asynchronous task"""
        pass
    
    async def reload_constraints(self) -> Dict[str, Any]:
        """Reload constraint models (hot reload)"""
        pass
    
    async def get_metrics(self) -> MetricSnapshot:
        """Get current metrics snapshot"""
        pass
```

## Context Flow and Spore Integration

### Context Management Strategy

The orchestrator maintains and tracks context throughout the task execution pipeline to satisfy Requirement 6:

**Context Bundle Structure**:
```python
{
    "task_context": {
        "original_request": "User's original task description",
        "user_info": {
            "user_id": "user-123",
            "preferences": {},
            "session_id": "session-456"
        },
        "task_metadata": {
            "task_id": "task-789",
            "created_at": "2025-11-07T10:00:00Z",
            "priority": "normal"
        }
    },
    "spore": {
        "type": "ContextSpore",  # or "PromptSpore"
        "spore_id": "spore-abc",
        "content": {
            # Portable context bundle content
        },
        "provenance": {
            "created_by": "orchestrator-service",
            "derived_from": ["previous-spore-xyz"]
        }
    },
    "execution_context": {
        "subtask_id": "subtask-123",
        "domain": "legal",
        "dependencies_resolved": ["subtask-100", "subtask-101"]
    }
}
```

**Context Flow Through Pipeline**:

1. **Task Reception**: User provides task + optional Spore
2. **Decomposition**: Context passed to LLM for task analysis
3. **Routing**: Context used to match service capabilities
4. **Execution**: Context bundle (including Spore) passed to reasoning services via MCP
5. **Synthesis**: Context provenance tracked in final response

**Spore Support**:
- **ContextSpore**: Maintains user context, preferences, and session state across subtasks
- **PromptSpore**: Reusable prompt logic for consistent task decomposition
- **Provenance Tracking**: Each context transformation recorded in `context_provenance` list
- **MCP Transport**: Spores exchanged via MCP protocol for secure context sharing

**Design Rationale**: Explicit Spore support enables portable context bundles that maintain continuity across agent sessions and multi-agent workflows. This is critical for the multi-agent mesh architecture where context must flow securely between the orchestrator and domain-specific reasoning services.

## Data Models

### Constraint Model Format

Constraint models can be in three formats:

**RDF/Turtle Format** (Preferred):
```turtle
@prefix caa: <http://nkllon.com/ontology/caa#> .
@prefix orch: <http://nkllon.com/ontology/orchestrator#> .

orch:config a caa:ConstraintModel ;
    orch:confidenceThreshold 0.9 ;
    orch:maxRetries 3 ;
    orch:retryBackoffMs 1000 .

orch:routingRule1 a orch:RoutingRule ;
    orch:domain "legal" ;
    orch:preferredService "legal-reasoning-service" ;
    orch:priority 1 .
```

**JSON Format**:
```json
{
  "confidence_threshold": 0.9,
  "max_retries": 3,
  "retry_backoff_ms": 1000,
  "routing_rules": [
    {
      "domain": "legal",
      "preferred_service": "legal-reasoning-service",
      "priority": 1
    }
  ]
}
```

**Markdown Format** (Least Preferred):
```markdown
# Orchestrator Configuration

## Confidence Settings
- Threshold: 90%
- Escalate below threshold: Yes

## Routing Rules
- Legal domain → legal-reasoning-service (priority 1)
- Investment domain → investment-reasoning-service (priority 1)
```

## Error Handling

### Error Types

1. **Service Unavailable**: Reasoning service is down or unreachable
   - Retry with exponential backoff: 1s, 2s, 4s (3 attempts total per Requirement 7)
   - Route to alternative service if available (using router's alternative selection)
   - Return error with escalation options if all services unavailable
   - Log each retry attempt with service_id, attempt_number, and error details

2. **Service Failure**: Reasoning service returns error response
   - Retry with exponential backoff: 1s, 2s, 4s (3 attempts total per Requirement 7)
   - Route to alternative service if retries exhausted
   - Log error with full context (task_id, subtask_id, service_id, error_message)
   - Maintain partial results from successful subtasks

3. **Decomposition Failure**: Cannot decompose task
   - Log error with task details and LLM response
   - Return error to user with explanation
   - Escalate to human if confidence too low
   - Provide original task context for human review

4. **Synthesis Failure**: Cannot synthesize results
   - Return partial results if available (per Requirement 7)
   - Log error with result details and conflict information
   - Escalate to human for manual synthesis
   - Include provenance of partial results

5. **Confidence Below Threshold**: Decision confidence too low
   - Escalate to human agent (per Requirement 5)
   - Provide full decision context (task, confidence scores, reasoning)
   - Log escalation event with decision_type and confidence_score
   - Update metrics tracker with escalation count

**Design Rationale**: The exponential backoff retry strategy (1s, 2s, 4s) provides resilience against transient failures while avoiding overwhelming failed services. Alternative service routing ensures task completion when possible. Partial result handling maintains value even when some subtasks fail, as specified in Requirement 7.

### Error Response Format

```python
{
    "task_id": "task-123",
    "status": "failed",
    "error": "Service unavailable: legal-reasoning-service",
    "error_type": "service_unavailable",
    "context": {
        "subtask_id": "subtask-456",
        "service_id": "legal-reasoning-service",
        "retry_count": 3
    },
    "escalation_options": [
        "retry_with_alternative",
        "escalate_to_human",
        "return_partial_results"
    ]
}
```

## Testing Strategy

### Unit Tests

**Location**: `backend/tests/orchestrator/`

Test each component independently:

1. **Constraint Loader Tests**:
   - Load RDF/Turtle models
   - Load JSON models
   - Load Markdown models
   - Combine multiple models
   - Hot reload functionality
   - Extract constraint values

2. **Task Decomposer Tests**:
   - Decompose simple tasks
   - Decompose complex tasks
   - Handle ambiguous tasks
   - Evaluate confidence
   - Parse LLM responses

3. **Task Router Tests**:
   - Match services to requirements
   - Filter by health status
   - Apply routing rules
   - Select optimal service
   - Evaluate routing confidence

4. **Execution Coordinator Tests**:
   - Execute single subtask
   - Execute multiple subtasks with dependencies
   - Handle service failures
   - Retry logic
   - Async execution

5. **Result Synthesizer Tests**:
   - Combine consistent results
   - Resolve conflicts
   - Build provenance
   - Handle partial results
   - Evaluate synthesis confidence

6. **Confidence Evaluator Tests**:
   - Evaluate decomposition confidence
   - Evaluate routing confidence
   - Evaluate synthesis confidence
   - Escalation logic

### Integration Tests

**Location**: `backend/tests/integration/orchestrator/`

Test component interactions:

1. **End-to-End Pipeline**:
   - Process complete task through pipeline
   - Verify decomposition → routing → execution → synthesis
   - Check confidence evaluation at each stage
   - Verify metrics tracking

2. **MCP Integration**:
   - Service discovery via MCP
   - Context exchange via MCP
   - Tool invocation via MCP
   - Trace layer recording

3. **Error Handling**:
   - Service failure scenarios
   - Retry and fallback logic
   - Partial result handling
   - Escalation workflows

### Mock Services

Create mock reasoning services for testing:
- Mock legal reasoning service
- Mock investment reasoning service
- Mock cognition reasoning service
- Configurable response times and failure rates

## Deployment Considerations

### Configuration

**Environment Variables**:
```bash
ORCHESTRATOR_CONSTRAINT_MODELS=/path/to/models
ORCHESTRATOR_CONFIDENCE_THRESHOLD=0.9
ORCHESTRATOR_MAX_RETRIES=3
MCP_CONFIG_PATH=/path/to/mcp/config.json
GEMINI_API_KEY=your-api-key
```

### Dependencies

**Required Dependencies**:
- **Domain Model Framework**: Core dependency for loading and parsing constraint models (RDF/Turtle, JSON, Markdown). The orchestrator uses the framework's model loading capabilities to implement the bow-tie pattern.
- **MCP Layer Infrastructure**: Required for service discovery, context exchange, and traceability (Requirement 10)
- **Google Gemini API**: General-purpose LLM for task decomposition and result synthesis
- **RDFLib**: RDF/Turtle processing (used by Domain Model Framework)
- **FastAPI**: API endpoints and async support
- **Redis** (or similar): Shared storage for async task state (Requirement 8)

**Design Rationale**: The Domain Model Framework is a prerequisite because it provides the model-loading infrastructure that enables the orchestrator's bow-tie pattern (general-purpose LLM constrained by models). This dependency must be implemented first before the orchestrator can function.

### Scaling

- Orchestrator service is stateless (except async task tracking)
- Can scale horizontally
- Async task state stored in shared cache (Redis or similar key-value store)
- Task identifiers are globally unique to support distributed execution
- Metrics aggregated across instances

**Design Rationale**: Using Redis for async task state enables horizontal scaling while maintaining task continuity. Task IDs are generated with sufficient entropy (UUID) to avoid collisions across instances. This satisfies Requirement 8 for asynchronous execution support.

### Monitoring

- Expose metrics endpoint (`/metrics`) for Prometheus scraping
- Metrics include: tasks processed, decomposition/routing/synthesis times, confidence scores, escalation rate, service selection counts, error rate
- Log all decisions and escalations with full context
- Track service health via MCP health monitor
- Alert on high escalation rates (>10%) or error rates (>5%)
- Dashboard displays real-time metrics from MetricsTracker

**Design Rationale**: Comprehensive metrics tracking (Requirement 9) enables performance monitoring, capacity planning, and identification of bottlenecks. The MetricsTracker component provides a centralized metrics collection point that can be exposed via standard monitoring interfaces.

## Security Considerations

1. **Authentication**: Verify user identity before processing tasks
2. **Authorization**: Check user permissions for requested operations
3. **Context Sanitization**: Sanitize user context before passing to services
4. **MCP Security**: Use secure MCP protocol for service communication
5. **Audit Trail**: Maintain complete audit trail via MCP trace layer

## Requirements Traceability

This section maps requirements from the requirements document to design components:

| Requirement | Design Component(s) | Implementation Details |
|-------------|---------------------|------------------------|
| Req 1: Load constraint models | ConstraintModelLoader | Loads RDF/Turtle, JSON, Markdown; supports hot reload; uses Domain Model Framework |
| Req 2: Decompose tasks | TaskDecomposer | Uses Gemini LLM constrained by models; creates SubTasks with domain assignments |
| Req 3: Route subtasks | TaskRouter | Queries MCP registry; matches capabilities; selects optimal service |
| Req 4: Synthesize results | ResultSynthesizer | Combines results; resolves conflicts; maintains provenance |
| Req 5: Evaluate confidence | ConfidenceEvaluator | Evaluates at each decision point; escalates below threshold (default 90%) |
| Req 6: Maintain context | OrchestratorTask, ExecutionCoordinator | Tracks context flow; supports Spores; maintains provenance |
| Req 7: Handle errors | ExecutionCoordinator | Retry with exponential backoff (3 attempts); route to alternatives; maintain partial results |
| Req 8: Async execution | ExecutionCoordinator, OrchestratorService | Task IDs; status queries; result retrieval; cancellation; Redis storage |
| Req 9: Track metrics | MetricsTracker | Tracks all key metrics; exposes via /metrics endpoint |
| Req 10: MCP integration | All components | Uses MCP for service discovery, context exchange, tool invocation, tracing |

## Future Enhancements

1. **Learning from Escalations**: Use human decisions to improve confidence evaluation
2. **Dynamic Routing**: Learn optimal routing patterns from execution history
3. **Caching**: Cache decomposition and routing decisions for similar tasks
4. **Parallel Execution**: Execute independent subtasks in parallel
5. **Streaming Results**: Stream partial results as subtasks complete
