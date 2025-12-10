# ADR-004: Workflow Configuration Validation CLI Command

**Status**: Accepted
**Date**: 2025-12-01
**Author**: Claude Agent (Backend Engineer)
**Context**: Task-099 - Workflow Config Validation CLI Command

---

## Context and Problem Statement

JP Spec Kit's workflow configuration (`jpspec_workflow.yml`) is a critical file that defines:
- Task lifecycle states (To Do, Specified, Planned, etc.)
- Workflow commands (`/jpspec:specify`, `/jpspec:implement`, etc.)
- State transitions and their valid paths
- Agent assignments for each workflow phase

**Problems**:
- Configuration errors are discovered at runtime during workflow execution
- Invalid state references cause cryptic errors when executing `/jpspec` commands
- Circular dependencies in state transitions can create infinite loops
- Unreachable states indicate dead code in workflow configuration
- No early validation catches schema violations before deployment
- Manual inspection of YAML is error-prone and time-consuming

**Goal**: Provide a CLI command that validates workflow configuration files before they're used, catching both syntax errors (schema validation) and semantic errors (logic issues) early in the development process.

---

## Decision Drivers

1. **Early Error Detection**: Catch configuration errors before runtime
2. **Clear Error Messages**: Provide actionable feedback for fixing issues
3. **Automation-Friendly**: Support CI/CD integration with JSON output
4. **Comprehensive Validation**: Check both structure and semantics
5. **Developer Experience**: Fast feedback with verbose mode for debugging
6. **Exit Code Conventions**: Standard codes for different error types

---

## Decision

Implement `specify workflow validate` CLI command with:

### Schema Validation (Structural)
- Validate against JSON schema (`memory/jpspec_workflow.schema.json`)
- Check required fields (version, states, workflows, transitions)
- Verify field types and value constraints
- Graceful degradation if `jsonschema` library not installed

### Semantic Validation (Logic)
- **Cycle Detection**: Ensure state transition graph is acyclic (DAG)
- **Reachability Analysis**: Verify all states reachable from "To Do"
- **Terminal State Check**: Ensure at least one end state exists
- **Reference Validation**: Check all state/workflow references are defined
- **Agent Warnings**: Warn about unknown agent names (non-blocking)

### CLI Interface
```bash
specify workflow validate                    # Default config
specify workflow validate --file custom.yml  # Custom file
specify workflow validate --verbose          # Detailed output
specify workflow validate --json             # CI/automation
```

### Exit Codes
- **0**: Validation passed (warnings are non-blocking)
- **1**: Validation errors (schema or semantic)
- **2**: File errors (not found, invalid YAML, read errors)

---

## Consequences

### Positive

1. **Prevents Runtime Errors**: Configuration errors caught before execution
   - Invalid state transitions fail fast
   - Circular dependencies detected upfront
   - Missing references identified immediately

2. **Improved Developer Experience**:
   - Clear, actionable error messages with context
   - Verbose mode for debugging complex configurations
   - Fast feedback loop (<1s for typical configs)

3. **CI/CD Integration**:
   - JSON output for automated pipeline validation
   - Standard exit codes for build scripts
   - Can gate deployments on config validity

4. **Self-Documenting**:
   - Validation errors explain configuration requirements
   - Context includes valid alternatives (e.g., "Valid states: [...]")
   - Helps users learn workflow configuration structure

5. **Maintainability**:
   - Reuses existing `WorkflowConfig` and `WorkflowValidator` classes
   - Comprehensive test coverage (84 tests total)
   - Defensive coding patterns throughout

### Negative

1. **Additional CLI Surface Area**:
   - One more command to maintain and test
   - Documentation burden (help text, examples, guides)
   - Potential for version drift if schema changes

2. **False Positives Possible**:
   - Unknown agent warnings may flag custom agents
   - Strict schema validation may reject valid extensions
   - Mitigated by: warnings vs errors, graceful degradation

3. **Performance Considerations**:
   - For very large configs (100+ states), validation may be slow
   - Currently not a concern (<1s for typical 10-20 state configs)
   - Could optimize with caching if needed

---

## Implementation Details

### Architecture

