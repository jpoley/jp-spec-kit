# ADR-001: Backlog.md CLI Integration for JPSpec Commands

**Status**: Accepted
**Date**: 2025-11-28
**Author**: Claude Agent
**Context**: Task-106 - Design backlog.md integration architecture

---

## Context and Problem Statement

JP Spec Kit's `/jpspec:*` commands orchestrate 15+ specialized AI agents across 6 workflows (specify, plan, research, implement, validate, operate). Currently, all task management is manual and ad-hoc with no standardized lifecycle tracking.

**Problems**:
- No automated task activation when agents start work
- No standardized progress tracking during execution
- No consistent completion verification (AC checking, notes, status)
- No visibility into multi-phase agent transitions
- Manual coordination across parallel/sequential agent execution
- Missing audit trail of agent work

**Goal**: Design a standardized backlog.md CLI integration pattern that all jpspec commands can adopt uniformly, enabling automated task lifecycle management from discovery through completion.

---

## Decision Drivers

1. **Consistency**: All 6 commands should follow identical patterns
2. **Agent Independence**: Minimal impact on existing agent contexts
3. **Reusability**: Shared templates reduce duplication
4. **Auditability**: Complete task lifecycle tracking
5. **Flexibility**: Support single-agent, parallel, and sequential workflows
6. **Human Oversight**: Preserve human approval gates (validate command)

---

## Considered Options

### Option 1: Command-Level Integration Only
**Approach**: Add backlog CLI calls only at command entry/exit in `.claude/commands/jpspec/*.md`

**Pros**:
- Minimal changes to agent contexts
- Simple to implement
- Clear separation of concerns

**Cons**:
- No visibility into sub-agent progress
- No phase transition tracking for multi-agent workflows
- Limited audit trail

### Option 2: Agent-Level Integration (Full Instrumentation)
**Approach**: Inject backlog instructions into every agent context, enabling agents to self-manage tasks

**Pros**:
- Complete lifecycle visibility
- Agents can create subtasks
- Rich audit trail
- Progress tracking during execution

**Cons**:
- Requires modifying all 15+ agent contexts
- Increased complexity
- Risk of inconsistent agent behavior

### Option 3: Hybrid Approach (Command + Strategic Agent Integration)
**Approach**: Command-level entry/exit hooks + backlog instructions injected into specific high-value agents

**Pros**:
- Balance of visibility and simplicity
- Strategic instrumentation where it matters
- Preserves agent independence
- Enables subtask creation where beneficial

**Cons**:
- Requires judgement on which agents to instrument
- More complex than option 1

---

## Decision Outcome

**Chosen Option**: **Option 3 - Hybrid Approach**

### Rationale

The hybrid approach provides the best balance of:
- **Command-level hooks** for guaranteed entry/exit lifecycle management
- **Strategic agent instrumentation** for high-value workflows (PM Planner, SRE)
- **Minimal disruption** to existing agent contexts
- **Incremental adoption** - start with command hooks, add agent instrumentation as needed

### Implementation Strategy

**Phase 1: Foundation (Command-Level Hooks)**
- All 6 commands get entry/exit hooks
- Standardized task activation, completion, and notes
- Immediate value with minimal changes

**Phase 2: Strategic Agent Instrumentation**
- PM Planner (specify): Create subtasks from task breakdown
- SRE Agent (operate): Track 9-phase operational deliverables
- Release Manager (validate): Document human approval decisions

**Phase 3: Optional Extensions**
- Other agents can opt-in to backlog CLI usage
- Template supports all agents uniformly
- No forced adoption

---

## Task Lifecycle State Machine

All jpspec-managed tasks follow this lifecycle:

```
┌─────────────┐
│   To Do     │  Initial state (task created but not started)
└──────┬──────┘
       │ Entry Hook: /jpspec:* command invoked
       │ Actions: assign agent(s), add plan
       ▼
┌─────────────┐
│ In Progress │  Active work phase
└──────┬──────┘
       │ During: Phase transitions, AC checks, progress notes
       │ Optional: Blocked state (dependency/issue)
       ▼
┌─────────────┐
│    Done     │  Task complete (all ACs checked, notes added)
└─────────────┘
```

