# ADR-003: Meta-Workflow Simplification

**Date**: 2025-12-26
**Status**: Accepted
**Deciders**: Autonomous refactor session
**Context**: Simplifying flowspec from 8 workflows to 3 meta-workflows

## Context

Flowspec currently has 8 distinct workflow commands:
1. `/flow:assess` - Complexity assessment
2. `/flow:specify` - Requirements specification
3. `/flow:research` - Research and validation
4. `/flow:plan` - Technical planning
5. `/flow:implement` - Code implementation
6. `/flow:validate` - QA and security validation
7. `/flow:operate` - Deployment and operations
8. `/flow:submit-n-watch-pr` - PR automation

**Problems**:
- High cognitive load for users (need to remember 8 commands and their sequence)
- Complex state machine (9 states, 16 transitions)
- Users must manually orchestrate multi-step workflows
- Not intuitive for newcomers
- Analysis shows this creates "horrible flow" (per docs/horrible-flow.png)

**Goals** (per docs/objective.md):
- Make flowspec more usable, less complicated, and more flexible
- Support complete customization via workflow editor (falcondev)
- Work across 4 AI tools: Claude Code, GitHub Copilot, Cursor, Gemini
- Maintain decision/event logging in JSONL
- Preserve power while improving simplicity

## Decision

We will implement **Meta-Workflows** that consolidate the 8 workflows into 3 high-level commands:

### 1. `/flow:research` - Plan It
**Purpose**: All upfront analysis and design activities
**Sub-Workflows**: assess → specify → (research) → plan
**Input State**: To Do
**Output State**: Planned
**Artifacts**: Assessment report, PRD, Research report (optional), ADRs, Technical spec

**Logic**:
- Always runs `assess` + `specify` + `plan`
- Conditionally runs `research` if complexity score ≥ 7 or user requests it
- Light mode: Skip research, use lightweight templates

### 2. `/flow:build` - Create It
**Purpose**: Implementation and verification
**Sub-Workflows**: implement → validate
**Input State**: Planned
**Output State**: Validated
**Artifacts**: Source code, tests, QA report, security report

**Logic**:
- Always runs `implement` + `validate` as atomic unit
- No intermediate state (direct Planned → Validated)
- Validation gates: tests pass, security checks clear, coverage ≥ threshold

### 3. `/flow:run` - Deploy It
**Purpose**: Deployment and operational readiness
**Sub-Workflows**: operate
**Input State**: Validated
**Output State**: Deployed/Done
**Artifacts**: Runbooks, deployment configs, monitoring setup

**Logic**:
- Currently maps 1:1 to `operate` command
- Future: Could auto-trigger CI/CD pipelines
- Terminal state transition

## Implementation Architecture

### 1. Extend flowspec_workflow.yml

Add new top-level section:

```yaml
meta_workflows:
  research:
    command: "/flow:research"
    description: "Upfront planning and design (assess + specify + research + plan)"
    sub_workflows:
      - workflow: assess
        required: true
      - workflow: specify
        required: true
      - workflow: research
        required: false
        condition: "complexity_score >= 7 OR light_mode == false"
      - workflow: plan
        required: true
    input_state: "To Do"
    output_state: "Planned"
    artifacts:
      - docs/assess/assessment-report.md
      - docs/prd/prd.md
      - docs/research/research-report.md (optional)
      - docs/adr/*.md
      - docs/platform/technical-spec.md

  build:
    command: "/flow:build"
    description: "Implementation and validation (implement + validate)"
    sub_workflows:
      - workflow: implement
        required: true
      - workflow: validate
        required: true
    input_state: "Planned"
    output_state: "Validated"
    artifacts:
      - src/**/*.{py,ts,tsx,go,etc}
      - tests/**/*.{py,test.ts,etc}
      - docs/qa/qa-report.md
      - docs/security/security-report.md
    gates:
      - type: test_coverage
        threshold: 80
      - type: security_scan
        severity: HIGH

  run:
    command: "/flow:run"
    description: "Deployment and operations (operate)"
    sub_workflows:
      - workflow: operate
        required: true
    input_state: "Validated"
    output_state: "Deployed"
    artifacts:
      - docs/runbooks/*.md
      - deploy/**/*.{yml,yaml,tf}
```

### 2. Create Meta-Workflow Orchestrator

New module: `src/flowspec_cli/workflow/meta_orchestrator.py`

**Responsibilities**:
- Load meta-workflow definitions from YAML
- Validate input state
- Execute sub-workflows in sequence
- Handle conditional logic (research skip)
- Aggregate artifacts
- Update final state
- Emit consolidated events

**Key Functions**:
```python
class MetaWorkflowOrchestrator:
    def execute_meta_workflow(self, meta_name: str, task_id: str) -> Result:
        """Execute meta-workflow by running sub-workflows in sequence"""

    def should_skip_sub_workflow(self, sub_config: dict) -> bool:
        """Evaluate conditions to skip optional sub-workflows"""

    def validate_gates(self, gates: list) -> bool:
        """Validate quality gates before transitioning state"""
```

