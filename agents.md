# AI Agent Guidance - Composable AI Advisors

## Project Purpose

**Composable AI Advisors** is a multi-agent mesh architecture system that decomposes general AI into a service-mesh of specialized reasoning engines. The system uses an orchestration LLM to coordinate domain-specific services, with secure context exchange via MCP (Model Context Protocol).

## Core Architecture

```mermaid
flowchart TD
  O[Orchestration<br/>(General-Purpose LLM)<br/>Constrained by Turtle/Markdown<br/>(Bow-Tie Pattern)]
  D1[Domain Model A<br/>(Tools + Rules)]
  D2[Domain Model B<br/>(Investments + Rules)]
  D3[Domain Model C<br/>(Cognition + Rules)]
  MCP[MCP Context &amp; Trace Layer<br/>(Secure Context Exchange)]
  C[Clients:<br/>Mapper, Legal DocBot, OSINT, Guidance, Audit, etc.]

  O --> D1
  O --> D2
  O --> D3
  D1 --> MCP
  D2 --> MCP
  D3 --> MCP
  MCP --> C
```

## Key Concepts

### 1. Multi-Agent Mesh
- **Not a monolithic LLM**: System uses multiple specialized reasoning services
- **Orchestration**: General-purpose LLM constrained by models (bow-tie pattern) decomposes tasks and routes to specialists
- **Service Mesh**: Services use domain models to provide independent domain-specific capabilities (MaaS pattern)
- **Domain Models**: Static, machine-readable model descriptions of a domain (Turtle, JSON, or Markdown format)
  - Used by LLMs to assume the position of a stakeholder for that domain
  - Must be machine-readable since an LLM needs to read it
  - Format preference: Turtle > JSON > Markdown (Markdown is least preferred)
- **Domain Model LLMs**: Each domain model's LLM follows a bow-tie pattern (general-purpose/for-purpose LLM → constrained by domain models → domain-specific behavior)
- **Current State**: Multi-genetic LLM advisory capabilities are working

### 2. MCP (Model Context Protocol)
- **Purpose**: Secure protocol for context exchange between agents
- **Components**: Context, tools, metadata, traceability
- **Implementation**: Configuration in `.mcp/` directory (to be added)
- **Benefits**: Provenance tracking, audit trails, secure context sharing

### 3. Spores
- **ContextSpore**: Portable context bundles for agent continuity
- **PromptSpore**: Reusable prompt logic packets
- **Purpose**: Maintain context across agent sessions and multi-agent workflows
- **Storage**: Tracked in `spore_registry.ttl` (RDF/Turtle)

### 4. Ontologies (RDF/Turtle)
- **Format**: Semantic web standards (RDF/Turtle)
- **Purpose**: Structured, machine-readable, interoperable data
- **Files**: 
  - `caa-glossary.ttl` - Core CAA ontology
  - `guidance.ttl` - Guidance registry
  - `spore_registry.ttl` - Spore tracking
  - `docs/pod/` - Plans of Day examples

### 5. Plans of Day (PoD)
- **Structure**: PDCA workflow (Plan-Do-Check-Act)
- **Format**: RDF/Turtle files
- **Purpose**: Structured daily planning with semantic relationships
- **AI Generation**: Uses Google Gemini AI for intelligent PoD creation

## Benefits of the Modular Pattern

- **Domain Accuracy**: Dedicated expert models reduce hallucinations and enforce domain logic
- **Personalization**: The context layer personalizes outputs per user and data source without retraining the general model
- **Governance**: Clear service boundaries make decisions auditable and explainable
- **Maintainability**: Independent upgrades per domain reduce time-to-change
- **Cost & Performance**: Right-size models and infrastructure by workload rather than one giant footprint

## Technology Stack

### Backend
- **Language**: Python 3.11
- **Framework**: FastAPI
- **RDF Processing**: RDFLib
- **AI Integration**: Google Gemini (Generative AI)
- **Deployment**: Google Cloud Run