### State Transitions

| From | To | Trigger | Required Actions |
|------|-----|---------|------------------|
| To Do | In Progress | Command entry hook | `--status "In Progress" --assign-to @agent` |
| In Progress | Blocked | Dependency/issue | `--status Blocked --append-notes "Blocker: ..."` |
| Blocked | In Progress | Issue resolved | `--status "In Progress" --append-notes "Resolved: ..."` |
| In Progress | Done | All ACs met + notes added | `--check-ac <all> --notes "<summary>" --status Done` |

### Phase Transitions (Multi-Agent Commands)

Commands with sequential phases (research, validate) update assignee during transitions:

```bash
# Example: research command (researcher → business validator)
# Phase 1 start
backlog task edit <id> -s "In Progress" --assign-to @researcher

# Phase 1 → Phase 2 transition
backlog task edit <id> --check-ac 1 --assign-to @business-validator

# Phase 2 complete
backlog task edit <id> --check-ac 2 --notes "<summary>" -s Done
```

---

## Shared Backlog Instructions Template

**Location**: `templates/partials/backlog-instructions.md`

**Purpose**: Reusable markdown snippet that can be injected into any agent context

**Injection Pattern**:
```markdown
# AGENT CONTEXT: [Agent Name]

[Agent-specific expertise and principles]

<!-- BACKLOG INTEGRATION START -->
{{> backlog-instructions.md}}
<!-- BACKLOG INTEGRATION END -->

# TASK: [Specific task description]
```

**Template Contents**:
- Task lifecycle overview
- Common CLI commands for task management
- AC management (check/uncheck)
- Implementation notes guidelines
- Definition of Done checklist

**Benefits**:
- Single source of truth for backlog CLI usage
- Consistent instructions across all agents
- Easy to update globally
- Optional inclusion (agents without integration skip it)

---

## Task Naming Conventions

All jpspec-created tasks follow this format:

```
jpspec-{command}-{feature-slug}-{yyyymmdd}-{descriptor}
```

### Format Breakdown

- **Prefix**: `jpspec-` (identifies creator)
- **Command**: One of: `specify`, `plan`, `research`, `implement`, `validate`, `operate`
- **Feature Slug**: Kebab-case feature identifier (e.g., `user-authentication`, `api-redesign`)
- **Timestamp**: Date in `yyyymmdd` format for uniqueness and ordering
- **Descriptor**: (Optional for main tasks, required for subtasks) Additional context

### Examples

**Main Tasks**:
```
jpspec-specify-user-auth-20251128
jpspec-implement-graphql-resolver-20251128
jpspec-validate-payment-flow-20251128
jpspec-operate-k8s-deployment-20251129
```

**Subtasks** (with descriptor):
```
jpspec-specify-user-auth-20251128-epic-signup
jpspec-implement-api-redesign-20251128-backend
jpspec-operate-k8s-deployment-20251129-observability
```

### Rationale

- **Parseable**: Easy to extract command, feature, date programmatically
- **Unique**: Timestamp prevents collisions
- **Sortable**: Alphabetical sort = chronological order
- **Searchable**: `backlog search "jpspec-implement"` finds all implementation tasks
- **Hierarchical**: Subtasks group under parent via naming

---

## Agent Instruction Injection Pattern

### Command-Level Injection (All Commands)

**Entry Hook Pattern** (add to `.claude/commands/jpspec/*.md`):

```markdown
## Pre-Execution: Task Activation

Before launching agents, activate the task in backlog.md:

```bash
# Read task context
backlog task <TASK_ID> --plain

# Activate task
backlog task edit <TASK_ID> -s "In Progress" --assign-to @<agent-name>

# Add implementation plan
backlog task edit <TASK_ID> --plan "1. [Phase 1]\n2. [Phase 2]\n3. [Phase 3]"
```

Continue with agent execution...
```

**Exit Hook Pattern**:

