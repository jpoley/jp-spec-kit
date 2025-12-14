# Backlog.md Integration with flowspec - Implementation Summary

**Date**: 2025-11-23
**Status**: Discovery Complete, MCP Configured, Ready for Implementation

---

## Executive Summary

This document summarizes the completed discovery and planning work for integrating **Backlog.md MCP** with **flowspec** to create a unified spec-driven development platform with AI-powered task management.

### What We've Accomplished

✅ **Research Complete**: Full analysis of Backlog.md capabilities and flowspec's task management
✅ **Chain of Thought Planning**: Comprehensive PRD with design decisions and trade-off analysis
✅ **MCP Configuration**: Backlog.md MCP server installed and configured for Claude Code
✅ **Integration Architecture**: Designed hybrid model for seamless spec-to-task workflow
✅ **Success Metrics Defined**: North Star metric (60% adoption) and leading/lagging indicators

### Key Deliverables Created

1. **Product Requirements Document** (PRD): `docs/prd-backlog-md-integration.md`
   - 12,000+ word comprehensive specification
   - DVF+V risk assessment with validation plans
   - User stories with acceptance criteria
   - Task breakdown for implementation
   - Success metrics and measurement approach

2. **MCP Configuration**: `.mcp.json` updated
   - Backlog.md MCP server added to Claude Code
   - Ready for AI-powered task management

3. **Backlog.md Initialization**: `backlog/` directory created
   - Project configured: flowspec
   - MCP integration mode enabled
   - Demonstration task created (task-1)

---

## Chain of Thought Reasoning - Key Design Decisions

### Decision 1: Integration Model

**Problem**: How should flowspec and Backlog.md work together?

**Options Evaluated**:
1. Backlog.md as source of truth (replace tasks.md completely)
2. tasks.md as source of truth (bidirectional sync)
3. **Hybrid: Generate once to Backlog.md** ✅ SELECTED

**Reasoning**:
- **Reality Check**: Specs stabilize early, tasks evolve during execution
- **Complexity Analysis**: Bidirectional sync creates conflict resolution nightmares
- **User Value**: Developers want task lifecycle management, not just static checklists
- **Risk Mitigation**: Generate-once with optional regeneration balances simplicity and flexibility

**Outcome**: flowspec generates tasks directly into Backlog.md format; tasks.md becomes optional reference or deprecated

---

### Decision 2: Task Format Mapping

**Problem**: How do we preserve flowspec's user-story-centric organization in Backlog.md's flat structure?

**Solution**: **Labels + Virtual Grouping**

**Mapping Strategy**:
```
flowspec:  - [ ] T012 [P] [US1] Create User model in src/models/user.py

Backlog.md:   task-012 - Create User model.md
              ---
              labels: [US1, parallelizable, implementation]
              dependencies: [task-foundational-auth]
              priority: high
              ---
```

**Benefits**:
- Preserves user story association (filter by US1, US2, etc.)
- Maintains parallelization markers
- Encodes phase dependencies
- Allows multiple organization axes (by story, by phase, by priority)

**Trade-off**: Loses explicit phase hierarchy, requires label-based filtering

---

### Decision 3: Source of Truth Strategy

**Problem**: Once tasks are generated, what happens when specs change?

**Solution**: **Generate-once with conflict-aware regeneration**

**Workflow**:
1. **Initial Generation**: `/flow:tasks` → Backlog.md tasks created
2. **Execution**: Developers update task status, add notes, assign work
3. **Spec Changes**: Developer runs `specify tasks regenerate`
4. **Conflict Detection**: System detects manually edited tasks
5. **Merge Options**: Overwrite, keep manual changes, or manual merge

**Validation Plan**:
- Prototype with 3-5 real features
- Test if regeneration is actually needed (hypothesis: rare)
- Measure conflict frequency in beta testing

---

## Integration Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Spec-Driven Workflow                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  /flow:specify       │
                    │  /flow:plan          │
                    │  /flow:research      │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  Spec Files Generated  │
                    │  - spec.md             │
                    │  - plan.md             │
                    │  - data-model.md       │
                    └───────────┬────────────┘
                                │
                                ▼
              ┌──────────────────────────────────────┐
              │  /flow:tasks (ENHANCED)            │
              │  - Parse spec.md user stories        │
              │  - Map to Backlog.md format          │
              │  - Generate task-*.md files          │
              │  - Set labels, dependencies          │
              └──────────────────┬───────────────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────────┐
              │  Backlog.md Storage                  │
              │  backlog/tasks/                      │
              │  ├── task-001 - Setup.md             │
              │  ├── task-012 - User model.md        │
              │  └── task-042 - Auth endpoint.md     │
              └──────────────────┬───────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
  │ CLI Commands │      │   Web UI     │      │  MCP Tools   │
  │              │      │              │      │              │
  │ - board      │      │ - Kanban     │      │ - create     │
  │ - browser    │      │ - Drag/drop  │      │ - update     │
  │ - search     │      │ - Filtering  │      │ - complete   │
  └──────────────┘      └──────────────┘      └──────┬───────┘
                                                      │
                                                      ▼
                                          ┌────────────────────┐
                                          │  Claude Code       │
                                          │  - AI task mgmt    │
                                          │  - Auto completion │
                                          └────────────────────┘
