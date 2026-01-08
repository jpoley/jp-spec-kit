# INITIAL: {{FEATURE_NAME}}

> **Purpose**: This INITIAL document is the canonical starting point for any new feature-level change. It provides structured context that flows into PRDs, PRPs, and implementation tasks.
>
> **Usage**: Copy this template to `docs/features/<feature-slug>-initial.md` and fill in each section. Then run `/flow:intake` to create a backlog task from this document.

---

## FEATURE

> Describe the problem, the desired outcome, key constraints, and why this matters.

### Problem Statement

<!-- What problem are we solving? Who experiences this problem? What is the impact? -->

[Describe the specific problem or pain point that this feature addresses. Be concrete about who is affected and how.]

### Desired Outcome

<!-- What does success look like? What will users be able to do that they couldn't before? -->

[Describe the end state after this feature is implemented. Focus on user capabilities and business value.]

### Key Constraints

<!-- What boundaries or limitations must we work within? -->

- **Technical**: [e.g., Must integrate with existing auth system, Must support offline mode]
- **Timeline**: [e.g., Needed for Q1 release, Blocking other features]
- **Resources**: [e.g., Single developer, Limited backend capacity]
- **Compatibility**: [e.g., Must support Node 18+, Must work on mobile]

### Why This Matters

<!-- What is the business or user impact? Why now? -->

[Explain the importance and urgency. Include metrics if available (e.g., "Affects 40% of users", "Reduces support tickets by estimated 25%")]

---

## EXAMPLES

> List relevant files under the `examples/` directory and explain what they illustrate.

<!-- Examples help implementers understand expected behavior, patterns, and edge cases -->

| Example File | Purpose | Relevance to This Feature |
|--------------|---------|---------------------------|
| `examples/[file1]` | [What this example demonstrates] | [How it relates to this feature] |
| `examples/[file2]` | [What this example demonstrates] | [How it relates to this feature] |

### Usage Patterns to Reference

<!-- Are there existing patterns in the codebase that this feature should follow? -->

- [ ] Pattern: [e.g., "See `src/commands/flow/specify.md` for command structure"]
- [ ] Pattern: [e.g., "See `src/skills/security-triage.md` for skill template"]

### Expected Behavior Examples

<!-- Describe concrete examples of how the feature should behave -->

**Example 1**: [Scenario description]
- Input: [What the user provides]
- Expected Output: [What should happen]

**Example 2**: [Scenario description]
- Input: [What the user provides]
- Expected Output: [What should happen]

---

## DOCUMENTATION

> Links to PRDs, ADRs, README sections, architecture docs, external specs, and previous related tasks.

### Internal Documentation

| Document | Link | Relevance |
|----------|------|-----------|
| PRD | `docs/prd/[filename].md` | [Brief note on relevance] |
| ADR | `docs/adr/[filename].md` | [Brief note on relevance] |
| Architecture | `docs/[filename].md` | [Brief note on relevance] |
| README Section | `README.md#section` | [Brief note on relevance] |

### External References

<!-- RFCs, API docs, library documentation, design specs, etc. -->

| Reference | URL | Relevance |
|-----------|-----|-----------|
| [Name] | [URL] | [Brief note on relevance] |

### Related Backlog Tasks

<!-- Previous or related tasks that provide context -->

| Task ID | Title | Status | Relevance |
|---------|-------|--------|-----------|
| `task-XXX` | [Title] | [Status] | [How it relates] |

---

## OTHER CONSIDERATIONS

> Known gotchas, previous failures, dependencies, security concerns, performance requirements, and other important context.

### Known Gotchas

<!-- Things that have tripped people up before or are easy to get wrong -->

- [ ] **Gotcha**: [Description of the pitfall]
  - **Impact**: [What goes wrong if you hit this]
  - **Mitigation**: [How to avoid it]

### Previous Failures

<!-- What has been tried before that didn't work? Why? -->

| Attempt | What Was Tried | Why It Failed | Lesson Learned |
|---------|----------------|---------------|----------------|
| [Date/Task] | [Approach] | [Reason] | [Key takeaway] |

### Dependencies

<!-- What does this feature depend on? What depends on this feature? -->

**Depends On**:
- [ ] [Feature/system/service this depends on]
- [ ] [External API or library requirement]

**Blocked By This**:
- [ ] [Feature that is waiting for this to be completed]

### Security Considerations

<!-- Security requirements, threats, compliance needs -->

- [ ] **Authentication**: [Requirements]
- [ ] **Authorization**: [Requirements]
- [ ] **Data Protection**: [Sensitive data handling]
- [ ] **Compliance**: [Regulatory requirements]

### Performance Requirements

<!-- Performance targets and constraints -->

- [ ] **Latency**: [e.g., "Response time < 200ms"]
- [ ] **Throughput**: [e.g., "Handle 1000 req/sec"]
- [ ] **Resource Usage**: [e.g., "Memory < 512MB"]

### Edge Cases to Consider

<!-- Boundary conditions and unusual scenarios -->

- [ ] [Edge case 1: Description]
- [ ] [Edge case 2: Description]
- [ ] [Edge case 3: Description]

---

## NEXT STEPS

> After completing this INITIAL document:

1. **Review**: Have stakeholders review and provide feedback
2. **Intake**: Run `/flow:intake docs/features/<feature-slug>-initial.md` to create a backlog task
3. **Assess**: Run `/flow:assess` to determine workflow complexity
4. **Specify**: Run `/flow:specify` to create a detailed PRD

---

*Template Version: 1.0.0*
*Based on: context-engineering-intro patterns (archon-inspired)*