```markdown
## Post-Execution: Task Completion

After agent(s) complete work, finalize the task:

```bash
# Check all acceptance criteria
backlog task edit <TASK_ID> --check-ac 1 --check-ac 2 --check-ac 3

# Add implementation notes (PR description)
backlog task edit <TASK_ID> --notes "Summary of work completed. Key changes: ..."

# Mark task done
backlog task edit <TASK_ID> -s Done
```
```

### Agent-Level Injection (Strategic Agents)

**Option 1: Partial Injection** (template reference only)

```markdown
# AGENT CONTEXT: Product Requirements Manager

[Existing context...]

## Task Management

You have access to backlog.md CLI for task management. See shared backlog instructions for details.

Key capabilities:
- Create subtasks: `backlog task create "Title" -p <parent-id>`
- Track progress: `backlog task edit <id> --check-ac <index>`
- Add notes: `backlog task edit <id> --append-notes "Update"`

# TASK: [Specific task]
```

**Option 2: Full Injection** (include entire template)

```markdown
# AGENT CONTEXT: SRE Agent

[Existing context...]

<!-- BACKLOG INTEGRATION START -->
{{> templates/partials/backlog-instructions.md}}
<!-- BACKLOG INTEGRATION END -->

# TASK: [Specific task]
```

**Guidelines for Agent Injection**:

| Agent Type | Injection Strategy | Rationale |
|------------|-------------------|-----------|
| Single-deliverable agents | None (command-level only) | Simple workflows don't need agent-level tracking |
| Multi-phase agents (SRE, QA) | Partial injection | Granular AC tracking valuable |
| Task-creating agents (PM Planner) | Full injection | Need complete CLI reference for subtask creation |
| Sequential agents (Researcher) | None (phase transitions in command) | Command handles transitions |

---

## Integration Points by Command

### /jpspec:specify (PM Planner)

**Entry Hook**:
```bash
backlog task edit <id> -s "In Progress" --assign-to @pm-planner
backlog task edit <id> --plan "1. Problem analysis\n2. DVF+V validation\n3. PRD creation\n4. Task breakdown"
```

**Note**: DVF+V stands for Desirability, Viability, Feasibility + Viability—the four critical risks framework from SVPG.

**Agent Instrumentation**: Full injection (enables subtask creation from section 6)

**During Execution**:
```bash
# PM Planner creates subtasks from task breakdown
backlog task create "Epic: User Signup" -p <spec-task-id> --ac "..." --priority high
```

**Exit Hook**:
```bash
backlog task edit <id> --check-ac 1 --check-ac 2 --notes "PRD created: X epics, Y stories" -s Done
```

---

### /jpspec:plan (Architect + Platform Engineer)

**Entry Hook**:
```bash
backlog task edit <id> -s "In Progress" --assign-to @architect,@platform-engineer
backlog task edit <id> --plan "1. Parallel architecture + platform planning\n2. Consolidate\n3. Build constitution"
```

**Agent Instrumentation**: None (command-level only sufficient)

**Exit Hook**:
```bash
backlog task edit <id> --check-ac 1 --check-ac 2 --check-ac 3
backlog task edit <id> --notes "Architecture: ADR-X, Y. Platform: CI/CD design, IaC setup" -s Done
```

---

### /jpspec:research (Researcher → Business Validator)

**Entry Hook**:
```bash
backlog task edit <id> -s "In Progress" --assign-to @researcher
backlog task edit <id> --plan "1. Market & technical research\n2. Business validation\n3. Go/No-Go decision"
```

**Agent Instrumentation**: None (phase transitions in command)

**Phase Transition**:
```bash
# After research phase
backlog task edit <id> --check-ac 1 --assign-to @business-validator --append-notes "Research: TAM $X, SAM $Y"
```

**Exit Hook**:
```bash
backlog task edit <id> --check-ac 2 --notes "Validation: GO with Z% confidence" -s Done
```

---

### /jpspec:implement (Engineers + Reviewers)

**Entry Hook**:
```bash
backlog task edit <id> -s "In Progress" --assign-to @frontend,@backend
backlog task edit <id> --plan "1. Parallel implementation\n2. Code review\n3. Address feedback"
```