```

---

## Installation and Configuration

### Current Status

✅ **Backlog.md Installed**: v1.20.1 (via pnpm)
✅ **Backlog.md Initialized**: Project "flowspec"
✅ **MCP Configured**: Added to `.mcp.json` for Claude Code
✅ **Directory Structure Created**: `backlog/` with tasks, docs, decisions

### Configuration Files

**`.mcp.json`** (MCP Server Configuration):
```json
{
  "mcpServers": {
    "backlog": {
      "command": "backlog",
      "args": ["mcp", "start"],
      "env": {},
      "description": "Backlog.md task management: create, update, search tasks with kanban board integration"
    }
  }
}
```

**`backlog/config.yml`** (Backlog.md Settings):
```yaml
project_name: "flowspec"
default_status: "To Do"
statuses: ["To Do", "In Progress", "Done"]
labels: []
milestones: []
date_format: yyyy-mm-dd
max_column_width: 20
auto_open_browser: true
default_port: 6420
remote_operations: true
auto_commit: false
bypass_git_hooks: false
check_active_branches: true
active_branch_days: 30
```

### Testing MCP Integration

**Verify Claude Code can access Backlog.md**:

You can now ask Claude Code:
- "List all tasks in the backlog"
- "Create a new task for implementing user authentication"
- "Update task-1 to Done status"
- "Show me all tasks labeled with US1"

The MCP server provides these tools:
- `backlog_list_tasks`: Query tasks with filters
- `backlog_create_task`: Create new tasks
- `backlog_update_task`: Update task status, assignees, labels
- `backlog_search`: Search across tasks, docs, decisions
- `backlog_get_task`: Retrieve task details

---

## Implementation Plan

### MVP Scope (Phase 1 - US1: Task Generation)

**Goal**: Generate Backlog.md tasks from flowspec specs

**User Story**:
> As a spec-driven developer, I want to automatically generate Backlog.md tasks from my spec.md and plan.md files, so that I don't have to manually create and organize tasks in a project management tool.

**Tasks** (from PRD):
```
Phase 2: Foundational
- [ ] T006 Implement task parser for flowspec format
- [ ] T007 Implement Backlog.md file writer
- [ ] T008 Create dependency graph builder
- [ ] T009 Implement task format mapper
- [ ] T010 Create Backlog.md config.yml generator

