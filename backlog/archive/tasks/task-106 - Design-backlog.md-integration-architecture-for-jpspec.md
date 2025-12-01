---
id: task-106
title: Design backlog.md integration architecture for jpspec
status: Done
assignee:
  - '@claude-agent-4'
created_date: '2025-11-28 16:54'
updated_date: '2025-11-28 19:44'
labels:
  - jpspec
  - backlog-integration
  - P0
  - design
dependencies:
  - task-105
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design the architectural approach for integrating backlog.md CLI into all jpspec commands. Define standard patterns, shared templates, and testing strategy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define standard task lifecycle: discovery → assignment → plan → execution → completion
- [x] #2 Design shared backlog instructions template (reusable across all agent prompts)
- [x] #3 Define task naming conventions for jpspec-created tasks
- [x] #4 Document sub-agent backlog.md instruction injection pattern
- [x] #5 Create architecture decision record (ADR) for backlog.md integration
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Designed comprehensive backlog.md integration architecture for jpspec commands.

Key Deliverables:
- ADR-001: Complete architectural decision record with hybrid integration approach
- Shared template: Reusable backlog instructions for agent contexts
- Task lifecycle: State machine (To Do → In Progress → Done, with optional Blocked state)
- Naming convention: jpspec-{command}-{feature-slug}-{yyyymmdd}
- Injection patterns: Command-level hooks (all) + strategic agent instrumentation (PM, SRE, Release Manager)

Architecture Highlights:
- Hybrid approach: Command-level entry/exit hooks + selective agent instrumentation
- 3-phase implementation: Foundation (hooks) → Strategic agents → Optional extensions
- Testing strategy: Unit tests for CLI integration, integration tests for workflows, manual checklist
- Human approval gates preserved (validate command)
- Graceful degradation if CLI unavailable

Files Created:
- docs/adr/ADR-001-backlog-md-integration.md (comprehensive architecture decision record)
- templates/partials/backlog-instructions.md (reusable agent instructions)

Impact:
- Standardizes task lifecycle across all 6 jpspec commands
- Enables complete audit trail of agent work
- Reduces manual task management overhead
- Preserves agent independence and flexibility
- Supports incremental adoption

Follow-up Implementation Tasks (from this design):
- task-107: Create shared backlog.md instructions template
- task-108: Create test framework for backlog.md integration
- task-109: Update jpspec:specify to use backlog.md CLI
- task-110: Update jpspec:plan to use backlog.md CLI
- task-111: Update jpspec:research to use backlog.md CLI
- task-112: Update jpspec:implement to use backlog.md CLI
- task-113: Update jpspec:validate to use backlog.md CLI
- task-114: Update jpspec:operate to use backlog.md CLI
- task-115: End-to-end integration tests
- task-116: Update documentation for integration
<!-- SECTION:NOTES:END -->