**Agent Instrumentation**: None (command-level sufficient)

**Phase Transitions**:
```bash
# After implementation, before review
backlog task edit <id> --check-ac 1 --check-ac 2 --append-notes "Implementation complete"

# After review, before feedback resolution
backlog task edit <id> --check-ac 3 --append-notes "Review feedback: ..."

# After feedback resolution
backlog task edit <id> --check-ac 4 --append-notes "All feedback addressed"
```

**Exit Hook**:
```bash
backlog task edit <id> --notes "Feature implemented: [summary]" -s Done
```

---

### /jpspec:validate (QA → Security → Docs → Release)

**Entry Hook**:
```bash
backlog task edit <id> -s "In Progress" --assign-to @qa,@security
backlog task edit <id> --plan "1. QA + Security\n2. Documentation\n3. Release readiness\n4. Human approval"
```

**Agent Instrumentation**: Partial injection for Release Manager (document approval)

**Phase Transitions**:
```bash
# Phase 1 → 2
backlog task edit <id> --check-ac 1 --check-ac 2 --assign-to @tech-writer

# Phase 2 → 3
backlog task edit <id> --check-ac 3 --assign-to @release-manager

# Phase 3 complete (WAIT FOR HUMAN APPROVAL)
backlog task edit <id> --check-ac 4 --append-notes "Pre-release validation complete. Awaiting approval."
```

**Exit Hook (After Human Approval)**:
```bash
backlog task edit <id> --append-notes "APPROVED by [name] on [date]. Reason: [rationale]"
backlog task edit <id> -s Done
```

**Critical**: NEVER mark task Done until human approval received.

---

### /jpspec:operate (SRE Agent)

**Entry Hook**:
```bash
backlog task edit <id> -s "In Progress" --assign-to @sre-agent
backlog task edit <id> --plan "1. SLOs\n2. CI/CD\n3. K8s\n4. DevSecOps\n5. Observability\n6. Incidents\n7. IaC\n8. Perf\n9. DR"
```

**Agent Instrumentation**: Partial injection (track 9 operational areas)

**During Execution**:
```bash
# SRE agent checks ACs as each area completes
backlog task edit <id> --check-ac 1 --append-notes "SLOs defined: 99.9% uptime, p95 < 200ms"
backlog task edit <id> --check-ac 2 --append-notes "CI/CD pipelines: build, test, deploy configured"
# ... (continue for all 9 areas)
```

**Exit Hook**:
```bash
backlog task edit <id> --notes "Operations complete: CI/CD, K8s, observability, runbooks" -s Done
```

---

## Testing Strategy

### Unit Testing (CLI Integration)

**Test Entry Hooks**:
```python
def test_specify_entry_hook():
    """Verify specify command activates task correctly."""
    task_id = "jpspec-specify-auth-20251128"

    # Simulate command entry hook
    result = subprocess.run([
        "backlog", "task", "edit", task_id,
        "-s", "In Progress",
        "--assign-to", "@pm-planner"
    ], capture_output=True)

    assert result.returncode == 0

    # Verify task state
    task = get_task(task_id)
    assert task.status == "In Progress"
    assert "@pm-planner" in task.assignees
```

**Test Phase Transitions**:
```python
def test_research_phase_transition():
    """Verify research → validation transition updates assignee."""
    task_id = "jpspec-research-market-20251128"

    # Phase 1 → Phase 2
    result = subprocess.run([
        "backlog", "task", "edit", task_id,
        "--check-ac", "1",
        "--assign-to", "@business-validator"
    ], capture_output=True)

    assert result.returncode == 0
    task = get_task(task_id)
    assert task.acs[0].checked
    assert "@business-validator" in task.assignees
```

