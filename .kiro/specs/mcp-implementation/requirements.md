# Requirements Document

## Introduction

This specification defines the requirements for implementing the Model Context Protocol (MCP) layer in the Composable AI Advisors system. MCP is the critical infrastructure that enables secure context exchange, tool sharing, and traceability between the orchestrator and domain-specific reasoning services in the multi-agent mesh architecture. Currently, the system has a working backend API for Plans of Day (PoD) and Spore registries, but lacks the MCP layer needed for true multi-agent orchestration.

## Glossary

- **MCP_System**: The Model Context Protocol implementation that governs secure context exchange between agents
- **Orchestrator**: The general-purpose LLM constrained by models (bow-tie pattern) that decomposes tasks and coordinates reasoning services
- **DomainModel**: A static, machine-readable file (Turtle, JSON, or Markdown) that describes a domain and is used by an LLM to assume the position of a stakeholder for that domain
- **ReasoningService**: An independent service that uses domain models to provide domain-specific reasoning capabilities (model-enabled LLM)
- **ToolAdapter**: An adapter that connects a reasoning service to concrete tools/APIs
- **ContextExchange**: The secure sharing of context, prompts, and metadata between agents via MCP
- **TraceLayer**: The audit and provenance tracking system for all agent interactions
- **MCPServer**: A reasoning service that exposes domain-specific capabilities via MCP protocol
- **MCPClient**: A component that consumes MCP services (typically the orchestrator)
- **Spore**: A portable context bundle for agent continuity
- **RuleSet**: Declarative rules (validation, policy, routing, safety) applied by a reasoning service

## Requirements

### Requirement 1

**User Story:** As a system architect, I want the MCP configuration infrastructure in place, so that I can define and manage MCP servers for reasoning services

#### Acceptance Criteria

1. WHEN THE MCP_System is initialized, THE MCP_System SHALL create a configuration directory at `.mcp/` with subdirectories named servers, domain-models, tools, and context
2. THE MCP_System SHALL provide a JSON configuration file at `.mcp/config.json` that defines MCP server connections and domain model file paths
3. THE MCP_System SHALL validate the configuration file against a schema that includes server name, domain model path, command, arguments, environment variables, and status fields
4. WHERE a ReasoningService is registered, THE MCP_System SHALL store the server definition in `.mcp/servers/` directory and reference its domain model files
5. THE MCP_System SHALL support enabling and disabling MCPServer instances without removing their configuration

### Requirement 2

**User Story:** As a reasoning service developer, I want to register my reasoning service as an MCP server, so that the orchestrator can discover and use my domain-specific capabilities

#### Acceptance Criteria

1. WHEN a ReasoningService is registered, THE MCP_System SHALL create a server configuration file in `.mcp/servers/` with the service name, domain model file path, capabilities, and connection details
2. THE MCP_System SHALL expose an API endpoint at `/api/mcp/servers` that returns all registered MCPServer instances with their associated DomainModel files
3. THE MCPServer SHALL declare its available tools via MCP protocol using a tools manifest
4. THE MCPServer SHALL declare its rule sets via MCP protocol using a rules manifest
5. THE MCP_System SHALL validate that each registered MCPServer references at least one DomainModel file and has at least one tool or rule set defined

### Requirement 3

**User Story:** As an orchestrator, I want to discover available reasoning services and their domain-specific capabilities, so that I can route tasks to the appropriate specialist

#### Acceptance Criteria

1. WHEN the Orchestrator queries for available services, THE MCP_System SHALL return a list of all enabled MCPServer instances with their DomainModel files and capabilities
2. THE MCP_System SHALL provide metadata for each MCPServer including DomainModel description, domain expertise, available tools, and rule sets
3. WHEN an MCPServer is disabled, THE MCP_System SHALL exclude it from the discovery results
4. THE MCP_System SHALL support filtering MCPServer instances by domain or capability type
5. THE MCP_System SHALL return response time in milliseconds and health status for each available MCPServer

### Requirement 4

**User Story:** As an orchestrator, I want to send context and tasks to reasoning services via MCP, so that I can leverage domain-specific reasoning capabilities

#### Acceptance Criteria

1. WHEN the Orchestrator sends a task to an MCPServer, THE MCP_System SHALL transmit the context via secure ContextExchange protocol
2. THE MCP_System SHALL support sending Spore instances as context bundles to MCPServer instances
3. WHEN an MCPServer receives context, THE MCP_System SHALL validate the context structure before processing
4. THE MCP_System SHALL support synchronous and asynchronous task execution modes
5. THE MCP_System SHALL return structured responses from MCPServer instances to the Orchestrator with provenance metadata

