# MCP Configuration Directory

## Purpose

This directory will contain MCP (Model Context Protocol) configuration files for the Composable AI Advisors project.

## Planned Structure

```
.mcp/
├── config.json          # Main MCP configuration
├── servers/              # MCP server definitions
│   ├── domain-model-a.json
│   ├── domain-model-b.json
│   └── domain-model-c.json
├── tools/                # Tool adapter configurations
│   └── ...
└── context/              # Context exchange protocols
    └── ...
```

## Status

**Pending**: MCP configuration will be added separately.

## When Adding MCP Configuration

1. Define MCP server for each domain model
2. Configure tool adapters
3. Set up context exchange protocols
4. Implement trace/audit layer
5. Test inter-agent communication

## Reference

- See `.cursor/rules/mcp.mdc` for MCP implementation guidelines
- MCP specification (to be referenced when added)

