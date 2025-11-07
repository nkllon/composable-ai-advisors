# Internal-Lingo Cheat Sheet for Non-Lou Stakeholders

## Key Terms & Acronyms  

| Term | Plain-language Definition |
|------|--------------------------|
| **LIM42** | Your design-scaffolding workflow toolset / template generator. |
| **BFG9K** | The agent-orchestration framework used in your multi-agent mesh. |
| **BeastMost Systems** | [Definition pending] |
| **Spore / ContextSpore / PromptSpore** | Modular, reusable packets of context or prompt logic for your agents. |
| **MCP (Model Context Protocol)** | The protocol that governs how agents exchange models, context, data, and metadata. |
| **.cursor/rules/*.mdc** | Directory naming convention: workspace (".cursor"), rule sets ("rules"), modelling context files ("*.mdc"). |
| **PROJECT_ONTOLOGY=chatbot.ttl, guidance/modules/*.ttl** | Naming conventions for ontology files (TTL format) and module folders. |
| **Mesh (multi-agent mesh)** | The network of specialist reasoning services (not one big LLM) coordinated by your orchestrator. |
| **MaaS (Models as a Service)** | Each specialist reasoning engine is exposed as an API/service, not embedded monolithically. |
| **Service Mesh of Reasoning Engines** | The overall architecture: domain-specific services + orchestrator + natural-language front-end. |
| **"11/11 Target Planning"** | Project alias for your hackathon/observatory upgrade initiative, aligned with your anniversary. |

## Why this ecosystem of terms?  

- Enables **consistency** and **repeatability** across projects (scaffolding, ontologies, naming).  

- Supports **multi-agent coordination**, with clear protocols (MCP) and context flow.  

- Provides **traceability** and **governance**, with explicit artefacts (TTL ontologies, rule files, versioning).  

- Fosters a **modular mindset**, emphasising reusable building blocks over monolithic logic.

## Key Messaging for Execs / Product Folks  

- **Exec framing**:  

  > "We are decomposing general-AI into a service-mesh of specialized reasoning engines, orchestrated by a natural-language interface, with data and regulatory constraints enforced via secure context and tool protocols."  

- **Product positioning**:  

  > "Composable AI Advisors: domain-expert reasoning services orchestrated by a general-LLM, personalized through secure context integration."

## Suggested Next Steps  

1. Share this cheat-sheet with your product & engineering teams.  

2. Annotate your existing artefacts (templates, ontologies, rules) using these term conventions.  

3. Use the lingo in your project descriptions, Jira tickets, sprint plans — so everyone aligns.  

4. Update your internal documentation (README.md) with this glossary.

---

**End of Cheat Sheet**