```
specify workflow validate
    ↓
workflow_validate() CLI function
    ↓
WorkflowConfig.load(validate=True)  → Schema validation
    ↓
WorkflowValidator(config._data).validate()  → Semantic validation
    ↓
ValidationResult (errors, warnings)
    ↓
Output (human-readable or JSON) + Exit code
```

### Error Handling Strategy

1. **File Errors (Exit 2)**:
   - `WorkflowConfigNotFoundError` → File not found
   - `WorkflowConfigError` → YAML parse error
   - `Exception` → Unexpected errors

2. **Validation Errors (Exit 1)**:
   - `WorkflowConfigValidationError` → Schema violations
   - `ValidationResult.errors` → Semantic issues

3. **Success (Exit 0)**:
   - No errors (warnings are allowed)

### JSON Output Format

```json
{
  "valid": true,
  "config_file": "/path/to/jpspec_workflow.yml",
  "schema_validation": {
    "passed": true,
    "error": null
  },
  "semantic_validation": {
    "passed": true,
    "errors": [],
    "warnings": [
      {
        "code": "UNKNOWN_AGENT",
        "message": "...",
        "context": {...}
      }
    ]
  }
}
```

### Key Design Decisions

1. **Use `print()` for JSON Output**:
   - Rich console adds ANSI codes even to JSON
   - Use built-in `print()` to avoid formatting
   - Ensures clean JSON for CI parsing

2. **Agent Objects Support**:
   - Handle both string agents: `["PM Planner"]`
   - And object agents: `[{"name": "PM Planner", "identity": "@pm"}]`
   - Defensive coding: check `isinstance()` for both

3. **Exit Code Hierarchy**:
   - File errors (2) are more severe than validation errors (1)
   - Allows CI to distinguish between config issues vs system issues
   - Following POSIX conventions

---

## Alternatives Considered

### Alternative 1: No Dedicated Command
**Approach**: Only validate during workflow execution (on-demand)

**Rejected Because**:
- Errors discovered too late (after work started)
- No way to validate configuration changes independently
- No CI/CD integration point for config validation

### Alternative 2: Separate Validator Binary
**Approach**: Standalone `workflow-validator` tool

**Rejected Because**:
- Adds complexity (separate packaging, deployment)
- Fragments user experience (two tools instead of one)
- Harder to maintain version compatibility

### Alternative 3: Python API Only (No CLI)
**Approach**: Provide only `WorkflowValidator` class, no CLI

**Rejected Because**:
- No CI/CD integration without CLI
- Requires users to write validation scripts
- Misses opportunity for user-friendly error messages

---

## Related Decisions

- **ADR-002**: Workflow Step Tracking Architecture (uses same config)
- **ADR-001**: Backlog.md Integration (depends on valid workflow state transitions)

---

## Testing Strategy

1. **Unit Tests** (63 tests): `tests/test_workflow_validator.py`
   - Cycle detection algorithms
   - Reachability checks
   - State reference validation
   - Agent name validation
   - Edge cases and defensive coding

2. **CLI Integration Tests** (21 tests): `tests/test_cli_workflow_validate.py`
   - Valid/invalid configs
   - File not found scenarios
   - Schema validation errors
   - Semantic validation errors
   - JSON output format
   - Exit code verification
   - Verbose mode output

3. **Manual Testing**:
   - Real `jpspec_workflow.yml` validation
   - Custom config files
   - CI/CD integration (exit codes, JSON parsing)

---

## Compliance and Governance

### Exit Code Standards
Follows POSIX conventions:
- 0 = success
- 1-125 = various error conditions
- 126+ = reserved for shell use

### JSON Schema Compliance
- Uses Draft 7 JSON Schema
- Optional `jsonschema` library (graceful degradation)
- Schema stored at `memory/jpspec_workflow.schema.json`

### Defensive Coding
- Type checking with `isinstance()`
- `.get()` with defaults throughout
- Null-safe operations
- Comprehensive error context

---

## References

- Task-099: Workflow Config Validation CLI Command
- `/home/jpoley/ps/jp-spec-kit/src/specify_cli/workflow/config.py`
- `/home/jpoley/ps/jp-spec-kit/src/specify_cli/workflow/validator.py`
- `/home/jpoley/ps/jp-spec-kit/tests/test_cli_workflow_validate.py`
- CLAUDE.md: Updated with `specify workflow validate` documentation
