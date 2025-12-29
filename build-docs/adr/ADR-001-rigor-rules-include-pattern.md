# ADR-001: Rigor Rules Include Pattern

**Status**: Proposed
**Date**: 2025-12-17
**Decision Maker**: Software Architect
**Stakeholders**: Engineering Team, DevOps, QA

## Context

The Rigor Rules system needs to be integrated across 7 different /flow:* commands (/flow:assess, /flow:specify, /flow:plan, /flow:implement, /flow:validate, /flow:operate, /flow:freeze). Each command needs access to the same set of rules but may enforce different subsets based on the workflow phase.

### Problem Statement

How should we distribute and maintain the rigor rules across multiple workflow commands while ensuring:
1. Single source of truth (no duplication)
2. Easy maintenance (changes propagate automatically)
3. Phase-specific rule subsets (not all rules apply to all commands)
4. Clear integration pattern (consistent across commands)

### Alternatives Considered

We evaluated four approaches:

#### Option 1: Inline Rules in Each Command
**Implementation**: Copy-paste rules into each command template.

**Pros**:
- Self-contained commands (no external dependencies)
- Fast to execute (no file I/O)
- Easy to understand for newcomers

**Cons**:
- High maintenance burden (update 7 files for each rule change)
- Drift risk (rules become inconsistent across commands)
- Bloated command files (1000+ lines per command)
- No versioning story (which command has the latest rules?)

**Verdict**: Rejected due to maintenance burden and drift risk.

---

#### Option 2: Python Module with Programmatic Rules
**Implementation**: Create `flowspec_cli/rigor_rules.py` with rule definitions as Python classes/functions.

```python
class RigorRule:
    def __init__(self, id, phase, severity, validator, remediation):
        self.id = id
        self.phase = phase
        self.severity = severity
        self.validator = validator
        self.remediation = remediation

class ExecWorktreeRule(RigorRule):
    def validate(self, context):
        # Python validation logic
        pass
```

**Pros**:
- Programmatic access to rules (can query, filter dynamically)
- Type safety (Python typing for rule definitions)
- Unit testable (mock context, test validators)
- Rich error handling (Python exceptions)

**Cons**:
- Language lock-in (rules only accessible from Python)
- Complexity overhead (need Python interpreter in command templates)
- Not human-readable in isolation (must browse Python code)
- Harder to customize (requires Python knowledge)
- Execution overhead (import, instantiate objects)

**Verdict**: Rejected due to complexity and language lock-in.

---

#### Option 3: Shared Include File (_rigor-rules.md)
**Implementation**: Create `templates/partials/flow/_rigor-rules.md` with all rules in Markdown. Commands include it via `{{INCLUDE:path/to/_rigor-rules.md}}`.

```markdown
<!-- In /flow:implement.md -->
{{INCLUDE:.claude/partials/flow/_rigor-rules.md}}

<!-- Results in rules being injected into command -->
```

**Pros**:
- Single source of truth (one file to update)
- Human-readable (Markdown, not code)
- Language-agnostic (bash, Python, any language can parse)
- Low overhead (text substitution at command load time)
- Consistent with existing patterns (_backlog-instructions.md, _workflow-state.md)
- Easy to version (git tracks changes to one file)
- Self-documenting (rules include rationale inline)

