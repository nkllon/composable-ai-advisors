---
inclusion: always
---
# MCP Rules - Model Context Protocol

## Overview

MCP (Model Context Protocol) is the protocol for secure context exchange, tool sharing, and traceability between agents in the multi-agent mesh.

## Core Principles

1. **Secure Context Exchange**: All context sharing via MCP protocol
2. **Tool Adapters**: Domain models expose tools via MCP
3. **Traceability**: Maintain audit trails and provenance
4. **Standardized Interface**: Consistent protocol across all agents

## MCP Components

### Context Exchange
- Agents share context through MCP protocol
- Context includes: prompts, responses, metadata, provenance
- Context is secure and traceable

### Tool Adapters
- Each domain model exposes tools via MCP
- Tools are domain-specific capabilities
- Tool adapters connect reasoning agents to concrete APIs

### Trace Layer
- All interactions logged and traceable
- Maintain provenance chains
- Support audit and compliance

## Implementation Guidelines

### MCP Configuration
- Configuration in `.mcp/config.json` (to be added)
- Define MCP servers for each domain model
- Configure context exchange protocols
- Set up trace/audit settings

### Domain Model Integration
- Each domain model registers as MCP server
- Expose tools and capabilities via MCP
- Participate in context exchange
- Maintain traceability

### Orchestrator Integration
- Orchestrator uses MCP to route to domain models
- Context flows through MCP layer
- Results synthesized via MCP protocol

## Anti-Patterns

❌ **Direct API Calls**: Don't bypass MCP for agent communication
✅ **MCP Protocol**: Use MCP for all inter-agent communication

❌ **Ad-hoc Context**: Don't share context outside MCP
✅ **MCP Context**: All context exchange via MCP

❌ **No Traceability**: Don't skip audit trails
✅ **Full Traceability**: Maintain provenance through MCP

## When Adding MCP Integration

1. **Define Server**: Configure MCP server for domain model
2. **Expose Tools**: Register tools via MCP
3. **Context Exchange**: Implement context sharing
4. **Traceability**: Set up audit logging
5. **Testing**: Verify MCP protocol compliance

## MCP and Spores

- Spores can be exchanged via MCP
- ContextSpores contain context bundles
- PromptSpores contain prompt logic
- MCP provides secure transport for Spores

## Future Implementation

When MCP configuration is added:
- Review MCP specification
- Configure servers for each domain model
- Set up context exchange protocols
- Implement trace/audit layer
- Test inter-agent communication

## Reference

- MCP specification (to be referenced when added)
- `.mcp/config.json` (to be created)
- Domain model MCP server definitions