### Requirement 5

**User Story:** As a compliance officer, I want all agent interactions traced and auditable, so that I can verify system behavior and maintain governance

#### Acceptance Criteria

1. WHEN any ContextExchange occurs, THE TraceLayer SHALL record the source agent, destination agent, timestamp, and context payload
2. THE TraceLayer SHALL generate unique trace identifiers for each interaction chain
3. THE TraceLayer SHALL store trace records in RDF/Turtle format with provenance relationships
4. THE TraceLayer SHALL support querying traces by agent, time range, or trace identifier
5. THE TraceLayer SHALL maintain trace records for a configurable retention period with a minimum of 90 days

### Requirement 6

**User Story:** As a reasoning service developer, I want to expose tools via MCP tool adapters, so that agents can invoke concrete APIs through my reasoning service

#### Acceptance Criteria

1. WHEN a ToolAdapter is registered, THE MCP_System SHALL store the tool definition in `.mcp/tools/` directory with a reference to the reasoning service
2. THE ToolAdapter SHALL declare its input schema, output schema, and invocation method
3. THE MCP_System SHALL validate tool invocations against the declared input schema
4. WHEN a tool is invoked, THE MCP_System SHALL record the invocation in the TraceLayer with input parameters and output results
5. THE MCP_System SHALL support tool invocation timeouts with a default of 30 seconds

### Requirement 7

**User Story:** As a system operator, I want to monitor MCP system health and performance, so that I can ensure reliable multi-agent operations

#### Acceptance Criteria

1. THE MCP_System SHALL expose a health check endpoint at `/api/mcp/health` that returns the status of all registered MCPServer instances
2. THE MCP_System SHALL track and report average response times in milliseconds for each MCPServer
3. WHEN an MCPServer fails to respond within the timeout period, THE MCP_System SHALL mark it as unhealthy and exclude it from routing
4. THE MCP_System SHALL provide metrics on ContextExchange volume, tool invocations, and error rates
5. THE MCP_System SHALL support integration with monitoring systems via Prometheus-compatible metrics endpoint at `/api/mcp/metrics`

### Requirement 8

**User Story:** As an orchestrator, I want to apply rule sets from reasoning services, so that I can enforce domain-specific constraints and policies

#### Acceptance Criteria

1. WHEN a RuleSet is registered, THE MCP_System SHALL store the rule definition in the MCPServer configuration
2. THE RuleSet SHALL be expressed in a declarative format that supports validation, policy, routing, and safety rules
3. THE MCP_System SHALL evaluate applicable RuleSet instances before executing tasks on an MCPServer
4. WHEN a rule evaluation fails, THE MCP_System SHALL return a structured error with the violated rule identifier and reason
5. THE MCP_System SHALL support rule precedence and conflict resolution based on rule priority values

### Requirement 9

**User Story:** As a developer, I want to integrate MCP with the existing PoD and Spore infrastructure, so that Plans of Day can be orchestrated across reasoning services

#### Acceptance Criteria

1. THE MCP_System SHALL support sending PoD workflow phases to appropriate MCPServer instances based on phase requirements and domain expertise
2. THE MCP_System SHALL enable Spore instances to be transmitted as context bundles via ContextExchange
3. WHEN a PoD is executed, THE MCP_System SHALL track which MCPServer instances participated in each workflow phase
4. THE MCP_System SHALL update the PoD RDF/Turtle file with provenance information about MCPServer participation
5. THE MCP_System SHALL support linking Spore instances to MCP trace records for continuity tracking

### Requirement 10

**User Story:** As a system architect, I want the MCP implementation to follow the bow-tie pattern, so that the orchestrator remains model-constrained and reasoning services maintain independence

#### Acceptance Criteria

1. THE Orchestrator SHALL remain a general-purpose LLM constrained by DomainModel files loaded from RDF/Turtle, JSON, or Markdown formats
2. THE MCP_System SHALL enforce service boundaries such that MCPServer instances cannot directly communicate with each other
3. THE MCP_System SHALL route all inter-agent communication through the Orchestrator
4. WHEN DomainModel files are updated, THE MCP_System SHALL reload the constraints without requiring code changes to the MCPServer instances
5. THE MCP_System SHALL support confidence thresholds with a default value of 0.90 for Orchestrator decisions
