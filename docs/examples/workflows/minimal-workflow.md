# Minimal Workflow Example

## Overview

This configuration provides the fastest possible SDD workflow with only essential phases:

1. **Specify** - Create requirements
2. **Implement** - Write code
3. **Done** - Complete

## Use Cases

- Rapid prototyping
- Personal projects
- Internal tools
- Low-compliance environments
- Proof-of-concept development
- Hackathons

## What's Skipped

| Phase | Why Skipped | Risk |
|-------|-------------|------|
| **Assessment** | Assumes all features suitable for SDD | May waste time on simple fixes |
| **Research** | Assumes requirements are clear | May build wrong solution |
| **Planning** | Assumes simple architecture | May encounter tech debt |
| **Validation** | Relies on manual testing | Quality issues may slip through |
| **Operations** | Relies on manual deployment | Deployment errors possible |

## Workflow Diagram

```
To Do
  ↓ /flow:specify
Specified
  ↓ /flow:implement
In Implementation
  ↓ manual
Done
```

## Usage

1. **Copy the configuration**:
   ```bash
   cp docs/examples/workflows/minimal-workflow.yml flowspec_workflow.yml
   ```

2. **Validate**:
   ```bash
   specify workflow validate
   ```

3. **Create a task**:
   ```bash
   backlog task create "Build user profile page"
   ```

4. **Run the workflow**:
   ```bash
   /flow:specify
   # Creates PRD at docs/prd/{feature}.md

   /flow:implement
   # Engineers implement, reviewers review

   backlog task edit task-123 -s Done
   # Mark complete
   ```

## Agents Involved

- **product-requirements-manager** - Creates lightweight PRD
- **frontend-engineer** - Implements UI
- **backend-engineer** - Implements API/logic
- **frontend-code-reviewer** - Reviews UI code
- **backend-code-reviewer** - Reviews backend code

## Customization

### Add Basic Testing

Add a validation step before marking Done:

```yaml
states:
  - "To Do"
  - "Specified"
  - "In Implementation"
  - "Tested"  # New state
  - "Done"

workflows:
  validate:
    command: "/flow:validate"
    agents:
      - name: "quality-guardian"
        # ...
    input_states: ["In Implementation"]
    output_state: "Tested"

transitions:
  - name: "validate"
    from: "In Implementation"
    to: "Tested"
    via: "validate"

  - name: "complete"
    from: "Tested"  # Changed from "In Implementation"
    to: "Done"
```

### Add Planning Phase

For slightly more complex projects:

```yaml
states:
  - "To Do"
  - "Specified"
  - "Planned"  # New state
  - "In Implementation"
  - "Done"

workflows:
  plan:
    command: "/flow:plan"
    agents:
      - name: "software-architect"
        # ...
    input_states: ["Specified"]
    output_state: "Planned"

  implement:
    input_states: ["Planned"]  # Changed from ["Specified"]
    # ...
```

## Comparison to Full Workflow

| Aspect | Minimal Workflow | Full SDD Workflow |
|--------|------------------|-------------------|
| **Phases** | 2 | 7 |
| **States** | 4 | 9 |
| **Agents** | 5 | 16 |
| **Time to Done** | ~1-2 days | ~1-2 weeks |
| **Quality Assurance** | Manual | Automated + Manual |
| **Compliance** | None | SOC2/SLSA ready |
| **Best For** | Prototypes | Production systems |

## Migration Path

As projects mature, gradually add phases:

1. Start with minimal workflow
2. Add **Planning** when architecture complexity increases
3. Add **Validation** when quality issues appear
4. Add **Operations** when deployment becomes frequent
5. Add **Research** for strategic features
6. Add **Assessment** for portfolio management

## Limitations

- No architecture planning (risk of tech debt)
- No security validation (risk of vulnerabilities)
- No compliance support (not suitable for regulated industries)
- No deployment automation (manual deployment overhead)
- No formal QA process (quality depends on code review)

## Best Practices

1. **Still write tests** - Even without formal validation phase
2. **Document architecture decisions** - Even without ADRs
3. **Run security scans** - Use pre-commit hooks
4. **Automate deployment** - Use CI/CD even without /flow:operate
5. **Review regularly** - Code review is your quality gate

## When to Upgrade

Consider upgrading to a fuller workflow when:

- Project becomes business-critical
- Team size grows beyond 2-3 people
- Compliance requirements emerge
- Deployment frequency increases
- Quality issues increase
- Architecture becomes complex

## Related Examples

- [Security Audit Workflow](./security-audit-workflow.md) - Adds security phase
- [Custom Agents Workflow](./custom-agents-workflow.md) - Organization-specific agents
