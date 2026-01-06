---
description: Create Architecture Decision Records (ADRs) for technical decisions.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command creates Architecture Decision Records (ADRs) to document significant architectural and technical decisions, their context, and their consequences.

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}

### Overview

The decide command helps you:
1. Document the context for a technical decision
2. Evaluate alternative approaches
3. Record the decision and its rationale
4. Document expected consequences
5. Create an ADR file following standard format

### When to Create an ADR

Create an ADR for decisions that:
- Affect system structure or architecture
- Have significant impact on non-functional requirements
- Introduce new patterns or technologies
- Resolve technical trade-offs
- Change development practices
- Impact security, scalability, or performance

### ADR Numbering

```bash
# Find the next ADR number
ls -1 docs/adr/ADR-*.md 2>/dev/null | wc -l
# Use this count + 1 for the new ADR number
```

### ADR Template

Create ADR at `./docs/adr/ADR-{NNN}-{slug}.md`:

```markdown
# ADR-{NNN}: {Decision Title}

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: {YYYY-MM-DD}
**Author**: {Your Name or Agent Identity}
**Related ADRs**: {Links to related ADRs if any}

---

## Context and Problem Statement

{Describe the context and the problem that needs to be solved. What is the issue that
motivates this decision or change?}

### Current Situation

{What is the current state? What are the limitations or problems with the status quo?}

### Requirements and Constraints

{What must the solution accomplish? What constraints exist (technical, organizational,
regulatory)?}

---

## Decision Drivers

{What factors are most important in making this decision?}

- **Performance**: {Impact on performance metrics}
- **Scalability**: {Impact on ability to scale}
- **Maintainability**: {Impact on code maintainability}
- **Security**: {Impact on security posture}
- **Cost**: {Financial implications}
- **Time**: {Time to implement}
- **Team Expertise**: {Match with team capabilities}
- **Vendor Lock-in**: {Risk of dependency}

---

## Considered Options

### Option 1: {Name}

**Description**: {What is this option?}

**Pros**:
- {Advantage 1}
- {Advantage 2}

**Cons**:
- {Disadvantage 1}
- {Disadvantage 2}

**Trade-offs**: {Key trade-offs of this approach}

---

### Option 2: {Name}

**Description**: {What is this option?}

**Pros**:
- {Advantage 1}
- {Advantage 2}

**Cons**:
- {Disadvantage 1}
- {Disadvantage 2}

**Trade-offs**: {Key trade-offs of this approach}

---

### Option 3: {Name} (if applicable)

**Description**: {What is this option?}

**Pros**:
- {Advantage 1}
- {Advantage 2}

**Cons**:
- {Disadvantage 1}
- {Disadvantage 2}

**Trade-offs**: {Key trade-offs of this approach}

---

## Decision Outcome

**Chosen Option**: {Option X: Name}

**Rationale**: {Why was this option selected over the alternatives? What makes it the
best fit for the context and requirements?}

### Expected Positive Consequences

- {Benefit 1}
- {Benefit 2}
- {Benefit 3}

### Expected Negative Consequences

- {Trade-off or limitation 1}
- {Trade-off or limitation 2}

### Mitigation Strategies

For negative consequences:
- {How to mitigate issue 1}
- {How to mitigate issue 2}

---

## Implementation Notes

### Key Changes Required

{What needs to change to implement this decision?}

1. {Change 1}
2. {Change 2}
3. {Change 3}

### Migration Path

{If changing from existing approach, how do we migrate?}

### Validation Criteria

{How will we know if this decision was correct?}

- {Metric or indicator 1}
- {Metric or indicator 2}

---

## References

{Links to supporting documents, research, discussions, etc.}

- {Reference 1}
- {Reference 2}
- {Reference 3}

---

**Reviewers**: {List who should review this ADR}
**Status Date**: {Date status was set}
**Next Review Date**: {When to re-evaluate if needed}
```

### Workflow Steps

1. **Identify the Decision**
   - What needs to be decided?
   - Why is this decision important?
   - What is the scope and impact?

2. **Gather Context**
   - Current situation and problems
   - Requirements and constraints
   - Decision drivers (what matters most)

3. **Research Options**
   - Identify at least 2-3 viable alternatives
   - Research pros/cons of each
   - Understand trade-offs

4. **Make the Decision**
   - Choose the best option
   - Document clear rationale
   - Acknowledge trade-offs

5. **Document Consequences**
   - Expected benefits
   - Expected drawbacks
   - Mitigation strategies

6. **Create ADR File**
   - Use sequential numbering
   - Include all sections
   - Save to `docs/adr/`

### Best Practices

1. **Be Specific**: Vague ADRs are not useful. Be concrete about the problem and solution.
2. **Include Context**: Future readers need to understand why this decision was made.
3. **Show Alternatives**: Document what was considered, not just what was chosen.
4. **Own Trade-offs**: Every decision has trade-offs. Acknowledge them openly.
5. **Keep It Concise**: ADRs should be readable in 5-10 minutes.
6. **Update Status**: If an ADR is superseded, update its status and link to the new ADR.

### Example Use Cases

```bash
# Example: Choosing a database
/arch:decide "Database selection for user service"

# Example: API design pattern
/arch:decide "REST vs GraphQL for public API"

# Example: Deployment strategy
/arch:decide "Blue-green vs canary deployment strategy"

# Example: Authentication approach
/arch:decide "JWT vs session-based authentication"
```

### Post-Completion

After creating the ADR:

1. **Review**: Have it reviewed by relevant stakeholders
2. **Update Status**: Change from "Proposed" to "Accepted" after approval
3. **Reference**: Link to this ADR from related documentation
4. **Track**: Add to backlog if implementation is needed

```bash
# Create implementation task if needed
backlog task create "Implement ADR-{NNN}: {Title}" \
  -d "Implementation of architectural decision documented in docs/adr/ADR-{NNN}-{slug}.md" \
  --ac "Implementation matches ADR specifications" \
  --ac "Migration path completed if applicable" \
  -l implement,architecture
```

### Quality Checks

Before finalizing the ADR:
- [ ] Problem statement is clear and specific
- [ ] At least 2 alternatives are documented
- [ ] Rationale for chosen option is well-explained
- [ ] Consequences (both positive and negative) are listed
- [ ] Implementation notes provide guidance
- [ ] References and reviewers are included

## Related Commands

- `/arch:design` - Comprehensive architecture planning
- `/arch:model` - Data modeling and system diagrams
- `/pm:define` - Product requirements that drive decisions
- `/dev:build` - Implementation of architectural decisions
