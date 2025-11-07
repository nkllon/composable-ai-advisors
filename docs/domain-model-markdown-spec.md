## Domain Model (Markdown) Structure

Markdown domain models MUST follow this section schema so they can be parsed into a normalized representation and validated against `/.mcp/schemas/domain_model.schema.json`.

### Required Headings (exact text)
- `# Domain` — single line value (domain identifier or name)
- `## Description` — free text description
- `## Version` — semantic version (e.g., `1.0.0`)

### Optional Headings
- `## Capabilities` — bullet list
- `## Tools` — bullet list of tool identifiers
- `## Rules` — bullet list of rule set identifiers
- `## Expertise` — bullet list of routing keywords

### Example

```markdown
# Domain
investments

## Description
Models portfolio allocation, risk, and compliance constraints for investment workflows.

## Version
1.2.0

## Capabilities
- risk_assessment
- allocation

## Tools
- market-data-adapter
- compliance-checker

## Rules
- investment-policies

## Expertise
- finance
- risk
```