**Test Exit Hooks**:
```python
def test_implement_exit_hook():
    """Verify implement command completes task correctly."""
    task_id = "jpspec-implement-api-20251128"

    # Simulate exit hook
    result = subprocess.run([
        "backlog", "task", "edit", task_id,
        "--check-ac", "1", "--check-ac", "2",
        "--notes", "Feature implemented with tests",
        "-s", "Done"
    ], capture_output=True)

    assert result.returncode == 0
    task = get_task(task_id)
    assert task.status == "Done"
    assert all(ac.checked for ac in task.acs)
    assert "Feature implemented" in task.notes
```

### Integration Testing (End-to-End Workflows)

**Test Specify Workflow**:
```python
def test_specify_workflow_end_to_end():
    """Verify complete specify workflow from entry to exit."""
    feature = "user-authentication"
    task_id = f"jpspec-specify-{feature}-20251128"

    # Entry hook
    activate_task(task_id, "@pm-planner")

    # Simulate PM Planner creating PRD and subtasks
    create_prd(feature)
    create_subtasks(task_id, ["signup", "login", "password-reset"])

    # Exit hook
    complete_task(task_id, "PRD created: 3 epics, 8 user stories")

    # Verify final state
    task = get_task(task_id)
    assert task.status == "Done"
    assert len(get_subtasks(task_id)) == 3
```

**Test Validate Human Approval Gate**:
```python
def test_validate_human_approval_required():
    """Verify validate command blocks until human approval."""
    task_id = "jpspec-validate-release-20251128"

    # Phases 1-3 complete
    complete_validation_phases(task_id)

    # Attempt to mark done without approval (should fail/warn)
    result = subprocess.run([
        "backlog", "task", "edit", task_id,
        "-s", "Done"
    ], capture_output=True)

    # Verify task remains in progress
    task = get_task(task_id)
    assert task.status == "In Progress"
    assert "awaiting approval" in task.notes.lower()

    # Grant approval
    approve_release(task_id, "john.doe", "All validations passed")

    # Now completion succeeds
    complete_task(task_id, "Release approved and ready")
    assert get_task(task_id).status == "Done"
```

### Manual Testing Checklist

- [ ] Run each jpspec command and verify entry hook activates task
- [ ] Verify multi-phase commands update assignees correctly
- [ ] Test AC checking during agent execution
- [ ] Verify exit hooks complete tasks with all ACs checked
- [ ] Test human approval gate in validate command (must block)
- [ ] Verify subtask creation from PM Planner works
- [ ] Test SRE agent's 9-phase AC tracking
- [ ] Verify backlog.md CLI errors are handled gracefully

---

## Consequences

### Positive

- **Standardized Lifecycle**: All jpspec tasks follow consistent lifecycle
- **Audit Trail**: Complete visibility into agent work and transitions
- **Reduced Manual Work**: Automated task activation and completion
- **Better Context**: Agents can query task state before/during work
- **Scalability**: Template approach scales to new agents easily
- **Flexibility**: Hybrid model supports simple and complex workflows
- **Human Oversight**: Preserves critical approval gates

### Negative

- **Implementation Effort**: Requires updating all 6 command files
- **Testing Overhead**: Each command needs integration tests
- **CLI Dependency**: Requires backlog.md CLI installed and working
- **Error Handling**: Must handle CLI failures gracefully
- **Learning Curve**: Developers must understand backlog CLI

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| backlog.md CLI not installed | Commands fail | Add pre-flight check: `which backlog || echo "Install backlog.md CLI"` |
| CLI version incompatibility | Unexpected behavior | Document required CLI version in README |
| Task ID not provided | Cannot activate task | Make task ID required parameter or auto-detect from context |
| Agent ignores backlog instructions | No progress tracking | Command-level hooks ensure minimum viable tracking |
| Human forgets approval gate | Premature release | Release Manager agent blocks without approval |

---

## Future Considerations

### Potential Enhancements

1. **Auto-Task Discovery**: Commands auto-detect applicable tasks from backlog
2. **Task Templates**: Pre-defined task structures for each command type
3. **Dependency Tracking**: Agents declare dependencies, system auto-schedules
4. **Progress Webhooks**: Integrate with external systems (Slack, Jira, Linear)
5. **Analytics Dashboard**: Visualize agent efficiency, task cycle time
6. **AI-Powered Suggestions**: Recommend tasks based on project context

