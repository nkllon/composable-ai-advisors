# Design Document

## Overview

This design document describes the implementation of the Orchestrator Service for the Composable AI Advisors system. The Orchestrator is a general-purpose LLM constrained by models (bow-tie pattern) that serves as the central coordination point in the multi-agent mesh architecture. It decomposes complex tasks, routes them to domain-specific reasoning services, and synthesizes results into coherent responses.

The Orchestrator follows the bow-tie pattern: it starts as a general-purpose LLM and is constrained by models (static RDF/Turtle, JSON, or Markdown files) to exhibit model-driven behavior. This allows the orchestrator's behavior to be updated by changing model files without code changes.

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
    spore: Optional[Dict[str, Any]] = None
    status: TaskStatus
    decomposition: Optional[TaskDecomposition] = None
    routing_decisions: List[RoutingDecision] = []
    results: List[TaskResult] = []
    final_response: Optional[SynthesizedResponse] = None
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None

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

