---
id: task-579
title: 'EPIC: Flowspec Release Alignment - Fix upgrade-repo and Agent Integration'
status: In Progress
assignee: []
created_date: '2026-01-06 17:19'
updated_date: '2026-01-06 18:49'
labels:
  - epic
  - release-blocker
  - architecture
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Master epic for fixing the broken flowspec upgrade-repo command and aligning with VSCode Copilot agent integration requirements. This is a P0 blocker for the flowspec release.

Root Cause: `flowspec upgrade-repo` is completely broken - it doesn't:
- Copy correct agent templates (wrong naming convention)
- Update .mcp.json
- Remove deprecated files/directories
- Update flowspec_workflow.yml to v2.0
- Remove /flow:operate references
- Sync skills

Source Analysis: auth.poley.dev vs flowspec (2026-01-06)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All Phase 0 tasks completed (upgrade-repo fixes)
- [ ] #2 All Phase 1 tasks completed (core fixes)
- [ ] #3 All Phase 2 tasks completed (MCP config)
- [ ] #4 Verification: grep -r 'operate' returns ZERO /flow:operate matches
- [ ] #5 Verification: flowspec upgrade-repo produces correct output on test repo
- [ ] #6 ADR created for agent naming convention decision
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Order (Critical Path)

**Phase 0 (Foundation) - BLOCKING**
1. task-579.01: Remove /flow:operate references (FIRST - unblocks everything)
2. task-579.02: Remove broken {{INCLUDE:}} directives
3. task-579.03: Fix upgrade-repo to call generate_mcp_json()
4. task-579.04: Fix upgrade-repo to sync skills
5. task-579.05: Fix upgrade-repo to update workflow to v2.0
6. task-579.06: Fix upgrade-repo to remove deprecated files

**Phase 1 (Agent Fixes) - BLOCKING**
7. task-579.07: Fix agent filenames (hyphens → dots)
8. task-579.08: Fix agent names (kebab-case → PascalCase)
9. task-579.09: Add flow.assess.agent.md template
10. task-579.10: Add .github/agents/ to flowspec repo
11. task-579.11: Remove /spec:* from templates
12. task-579.12: Update agent handoffs (depends on 579.08)

**Phase 2 (MCP Config)**
13. task-579.13: Create comprehensive .mcp.json template
14. task-579.14: Update generate_mcp_json() (depends on 579.03)
15. task-579.15: Add MCP health check (optional, P2)

**Phase 4 (Documentation)**
16. task-579.16: Update user documentation
17. task-579.17: Archive build-docs (low priority)

**Phase 5 (Verification) - RELEASE GATE**
18. task-579.18: Test on auth.poley.dev (depends on ALL above)

## Critical Path (Blocking Release)
579.01 → 579.05 → 579.07 → 579.08 → 579.12 → 579.18

## Parallelization Opportunities
- 579.02, 579.03, 579.04 can run in parallel after 579.01
- 579.13, 579.16 can start anytime
- 579.09, 579.10, 579.11 can run in parallel after 579.07

## Estimated Timeline
- Sequential: 14-18 days
- 2-person parallel: 8-10 days
<!-- SECTION:PLAN:END -->
