# Kinsale Machine - December 5th Sprint Plan

## Overview

This document outlines the execution plan for the remaining kinsale-assigned tasks, prioritized by dependencies, impact, and complexity.

## Task Status Summary

### Completed (5 tasks)
| Task | Description | Status |
|------|-------------|--------|
| task-243 | Detect existing projects without constitution | Done |
| task-244 | Implement /speckit:constitution LLM customization | Done |
| task-245 | Add constitution validation guidance | Done |
| task-246 | Integration tests for constitution template | Done |
| task-249 | Implement Tool Dependency Management Module | Done |

### Remaining (14 tasks)

#### HIGH Priority (3 tasks)
| Task | Description | Est. Effort |
|------|-------------|-------------|
| task-184 | Add permissions.deny Security Rules | Small (1-2 hrs) |
| task-083 | Pre-Implementation Quality Gates | Medium (4-6 hrs) |
| task-182 | Extend specify init for Validation Modes | Large (6-8 hrs) |

#### MEDIUM Priority (7 tasks)
| Task | Description | Est. Effort |
|------|-------------|-------------|
| task-085 | Local CI Simulation Script | Medium (3-4 hrs) |
| task-079 | Stack Selection During Init | Large (6-8 hrs) |
| task-081 | Claude Plugin Architecture | Large (8+ hrs) |
| task-084 | Spec Quality Metrics Command | Medium (4-6 hrs) |
| task-086 | Spec-Light Mode for Medium Features | Medium (4-6 hrs) |
| task-136 | claude-trace Observability Tool | Medium (3-4 hrs) |
| task-171 | Library documentation MCP replacement | Research (2-3 hrs) |

#### LOW Priority (4 tasks)
| Task | Description | Est. Effort |
|------|-------------|-------------|
| task-168 | Add macOS CI Matrix Testing | Small (1-2 hrs) |
| task-195 | Create Flowspec Plugin Package | Large (8+ hrs) |
| task-196 | Experiment with Output Styles | Small (2-3 hrs) |
| task-197 | Create Custom Statusline | Medium (3-4 hrs) |

---

## Execution Order

### Phase 1: Quick Wins (Day 1 Morning)

**1. task-184 - Add permissions.deny Security Rules** ⭐ START HERE
- **Why first**: Quick win, HIGH priority, no dependencies
- **Deliverable**: Updated .claude/settings.json with security rules
- **ACs**: 6 acceptance criteria (deny rules + docs)
- **Risk**: Low

**2. task-168 - Add macOS CI Matrix Testing**
- **Why next**: Small task, unblocks CI confidence
- **Deliverable**: Updated CI workflow with macOS matrix
- **ACs**: Already partially complete (AC#9 done)
- **Risk**: Low

### Phase 2: Quality Infrastructure (Day 1 Afternoon)

**3. task-083 - Pre-Implementation Quality Gates**
- **Why**: HIGH priority, enables quality workflow
- **Deliverable**: .claude/hooks/pre-implement.sh
- **ACs**: 8 acceptance criteria
- **Dependencies**: None
- **Risk**: Medium (hook integration)

**4. task-085 - Local CI Simulation Script**
- **Why**: Enables faster local testing
- **Deliverable**: scripts/bash/run-local-ci.sh
- **ACs**: 9 acceptance criteria (1 done)
- **Dependencies**: Docker, act
- **Risk**: Medium (environment setup)

### Phase 3: Workflow Enhancement (Day 2)

**5. task-182 - Extend specify init for Validation Modes**
- **Why**: HIGH priority, workflow foundation
- **Deliverable**: Interactive init with validation config
- **ACs**: 9 acceptance criteria
- **Dependencies**: flowspec_workflow.yml structure
- **Risk**: Medium-High (UI complexity)

**6. task-084 - Spec Quality Metrics Command**
- **Why**: Pairs with quality gates (task-083)
- **Deliverable**: `specify spec-quality` command
- **ACs**: To be reviewed
- **Dependencies**: task-083 (quality threshold)
- **Risk**: Medium

### Phase 4: Feature Expansion (Day 3)

**7. task-086 - Spec-Light Mode for Medium Features**
- **Why**: Reduces ceremony for simple features
- **Deliverable**: Lightweight spec workflow option
- **Risk**: Medium

**8. task-079 - Stack Selection During Init**
- **Why**: Better onboarding experience
- **Deliverable**: Interactive stack selection UI
- **ACs**: 8 acceptance criteria
- **Risk**: Medium-High (UI + file operations)

### Phase 5: Observability & Integration (Day 4)

**9. task-136 - claude-trace Observability Tool**
- **Why**: Debugging capability
- **Deliverable**: claude-trace integration docs
- **Risk**: Low (documentation focused)

**10. task-171 - Library documentation MCP replacement**
- **Why**: Research task, informs future work
- **Deliverable**: Research findings document
- **Risk**: Low (research only)

### Phase 6: Advanced Features (Backlog)

**11. task-081 - Claude Plugin Architecture**
- **Why**: Foundation for extensibility
- **Complexity**: HIGH - defer to later sprint

**12. task-195 - Create Flowspec Plugin Package**
- **Why**: Depends on task-081
- **Complexity**: HIGH - defer

**13. task-196 - Experiment with Output Styles**
- **Why**: Polish, not critical path
- **Complexity**: LOW - can do anytime

**14. task-197 - Create Custom Statusline**
- **Why**: Nice-to-have
- **Complexity**: MEDIUM - defer

---

## Recommended Focus for Today (Dec 5)

### Morning Session
1. **task-184** - permissions.deny rules (1-2 hrs)
2. **task-168** - macOS CI matrix (1 hr)

### Afternoon Session
3. **task-083** - Pre-implementation quality gates (4-6 hrs)

### Evening Session (if time)
4. **task-085** - Local CI simulation script (start)

---

## Dependencies Graph

```
task-083 (Quality Gates)
    └── task-084 (Spec Quality Metrics) - uses threshold

task-081 (Plugin Architecture)
    └── task-195 (Plugin Package) - depends on architecture

task-085 (Local CI)
    └── task-168 (macOS CI) - testing coverage
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Hook integration issues | Test hooks in isolation first |
| act compatibility | Document known limitations upfront |
| Interactive UI complexity | Use existing Typer/Rich patterns |
| Cross-platform issues | Test on both Linux and macOS |

---

## Success Metrics

- [ ] All HIGH priority tasks complete by EOD Dec 5
- [ ] At least 2 MEDIUM tasks complete by EOD Dec 5
- [ ] All changes have passing CI
- [ ] No regressions in existing tests

---

## Notes

- Focus on completing tasks fully (all ACs checked) before moving to next
- Create PRs incrementally, don't batch too many changes
- Run full test suite before each PR
- Use `backlog task edit --check-ac` to track progress
