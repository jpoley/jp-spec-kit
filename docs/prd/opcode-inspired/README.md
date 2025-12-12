# Opcode-Inspired Feature Specifications

This directory contains feature specifications inspired by [opcode](https://github.com/winfunc/opcode), a GUI desktop application for Claude Code. These specs adapt opcode's most valuable features for flowspec's CLI-first, workflow-oriented approach.

## Background

See [docs/research/opcode.md](/docs/research/opcode.md) for the complete comparison between opcode and flowspec.

## Feature Specifications

| ID | Feature | Priority | Dependencies | Status |
|----|---------|----------|--------------|--------|
| [OP-001](op-001-cost-usage-tracking.md) | Cost/Usage Tracking System | High | None | Draft |
| [OP-002](op-002-execution-metrics.md) | Execution Metrics per Workflow Phase | High | OP-001 | Draft |
| [OP-003](op-003-auto-checkpoint.md) | Auto-Checkpoint on Phase Transitions | High | None | Draft |
| [OP-004](op-004-workflow-status-tui.md) | Workflow Status TUI | Medium | backlog.md | Draft |
| [OP-005](op-005-cost-budget-warnings.md) | Cost Budget Warnings | Medium | OP-001 | Draft |
| [OP-006](op-006-task-session-view.md) | Task-Centric Session View | Medium | OP-001, backlog.md | Draft |

## Implementation Order

**Recommended implementation sequence:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Phase 1: Foundation                       │
├─────────────────────────────────────────────────────────────┤
│  OP-001: Cost/Usage Tracking                                │
│  ├── JSONL parser                                           │
│  ├── Pricing calculations                                   │
│  └── CLI commands (specify usage)                           │
├─────────────────────────────────────────────────────────────┤
│                    Phase 2: Metrics                          │
├─────────────────────────────────────────────────────────────┤
│  OP-002: Execution Metrics                                  │
│  ├── Phase metrics collection                               │
│  ├── Display after /flow:* commands                         │
│  └── Storage in task notes                                  │
│                                                             │
│  OP-005: Budget Warnings                                    │
│  ├── Budget configuration                                   │
│  ├── Warning display                                        │
│  └── Workflow integration                                   │
├─────────────────────────────────────────────────────────────┤
│                    Phase 3: Safety                           │
├─────────────────────────────────────────────────────────────┤
│  OP-003: Auto-Checkpoint                                    │
│  ├── Git-based checkpoint system                            │
│  ├── Workflow phase integration                             │
│  └── Rollback commands                                      │
├─────────────────────────────────────────────────────────────┤
│                    Phase 4: Visibility                       │
├─────────────────────────────────────────────────────────────┤
│  OP-004: Workflow Status TUI                                │
│  ├── Textual app implementation                             │
│  ├── Pipeline visualization                                 │
│  └── Keyboard navigation                                    │
│                                                             │
│  OP-006: Task-Session View                                  │
│  ├── Session correlation                                    │
│  ├── Conversation extraction                                │
│  └── Export functionality                                   │
└─────────────────────────────────────────────────────────────┘
```

## Key Differences from Opcode

| Aspect | Opcode Approach | Flowspec Approach |
|--------|-----------------|-------------------|
| **Checkpoint Storage** | Custom file snapshots with zstd | Git-based (stash/tags) |
| **Session Management** | SQLite database | File-based with JSONL parsing |
| **UI** | Full Tauri/React GUI | Terminal-based (rich, textual) |
| **Cost Tracking** | Real-time dashboard | CLI commands + workflow integration |
| **Agent System** | Custom CC Agents | Workflow-integrated skills |

## Integration with Existing Features

These features enhance but don't replace existing flowspec functionality:

- **backlog.md**: Task sessions, budget tracking, and metrics integrate with tasks
- **flowspec_workflow.yml**: Checkpoint and budget configuration
- **Workflow commands**: Metrics displayed after `/flow:*` commands
- **Skills**: No changes to skill system

## New Dependencies

```toml
# pyproject.toml additions
[project.dependencies]
textual = ">=0.47.0"  # For TUI (OP-004)
```

## Configuration Summary

```yaml
# flowspec_workflow.yml additions

# OP-001, OP-002: Usage tracking
usage:
  show_phase_costs: true
  track_task_costs: true

# OP-003: Checkpoints
checkpoint:
  strategy: "before_modify"
  always_checkpoint: ["implement"]
  max_per_task: 10

# OP-004: TUI
tui:
  default_mode: "simple"
  hide_done: true

# OP-005: Budgets
budgets:
  enabled: true
  session:
    warn_at: 5.00
  task:
    warn_at: 10.00
  phases:
    implement:
      warn_at: 5.00
      expected: 3.00

# OP-006: Sessions
sessions:
  enable_correlation: true
  auto_track: true
```

## Success Metrics

After implementation, developers should be able to:

1. **Know their costs**: `specify usage` shows spending by day/project/model
2. **See phase metrics**: Each `/flow:*` command shows duration and cost
3. **Rollback safely**: Checkpoints exist at phase boundaries
4. **Visualize pipeline**: `specify status --tui` shows kanban view
5. **Stay on budget**: Warnings appear when thresholds exceeded
6. **Review history**: `specify task sessions TASK-123` shows conversation history

## References

- [Opcode Repository](https://github.com/winfunc/opcode)
- [Flowspec/Opcode Comparison](/docs/research/opcode.md)
- [Claude API Pricing](https://www.anthropic.com/pricing)
- [Textual Documentation](https://textual.textualize.io/)
