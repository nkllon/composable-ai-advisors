# Composable AI Advisors

A multi-agent mesh orchestration framework with RDF/Turtle ontologies, MCP context exchange, and Cloud Run deployment.

## 🎯 Overview

Composable AI Advisors implements a **multi-agent mesh** pattern where:

- A **general Orchestration LLM** (BFG9K) decomposes tasks and coordinates specialist domain models
- **Domain Models** expose tools + rule packs for their specific domains
- The **MCP Context & Trace layer** provides secure context exchange, provenance, and audit
- **Client applications** (Viewer, Mapper, Legal DocBot, OSINT, Guidance, Audit) consume outputs

## 🏗️ Architecture

The system follows a service mesh architecture:

```
┌─────────────────┐
│  Orchestrator   │  (BFG9K - General LLM)
│     (BFG9K)     │
└────────┬────────┘
         │ orchestrates
         ├──────────────────┬──────────────────┐
         ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Domain Model│  │ Domain Model│  │ Domain Model│
│     A       │  │     B       │  │     C       │
│ (Tools +    │  │ (Tools +    │  │ (Tools +    │
│  Rules)     │  │  Rules)     │  │  Rules)     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                         │ exchanges context
                         ▼
              ┌──────────────────────┐
              │  MCP Context & Trace │
              │  (Secure exchange,   │
              │   provenance, audit) │
              └──────────┬───────────┘
                         │ produces for
                         ▼
              ┌──────────────────────┐
              │    Client Apps       │
              │ Viewer, Mapper,      │
              │ Legal DocBot, OSINT, │
              │ Guidance, Audit      │
              └──────────────────────┘
```

See the architecture diagrams:
- `composable-ai-advisors-architecture.puml` (PlantUML)
- `composable-ai-advisors-architecture.dot` (Graphviz)

## 🔑 Key Concepts

### Spores
Portable context bundles that carry domain context, data pointers, policies, and prompt templates:

- **Spore**: Base class for portable context bundles
- **ContextSpore**: Carries domain context, data pointers, and policies
- **PromptSpore**: Carries prompt/program templates and routing hints

### MCP (Model Context Protocol)
Protocol governing secure context exchange, tools, and traceability between agents. Ensures:
- Secure context exchange
- Provenance tracking
- Audit trails
- Tool interoperability

### MaaS (Models as a Service)
Each specialist reasoning engine runs as its own service, exposed via API rather than embedded monolithically.

### Domain Models
Specialist reasoning services that:
- Expose domain-specific tools via adapters
- Apply declarative rule sets (validation, policy, routing, safety)
- Exchange context via MCP layer

## 📦 Project Structure

```
composable-ai-advisors/
├── backend/                              # FastAPI backend service
│   ├── main.py                          # API endpoints
│   ├── requirements.txt                 # Python dependencies
│   ├── Dockerfile                       # Container definition
│   └── service.yaml                     # Cloud Run config
├── frontend/                            # React frontend service
│   ├── src/                            # React source code
│   ├── Dockerfile                       # Container definition
│   └── nginx.conf                      # Nginx configuration
├── docs/                                # Documentation
│   └── pod/                            # Plans of Day examples
├── caa-glossary.ttl                    # CAA ontology (RDF/Turtle)
├── guidance.ttl                        # Guidance registry
├── spore_registry.ttl                  # Spore registry
├── composable-ai-advisors-architecture.puml  # PlantUML diagram
├── composable-ai-advisors-architecture.dot  # Graphviz diagram
└── README-snippet.md                    # Architecture notes
```

## 🧠 Ontology

The `caa-glossary.ttl` file contains the minimal classes, properties, and SHACL shapes that map the architecture to RDF/Turtle:

- **Core Classes**: `Orchestrator`, `DomainModel`, `ToolAdapter`, `RuleSet`, `MCPContext`, `ClientApp`, `Spore`
- **Properties**: Relationships between components (`orchestrates`, `usesTool`, `appliesRules`, `exchangesContextWith`, `producesFor`, `hasSpore`)
- **SHACL Shapes**: Validation constraints for domain models and orchestrators

## 🚀 Getting Started

### Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and configured
- Docker installed
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
export PORT=8080
python main.py
```

#### Frontend

```bash
cd frontend
npm install
export REACT_APP_API_URL=http://localhost:8080
npm start
```

### Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Cloud Run deployment instructions.

## 📡 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /api/pods` - Get all Plans of Day
- `GET /api/pods/{pod_id}` - Get specific PoD
- `GET /api/spores` - Get all Spores
- `POST /api/pods/generate` - Generate new PoD using AI

## 🔗 Related Projects

This project complements the [Graph RAG Chat Application](https://github.com/nkllon/graph_RAG), which demonstrates advanced Graph RAG patterns with GraphDB and SPARQL.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Lou** - BeastMost Systems / nkllon observatory