### Migration Path

**Phase 1: Manual Task Creation**
- Developers manually create tasks before running jpspec commands
- Commands handle lifecycle management only

**Phase 2: Semi-Automated Creation**
- Commands prompt for task creation if none provided
- Optional task templates reduce friction

**Phase 3: Fully Automated**
- Commands auto-create tasks from feature descriptions
- Intelligent task breakdown based on complexity

---

## References

- **Audit Document**: `docs/audits/jpspec-command-audit.md`
- **Backlog.md CLI**: https://backlog.md
- **Command Files**: `.claude/commands/jpspec/*.md`
- **Agent Context Files**: `templates/agent-contexts/`
- **Task-106**: Backlog task tracking this architecture design

---

## Appendix: Complete CLI Command Reference

### Task Activation (Entry Hooks)

```bash
# Single agent
backlog task edit <id> -s "In Progress" --assign-to @agent-name

# Multiple agents (parallel)
backlog task edit <id> -s "In Progress" --assign-to @agent1,@agent2

# With implementation plan
backlog task edit <id> --plan "1. Phase 1\n2. Phase 2\n3. Phase 3"
```

### Progress Tracking (During Execution)

```bash
# Check acceptance criteria
backlog task edit <id> --check-ac 1
backlog task edit <id> --check-ac 1 --check-ac 2 --check-ac 3  # Multiple ACs

# Append progress notes
backlog task edit <id> --append-notes "Completed X, starting Y"

# Change assignee (phase transitions)
backlog task edit <id> --assign-to @next-agent
```

### Task Completion (Exit Hooks)

```bash
# Check all remaining ACs
backlog task edit <id> --check-ac 1 --check-ac 2 --check-ac 3

# Add final implementation notes
backlog task edit <id> --notes "Summary: Feature implemented with X, Y, Z. Tests: A, B, C."

# Mark task done
backlog task edit <id> -s Done

# All-in-one completion
backlog task edit <id> --check-ac 1 --check-ac 2 --notes "Summary" -s Done
```

### Subtask Creation

```bash
# Create subtask linked to parent
backlog task create "Epic: User Signup" -p <parent-task-id> --ac "Criterion" --priority high

# Create with full metadata
backlog task create "Title" -p <parent-id> -d "Description" --ac "AC1" --ac "AC2" -l label1,label2
```

### Task Querying

```bash
# View task details (AI-friendly)
backlog task <id> --plain

# List tasks by status
backlog task list -s "In Progress" --plain

# Search tasks
backlog search "jpspec-implement" --plain
```

---

## Appendix: Template Injection Example

**Before Integration** (`.claude/commands/jpspec/specify.md`):

```markdown
## Execution Instructions

Use the Task tool to launch a general-purpose agent:

```
# AGENT CONTEXT: Product Requirements Manager
[Full agent context...]
# TASK: Create PRD for [feature]
```
```

**After Integration** (with entry/exit hooks):

```markdown
## Pre-Execution: Task Activation

Activate the task before launching agent:

```bash
backlog task edit <TASK_ID> -s "In Progress" --assign-to @pm-planner
backlog task edit <TASK_ID> --plan "1. Problem analysis\n2. PRD creation\n3. Task breakdown"
```

## Execution Instructions

Use the Task tool to launch a general-purpose agent:

```
# AGENT CONTEXT: Product Requirements Manager
[Full agent context...]

<!-- BACKLOG INTEGRATION START -->
{{> templates/partials/backlog-instructions.md}}
<!-- BACKLOG INTEGRATION END -->

# TASK: Create PRD for [feature]
```

## Post-Execution: Task Completion

After agent completes, finalize the task:

```bash
backlog task edit <TASK_ID> --check-ac 1 --check-ac 2
backlog task edit <TASK_ID> --notes "PRD created: X epics, Y stories"
backlog task edit <TASK_ID> -s Done
```
```

---

**Decision**: This architecture balances automation, visibility, and simplicity while preserving agent independence and enabling incremental adoption.
