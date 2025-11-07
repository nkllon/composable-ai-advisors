# Composable AI Advisors — Alignment Notes

This repo uses a **multi‑agent mesh** pattern:
- A **general Orchestration LLM** decomposes tasks and coordinates specialists.
- **Domain Models** expose tools + rule packs for their domain (A/B/C shown for reference).
- The **MCP Context & Trace layer** provides secure context exchange, provenance, and audit.
- **Client apps** (Viewer, Mapper, Legal DocBot, OSINT, Guidance, Audit) consume outputs.

**Key terms**
- **Spore / ContextSpore / PromptSpore** — portable context/prompt bundles.
- **MCP** — protocol for context, tools, and traceability between agents.
- **MaaS** — models-as-a-service; each specialist reasoner runs as its own service.

**Diagram sources**
- `composable-ai-advisors-architecture.puml` (PlantUML)
- `composable-ai-advisors-architecture.dot` (Graphviz)

**Ontology**
- `caa-glossary.ttl` contains the minimal classes, properties, and SHACL shapes to map the architecture to RDF/TTL.