### Frontend
- **Framework**: React 18.2
- **HTTP Client**: Axios
- **Web Server**: Nginx
- **Deployment**: Google Cloud Run

### Data & Protocols
- **Ontologies**: RDF/Turtle (.ttl files)
- **Context Protocol**: MCP (Model Context Protocol)
- **API Format**: JSON (RESTful)

### Infrastructure
- **Laboratory**: Public external endpoint at `observatory.niklon.com` (served through Cloudflare)
- **Multi-LLM Development**: Lab fully wired for multi-LLM development
- **Component Repositories**: Niklon organization repositories contain concrete, publicly available components
- **Package Management**: Several components available via PyPI
- **CI/CD**: SonarCloud-enabled CI/CD pipelines for component repositories

## Development Workflow

### When Working on Backend

1. **API Endpoints**: Follow FastAPI patterns, use type hints
2. **RDF Processing**: Use RDFLib, respect namespace conventions
3. **AI Integration**: Google Gemini API for PoD generation
4. **Service Boundaries**: Design as independent, orchestrated service
5. **MCP Awareness**: Consider context exchange implications

### When Working on Frontend

1. **React Patterns**: Component-based, modern hooks
2. **API Integration**: Use Axios, handle async properly
3. **Data Visualization**: Display PoDs, Spores, relationships
4. **UI/UX**: Modern, responsive design
5. **State Management**: Consider context/state patterns

### When Working with Ontologies

1. **Namespace Usage**: Follow conventions in `caa-glossary.ttl`
2. **SHACL Shapes**: Use for validation when appropriate
3. **Relationships**: Maintain semantic links (prov:wasGeneratedBy, etc.)
4. **Provenance**: Track creation, modification, sources
5. **Consistency**: Keep ontology files aligned with code

### When Adding MCP Integration

1. **Protocol Compliance**: Follow MCP specifications
2. **Context Exchange**: Secure, traceable context sharing
3. **Tool Adapters**: Connect domain models to concrete tools
   - Tool adapter requirements for product delivery are being determined
   - Specific tool APIs and adapters will be defined based on product needs
4. **Traceability**: Maintain audit trails
5. **Configuration**: Use `.mcp/config.json` structure

### Orchestration Logic

The system uses **three bow-tie patterns** (all are present):

1. **Architectural Bow-Tie**: Many domain models → Constrained orchestrator → Many client applications
   - This is the overall system architecture pattern
   
2. **Orchestrator Internal Bow-Tie**: General-purpose LLM → Constrained by models → Model-driven behavior
   - This is how the orchestrator itself works internally
   
3. **Domain Model/LLM Internal Bow-Tie**: Each participant LLM (general-purpose or for-purpose) → Constrained by models → Domain-specific behavior
   - Each domain model's LLM starts as a general-purpose or for-purpose LLM (e.g., coding-specific LLM for coding tasks)
   - Models constrain each LLM to conform to domain requirements
   - This is how each domain model's reasoning engine works internally

**Key Points**:
- **General-Purpose LLM**: The orchestrator is a general-purpose LLM
- **Model Constraint**: Models (RDF/Turtle or Markdown) constrain/whittle down the LLM's behavior
- **Model Sources**: Model can be RDF/Turtle files or Markdown documents
- **Perspective Evaluation**: Build model for orchestrator to properly evaluate different perspectives
- **Confidence Threshold**: Orchestrator must meet a confidence threshold (typically 90%)
- **"Heat"**: The confidence measure is based on how the orchestrator is constructed
- **Escalation**: If confidence < threshold, escalate to human agent
- **Decision Making**: Orchestrator evaluates perspectives and makes recommendations when confident

## Common Patterns

### Adding a New Domain Model

1. Create domain model description file (preferably RDF/Turtle, or JSON/Markdown)
   - Model must be machine-readable
   - Describes the domain and stakeholder perspective
   - Used by LLM to assume stakeholder position for that domain