Phase 3: User Story 1 (MVP)
- [ ] T011 Implement `specify tasks generate --format backlog-md` command
- [ ] T012 Integrate task parser with spec.md reader
- [ ] T013 Generate Backlog.md task files from parsed tasks
- [ ] T014 Map user story labels (US1, US2) to Backlog.md labels
- [ ] T015 Map [P] markers to "parallelizable" label
- [ ] T016 Build and write task dependencies
- [ ] T017 Generate summary output
- [ ] T018 Add error handling
```

**Acceptance Criteria**:
- ✅ Run `/flow:tasks --format backlog-md` on existing feature
- ✅ Verify `backlog/tasks/` directory created with task-*.md files
- ✅ Verify user story labels preserved: `labels: [US1]`, `labels: [US2]`
- ✅ Verify parallelizable tasks have `labels: [parallelizable]`
- ✅ Verify dependencies: Foundational tasks block User Story tasks
- ✅ Run `backlog board` and see organized Kanban view
- ✅ Filter by user story: `backlog board --filter US1`

**Success Metrics**:
- 95%+ task generation accuracy (manual verification)
- <5 minutes setup time
- <10 seconds generation time for 200 tasks

---

### Phase 2: CLI Commands & Migration (US2, US3)

**US2: CLI Commands**
- Wrap Backlog.md commands in `specify backlog <command>`
- Provide convenient shortcuts
- Add status summaries

**US3: Migration**
- Migrate existing `tasks.md` files to Backlog.md
- Preserve task state (checked → done)
- Create backups before migration

---

### Phase 3: MCP Setup & Regeneration (US4, US5)

**US4: MCP Integration**
- Automate MCP configuration during `specify init`
- Verify MCP connection
- Document AI workflows

**US5: Regeneration**
- Detect conflicts when specs change
- Provide merge strategies
- Backup before regeneration

---

## Testing Strategy

### Discovery Validation (Completed)

✅ **Research**: Backlog.md capabilities documented
✅ **Technical Feasibility**: MCP integration verified
✅ **Architecture Design**: Hybrid model designed
✅ **PRD Created**: Comprehensive specification

### Next: Beta Testing Plan

**Week 1-2** (Concierge Test):
- Manually set up integration for 3 pilot users
- Gather qualitative feedback
- Success: 2/3 users continue using

**Week 3-4** (MVP Development):
- Build US1 (Task Generation)
- Self-dogfood on flowspec project
- Test with 3 existing features

**Week 5-6** (Beta Release):
- Release to 10 beta users
- Measure: generation success rate, setup time, task accuracy
- Iterate based on feedback

**Week 7-8** (Feature Expansion):
- US2 (CLI Commands)
- US3 (Migration)
- Beta test with 50 users

**Week 9-10** (Public Launch):
- US4 (MCP Setup)
- US5 (Regeneration)
- Documentation and tutorials
- Public release

---

## Success Metrics

### North Star Metric
**% of flowspec generated features actively tracked in Backlog.md**
- Target: 60% within 6 months

### Leading Indicators (Month 1-3)
- Task generation success rate: 95%+
- Integration setup time: <5 minutes
- Developer adoption rate: 60%+

### Lagging Indicators (Month 6)
- Task completion velocity: +20% improvement
- Developer satisfaction (NPS): +15 points
- AI-assisted task completion: 40%+
- Retention rate (3mo): 70%+

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|-----------|
| Backlog.md API changes | Pin to specific version, adapter layer |
| MCP protocol changes | Isolate MCP code, maintain fallback |
| Performance at scale | Load testing, batch operations |

### Adoption Risks

| Risk | Mitigation |
|------|-----------|
| User resistance to change | Opt-in initially, preserve tasks.md fallback |
| Complexity perceived too high | Strong onboarding, video tutorials |
| Integration not valuable | Strong MVP validation before full build |

---

## Next Steps

### Immediate (This Week)

1. **Review PRD**: Stakeholder review of `docs/prd-backlog-md-integration.md`
2. **Validation Experiments**:
   - Concierge test with 3 pilot users (recruit from Discord/GitHub)
   - Technical spike: Build task parser prototype
   - Usability test: 5 developers attempt setup

3. **Go/No-Go Decision**: Review validation results, decide to proceed or pivot

### Short Term (Next 2-4 Weeks)

4. **MVP Development**: Build US1 (Task Generation)
   - Implement task parser (`src/specify_cli/backlog/parser.py`)
   - Implement Backlog.md writer (`src/specify_cli/backlog/writer.py`)
   - Implement mapper (`src/specify_cli/backlog/mapper.py`)
   - Create CLI command: `specify tasks generate --format backlog-md`

5. **Self-Dogfooding**: Use integration on flowspec project
   - Migrate 2-3 existing features
   - Document pain points and improvements

6. **Beta Release**: Ship MVP to 10 pilot users

### Medium Term (Next 2-3 Months)

7. **Feature Expansion**: US2-US5
8. **Documentation**: User guide, API reference, video tutorials
9. **Public Launch**: Release to community

---

## Resources

### Documentation
- **PRD**: `docs/prd-backlog-md-integration.md` (12,000 words, comprehensive specification)
- **Backlog.md Docs**: https://github.com/MrLesk/Backlog.md
- **MCP Protocol**: https://modelcontextprotocol.io

### Current Project Files
- **MCP Config**: `.mcp.json` (Backlog.md server added)
- **Backlog Config**: `backlog/config.yml` (flowspec project)
- **Demo Task**: `backlog/tasks/task-1 - Integrate-Backlog.md-with-flowspec.md`

### Tools Available
- **Backlog.md CLI**: v1.20.1 installed via pnpm
- **MCP Server**: Configured for Claude Code
- **flowspec**: Current task generation via `/flow:tasks`

---

## Questions for Review

1. **Strategic Alignment**: Does this integration align with flowspec's vision and roadmap?
2. **Resource Commitment**: Can we commit developer time for 12-week implementation?
3. **Scope Decision**: Should MVP be US1 only, or include US2/US3?
4. **Validation Plan**: Which validation experiments should we run first?
5. **Beta Recruitment**: How do we recruit 10 pilot users for beta testing?

---

## Conclusion

We have completed comprehensive discovery and planning for the Backlog.md integration. The PRD provides:
- **Strategic rationale** (why integrate?)
- **Design decisions** with chain of thought reasoning
- **Integration architecture** (how it works)
- **Implementation plan** (what to build)
- **Success metrics** (how to measure)
- **Risk mitigation** (what could go wrong)

**The integration is feasible, valuable, and ready for validation experiments.**

Next step: **Stakeholder review and validation sprint to confirm user demand before full implementation.**

---

**Status**: ✅ Discovery Complete | 🚧 Awaiting Validation Experiments | ⏳ Implementation Not Started

**Last Updated**: 2025-11-23
