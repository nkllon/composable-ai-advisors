# Project Context - Composable AI Advisors

## Current State

### Project Status
- **Phase**: Transitioning from hackathon submission to production system
- **Architecture**: Multi-agent mesh with MCP protocol
- **Status**: Multi-genetic LLM advisory capabilities working
- **Infrastructure**: Laboratory at `observatory.niklon.com` (Cloudflare) fully wired for multi-LLM development
- **Components**: Niklon organization repositories contain concrete, publicly available components (some on PyPI, SonarCloud CI/CD)

### Active Components

#### Backend (`backend/`)
- FastAPI service operational
- RDF/Turtle processing via RDFLib
- Google Gemini AI integration for PoD generation
- RESTful API endpoints for PoDs and Spores

#### Frontend (`frontend/`)
- React 18.2 application
- UI for visualizing PoDs and Spores
- API integration via Axios
- Nginx for production serving

#### Ontologies
- `caa-glossary.ttl` - Core CAA ontology definitions
- `guidance.ttl` - Plans of Day registry
- `spore_registry.ttl` - Spore tracking
- `docs/pod/2025/` - Example PoD files

## Known Issues

1. **README.md**: Currently hackathon-focused, needs update for actual project
2. **MCP Configuration**: Not yet implemented, pending addition
3. **Documentation**: Some docs may reference hackathon context

## Development Priorities

### Immediate
- [ ] Update README.md to reflect actual project purpose
- [ ] Add MCP configuration structure
- [ ] Complete Cursor rules setup

### Short-term
- [ ] Implement MCP server definitions
- [ ] Add more domain models
- [ ] Enhance Spore management
- [ ] Improve ontology coverage

### Long-term
- [ ] Full MCP integration
- [ ] Additional domain models
- [ ] Enhanced orchestration
- [ ] Production deployment improvements

## Integration Points

### MCP Integration (Pending)
- Configuration in `.mcp/config.json`
- Server definitions for domain models
- Context exchange protocols
- Trace/audit layer

### Domain Models
- **Static Model Descriptions**: Domain models are static, machine-readable files (not services)
- **Format**: Turtle (preferred), JSON, or Markdown (least preferred)
- **Purpose**: Model description of a domain that an LLM uses to assume the position of a stakeholder for that domain
- **Machine-Readable**: Must be machine-readable since an LLM needs to read it
- Examples: Domain Model A, B (Investments), C (Cognition) are conceptual examples
- Services use domain models to provide domain-specific reasoning capabilities

### Client Applications
- **Arbitrary Examples**: Mapper, Legal DocBot, OSINT, Guidance, Audit
- These are conceptual examples, not fixed requirements
- Any application can consume orchestrated outputs

### Orchestration Logic
- **Three Bow-Tie Patterns** (all are present):
  1. **Architectural Bow-Tie**: Many domain models → Constrained orchestrator → Many client applications
     - This is the overall system architecture pattern
  2. **Orchestrator Internal Bow-Tie**: General-purpose LLM → Constrained by models → Model-driven behavior
     - This is how the orchestrator itself works internally
  3. **Domain Model/LLM Internal Bow-Tie**: Each participant LLM (general-purpose or for-purpose) → Constrained by models → Domain-specific behavior
     - Each domain model's LLM starts as general-purpose or for-purpose (e.g., coding-specific LLM)
     - Models constrain each LLM to conform to domain requirements
     - This is how each domain model's reasoning engine works internally
- **General-Purpose LLM**: The orchestrator is a general-purpose LLM
- **Model Constraint**: Models (RDF/Turtle or Markdown) constrain/whittle down the LLM's behavior
- **Model Sources**: Model can be RDF/Turtle files or Markdown documents
- **Perspective Evaluation**: Model built for orchestrator to evaluate different perspectives
- **Confidence Threshold**: Typically 90% (configurable)
- **"Heat"**: Confidence measure based on how orchestrator is constructed
- **Escalation**: If confidence < threshold, escalate to human agent
- **Tested Mechanism**: Orchestration logic is tested and working

### Infrastructure
- **Laboratory**: `observatory.niklon.com` (public endpoint via Cloudflare)
- **Multi-LLM Development**: Fully wired lab environment
- **Component Repositories**: Niklon organization repos (check GitHub)
- **Package Management**: Components available via PyPI
- **CI/CD**: SonarCloud-enabled pipelines

### Tool Adapters
- **Status**: Requirements for product delivery being determined
- **Decision Pending**: Specific tool adapters and tool APIs to be defined based on product needs

## Key Files Reference

### Configuration
- `.cursorrules` - Main Cursor rules
- `agents.md` - AI agent guidance
- `.cursor/rules/*.mdc` - Detailed rule sets

### Documentation
- `ARCHITECTURE.md` - System architecture
- `internal-lingo-cheatsheet.md` - Terminology
- `BOOTSTRAP.md` - Project bootstrap guide
- `DEPLOYMENT.md` - Deployment instructions

### Ontologies
- `caa-glossary.ttl` - Core ontology
- `guidance.ttl` - PoD registry
- `spore_registry.ttl` - Spore registry

### Architecture Diagrams
- `composable-ai-advisors-architecture.puml` - PlantUML
- `composable-ai-advisors-architecture.dot` - Graphviz

## Development Workflow

1. **Check Context**: Review this file and `agents.md`
2. **Follow Rules**: Reference `.cursorrules` and `.cursor/rules/*.mdc`
3. **Maintain Ontologies**: Update `.ttl` files when adding concepts
4. **MCP Awareness**: Consider MCP integration implications
5. **Document Changes**: Update relevant documentation

## Notes

- Project emphasizes modularity and composability
- Multi-agent mesh pattern is core architecture
- RDF/Turtle for structured data
- MCP for context exchange (when implemented)
- Spores for context continuity