2. Define domain ontology in RDF/Turtle (if using Turtle format)
3. Create service API (FastAPI endpoint) that uses the domain model
4. Implement tool adapters for domain-specific tools
5. Register in MCP configuration
6. Update architecture documentation

### Creating a Spore

1. Define Spore structure in RDF/Turtle
2. Register in `spore_registry.ttl`
3. Link to relevant PoDs/milestones
4. Include provenance information
5. Make available via API

### Generating a PoD

1. User provides natural language prompt
2. Backend calls Gemini AI with context
3. AI generates structured PDCA workflow
4. Convert to RDF/Turtle format
5. Store in `docs/pod/` directory
6. Register in `guidance.ttl`

## Anti-Patterns to Avoid

❌ **Monolithic Design**: Don't create single large service
✅ **Modular Services**: Design independent, orchestrated components

❌ **Hard-coded Context**: Don't embed context in code
✅ **Spore-based Context**: Use Spores for portable context

❌ **Ad-hoc Data**: Don't use unstructured data formats
✅ **Ontology-driven**: Use RDF/Turtle for structured data

❌ **Direct Agent Communication**: Don't bypass MCP
✅ **MCP Protocol**: Use MCP for all agent communication

❌ **Tight Coupling**: Don't create dependencies between domain models
✅ **Loose Coupling**: Orchestrator coordinates, services are independent

## File Organization

### Root Level
- `*.ttl` - RDF/Turtle ontology files
- `*.md` - Documentation files
- `.cursorrules` - Main Cursor rules
- `agents.md` - This file

### Backend (`backend/`)
- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition
- `service.yaml` - Cloud Run config

### Frontend (`frontend/`)
- `src/` - React source code
- `public/` - Static files
- `package.json` - Node dependencies
- `Dockerfile` - Container definition
- `nginx.conf` - Web server config

### Documentation (`docs/`)
- `pod/` - Plans of Day examples
- Architecture diagrams
- Deployment guides

### Cursor Configuration (`.cursor/`)
- `rules/*.mdc` - Modular rule sets
- `context/` - Project context files

### MCP Configuration (`.mcp/` - to be added)
- `config.json` - MCP server configuration
- Domain model definitions
- Tool adapter configurations

## Terminology Reference

See `internal-lingo-cheatsheet.md` for complete glossary. Quick reference:

- **LIM42**: Design-scaffolding workflow toolset
- **BFG9K**: Agent-orchestration framework (separate product/repo, not part of this architecture)
- **Spore**: Modular context/prompt packet
- **MCP**: Model Context Protocol
- **MaaS**: Models as a Service
- **Mesh**: Multi-agent service network
- **PoD**: Plan of Day (PDCA workflow)
- **PDCA**: Plan-Do-Check-Act cycle

## Questions to Consider

When implementing features, ask:

1. **Architecture**: Does this fit the multi-agent mesh pattern?
2. **MCP**: How does this interact with MCP context exchange?
3. **Ontology**: Should this be represented in RDF/Turtle?
4. **Spores**: Does this need context continuity via Spores?
5. **Orchestration**: How does the orchestrator coordinate this?
6. **Service Boundaries**: Is this properly modularized?

## Getting Help

- **Architecture**: See `ARCHITECTURE.md`, `docs/architecture/composable-ai-advisors-architecture.*`, and `docs/architecture/modular-ai-framework-diagram.md`
- **Terminology**: See `internal-lingo-cheatsheet.md`
- **Ontology**: See `caa-glossary.ttl` and other `.ttl` files
- **Deployment**: See `DEPLOYMENT.md`
- **Rules**: See `.cursorrules` and `.cursor/rules/*.mdc`

## Important Notes

- This project is transitioning from hackathon submission to production system
- MCP configuration will be added separately
- Current README.md may not reflect actual project state
- Always prioritize modularity and composability
- Maintain semantic web standards (RDF/Turtle) for data