**Cons**:
- Static at load time (can't query rules dynamically during execution)
- Requires include processing (tooling must support {{INCLUDE}} syntax)
- Phase filtering must be done at runtime (can't prefilter in include)

**Verdict**: **SELECTED** - Best balance of simplicity, maintainability, and consistency.

---

#### Option 4: YAML Configuration with Validator Plugins
**Implementation**: Define rules in `.flowspec/rigor-rules.yml` with validator plugins.

```yaml
rules:
  EXEC-001:
    name: "Git Worktree Required"
    phase: execution
    severity: blocking
    validator: worktree_validator
    remediation: "Run: git worktree add ..."
```

**Pros**:
- Structured data (easy to parse and query)
- Plugin architecture (custom validators)
- Configuration-driven (no code changes for new rules)

**Cons**:
- Requires validator plugin system (significant infrastructure)
- Two places to maintain (YAML + validator implementations)
- Less human-readable than Markdown (YAML syntax)
- Overhead of YAML parsing at runtime
- Plugin loading complexity

**Verdict**: Rejected due to infrastructure complexity and split maintenance burden.

---

## Decision

**We will use the Shared Include File pattern (_rigor-rules.md)** for the following reasons:

### Primary Reasons

1. **Single Source of Truth**: All 23 rules live in one file. Updates automatically propagate to all commands.

2. **Consistency with Existing Patterns**: Flowspec already uses shared includes:
   - `_backlog-instructions.md` (task management patterns)
   - `_workflow-state.md` (workflow state validation)
   - `_constitution-check.md` (constitution validation)

   Adding `_rigor-rules.md` follows the established convention.

3. **Human-Readable**: Rules are written in Markdown with clear sections:
   ```markdown
   ### Rule: EXEC-001 - Git Worktree Required
   **Severity**: BLOCKING
   **Enforcement**: strict

   **Validation**:
   ```bash
   # Bash validation logic
   ```

   **Remediation**:
   ```bash
   # Fix commands
   ```

   **Rationale**: Explanation of why this rule exists
   ```

4. **Language-Agnostic**: Rules can be executed by:
   - Bash scripts (inline validation)
   - Python (via subprocess or parsing)
   - Future languages (no Python dependency)

5. **Low Maintenance Burden**: Single file to edit. No need to update multiple locations.

6. **Self-Documenting**: Every rule includes:
   - ID (e.g., EXEC-001)
   - Severity (BLOCKING, ADVISORY)
   - Validation script
   - Remediation steps
   - Rationale

### Trade-offs Accepted

1. **Static Rule Loading**: Rules are loaded at command invocation, not dynamically queried.
   - **Impact**: Can't change rules mid-execution (acceptable - rules should be stable)
   - **Mitigation**: None needed - this is desired behavior

2. **Phase Filtering at Runtime**: All rules are loaded, phase filtering happens during execution.
   - **Impact**: Slight overhead (parsing all rules, filtering by phase)
   - **Mitigation**: Negligible performance impact (<10ms), acceptable

3. **Include Processing Dependency**: Commands must support `{{INCLUDE:path}}` syntax.
   - **Impact**: Requires include processor (already exists in Flowspec)
   - **Mitigation**: None needed - existing infrastructure

## Implementation Details

### File Location
```
templates/partials/flow/_rigor-rules.md
```

### Include Syntax
Commands include rules using:
```markdown
{{INCLUDE:.claude/partials/flow/_rigor-rules.md}}
```

### Phase Detection
The _rigor-rules.md file includes phase detection logic:
```bash
# Detect phase from command context
COMMAND="$1"
case "$COMMAND" in
  "/flow:assess"|"/flow:specify") PHASE="setup" ;;
  "/flow:plan"|"/flow:implement") PHASE="execution" ;;
  "/flow:freeze") PHASE="freeze" ;;
  "/flow:validate") PHASE="validation" ;;
esac
```

### Rule Structure Template
```markdown
### Rule: {PHASE}-{NNN} - {Rule Name}
**Severity**: BLOCKING|ADVISORY
**Enforcement**: strict|warn|off

{Description}

**Validation**:
```bash
# Validation logic that returns 0 (pass) or 1 (fail)
```

**Remediation**:
```bash
# Commands to fix the violation
```

**Rationale**: {Why this rule exists}
```

### Integration Pattern
Each /flow:* command follows this pattern:
```markdown
---
description: Command description
---

## User Input
$ARGUMENTS

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}
{{INCLUDE:.claude/partials/flow/_workflow-state.md}}
{{INCLUDE:.claude/partials/flow/_rigor-rules.md}}  # <-- Inject rules here

## Execution Instructions
[Command-specific logic]
```

## Consequences

### Positive

1. **Maintainability**: 1 file to update vs 7 files (85% reduction in maintenance effort)
2. **Consistency**: Zero chance of rules drifting across commands
3. **Discoverability**: All rules documented in one place
4. **Versioning**: Git tracks all rule changes in one file
5. **Extensibility**: New rules added once, available everywhere
6. **Testing**: Rules can be tested independently of commands

### Negative

1. **File Size**: _rigor-rules.md will grow to ~800 lines (acceptable - still manageable)
2. **Load Time**: Commands load all rules, not just phase-specific (negligible <10ms overhead)
3. **Include Dependency**: Requires working include processor (already exists)

### Neutral

1. **No Dynamic Querying**: Rules can't be queried programmatically at runtime (not needed)
2. **No Rule Plugins**: Custom validators must be added to _rigor-rules.md (acceptable)

## Validation

### Success Criteria

1. **Single Update Point**: Changing a rule requires editing only _rigor-rules.md
2. **Automatic Propagation**: All commands see rule changes immediately
3. **Phase Isolation**: Commands only execute rules for their phase
4. **Clear Documentation**: Every rule has validation, remediation, and rationale

### Metrics

- **File Count**: 1 file (vs 7 with inline approach)
- **Rule Coverage**: 23 rules across 5 phases
- **Load Overhead**: <10ms per command invocation
- **Maintenance Time**: <5 minutes to add new rule (vs 30+ minutes with inline)

## Related Decisions

- **ADR-002**: [JSONL Decision Logging](./ADR-002-jsonl-decision-logging.md) - Complements rigor rules with decision traceability
- **ADR-003**: [Branch Naming Convention](./ADR-003-branch-naming-convention.md) - Enforced by EXEC-002 rule
- **ADR-004**: [PR Iteration Pattern](./ADR-004-pr-iteration-pattern.md) - Enforced by PR-003 rule

## References

- Existing shared includes pattern: `templates/partials/flow/_backlog-instructions.md`
- Include processor implementation: `flowspec_cli/template_processor.py`
- Command template structure: `templates/commands/flow/*.md`

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-17 | 1.0 | Software Architect | Initial decision |
