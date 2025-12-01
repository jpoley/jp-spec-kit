# ADR-005: Workflow Constraint Enforcement

## Status
Accepted

## Context
/jpspec commands can be run in any order, which may lead to skipped phases or invalid state transitions. We need to enforce workflow constraints while maintaining backward compatibility.

## Decision
Implement a `WorkflowStateGuard` class that:
1. Validates current task state against allowed input states before command execution
2. Provides clear error messages with suggestions when state check fails
3. Updates task state to output_state after successful execution
4. Supports `--skip-state-check` flag for power users

### Key Design Choices

**Soft enforcement by default**: When no `jpspec_workflow.yml` exists, commands proceed without blocking. This maintains backward compatibility.

**Case-insensitive matching**: State comparisons are case-insensitive to handle variations like "To Do" vs "to do".

**Helpful error messages**: When blocked, show:
- Current state
- Required states
- Valid workflows for current state
- How to bypass (not recommended)

## Alternatives Considered

1. **Hard enforcement always**: Block commands without config
   - Rejected: Breaks existing projects

2. **No enforcement**: Leave as-is
   - Rejected: Users asked for workflow guardrails

3. **Warnings only**: Warn but don't block
   - Rejected: Too easy to ignore

## Consequences

### Positive
- Prevents accidental out-of-order execution
- Clear feedback on workflow progression
- Backward compatible with existing projects
- Power users can bypass when needed

### Negative
- Requires jpspec_workflow.yml for full enforcement
- Adds complexity to command execution
- May frustrate users who want flexibility

## Implementation
- `src/specify_cli/workflow/state_guard.py`: Core validation logic
- `tests/workflow/test_state_guard.py`: Comprehensive tests
- Integration: Each /jpspec command imports and uses WorkflowStateGuard
