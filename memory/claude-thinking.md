# Extended Thinking Mode

Claude Code supports extended thinking mode for complex reasoning tasks. Use thinking triggers to improve output quality for architecture, security, and research decisions.

## Thinking Budget Levels

| Trigger | Budget | Use Case |
|---------|--------|----------|
| `think` | 4,000 tokens | Quick decisions, simple analysis |
| `think hard` | 10,000 tokens | Architecture decisions, security review |
| `megathink` | 10,000 tokens | Complex research, comprehensive analysis |
| `ultrathink` | 31,999 tokens | Critical decisions, multi-factor tradeoffs |

## When to Trigger Extended Thinking

### Architecture Decisions (`think hard`)
- System design choices
- Technology selection
- API design patterns
- Database schema decisions
- Integration architecture

### Security Analysis (`think hard`)
- Vulnerability assessment
- Threat modeling
- Security architecture review
- Compliance verification
- Attack surface analysis

### Research Tasks (`megathink`)
- Technology evaluation
- Competitive analysis
- Feasibility studies
- Performance benchmarking
- Market research

### Critical Decisions (`ultrathink`)
- Major architectural changes
- Security-critical decisions
- Complex tradeoff analysis
- High-stakes technical choices

## Integration with /flowspec Commands

### /flow:plan
Architecture and platform design require deep thinking:
```
Think hard about the architecture decisions. Consider:
- Scalability requirements
- Technology tradeoffs
- Long-term maintainability
- Integration complexity
```

### /flow:validate
Security and QA review benefit from extended analysis:
```
Think hard about security implications. Analyze:
- Attack vectors
- Data flow security
- Authentication/authorization
- Compliance requirements
```

### /flow:research
Comprehensive research needs maximum thinking:
```
Megathink on this research. Consider:
- All relevant technologies
- Long-term implications
- Market trends
- Technical feasibility
```

## Best Practices

### 1. Match Trigger to Task Complexity
- Simple: No trigger needed
- Medium: `think`
- Complex: `think hard`
- Research: `megathink`
- Critical: `ultrathink`

### 2. Be Specific About What to Think About
Bad: "Think about this"
Good: "Think hard about the security implications of this API design"

### 3. Allow Time for Processing
Extended thinking takes longer but produces better results.
Don't interrupt the thinking process.

### 4. Review Thinking Output
When Claude explains its reasoning, review for:
- Missed considerations
- Incorrect assumptions
- Alternative approaches

## Command Examples

```bash
# Architecture planning with extended thinking
/flow:plan
# Then in your message: "Think hard about the architecture decisions. Consider scalability, technology tradeoffs, and long-term maintainability."

# Security validation with focused analysis
/flow:validate
# Then in your message: "Think hard about security implications. Analyze attack vectors, data flow security, and compliance requirements."

# Comprehensive research
/flow:research
# Then in your message: "Megathink on this research. Consider all relevant technologies, long-term implications, and market trends."
```

## Limitations

- Extended thinking uses more tokens
- Some models may not support all thinking levels
- Not all tasks benefit from extended thinking
- Simple tasks may be slower without benefit
