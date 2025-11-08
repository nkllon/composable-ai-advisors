## Composable AI Advisors – Architecture Diagrams

This document wraps the PlantUML and Graphviz sources with inline renderings for easy viewing on GitHub.

### PlantUML

Source: `docs/architecture/composable-ai-advisors-architecture.puml`

Rendered:

![PlantUML rendering](./composable-ai-advisors-architecture.svg)

For reference, the source is included below:

```plantuml
@startuml
skinparam shadowing false
skinparam dpi 150
skinparam rectangle {
  RoundCorner 12
  FontSize 14
}
title Composable AI Advisors – Reference Architecture

rectangle "Orchestration LLM\n(General Reasoner)" as Orchestrator

rectangle "Domain Model A\n(Tools + Rules)" as A
rectangle "Domain Model B\n(Investments, etc. + Rules)" as B
rectangle "Domain Model C\n(Cognition + Rules)" as C

rectangle "MCP Context & Trace Layer" as MCP
rectangle "Clients / Viewers\nMapper • Legal DocBot • OSINT • Guidance • Audit" as Clients

Orchestrator --> A
Orchestrator --> B
Orchestrator --> C

A --> MCP
B --> MCP
C --> MCP

MCP --> Clients
@enduml
```

### Graphviz (DOT)

Source: `docs/architecture/composable-ai-advisors-architecture.dot`

Rendered:

![Graphviz rendering](./composable-ai-advisors-architecture.dot.svg)

For reference, the source is included below:

```dot
digraph G {
    rankdir=LR;
    node [shape=box, style=rounded];

    Orchestrator [label="Orchestration LLM\n(General Reasoner)"];
    A [label="Domain Model A\n(Tools + Rules)"];
    B [label="Domain Model B\n(Investments, etc. + Rules)"];
    C [label="Domain Model C\n(Cognition + Rules)"];
    MCP [label="MCP Context & Trace Layer"];
    Clients [label="Clients / Viewers\nMapper • Legal DocBot • OSINT • Guidance • Audit"];

    Orchestrator -> A;
    Orchestrator -> B;
    Orchestrator -> C;

    A -> MCP;
    B -> MCP;
    C -> MCP;

    MCP -> Clients;
}
```

