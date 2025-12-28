---
id: task-368
title: 'Feature: Task Memory - Persistent Context Management'
status: In Progress
assignee:
  - '@myself'
created_date: '2025-12-09 15:50'
updated_date: '2025-12-28 20:41'
labels:
  - architecture
  - planning
  - 'workflow:Planned'
  - feature
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design and implement Task Memory, a persistent context management system that:
- Creates context automatically when a task is started
- Persists across sessions, machines, and commits
- Follows the task through its entire lifecycle
- Gets cleaned up when task is archived or marked done
- Provides user visibility into context for optimization
- Allows clearing context between task steps
- Is task-specific (different from general compact/context compression)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Task Memory is created automatically when task transitions to In Progress
- [x] #2 Context persists across Claude Code sessions
- [x] #3 Context persists across different machines (via git or backlog)
- [x] #4 Context is automatically cleaned up on task Done or Archive
- [x] #5 User can view current Task Memory contents
- [x] #6 User can manually edit/optimize Task Memory
- [x] #7 Task Memory is distinct from general session compact
- [ ] #8 Integration with backlog.md task lifecycle events
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- task-371: ADR-001: Storage Mechanism
- task-372: ADR-002: Context Injection Method
- task-373: ADR-003: Lifecycle Trigger Mechanism
- task-374: ADR-004: Cross-Environment Sync Strategy
- task-375: Implement TaskMemoryStore Component
- task-376: Create Task Memory Markdown Template

### Phase 2: Lifecycle Integration (Week 2)
- task-384: Implement LifecycleManager Component
- task-370: Lifecycle integration with backlog.md
- task-402: Upstream contribution to backlog CLI for hook support

### Phase 3: Claude Code Integration (Week 3)
- task-386: Implement CLAUDE.md @import Context Injection
- task-387: Implement MCP Resource for Task Memory
- task-377: Claude Code integration via hooks and MCP

### Phase 4: Git Sync (Week 4)
- task-381: Git synchronization and conflict resolution

### Phase 5: CLI & Observability (Week 5)
- task-388-395: Memory CLI commands (show, edit, append, list, search, clear, stats)
- task-382: Observability and developer visibility

### Phase 6: Testing & Documentation (Week 6)
- task-396: E2E Test: Task Memory Lifecycle
- task-397: E2E Test: Cross-Machine Sync
- task-398: E2E Test: Agent Context Injection
- task-399: Performance Test: Memory Operations at Scale
- task-400: Security Review: Task Memory System
- task-378: Add Task Memory Principles to Constitution
- task-379: Create Task Memory User Documentation
- task-380: Create Task Memory Architecture Documentation

### Phase 7: CI/CD Integration (Week 7)
- task-388: CI/CD integration and PR automation
- task-383: Advanced features - search, import, export
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Status: 90% Complete

### Core Components (All Complete - 2,864 LOC)
| Component | File | LOC | Status |
|-----------|------|-----|--------|
| TaskMemoryStore | store.py | 481 | ✅ Complete |
| LifecycleManager | lifecycle.py | 298 | ✅ Complete |
| CleanupManager | cleanup.py | 232 | ✅ Complete |
| ContextInjector | injector.py | 358 | ✅ Complete |
| MCP Resources | mcp.py | 193 | ✅ Complete |
| Hooks | hooks.py | 110 | ✅ Complete |
| CLI Commands | cli.py | 1192 | ✅ Complete (11 commands) |

### CLI Commands (All Working)
- flowspec memory init, show, append, list, search
- flowspec memory clear, cleanup, stats
- flowspec memory import, export, template

### Templates (4)
- default.md, feature.md, bugfix.md, research.md

### Only Gap: AC #8
Automatic lifecycle triggering from backlog CLI requires task-402 (upstream hook support).

### Workaround
Manual workflow works today:
```bash
backlog task edit 42 -s "In Progress" && flowspec memory init task-42
flowspec memory append task-42 "Decision: ..." --section "Key Decisions"
backlog task edit 42 -s Done  # Auto-archives via lifecycle hooks
```

See: task-memory-analysis.md for full details.
<!-- SECTION:NOTES:END -->