### 3. Create Command Templates

**New Templates**:
- `templates/commands/flow/research.md` - Research meta-workflow
- `templates/commands/flow/build.md` - Build meta-workflow
- `templates/commands/flow/run.md` - Run meta-workflow

**Template Structure**:
```markdown
# /flow:research - Research Meta-Workflow

## Purpose
Consolidates assess + specify + (research) + plan into single command.

## Execution
1. Load meta-workflow config from flowspec_workflow.yml
2. Validate current task state = "To Do"
3. Execute sub-workflows:
   - /flow:assess (always)
   - /flow:specify (always)
   - /flow:research (if complexity ≥ 7)
   - /flow:plan (always)
4. Update task state to "Planned"
5. Emit workflow.planned event

## Usage
/flow:research [--task-id TASK_ID] [--skip-research] [--light-mode]
```

### 4. Backward Compatibility

**Preserve existing commands**: All 8 original commands remain available

**Reason**:
- Power users may want fine-grained control
- Partial re-runs after failures
- Custom workflows that don't fit meta-workflow model
- Migration path for existing users

**Documentation**: Recommend meta-workflows for new users, granular commands for advanced use

## Alternatives Considered

### Alternative 1: Replace existing commands entirely
**Rejected**: Breaking change, no migration path, loses flexibility

### Alternative 2: Hard-code meta-workflows in Python
**Rejected**: Not customizable, violates config-driven architecture

### Alternative 3: Keep 8 commands, add aliases
**Rejected**: Doesn't solve complexity problem, just adds more commands

### Alternative 4: External orchestration (shell scripts)
**Rejected**: Doesn't integrate with workflow config, loses validation

## Consequences

### Positive
✅ **Simplicity**: 3 commands vs. 8 for common path
✅ **Flexibility**: Still have granular commands for edge cases
✅ **Customizable**: Meta-workflows defined in YAML, user can modify
✅ **Cross-tool compatible**: Works in Claude, Copilot, Cursor, Gemini
✅ **Atomic validation**: Build ensures implementation + validation together
✅ **Config-driven**: Extends existing architecture pattern
✅ **Backward compatible**: Existing commands still work

### Negative
⚠️ **Learning curve**: Users need to understand meta vs. granular workflows
⚠️ **Documentation complexity**: Two tiers of commands to document
⚠️ **Error handling**: Failure mid-meta-workflow requires recovery logic
⚠️ **State granularity**: Lose intermediate states (e.g., "Specified" not visible)

### Mitigation
- Clear documentation with decision tree (when to use meta vs. granular)
- Resume/retry mechanism for partial failures
- Optional intermediate state logging (events still emitted)
- Migration guide for existing users

## Implementation Plan

### Phase 1: Foundation (15 min)
1. Extend `flowspec_workflow.yml` schema with `meta_workflows`
2. Update schema validator to support meta-workflows
3. Add meta-workflow queries to `WorkflowConfig` class

### Phase 2: Orchestrator (20 min)
4. Create `meta_orchestrator.py` module
5. Implement sub-workflow execution logic
6. Add conditional skip logic
7. Add quality gate validation
8. Integrate with event system

### Phase 3: Commands (15 min)
9. Create `/flow:research` template
10. Create `/flow:build` template
11. Create `/flow:run` template
12. Symlink templates to .claude/commands/

### Phase 4: Testing (10 min)
13. Test research meta-workflow end-to-end
14. Test build meta-workflow with failing tests (gate validation)
15. Test run meta-workflow
16. Test backward compatibility (granular commands still work)

## Validation Criteria

✅ Meta-workflows execute sub-workflows in correct order
✅ Conditional logic works (research skip in light mode)
✅ Quality gates prevent invalid transitions
✅ Events emitted for each sub-workflow
✅ Final state correctly updated
✅ Backward compatible (existing commands work)
✅ YAML config validates against schema
✅ Error handling recovers from mid-workflow failures

## References

- `docs/objective.md` - User requirements for simplification
- `docs/analysis-flowspec.md` - Research/Build/Run proposal
- `docs/cleaner-flow.png` - Visual reference for desired workflow
- `flowspec_workflow.yml` - Existing workflow configuration
- `src/flowspec_cli/workflow/config.py` - Workflow config loader

## Notes

This ADR addresses the core objective: making flowspec "more usable, less complicated, and more flexible" while maintaining power and customizability. The meta-workflow approach provides a gentle slope of complexity: new users see 3 simple commands, power users can drop to 8 granular commands when needed.

## One-Way Doors

✅ **Reversible**: Can remove meta-workflows without breaking existing commands
✅ **Additive**: Adding meta-workflows doesn't change existing behavior
✅ **Config-driven**: Users can modify meta-workflows via YAML

No one-way doors identified.
