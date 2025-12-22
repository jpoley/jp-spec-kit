# Execution Plan: Dec 22, 2025 Sprint

## Overview

This sprint focuses on 5 high-priority tasks that enhance flowspec's core capabilities:
- **Task Memory**: Persistent context management for AI workflows
- **flowspec init**: Complete project bootstrapping with dual-agent support

## Active Tasks

| Task | Title | Status | Dependencies |
|------|-------|--------|--------------|
| task-368 | Task Memory - Persistent Context Management | In Progress | None (parent) |
| task-386 | CLAUDE.md @import Context Injection | In Progress | task-377 |
| task-279 | Documentation branding updates | In Progress | None |
| task-470 | flowspec init: Deploy skills + GitHub prompts | In Progress | None |
| task-480 | flowspec init --complete option | In Progress | task-470 |

## Dependency Graph

```
                    ┌─────────────┐
                    │  task-279   │ (Independent - Docs)
                    │   [DOCS]    │
                    └─────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    TASK MEMORY TRACK                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │  task-368   │───▶│  task-377   │───▶│  task-386   │      │
│  │  [PARENT]   │    │[Claude Int] │    │  [@import]  │      │
│  └─────────────┘    └─────────────┘    └─────────────┘      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   FLOWSPEC INIT TRACK                        │
│  ┌─────────────┐    ┌─────────────┐                         │
│  │  task-470   │───▶│  task-480   │                         │
│  │  [Skills]   │    │ [--complete]│                         │
│  └─────────────┘    └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Execution Order

### Phase 1: Parallel Foundation (can run simultaneously)

#### Track A: Documentation (task-279)
**Agent**: backend-engineer or general-purpose
**Effort**: 1-2 hours
**Remaining Work**:
- [ ] Fix GitHub Pages environment protection rules (manual)
- [ ] Verify docs deploy after fix

#### Track B: flowspec init Skills (task-470)
**Agent**: backend-engineer
**Effort**: 4-6 hours
**Work**:
- [ ] AC#1: Copy skills from templates/skills/ to .claude/skills/
- [ ] AC#2: Maintain SKILL.md directory structure
- [ ] AC#3: Add --force flag for overwrite protection
- [ ] AC#4: Add --skip-skills flag
- [ ] AC#5: Document skill deployment in output
- [ ] AC#6: Deploy GitHub Copilot prompts to .github/prompts/
- [ ] AC#7: Create sync mechanism for dual-agent support

#### Track C: Task Memory Foundation (task-368 + task-377)
**Agent**: backend-engineer
**Effort**: 6-8 hours
**Work**:
- [ ] Complete task-377: Claude Code hooks integration
- [ ] Wire LifecycleManager to backlog task transitions
- [ ] Implement auto-creation of Task Memory on "In Progress"
- [ ] Implement auto-cleanup on "Done" or "Archive"

### Phase 2: Dependent Tasks (after Phase 1)

#### task-386: CLAUDE.md @import (after task-377)
**Agent**: backend-engineer
**Effort**: 2-3 hours
**Work**:
- [ ] AC#2: Integrate ContextInjector with LifecycleManager
- [ ] AC#3: Manual test with Claude Code
- [ ] AC#7: Document @import mechanism

#### task-480: flowspec init --complete (after task-470)
**Agent**: backend-engineer
**Effort**: 3-4 hours
**Work**:
- [ ] AC#1: Implement --complete flag
- [ ] AC#2: Enable all skills deployment
- [ ] AC#3: Enable all hooks in hooks.yaml
- [ ] AC#4: Full CI/CD template deployment
- [ ] AC#5: Complete VSCode settings
- [ ] AC#6: MCP configuration creation
- [ ] AC#7: Documentation

## Parallelization Strategy

```
Time ──────────────────────────────────────────────────────────▶

Hour 0-2:   [task-279: Docs]  [task-470: Skills]  [task-368/377: Memory]
              │                    │                    │
Hour 2-4:   [DONE]            [task-470 cont.]    [task-377 cont.]
                                   │                    │
Hour 4-6:                     [task-480: --complete]  [task-386: @import]
                                   │                    │
Hour 6-8:                     [DONE]              [DONE]
```

**Maximum Parallelism**: 3 agents working simultaneously in Phase 1

## Sub-Agent Assignments

### Recommended Agent Configuration

```yaml
agents:
  track_a_docs:
    type: backend-engineer
    task: task-279
    priority: low  # Quick win, mostly done

  track_b_init:
    type: backend-engineer
    tasks: [task-470, task-480]
    priority: high
    sequence: true  # task-480 after task-470

  track_c_memory:
    type: backend-engineer
    tasks: [task-368, task-377, task-386]
    priority: high
    sequence: true  # task-386 after task-377; task-368 can run independently
```

### Parallel Execution Command

```bash
# Launch all three tracks in parallel
# Track A: Documentation
claude --task "Complete task-279: Fix GitHub Pages deployment, verify docs build"

# Track B: flowspec init (in parallel)
claude --task "Complete task-470: Add skills deployment to flowspec init with GitHub prompts support"

# Track C: Task Memory (in parallel)
claude --task "Complete task-377 and task-386: Wire LifecycleManager to ContextInjector"
```

## Success Criteria

### Sprint Complete When:
- [ ] task-279: Documentation deploys to GitHub Pages
- [ ] task-470: `flowspec init` deploys skills to .claude/skills/ and .github/
- [ ] task-480: `flowspec init --complete` deploys everything in one command
- [ ] task-386: Task Memory context auto-injects via @import
- [ ] task-368: Task Memory creates/cleans up automatically on task state changes

### Quality Gates:
- [ ] All tests pass (`pytest tests/`)
- [ ] Linting passes (`ruff check .`)
- [ ] No regressions in existing functionality
- [ ] Documentation updated for new features

## Notes

### Security Tasks On Hold
13 security/scanning tasks have been placed on hold (Dec 2025) as they may move to a dedicated security repository. Tasks affected:
- task-216, task-217, task-219, task-220
- task-223, task-225, task-248, task-250
- task-251, task-252, task-253, task-254, task-520

### Branding Updates
All "specify" references in task titles/descriptions have been updated to "flowspec" as part of this sprint planning.

### Completed in This Release
- task-542: JSONL decision logging infrastructure
- task-543: Rigor rules in /flow:implement
- task-544: Rigor rules in /flow:validate

---

*Generated: 2025-12-22*
*Sprint: Dec 22-29, 2025*
