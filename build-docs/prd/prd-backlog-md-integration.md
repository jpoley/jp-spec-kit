# Product Requirements Document: Backlog.md MCP Integration with flowspec

**Version**: 1.0
**Date**: 2025-11-23
**Status**: Draft - Discovery Phase
**Owner**: Product Strategy Team

---

## Executive Summary

### Problem Statement

**Customer Opportunity**: Developers using flowspec for Spec-Driven Development (SDD) lack robust task lifecycle management, visual task boards, and AI-powered task execution capabilities. While flowspec excels at generating structured, user-story-centric tasks from specifications, it stops short of providing the task management infrastructure needed for effective execution and team collaboration.

**Current Pain Points**:
- **Limited Visibility**: Tasks live in static markdown files without visual boards or status tracking
- **No Lifecycle Management**: Once generated, tasks have no workflow states, assignees, or progress tracking
- **Collaboration Gaps**: No support for multi-developer coordination, task assignment, or dependencies enforcement
- **Context Switching**: Developers must leave their workflow to use external project management tools
- **AI Integration Barrier**: No programmatic API for AI assistants to manage, update, or complete tasks

### Proposed Solution

Integrate **Backlog.md MCP** as the task management layer for flowspec, creating a unified spec-driven development platform where:

1. **flowspec generates tasks** from specifications (spec.md, plan.md) using its proven user-story-centric approach
2. **Backlog.md manages task lifecycle** with status tracking, assignees, dependencies, labels, and priorities
3. **MCP protocol enables AI-powered task execution** where Claude Code and other AI assistants can programmatically create, update, and complete tasks
4. **Developers gain visual task management** via terminal Kanban boards and web UI while staying within their Git repository
5. **Spec-driven workflow remains primary** with Backlog.md enhancing rather than replacing flowspec's core value proposition

**Key Insight**: This is not a replacement but an **enhancement layer**—flowspec remains the source of truth for task generation from specs, while Backlog.md provides the execution infrastructure that's currently missing.

### Success Metrics

**North Star Metric**: **% of flowspec generated features actively tracked in Backlog.md**

**Leading Indicators** (Early Signals):
- Task generation success rate: **95%+** (tasks correctly synced to Backlog.md)
- Integration setup time: **<5 minutes** (from init to first synced task)
- Developer adoption rate: **60%+** within 30 days of release

**Lagging Indicators** (Final Outcomes):
- Task completion velocity: **+20% improvement** vs. pre-integration baseline
- Developer satisfaction (NPS): **+15 points** increase
- Reduced context switching: **30% fewer external tool references** (measured via user feedback)
- AI-assisted task completion: **40%+ of tasks** completed with AI assistance

**Measurement Approach**:
- CLI analytics (opt-in telemetry)
- Quarterly user surveys
- Usage pattern analysis (backlog.md command frequency)
- Integration health checks (sync errors, conflict rate)

### Business Value & Strategic Alignment

**flowspec Vision**: Become the standard toolkit for spec-driven development, enabling teams to ship customer value faster through structured, AI-assisted workflows.

**This Integration Delivers**:
1. **Competitive Differentiation**: First spec-driven tool with integrated AI-powered task management
2. **Ecosystem Expansion**: Positions flowspec as a platform (specs + tasks + execution)
3. **Retention Driver**: Developers using Backlog.md integration are less likely to switch tools
4. **Network Effects**: Backlog.md's standalone value attracts new flowspec users
5. **AI-First Positioning**: Demonstrates flowspec's commitment to AI-assisted development workflows

**Strategic Bets**:
- MCP protocol becomes standard for AI tool integration (HIGH confidence)
- Developers prefer local-first, repo-integrated task management (MEDIUM confidence)
- Spec-driven development adoption accelerates with better task management (HIGH confidence)

---

## Chain of Thought Analysis

### 🧠 Problem Decomposition

**Why integrate these systems?**

Let me break down the core problem:

1. **flowspec's Current Strength**: Transforms specifications into actionable, user-story-organized task lists
   - *Why this matters*: Ensures tasks are traceable to requirements and user value
   - *What's missing*: Once generated, tasks are static—no status updates, no assignees, no progress tracking

2. **Backlog.md's Strength**: Provides rich task lifecycle management with AI integration
   - *Why this matters*: Developers need to track "who's working on what" and "what's done vs. in progress"
   - *What's missing*: No connection to spec-driven workflows or automatic task generation from requirements

3. **The Integration Opportunity**: Combine spec generation with task management
   - flowspec → **WHAT to build** (derived from specs)
   - Backlog.md → **HOW to execute** (task states, assignees, boards)
   - MCP → **AI-powered execution** (assistants manage tasks programmatically)

**Outcome Sought**: Developers can go from "spec written" to "tasks tracked and completed" without leaving their Git repository or using external tools.

### 🤔 Design Decisions & Trade-offs

#### Decision 1: Source of Truth Strategy

**Question**: Should Backlog.md be the source of truth, or should tasks.md remain canonical?

**Options Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **A) Backlog.md as source of truth** | - Single source of truth<br>- Rich metadata natively stored<br>- AI tools directly update | - Breaks flowspec's current model<br>- Migration complexity<br>- Users lose tasks.md simplicity | ❌ Rejected |
| **B) tasks.md as source of truth** | - Preserves flowspec model<br>- Familiar to users<br>- Simple rollback | - Backlog.md becomes stale if tasks.md changes<br>- Bidirectional sync complexity<br>- Conflict resolution needed | ❌ Rejected |
| **C) Hybrid: Generation → Backlog.md** | - flowspec generates to Backlog.md directly<br>- tasks.md becomes optional reference<br>- Backlog.md manages execution | - Requires rethinking tasks.md role<br>- Potential user confusion<br>- Migration path needed | ✅ **SELECTED** |

**Decision**: **Hybrid model—flowspec generates tasks directly into Backlog.md format**

**Reasoning**:
- **Problem**: Bidirectional sync between tasks.md and Backlog.md creates complexity (conflicts, staleness, sync errors)
- **Insight**: tasks.md was always meant as a *template for execution*, not a persistent tracker
- **Solution**: Generate tasks once into Backlog.md; optionally keep tasks.md as a "blueprint" or deprecate it
- **Migration**: Existing projects can run a one-time migration command; new projects go straight to Backlog.md

**Validation Needed**: User research—do developers value tasks.md as a reference, or is it just a stepping stone?

#### Decision 2: Task Format Mapping

**Question**: How do we map flowspec's task format to Backlog.md's format?

**flowspec Format**:
```markdown
- [ ] T012 [P] [US1] Create User model in src/models/user.py
```

**Backlog.md Format**:
```markdown
task-012 - Create User model in src models user.py.md

---
status: todo
assignees: []
labels: [US1, parallelizable]
priority: medium
dependencies: [task-011]
---

## Description
Create User model in src/models/user.py

## Acceptance Criteria
- [ ] Model includes required fields
- [ ] Validation logic implemented
- [ ] Tests pass
```

**Mapping Strategy**:

| flowspec Element | Backlog.md Mapping | Reasoning |
|---------------------|-------------------|-----------|
| **TaskID** (T012) | `task-012` filename | Direct ID mapping preserves traceability |
| **[P] marker** | `labels: [parallelizable]` | Allows filtering for parallel execution |
| **[US1] label** | `labels: [US1]` | Preserves user story organization |
| **Description** | Filename + Description field | Human-readable in filename, full text in body |
| **File path** | Included in Description | Implementation detail for developer context |
| **Priority** (implicit from phase) | `priority: high/medium/low` | Phase 1-2 = high, user stories = priority order |
| **Dependencies** (phase-based) | `dependencies: [task-xxx]` | Foundational tasks block user stories |

**Trade-off**: Backlog.md filenames have character limits; long descriptions may be truncated in filename but preserved in body.

#### Decision 3: Integration Pattern

**Question**: Generate-once vs. continuous sync?

**Options**:

| Pattern | When to Use | Pros | Cons |
|---------|------------|------|------|
| **Generate-once** | Tasks generated from spec, then managed in Backlog.md | - Simple, clear ownership<br>- No sync conflicts<br>- Backlog.md is source of truth post-generation | - Spec changes require manual task updates<br>- No re-generation from updated specs |
| **Continuous sync** | Tasks.md and Backlog.md stay in sync | - Spec changes auto-update tasks<br>- tasks.md remains useful reference | - Complex conflict resolution<br>- Risk of data loss<br>- Sync failures |
| **Regeneration on demand** | Developer triggers re-sync when specs change significantly | - Balances simplicity and flexibility<br>- Clear developer control | - Potential to overwrite manual changes<br>- Requires merge strategy |

**Decision**: **Generate-once with optional regeneration**

**Reasoning**:
- **Reality**: Specs stabilize early; tasks evolve during implementation
- **Risk**: Continuous sync risks overwriting developer updates (assignees, status, notes)
- **Solution**: Generate once when spec is ready; provide `/speckit.backlog regenerate` for major spec changes with conflict detection

**Validation**: Prototype with 3-5 real features to test if regeneration is actually needed or if generate-once suffices.

#### Decision 4: User Story Preservation

**Question**: How do we maintain flowspec's user-story-centric organization in Backlog.md?

**Backlog.md's Model**: Flat list of tasks with labels and dependencies

**flowspec's Model**: Hierarchical phases organized by user stories

**Solution**: **Use labels + virtual grouping**

```yaml
# Task from User Story 1
labels: [US1, setup, p0]
dependencies: []

# Task from User Story 2
labels: [US2, feature, p1]
dependencies: [task-foundational-auth]
```

**Benefits**:
- Backlog.md board can filter by `US1`, `US2`, etc. to view story-specific tasks
- Dependencies encode phase relationships (Foundational tasks are dependencies for user story tasks)
- Labels allow parallel organization (by story, by phase, by priority)

**Trade-off**: Loses explicit phase hierarchy; developers must use labels/filters instead.

**Validation**: Test with users whether label-based filtering provides adequate organization.

### 🔄 User Experience Workflow

**Developer Journey**: From Spec to Completed Tasks

```
1. [Spec Creation]
   Developer: Run /flow:specify to create spec.md
   Output: spec.md with user stories

2. [Planning]
   Developer: Run /flow:plan to create plan.md
   Output: plan.md with architecture

3. [Task Generation] ← NEW INTEGRATION POINT
   Developer: Run /flow:tasks (modified to generate Backlog.md tasks)
   Output:
   - Backlog.md initialized (if first time)
   - Tasks generated as individual task-*.md files
   - Tasks organized by user story labels
   - Dependencies auto-configured

4. [Task Execution] ← ENHANCED WITH BACKLOG.MD
   Developer:
   - Run `backlog board` to see Kanban view
   - Use Claude Code with MCP to: "Complete task-012"
   - AI assistant updates task status automatically
   - Or: Update tasks manually via `backlog browser` web UI

5. [Progress Tracking] ← NEW CAPABILITY
   Developer:
   - View progress: `backlog board --filter US1`
   - Search tasks: `backlog search "User model"`
   - Check dependencies: `backlog show task-012`

6. [Completion]
   Developer: All tasks for US1 complete
   - Deploy MVP
   - Move to US2
   - Backlog.md preserves task history for retrospectives
```

**Learning Curve**:
- **Existing flowspec users**: Learn `backlog` CLI commands (5-10 minutes)
- **New users**: Learn flowspec workflow + Backlog.md (30 minutes)

**Friction Points**:
- Initial setup (Backlog.md installation + MCP configuration)
- Understanding label-based vs. phase-based organization
- Migration for existing projects with tasks.md files

**Mitigation**:
- Auto-install Backlog.md during `specify init` if user opts in
- Provide migration wizard: `specify migrate-to-backlog`
- Documentation with video walkthrough

### ⚠️ Risk Mitigation

**What could go wrong?**

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| **Backlog.md API changes** break integration | HIGH | MEDIUM | - Pin to specific Backlog.md version<br>- Monitor Backlog.md releases<br>- Maintain adapter layer |
| **Users resist change** from tasks.md | MEDIUM | HIGH | - Make integration opt-in initially<br>- Preserve tasks.md as fallback<br>- Provide migration guide |
| **Sync conflicts** during regeneration | HIGH | LOW | - Implement conflict detection<br>- Backup tasks before regen<br>- Manual merge resolution UI |
| **Performance degradation** with 1000+ tasks | MEDIUM | MEDIUM | - Batch task creation<br>- Lazy loading in Backlog.md<br>- Performance testing |
| **MCP integration complexity** | MEDIUM | MEDIUM | - Start with direct Backlog.md CLI calls<br>- Add MCP in Phase 2<br>- Fallback to file-based approach |
| **Data loss** during migration | CRITICAL | LOW | - Dry-run mode<br>- Automatic backups<br>- Rollback capability |

---

## User Stories and Use Cases

### Primary User Personas

#### Persona 1: **Solo Developer Sam**
- **Profile**: Individual developer building side projects, uses AI assistants heavily
- **Goals**: Fast iteration, minimal overhead, AI-powered task completion
- **Pain Points**: Context switching between tools, manual task tracking in notebooks/text files
- **Value from Integration**: AI assistant manages entire task lifecycle while Sam focuses on coding

#### Persona 2: **Team Lead Taylor**
- **Profile**: Leading 3-5 developer team, needs visibility into progress and blockers
- **Goals**: Track who's working on what, identify bottlenecks, ensure user stories complete independently
- **Pain Points**: Static tasks.md doesn't show real-time status, hard to see dependencies
- **Value from Integration**: Kanban board shows team progress, assignees visible, dependencies enforced

#### Persona 3: **Enterprise Architect Alex**
- **Profile**: Architect at large company, mandates spec-driven development for compliance
- **Goals**: Ensure all features traceable to requirements, audit trail for changes
- **Pain Points**: External project management tools disconnect from specs
- **Value from Integration**: Tasks generated from specs with full traceability, all data in Git repo

### User Journey Maps

#### Journey 1: New Feature Development (Solo Developer)

**Starting Point**: Spec written, ready to implement

| Step | User Action | System Response | Pain/Delight |
|------|------------|----------------|--------------|
| 1 | Run `/flow:tasks` | Tasks generated into Backlog.md | ✅ Delight: Automatic setup |
| 2 | Run `backlog board` | See Kanban with all tasks in "todo" | ✅ Delight: Visual clarity |
| 3 | Ask Claude: "Start task-001" | AI updates task status to "in_progress", opens relevant files | ✅ Delight: AI integration |
| 4 | Implement feature | AI completes subtasks automatically | ✅ Delight: Reduced manual tracking |
| 5 | Ask Claude: "Complete task-001" | AI marks complete, moves to next task | ✅ Delight: Seamless flow |
| 6 | Check progress: `backlog board --filter US1` | See US1 tasks: 5 done, 2 in progress, 3 todo | ✅ Delight: Progress visibility |

**Outcome**: Feature completed 20% faster due to reduced task management overhead.

#### Journey 2: Team Collaboration (Team Lead)

**Starting Point**: Feature spec approved, ready to distribute work

| Step | User Action | System Response | Pain/Delight |
|------|------------|----------------|--------------|
| 1 | Run `/flow:tasks` | Tasks generated, unassigned | ✅ Delight: Tasks ready for assignment |
| 2 | Run `backlog browser` | Web UI opens, drag tasks to assign | ✅ Delight: Visual assignment |
| 3 | Assign US1 to Dev1, US2 to Dev2 | Tasks updated with assignees | ✅ Delight: Clear ownership |
| 4 | Daily: Check `backlog board` | See who's blocked, what's in progress | ✅ Delight: Team visibility |
| 5 | Dev1 asks Claude: "Complete US1" | AI completes all US1 tasks, updates board | ✅ Delight: Automated status |
| 6 | Standup: Share board view | Team sees visual progress | ✅ Delight: Shared context |

**Outcome**: Team coordination improved, fewer status meetings needed.

### Detailed User Stories with Acceptance Criteria

#### Epic 1: Task Generation from Specs

**US1.1**: Generate Backlog.md Tasks from flowspec Specs
- **As a** spec-driven developer
- **I want** to automatically generate Backlog.md tasks from my spec.md and plan.md files
- **So that** I don't have to manually create and organize tasks in a project management tool

**Acceptance Criteria**:
- **Given** I have a valid spec.md with user stories and a plan.md
- **When** I run `/flow:tasks` or `specify tasks generate`
- **Then** the system should:
  - Create a `backlog/` directory if it doesn't exist
  - Generate one `task-<id> - <title>.md` file per task
  - Preserve user story labels (US1, US2) as Backlog.md labels
  - Set task dependencies based on phase relationships (Foundational blocks User Stories)
  - Assign priorities based on user story priority (P1 = high, P2 = medium)
  - Include file paths in task descriptions
  - Mark parallelizable tasks with "parallelizable" label
  - Create a summary: "Generated X tasks across Y user stories"

**Edge Cases**:
- **Existing backlog/**: Prompt user "Backlog exists, regenerate? (yes/no/merge)"
- **Missing spec.md**: Error with guidance to run `/flow:specify` first
- **Invalid task format in tasks.md**: Validation error with line numbers

---

**US1.2**: Preserve User Story Organization in Backlog.md
- **As a** product-focused developer
- **I want** tasks grouped by user story even in Backlog.md
- **So that** I can deliver and test user stories independently

**Acceptance Criteria**:
- **Given** tasks generated from a spec with 3 user stories
- **When** I run `backlog board --filter US1`
- **Then** I see only tasks labeled with US1
- **And** tasks are ordered by dependency (setup → foundational → implementation)

---

#### Epic 2: AI-Powered Task Execution via MCP

**US2.1**: AI Assistant Can Update Task Status
- **As a** developer using Claude Code
- **I want** Claude to update task status when I complete work
- **So that** I don't have to manually track progress

**Acceptance Criteria**:
- **Given** Claude Code has MCP connection to Backlog.md
- **When** I say "Claude, complete task-012"
- **Then** Claude should:
  - Verify task-012 exists
  - Update status to "done"
  - Add completion timestamp
  - Show confirmation: "Task-012 (Create User model) marked complete"

---

**US2.2**: AI Assistant Can Create Subtasks
- **As a** developer encountering unexpected complexity
- **I want** Claude to break down a task into subtasks
- **So that** I can track granular progress

**Acceptance Criteria**:
- **Given** I'm working on task-042
- **When** I say "Claude, this is complex, break it into subtasks"
- **Then** Claude should:
  - Analyze task description
  - Create 3-5 subtasks as child tasks (task-042-1, task-042-2, etc.)
  - Link them via dependencies to parent task
  - Mark parent as blocked until subtasks complete

---

#### Epic 3: Migration and Compatibility

**US3.1**: Migrate Existing tasks.md to Backlog.md
- **As a** developer with existing flowspec projects
- **I want** to migrate my tasks.md files to Backlog.md format
- **So that** I can use the new integration without starting over

**Acceptance Criteria**:
- **Given** I have an existing `/specs/001-auth-feature/tasks.md` file
- **When** I run `specify migrate-to-backlog --feature 001-auth-feature`
- **Then** the system should:
  - Parse tasks.md and extract all tasks
  - Create corresponding Backlog.md task files
  - Preserve task IDs, descriptions, file paths
  - Map [P] markers to "parallelizable" label
  - Map [US*] labels to Backlog.md labels
  - Create backup: `tasks.md.backup`
  - Generate migration report

---

## DVF+V Risk Assessment

### Value Risk (Desirability)

**Question**: Will developers actually adopt this integration, or will they stick with their existing workflows?

**Assumptions to Test**:
1. Developers prefer local, repo-integrated task management over external tools (Jira, Linear, etc.)
2. AI-powered task execution is compelling enough to change workflows
3. Visual task boards (Kanban) add sufficient value over static tasks.md files

**Validation Plan** (Fast & Cheap):

| Experiment | Method | Success Criteria | Timeline |
|-----------|--------|-----------------|----------|
| **Concierge Test** | Manually set up Backlog.md for 3 pilot users, help them use it for 1 sprint | 2/3 users continue using after concierge support ends | 2 weeks |
| **Landing Page MVP** | Create demo video showing spec → task generation → AI completion workflow | 100+ email signups for beta | 1 week |
| **Customer Interviews** | Interview 10 flowspec users about current task tracking pain points | 7/10 express strong interest in integration | 1 week |
| **Wizard of Oz** | Use Claude Code to manually manage Backlog.md tasks, simulate MCP integration | Users find workflow intuitive, complete tasks faster | 1 week |

**Go/No-Go Decision**: Proceed to MVP if 2/4 experiments show positive results.

### Usability Risk (Experience)

**Question**: Can users figure out how to use the integration without extensive documentation or support?

**Assumptions to Test**:
1. Setup process (<5 minutes) is acceptable for most developers
2. Label-based user story filtering is intuitive (vs. phase-based hierarchy)
3. Backlog.md CLI commands are discoverable and easy to learn
4. Conflict resolution during regeneration is understandable

**Validation Plan**:

| Experiment | Method | Success Criteria | Timeline |
|-----------|--------|-----------------|----------|
| **Usability Testing** | 5 developers (unfamiliar with Backlog.md) attempt setup and first task generation | 4/5 complete without asking for help | 3 days |
| **Rapid Prototyping** | Build CLI wizard: `specify init --with-backlog` that guides setup | Users rate setup as "easy" (4+/5) | 1 week |
| **Think-Aloud Sessions** | Watch 3 developers use `backlog board --filter US1`, observe confusion points | Identify top 3 UX improvements | 2 days |
| **Documentation Review** | Have non-technical user read setup guide, note questions/confusion | Identify gaps in documentation | 1 day |

**Go/No-Go Decision**: Proceed if 4/5 complete setup unaided and rate experience 4+/5.

### Feasibility Risk (Technical)

**Question**: Can we build this integration reliably with Python + Backlog.md CLI + MCP?

**Assumptions to Test**:
1. Backlog.md CLI is stable and supports batch operations
2. MCP integration with Backlog.md works reliably in Claude Code
3. Task generation at scale (1000+ tasks) performs acceptably
4. Conflict detection during regeneration is technically feasible

**Validation Plan**:

| Experiment | Method | Success Criteria | Timeline |
|-----------|--------|-----------------|----------|
| **Engineering Spike** | Build prototype: parse tasks.md → generate Backlog.md tasks for 1 feature | Successful generation, all metadata preserved | 3 days |
| **Feasibility Prototype** | Test Backlog.md MCP integration with Claude Code on 50 tasks | AI can create, update, complete tasks via MCP | 2 days |
| **Load Testing** | Generate 1000 tasks from synthetic spec, measure performance | <10 seconds generation time, <1 second board load | 1 day |
| **Architecture Review** | Review Backlog.md source code for API stability and extensibility | No blocking issues identified | 1 day |

**Go/No-Go Decision**: Proceed if all spikes succeed and performance meets targets.

### Business Viability Risk (Organizational)

**Question**: Does this integration align with flowspec's business model and strategic direction?

**Assumptions to Test**:
1. Integration increases flowspec adoption (more users)
2. Integration increases retention (users stay longer)
3. Maintenance burden is acceptable (no dedicated Backlog.md team)
4. Dependency on external tool (Backlog.md) is strategically acceptable

**Validation Plan**:

| Experiment | Method | Success Criteria | Timeline |
|-----------|--------|-----------------|----------|
| **Stakeholder Mapping** | Interview flowspec maintainers, gather concerns/requirements | No blocking objections, 2+ enthusiastic supporters | 1 week |
| **Cost Analysis** | Estimate development (40-80 hours) + maintenance (5 hours/month) costs | ROI positive within 6 months based on adoption projections | 2 days |
| **Competitive Analysis** | Survey 5 competitor tools (Linear, Jira, etc.) for spec-driven integrations | flowspec integration is differentiated | 3 days |
| **Legal Review** | Check Backlog.md license (likely MIT/Apache), ensure compatibility | No licensing conflicts | 1 day |

**Go/No-Go Decision**: Proceed if ROI positive and no legal/strategic blockers.

---

## Functional Requirements

### FR1: Task Generation

**FR1.1**: Generate Backlog.md Tasks from Specification Documents

**Input**:
- `/specs/[feature-id]/spec.md` (required): User stories with priorities
- `/specs/[feature-id]/plan.md` (required): Technical architecture, file paths
- `/specs/[feature-id]/data-model.md` (optional): Entity definitions
- `/specs/[feature-id]/contracts/` (optional): API contracts

**Process**:
1. Parse spec.md to extract user stories and priorities
2. Parse plan.md to extract tech stack and project structure
3. Parse tasks.md template (or generate tasks on-the-fly)
4. For each task in tasks.md:
   - Extract task ID, description, file path, markers ([P], [US*])
   - Create Backlog.md task file: `backlog/task-<id> - <title>.md`
   - Set frontmatter:
     - `status: todo`
     - `labels:` [user story label, "parallelizable" if [P], phase label]
     - `priority:` (high for setup/foundational, medium/low for user stories based on P1/P2/P3)
     - `dependencies:` (based on phase relationships)
   - Set body: description with file path and acceptance criteria
5. Generate `backlog/config.yml` if not exists

**Output**:
- `backlog/task-001 - Create project structure.md`
- `backlog/task-002 - Initialize Python project.md`
- ...
- `backlog/task-N - Final task.md`
- Summary: "Generated N tasks across M user stories"

**Error Handling**:
- Missing spec.md: Error "Spec file not found. Run `/flow:specify` first."
- Invalid task format: Validation error with line number
- Backlog already exists: Prompt for regeneration strategy (overwrite/merge/cancel)

---

**FR1.2**: Preserve User Story Metadata

**Requirement**: Tasks must retain their user story association for filtering and organization.

**Implementation**:
- User story labels (US1, US2, US3) added to `labels:` array
- Phase labels (setup, foundational, polish) added to `labels:` array
- Priority mapping: User stories ordered P1 → P2 → P3 map to high → medium → low

**Example**:
```yaml
# task-012 - Create User model.md
---
status: todo
labels: [US1, implementation, backend]
priority: high
dependencies: [task-005]  # Foundational auth task
---
```

---

**FR1.3**: Map Task Dependencies

**Requirement**: Encode flowspec's phase-based dependencies into Backlog.md's dependency system.

**Mapping Rules**:
- **Setup tasks** (Phase 1): No dependencies
- **Foundational tasks** (Phase 2): Depend on all Setup tasks
- **User Story tasks** (Phase 3+): Depend on all Foundational tasks
- **Within User Story**: Tasks depend on previous tasks in same story (unless marked [P])
- **Polish tasks** (Final phase): Depend on all user story tasks

**Implementation**:
- Parse tasks.md phases
- Build dependency graph
- Detect circular dependencies (error if found)
- Write `dependencies: [task-xxx, task-yyy]` in frontmatter

---

### FR2: Backlog.md Lifecycle Management

**FR2.1**: CLI Commands for Task Management

**Commands to Implement/Wrap**:

| Command | Description | Example |
|---------|-------------|---------|
| `specify backlog init` | Initialize Backlog.md in current repo | `specify backlog init` |
| `specify backlog sync` | Generate tasks from latest specs | `specify backlog sync --feature 001-auth` |
| `specify backlog board` | Open terminal Kanban (wrapper for `backlog board`) | `specify backlog board --filter US1` |
| `specify backlog browser` | Open web UI (wrapper for `backlog browser`) | `specify backlog browser` |
| `specify backlog status` | Show summary statistics | `specify backlog status` |
| `specify backlog migrate` | Migrate existing tasks.md to Backlog.md | `specify backlog migrate --feature 001-auth` |

---

**FR2.2**: Task Status Workflow

**Supported Statuses** (Backlog.md standard):
- `todo`: Not started
- `in_progress`: Currently being worked on
- `blocked`: Waiting on dependency or external factor
- `done`: Completed
- `archived`: No longer relevant

**Workflow Transitions**:
```
todo → in_progress → done
  ↓         ↓
blocked → archived
```

**AI Integration**: Claude Code can transition tasks via MCP tools.

---

### FR3: MCP Integration

**FR3.1**: Claude Code MCP Tool Support

**Required MCP Tools** (provided by Backlog.md):
- `backlog_create_task`: Create new task programmatically
- `backlog_update_task`: Update task status, assignees, labels
- `backlog_get_task`: Retrieve task details
- `backlog_list_tasks`: List tasks with filters
- `backlog_archive_task`: Archive completed/irrelevant tasks

**flowspec Responsibilities**:
- Ensure Backlog.md MCP server is configured during setup
- Provide documentation for Claude Code integration
- Test MCP commands work correctly

**Example AI Interaction**:
```
User: "Claude, start working on task-012"
Claude (via MCP):
  1. Call backlog_get_task(id=012) to verify it exists
  2. Call backlog_update_task(id=012, status=in_progress)
  3. Open src/models/user.py (from task description)
  4. Respond: "Started task-012: Create User model. Opening src/models/user.py"
```

---

**FR3.2**: MCP Configuration Setup

**Requirement**: Automate MCP server configuration for users.

**Implementation**:
1. During `specify init --with-backlog`:
   - Check if Backlog.md is installed (`which backlog`)
   - If not: Prompt to install (`npm i -g backlog.md` or `brew install backlog-md`)
   - Run `claude mcp add backlog --scope user -- backlog mcp start`
   - Verify MCP connection: Test `backlog_list_tasks` call
   - Document in setup guide

2. Fallback: If MCP unavailable, provide instructions for manual setup

---

### FR4: Migration and Compatibility

**FR4.1**: Migrate Existing tasks.md to Backlog.md

**Command**: `specify backlog migrate --feature <feature-id>`

**Process**:
1. Locate `/specs/<feature-id>/tasks.md`
2. Parse tasks using flowspec's task format rules
3. Generate Backlog.md tasks (same as FR1.1)
4. Create backup: `tasks.md.backup`
5. Optionally deprecate tasks.md: Add note "Tasks migrated to backlog/"
6. Generate migration report: tasks migrated, warnings, errors

**Edge Cases**:
- Manual edits in tasks.md: Preserve as notes in Backlog.md task body
- Completed tasks (checked boxes): Set status to `done`
- Tasks with comments: Migrate as task notes

---

**FR4.2**: Support Both Workflows (Transition Period)

**Requirement**: Allow users to use tasks.md OR Backlog.md for 1-2 releases during transition.

**Implementation**:
- `/flow:tasks` accepts `--format` flag: `tasks-md` (default) or `backlog-md`
- Documentation clearly states Backlog.md is recommended for new projects
- Deprecation notice in tasks.md format: "Consider migrating to Backlog.md for enhanced task management"

---

## Non-Functional Requirements

### NFR1: Performance

**NFR1.1**: Task Generation Latency
- **Requirement**: Generate tasks in <10 seconds for features with up to 200 tasks
- **Measurement**: Time from command execution to completion message
- **Rationale**: Developers expect fast feedback; 10s is acceptable for batch operation

**NFR1.2**: Board Loading Time
- **Requirement**: Backlog.md board loads in <2 seconds for 500 tasks
- **Measurement**: Time from `backlog board` command to rendered board
- **Rationale**: Dependent on Backlog.md performance; validate during feasibility spike

---

### NFR2: Scalability

**NFR2.1**: Large Feature Support
- **Requirement**: Handle features with up to 1000 tasks
- **Test**: Generate 1000 synthetic tasks, verify all operations work
- **Rationale**: Enterprise projects may have very large feature sets

**NFR2.2**: Repository Size Impact
- **Requirement**: Backlog task files should not bloat repository significantly
- **Target**: <50KB per task file, total increase <50MB for 1000 tasks
- **Rationale**: Keep Git repositories performant

---

### NFR3: Reliability

**NFR3.1**: Zero Data Loss
- **Requirement**: No task data lost during generation, migration, or regeneration
- **Implementation**: Automatic backups before destructive operations
- **Testing**: Simulate failures during migration, verify rollback works

**NFR3.2**: Conflict Detection
- **Requirement**: Detect conflicts when regenerating tasks that have been manually edited
- **Implementation**: Compare task content hashes, prompt for merge strategy
- **Testing**: Manually edit tasks, trigger regeneration, verify conflict detection

**NFR3.3**: Graceful Degradation
- **Requirement**: If Backlog.md or MCP unavailable, provide clear error messages and fallback
- **Example**: "Backlog.md not found. Install with: npm i -g backlog.md"

---

### NFR4: Usability

**NFR4.1**: Setup Time
- **Requirement**: New users complete setup in <5 minutes
- **Measurement**: Time from `specify init --with-backlog` to first generated task
- **Validation**: Usability testing with 5 users

**NFR4.2**: CLI Discoverability
- **Requirement**: All Backlog.md commands accessible via `specify backlog <command>`
- **Help Text**: `specify backlog --help` shows all available commands with examples

**NFR4.3**: Error Messages
- **Requirement**: Errors include actionable guidance, not just failure messages
- **Example**: ❌ "Task generation failed" → ✅ "spec.md not found. Create it with: /flow:specify"

---

### NFR5: Security & Privacy

**NFR5.1**: Local Data Only
- **Requirement**: All task data remains in local Git repository, no external services
- **Rationale**: Developers must trust flowspec with potentially sensitive project information
- **Verification**: Audit Backlog.md for network calls (should be zero)

**NFR5.2**: No Telemetry Without Consent
- **Requirement**: Usage analytics opt-in only
- **Implementation**: Prompt during setup: "Send anonymous usage data to improve flowspec? (yes/no)"

---

## Integration Architecture Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      flowspec Ecosystem                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │ /flow:    │───▶│ Spec Files   │───▶│ Task Generator  │  │
│  │  specify    │    │              │    │                 │  │
│  │  plan       │    │ - spec.md    │    │ Parses specs    │  │
│  │  research   │    │ - plan.md    │    │ Creates tasks   │  │
│  └─────────────┘    │ - data-      │    │ Maps metadata   │  │
│                     │   model.md   │    └────────┬────────┘  │
│                     └──────────────┘             │            │
│                                                  │            │
│                                                  ▼            │
│                     ┌─────────────────────────────────────┐  │
│                     │  Backlog.md Task Generator          │  │
│                     │                                     │  │
│                     │  - Map TaskID → task-<id>           │  │
│                     │  - Map [P] → labels: parallelizable │  │
│                     │  - Map [US*] → labels: US1, US2     │  │
│                     │  - Build dependency graph           │  │
│                     │  - Write task-*.md files            │  │
│                     └─────────────┬───────────────────────┘  │
│                                   │                          │
│                                   ▼                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Backlog.md Storage Layer                    │   │
│  │                                                      │   │
│  │  backlog/                                            │   │
│  │  ├── config.yml                                      │   │
│  │  ├── task-001 - Create project structure.md         │   │
│  │  ├── task-002 - Initialize Python project.md        │   │
│  │  ├── task-012 - Create User model.md                │   │
│  │  └── ...                                             │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        Backlog.md Task Management Layer             │   │
│  │                                                      │   │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────┐ │   │
│  │  │ CLI Commands │  │   Web UI      │  │ MCP API  │ │   │
│  │  │              │  │               │  │          │ │   │
│  │  │ - board      │  │ - Kanban view │  │ - create │ │   │
│  │  │ - browser    │  │ - Drag & drop │  │ - update │ │   │
│  │  │ - search     │  │ - Filtering   │  │ - get    │ │   │
│  │  └──────────────┘  └───────────────┘  └─────┬────┘ │   │
│  └─────────────────────────────────────────────┼──────┘   │
│                                                 │          │
└─────────────────────────────────────────────────┼──────────┘
                                                  │
                                                  ▼
                         ┌────────────────────────────────────┐
                         │   Claude Code / AI Assistants      │
                         │                                    │
                         │   - Read tasks via MCP             │
                         │   - Update task status             │
                         │   - Create subtasks                │
                         │   - Complete tasks automatically   │
                         └────────────────────────────────────┘
```

### Data Flow

**Flow 1: Task Generation (Spec → Backlog.md)**

```
1. User runs: /flow:tasks --feature 001-auth

2. flowspec Task Generator:
   a. Read /specs/001-auth/spec.md
   b. Read /specs/001-auth/plan.md
   c. Parse user stories (US1, US2, US3)
   d. Parse task list from tasks.md template

3. Backlog.md Generator Module:
   a. For each task in tasks.md:
      - Parse: "- [ ] T012 [P] [US1] Create User model in src/models/user.py"
      - Extract: id=012, parallel=true, story=US1, desc="Create User model..."
      - Create file: backlog/task-012 - Create User model.md
      - Write frontmatter:
        ```yaml
        status: todo
        labels: [US1, parallelizable, implementation]
        priority: high
        dependencies: [task-005]
        ```
      - Write body: description + file path + acceptance criteria

4. Output:
   - backlog/ directory with N task files
   - Summary: "Generated 42 tasks across 3 user stories"
```

**Flow 2: Task Execution (AI Assistant)**

```
1. User: "Claude, complete task-012"

2. Claude Code:
   a. Via MCP: Call backlog_get_task(id=012)
   b. Backlog.md MCP Server returns task details
   c. Claude reads task description, identifies file: src/models/user.py
   d. Claude implements the User model
   e. Via MCP: Call backlog_update_task(id=012, status=done)
   f. Backlog.md MCP Server updates task file

3. Developer runs: backlog board
   - See task-012 moved to "Done" column
```

**Flow 3: Migration (tasks.md → Backlog.md)**

```
1. User runs: specify backlog migrate --feature 001-auth

2. Migration Module:
   a. Read /specs/001-auth/tasks.md
   b. Parse all tasks (same as generation flow)
   c. Check for completed tasks (checked boxes): map to status=done
   d. Backup: Create tasks.md.backup
   e. Generate Backlog.md tasks
   f. Add deprecation note to tasks.md

3. Output:
   - backlog/ directory with migrated tasks
   - tasks.md.backup
   - Migration report: "Migrated 42 tasks, 12 already completed"
```

### Component Responsibilities

| Component | Responsibilities | Dependencies |
|-----------|-----------------|--------------|
| **Task Generator** | - Parse spec.md, plan.md<br>- Generate task list<br>- Organize by user stories | - Python pathlib<br>- YAML parser<br>- Markdown parser |
| **Backlog.md Adapter** | - Map flowspec format → Backlog.md format<br>- Write task-*.md files<br>- Build dependency graph | - Task Generator output<br>- Backlog.md file format spec |
| **CLI Commands** | - User-facing commands (`specify backlog ...`)<br>- Wrapper for Backlog.md CLI<br>- Error handling | - Backlog.md CLI installed<br>- subprocess module |
| **Migration Module** | - Parse existing tasks.md<br>- Detect completed tasks<br>- Generate Backlog.md tasks<br>- Create backups | - Task Generator<br>- Backlog.md Adapter |
| **MCP Integration** | - Configure MCP server during setup<br>- Verify MCP connection<br>- Document AI workflows | - Claude Code<br>- Backlog.md MCP server |

### Storage Strategy

**Decision: Backlog.md as Source of Truth (Post-Generation)**

**Rationale**:
- Tasks generated once from specs
- Developers update tasks via Backlog.md (status, assignees, notes)
- tasks.md becomes optional blueprint/reference
- Regeneration is opt-in with conflict detection

**Directory Structure**:

```
my-project/
├── .specify/
│   └── templates/
│       └── tasks-template.md
├── specs/
│   └── 001-auth-feature/
│       ├── spec.md
│       ├── plan.md
│       ├── data-model.md
│       └── tasks.md (optional reference, deprecated)
├── backlog/
│   ├── config.yml
│   ├── task-001 - Create project structure.md
│   ├── task-002 - Initialize Python project.md
│   ├── task-012 - Create User model.md
│   └── ...
└── src/
    └── (implementation files)
```

**Data Persistence**:
- All task data in `backlog/*.md` files (Git-tracked)
- No database, no external services
- Editable by humans and AI assistants
- Diffable, reviewable in PRs

---

## Task Breakdown for /speckit.tasks

### Phase 1: Setup and Prerequisites

**Purpose**: Install dependencies and prepare project for integration

- [ ] T001 Install Backlog.md CLI and verify installation (`backlog --version`)
- [ ] T002 [P] Research Backlog.md file format and API
- [ ] T003 [P] Document Backlog.md MCP tools available
- [ ] T004 Create integration module structure: `src/specify_cli/backlog/`
- [ ] T005 [P] Add Backlog.md documentation to flowspec docs

**Checkpoint**: Development environment ready for integration work

---

### Phase 2: Foundational (Blocking Prerequisites for All User Stories)

**Purpose**: Core infrastructure that all user stories depend on

- [ ] T006 Implement task parser for flowspec format in `src/specify_cli/backlog/parser.py`
- [ ] T007 [P] Implement Backlog.md file writer in `src/specify_cli/backlog/writer.py`
- [ ] T008 [P] Create dependency graph builder in `src/specify_cli/backlog/dependencies.py`
- [ ] T009 Implement task format mapper (flowspec → Backlog.md) in `src/specify_cli/backlog/mapper.py`
- [ ] T010 Create Backlog.md config.yml generator in `src/specify_cli/backlog/config.py`

**Checkpoint**: Core utilities ready for task generation

---

### Phase 3: User Story 1 - Generate Backlog.md Tasks from Specs (Priority: P0) 🎯 MVP

**Goal**: Enable developers to generate Backlog.md tasks from spec.md and plan.md files

**Independent Test**:
1. Create a sample spec.md with 3 user stories
2. Run `specify tasks generate --format backlog-md`
3. Verify `backlog/` directory created with correct task files
4. Verify task metadata (labels, dependencies, priorities) correct
5. Run `backlog board` and see tasks organized by user story

#### Implementation for User Story 1

- [ ] T011 [P] [US1] Implement `specify tasks generate --format backlog-md` command in `src/specify_cli/cli.py`
- [ ] T012 [US1] Integrate task parser with spec.md reader
- [ ] T013 [US1] Generate Backlog.md task files from parsed tasks using writer
- [ ] T014 [US1] Map user story labels (US1, US2) to Backlog.md labels
- [ ] T015 [US1] Map [P] markers to "parallelizable" label
- [ ] T016 [US1] Build and write task dependencies based on phases
- [ ] T017 [US1] Generate summary output: "Generated X tasks across Y user stories"
- [ ] T018 [US1] Add error handling: missing spec.md, invalid task format

**Checkpoint**: Can generate Backlog.md tasks from specs

---

### Phase 4: User Story 2 - CLI Commands for Backlog.md Management (Priority: P1)

**Goal**: Provide convenient CLI commands to interact with Backlog.md

**Independent Test**:
1. Run `specify backlog board` and verify Kanban board appears
2. Run `specify backlog status` and see task summary
3. Verify commands are wrappers for Backlog.md CLI

#### Implementation for User Story 2

- [ ] T019 [P] [US2] Implement `specify backlog init` command in `src/specify_cli/backlog/cli.py`
- [ ] T020 [P] [US2] Implement `specify backlog board` wrapper command
- [ ] T021 [P] [US2] Implement `specify backlog browser` wrapper command
- [ ] T022 [P] [US2] Implement `specify backlog status` command with summary stats
- [ ] T023 [US2] Add help text and examples to all backlog commands
- [ ] T024 [US2] Verify Backlog.md installed before running commands, provide install instructions if missing

**Checkpoint**: Developers can manage Backlog.md tasks via flowspec CLI

---

### Phase 5: User Story 3 - Migration from tasks.md to Backlog.md (Priority: P1)

**Goal**: Enable users with existing tasks.md files to migrate to Backlog.md format

**Independent Test**:
1. Create sample tasks.md with 20 tasks (some checked, some unchecked)
2. Run `specify backlog migrate --feature 001-auth`
3. Verify Backlog.md tasks created correctly
4. Verify completed tasks have status=done
5. Verify backup created: tasks.md.backup

#### Implementation for User Story 3

- [ ] T025 [US3] Implement migration parser for existing tasks.md in `src/specify_cli/backlog/migration.py`
- [ ] T026 [US3] Detect completed tasks (checked boxes) and map to status=done
- [ ] T027 [US3] Implement `specify backlog migrate --feature <id>` command
- [ ] T028 [US3] Create backup mechanism: tasks.md.backup before migration
- [ ] T029 [US3] Generate migration report: tasks migrated, completed, warnings
- [ ] T030 [US3] Add deprecation note to migrated tasks.md file

**Checkpoint**: Existing flowspec projects can migrate to Backlog.md

---

### Phase 6: User Story 4 - MCP Integration Setup (Priority: P2)

**Goal**: Automate MCP server configuration for Claude Code integration

**Independent Test**:
1. Run `specify init --with-backlog`
2. Verify Backlog.md MCP server configured
3. Test Claude Code command: "List all tasks"
4. Verify Claude can read tasks via MCP

#### Implementation for User Story 4

- [ ] T031 [US4] Add `--with-backlog` flag to `specify init` command
- [ ] T032 [US4] Implement Backlog.md installation check in `src/specify_cli/backlog/setup.py`
- [ ] T033 [US4] Implement MCP server configuration: `claude mcp add backlog` in setup
- [ ] T034 [US4] Verify MCP connection with test command: `backlog_list_tasks`
- [ ] T035 [US4] Create troubleshooting guide for MCP setup issues
- [ ] T036 [US4] Document AI workflows in `docs/backlog-md-ai-integration.md`

**Checkpoint**: Claude Code can interact with Backlog.md tasks via MCP

---

### Phase 7: User Story 5 - Conflict Detection and Regeneration (Priority: P2)

**Goal**: Allow users to regenerate tasks from updated specs with conflict detection

**Independent Test**:
1. Generate tasks from spec
2. Manually edit a task in Backlog.md (change status, add notes)
3. Update spec and run `specify tasks regenerate`
4. Verify conflict detected and merge options presented

#### Implementation for User Story 5

- [ ] T037 [US5] Implement task content hashing for change detection in `src/specify_cli/backlog/diff.py`
- [ ] T038 [US5] Implement `specify tasks regenerate` command with conflict detection
- [ ] T039 [US5] Create merge strategies: overwrite, keep manual changes, manual merge
- [ ] T040 [US5] Implement backup before regeneration
- [ ] T041 [US5] Create conflict resolution UI (CLI prompts)

**Checkpoint**: Developers can safely regenerate tasks after spec updates

---

### Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and documentation

- [ ] T042 [P] Write comprehensive integration guide in `docs/backlog-md-integration.md`
- [ ] T043 [P] Create video tutorial: Spec → Tasks → AI Execution
- [ ] T044 [P] Add integration tests: end-to-end task generation and migration
- [ ] T045 Update README with Backlog.md integration announcement
- [ ] T046 [P] Add telemetry (opt-in): track adoption rate and task generation success
- [ ] T047 Create migration guide for existing users
- [ ] T048 Add to CHANGELOG and prepare release notes

**Checkpoint**: Integration ready for release

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Task Generation) → MUST complete first (MVP)
  - US2 (CLI Commands) → Can run in parallel with US3
  - US3 (Migration) → Can run in parallel with US2
  - US4 (MCP Setup) → Depends on US1 (needs tasks to test)
  - US5 (Regeneration) → Depends on US1 (needs generation logic)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P0)**: No dependencies on other stories - MVP foundation
- **US2 (P1)**: Independent, can run parallel to US3
- **US3 (P1)**: Independent, can run parallel to US2
- **US4 (P2)**: Depends on US1 (needs task generation working)
- **US5 (P2)**: Depends on US1 (needs generation logic to extend)

### Parallel Opportunities

- Phase 1: T002, T003, T005 (research and docs) can run in parallel
- Phase 2: T007, T008 (writer, dependencies) can run in parallel after T006
- US1: T011 (CLI command) can run in parallel with T014, T015 (mapping logic)
- US2: All CLI wrapper commands (T019-T021) can run in parallel
- US3: T025 (parser) can run in parallel with T028 (backup mechanism)

---

## Discovery and Validation Plan

### Sprint 0: Fast Validation (Week 1-2)

**Learning Goals**:
1. Will developers adopt Backlog.md integration?
2. Is the task generation accurate and useful?
3. Can we technically integrate Backlog.md with flowspec reliably?
4. Is MCP integration with Claude Code stable?

**Experiments**:

| Day | Experiment | Method | Success Criteria |
|-----|-----------|--------|-----------------|
| 1-2 | **Concierge Test** | Manually set up Backlog.md for 3 pilot users (Discord/GitHub) | 2/3 users find it valuable, continue using |
| 3 | **Technical Spike** | Build prototype: tasks.md → Backlog.md generation | Successfully generate 50 tasks with correct metadata |
| 4 | **MCP Feasibility** | Test Backlog.md MCP with Claude Code | Claude can create, update, complete tasks |
| 5-7 | **Usability Test** | 5 new users attempt setup and task generation | 4/5 complete without help in <10 minutes |
| 8-10 | **Customer Interviews** | Interview 10 flowspec users about task management pain | 7/10 express strong interest in integration |

**Go/No-Go Decision**:
- **GO** if: 2/3 concierge users adopt, technical spike succeeds, 4/5 usability tests pass
- **NO-GO** if: Users don't see value, MCP integration unstable, >50% usability failures

---

### Sprint 1-2: MVP Development (Week 3-6)

**Goal**: Build and ship US1 (Task Generation) as MVP

**Validation Checkpoints**:

| Week | Milestone | Validation |
|------|-----------|-----------|
| 3 | T006-T010 (Foundational) complete | Unit tests pass, can parse tasks.md correctly |
| 4 | T011-T014 (Core generation) complete | Generate Backlog.md tasks from real spec, manual review |
| 5 | T015-T018 (Metadata & errors) complete | Test with 3 real flowspec projects, verify accuracy |
| 6 | US1 complete | Beta release to 10 pilot users, gather feedback |

**Success Metrics**:
- 95%+ task generation accuracy (manual verification)
- <5 minutes setup time (pilot user measurement)
- 8/10 pilot users rate MVP as "valuable" (4+/5)

---

### Sprint 3-4: Iteration and Feature Expansion (Week 7-10)

**Goal**: Add US2 (CLI), US3 (Migration), US4 (MCP Setup)

**Validation Checkpoints**:

| Week | Milestone | Validation |
|------|-----------|-----------|
| 7 | US2 (CLI) complete | Test all commands with pilot users |
| 8 | US3 (Migration) complete | Migrate 5 existing projects, verify no data loss |
| 9 | US4 (MCP) complete | Test Claude Code integration with 3 users |
| 10 | Feature-complete beta | Beta test with 50 users, NPS survey |

**Success Metrics**:
- Zero data loss during migration (verified with 5 projects)
- MCP works on 90%+ of machines (Claude Code with Backlog.md)
- NPS >40 from beta users

---

### Sprint 5: Polish and Release (Week 11-12)

**Goal**: US5 (Regeneration) + documentation + public launch

**Validation Checkpoints**:

| Week | Milestone | Validation |
|------|-----------|-----------|
| 11 | US5 (Regeneration) + docs complete | Test conflict detection with 10 scenarios |
| 12 | Public release | Monitor GitHub issues, usage analytics |

**Success Metrics**:
- Conflict detection catches 100% of manual edits (tested scenarios)
- <10 GitHub issues in first week post-launch
- 100+ new installations in first month

---

## Acceptance Criteria and Testing

### User Story 1: Task Generation

**Given** a valid specification with 3 user stories (US1, US2, US3) and a plan
**When** the developer runs `specify tasks generate --format backlog-md`
**Then** the system should:
- ✅ Create `backlog/` directory with config.yml
- ✅ Generate one task file per task: `task-<id> - <title>.md`
- ✅ Set correct status: `todo` for all new tasks
- ✅ Apply user story labels: `labels: [US1]`, `labels: [US2]`, etc.
- ✅ Apply parallelizable label for tasks marked [P]
- ✅ Set priorities: high for setup/foundational, medium/low based on P1/P2/P3
- ✅ Build dependencies: Foundational blocks User Stories
- ✅ Include file paths in task descriptions
- ✅ Output summary: "Generated 42 tasks across 3 user stories"

**Edge Case Testing**:
- ❌ Missing spec.md → Error: "spec.md not found. Run /flow:specify first"
- ❌ Invalid task format → Error with line number
- ❌ Existing backlog/ → Prompt: "Regenerate? (yes/no/merge)"
- ✅ Large spec (200 tasks) → Complete in <10 seconds

---

### User Story 2: CLI Commands

**Given** Backlog.md is installed and tasks are generated
**When** the developer runs `specify backlog board`
**Then** the system should:
- ✅ Display Kanban board with columns: Todo, In Progress, Done
- ✅ Show all tasks organized by status
- ✅ Support filtering: `specify backlog board --filter US1`

**When** the developer runs `specify backlog status`
**Then** the system should:
- ✅ Show summary: "42 tasks total, 5 done, 3 in progress, 34 todo"
- ✅ Show breakdown by user story

**Edge Case Testing**:
- ❌ Backlog.md not installed → Error: "Install with: npm i -g backlog.md"
- ❌ No tasks → "No tasks found. Run: specify tasks generate"

---

### User Story 3: Migration

**Given** an existing project with `/specs/001-auth/tasks.md` containing 20 tasks (12 unchecked, 8 checked)
**When** the developer runs `specify backlog migrate --feature 001-auth`
**Then** the system should:
- ✅ Parse all 20 tasks correctly
- ✅ Create 20 Backlog.md task files
- ✅ Set status=done for 8 checked tasks
- ✅ Set status=todo for 12 unchecked tasks
- ✅ Preserve all metadata (IDs, labels, descriptions)
- ✅ Create backup: `tasks.md.backup`
- ✅ Output: "Migrated 20 tasks, 8 already completed"

**Edge Case Testing**:
- ❌ tasks.md missing → Error: "No tasks.md found for feature 001-auth"
- ✅ Manual edits in tasks.md → Preserved as notes in Backlog.md
- ✅ Large tasks.md (500 tasks) → Complete in <30 seconds, no data loss

---

### User Story 4: MCP Integration

**Given** Backlog.md MCP server is configured
**When** the user asks Claude: "List all tasks for US1"
**Then** Claude should:
- ✅ Call `backlog_list_tasks` via MCP with filter: labels=US1
- ✅ Display task list with IDs and descriptions

**When** the user asks Claude: "Complete task-012"
**Then** Claude should:
- ✅ Call `backlog_get_task(id=012)` to verify task exists
- ✅ Call `backlog_update_task(id=012, status=done)`
- ✅ Confirm: "Task-012 (Create User model) marked complete"

**Edge Case Testing**:
- ❌ MCP not configured → Guide user through setup
- ❌ Task doesn't exist → "Task-999 not found"
- ✅ MCP connection lost → Graceful error, retry suggestion

---

### User Story 5: Regeneration with Conflict Detection

**Given** tasks generated from spec, then task-012 manually edited (status changed, notes added)
**When** the spec is updated and developer runs `specify tasks regenerate`
**Then** the system should:
- ✅ Detect task-012 has been manually edited (content hash changed)
- ✅ Prompt: "Conflict detected in task-012. Options: (o)verwrite, (k)eep manual changes, (m)erge manually"
- ✅ If overwrite: Replace with new content from spec
- ✅ If keep: Preserve manual changes, skip regeneration for task-012
- ✅ If merge: Show diff, allow manual resolution
- ✅ Create backup before regeneration: `backlog.backup/`

**Edge Case Testing**:
- ✅ No conflicts → Regenerate all tasks silently
- ✅ Multiple conflicts → Handle each one sequentially
- ❌ Backup fails → Abort regeneration, show error

---

### Definition of Done (Per User Story)

- [ ] All tasks in user story completed
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration test for user story complete
- [ ] Documentation updated (user guide + API reference)
- [ ] Code reviewed and approved
- [ ] Manual testing with real flowspec project
- [ ] No high/critical bugs open
- [ ] User story demo recorded (for release notes)

---

### Quality Gates

**Pre-Merge**:
- All unit tests pass
- Code coverage >80% for new code
- Linting passes (ruff check, ruff format)
- Manual smoke test successful

**Pre-Release**:
- All integration tests pass
- Beta testing with 10+ users, no blocking issues
- Documentation complete and reviewed
- Migration guide tested with 3 existing projects
- NPS from beta >40

---

### Test Coverage Requirements

| Test Type | Scope | Coverage Target |
|-----------|-------|----------------|
| **Unit Tests** | Individual functions (parser, mapper, writer) | >80% |
| **Integration Tests** | End-to-end workflows (generate, migrate, regenerate) | 100% happy paths |
| **Edge Case Tests** | Error handling, conflicts, missing files | 100% known edge cases |
| **Performance Tests** | 1000 task generation, board loading | <10s generation, <2s board |
| **Regression Tests** | Previously found bugs | 100% |

---

## Dependencies and Constraints

### Technical Dependencies

| Dependency | Version | Purpose | Risk Level |
|-----------|---------|---------|-----------|
| **Backlog.md** | Latest (>1.0) | Task management backend | HIGH - External tool |
| **Node.js/npm** | 18+ | Install Backlog.md CLI | MEDIUM - Common dependency |
| **Claude Code** | Latest | MCP integration host | MEDIUM - Some users may not use Claude |
| **MCP Protocol** | 1.0+ | AI assistant integration | MEDIUM - Relatively new standard |
| **Python** | 3.11+ | flowspec runtime | LOW - Already required |
| **YAML parser** | PyYAML | Parse/write frontmatter | LOW - Stable library |

**Mitigation Strategies**:
- **Backlog.md API changes**: Pin to specific version, test before upgrading
- **MCP instability**: Provide fallback docs for manual Backlog.md usage
- **Node.js unavailability**: Detect and guide user through installation

---

### External Dependencies

| Dependency | Owner | SLA/Support | Contingency Plan |
|-----------|-------|------------|------------------|
| **Backlog.md project** | @MrLesk (GitHub) | Community support | Fork and maintain if abandoned |
| **MCP specification** | Anthropic | Active development | Adapter layer to isolate changes |
| **Claude Code** | Anthropic | Official support | Works without Claude (manual Backlog.md) |

---

### Timeline Constraints

**No Hard Deadlines** - Feature will ship when ready, prioritizing quality over speed

**Suggested Timeline** (Based on 1 developer, part-time):
- Sprint 0 (Validation): 2 weeks
- Sprint 1-2 (MVP): 4 weeks
- Sprint 3-4 (Feature expansion): 4 weeks
- Sprint 5 (Polish): 2 weeks
- **Total**: 12 weeks (~3 months)

---

### Resource Constraints

**Development Team**: 1 developer (part-time, ~20 hours/week)
**Design/UX**: Not required (CLI-focused)
**Documentation**: Same developer (included in estimates)
**Testing**: Community beta testers (10-50 volunteers)

**Budget**: $0 (open-source project)

---

### Risk Factors

| Risk | Impact | Probability | Mitigation |
|------|--------|-----------|-----------|
| **Backlog.md breaking changes** | Critical | Medium | Pin version, monitor releases, adapter layer |
| **Low user adoption** | High | Medium | Strong MVP validation, early user feedback |
| **MCP protocol changes** | High | Low | Isolate MCP code, maintain manual fallback |
| **Performance issues at scale** | Medium | Low | Load testing, optimize before release |
| **Developer availability** | Medium | Medium | Flexible timeline, no hard deadlines |
| **Complexity creep** | Medium | High | Strict scope control, MVP-first approach |

---

## Success Metrics (Outcome-Focused)

### North Star Metric

**% of flowspec generated features actively tracked in Backlog.md**

**Definition**:
- Numerator: # of features with active `backlog/` directory and >1 task file
- Denominator: # of features generated via `/flow:tasks` in last 90 days
- **Target**: 60% within 6 months of release

**Why This Metric**:
- Directly measures integration adoption
- Indicates real usage (not just installation)
- Trackable via opt-in telemetry
- Aligns with goal: make Backlog.md the preferred task management layer

---

### Leading Indicators (Early Signals)

| Metric | Definition | Target | Timeline |
|--------|-----------|--------|---------|
| **Task Generation Success Rate** | % of `specify tasks generate` commands that complete without errors | 95%+ | Month 1 |
| **Integration Setup Time** | Median time from `specify init --with-backlog` to first task synced | <5 minutes | Month 1 |
| **Developer Adoption Rate** | % of new flowspec users who opt into Backlog.md during init | 60%+ | Month 3 |
| **MCP Connection Success** | % of setups where MCP integration works on first try | 80%+ | Month 2 |
| **Migration Success Rate** | % of `specify backlog migrate` commands that complete without data loss | 100% | Month 2 |

**Data Collection**:
- Opt-in CLI telemetry (anonymized)
- GitHub issue tracker (error reports)
- User surveys (post-setup, quarterly)

---

### Lagging Indicators (Final Outcomes)

| Metric | Definition | Target | Timeline |
|--------|-----------|--------|---------|
| **Task Completion Velocity** | Average tasks completed per week (pre vs. post integration) | +20% improvement | Month 6 |
| **Developer Satisfaction (NPS)** | Net Promoter Score for flowspec with Backlog.md | +15 points | Month 6 |
| **Context Switching Reduction** | % decrease in "used external project tool" (self-reported) | 30% fewer | Month 6 |
| **AI-Assisted Task Completion** | % of tasks completed with AI assistant help (vs. manual) | 40%+ | Month 6 |
| **Retention Rate** | % of developers still using Backlog.md integration after 3 months | 70%+ | Month 6 |

**Data Collection**:
- Quarterly user surveys (NPS, workflow questions)
- Usage analytics (task completion timestamps, AI MCP calls)
- Community feedback (Discord, GitHub discussions)

---

### Measurement Approach

**Telemetry** (Opt-In):
```python
# Example: Track task generation event
analytics.track(event="task_generation", properties={
    "feature_id": "001-auth",
    "task_count": 42,
    "user_story_count": 3,
    "format": "backlog-md",
    "duration_seconds": 3.2,
    "success": True
})
```

**Surveys** (Quarterly):
- NPS: "How likely are you to recommend flowspec with Backlog.md to a colleague?"
- Workflow: "How often do you use Backlog.md vs. external tools?"
- Satisfaction: "How satisfied are you with task generation accuracy?"

**Qualitative Feedback**:
- GitHub discussions: Feature requests, pain points
- Discord community: Usage patterns, tips, issues
- User interviews: Deep dive with 5-10 power users quarterly

---

### Target Values Summary

| Metric | 1 Month | 3 Months | 6 Months |
|--------|---------|---------|---------|
| **Adoption Rate** | 30% | 50% | 60% |
| **Generation Success** | 90% | 95% | 95% |
| **NPS Improvement** | +5 | +10 | +15 |
| **Velocity Improvement** | +5% | +15% | +20% |
| **AI-Assisted Completion** | 20% | 30% | 40% |
| **Retention (3mo)** | N/A | N/A | 70% |

---

## Conclusion and Next Steps

### Summary

This PRD outlines a strategic integration between **flowspec** (spec-driven task generation) and **Backlog.md** (AI-powered task management), creating a unified platform for modern, AI-assisted software development workflows.

**Key Design Decisions**:
1. **Hybrid Model**: flowspec generates tasks directly into Backlog.md format (no complex bidirectional sync)
2. **Backlog.md as Execution Layer**: Source of truth post-generation, managed via CLI/web UI/MCP
3. **User Story Preservation**: Labels and dependencies encode flowspec's user-story organization
4. **MVP-First Approach**: Ship US1 (Task Generation) as standalone value, iterate based on feedback

**Expected Outcomes**:
- **60% adoption rate** within 6 months
- **20% task completion velocity** improvement
- **+15 NPS points** increase
- **40% AI-assisted task completion** rate

### Immediate Next Steps

**Week 1-2** (Discovery Sprint):
1. ✅ Run concierge test with 3 pilot users
2. ✅ Build technical spike: tasks.md → Backlog.md generation
3. ✅ Test MCP integration with Claude Code
4. ✅ Conduct usability testing with 5 new users
5. ✅ Interview 10 flowspec users about task management needs

**Week 3** (Go/No-Go Decision):
- Review discovery results
- Make Go/No-Go decision based on validation criteria
- If GO: Proceed to MVP development (US1)
- If NO-GO: Document learnings, consider alternatives

**Week 4-9** (MVP Development - US1):
- Build Phase 1 (Setup) and Phase 2 (Foundational)
- Implement US1: Task Generation
- Beta release to 10 pilot users
- Gather feedback, iterate

**Week 10+** (Feature Expansion):
- US2: CLI Commands
- US3: Migration
- US4: MCP Setup
- US5: Regeneration
- Public release

---

### Open Questions for Stakeholder Review

1. **Strategic Alignment**: Does this integration align with flowspec's 5-10 year vision?
2. **Resource Commitment**: Can we commit 1 developer for 12 weeks?
3. **Dependency Risk**: Are we comfortable depending on Backlog.md (external project)?
4. **Scope Creep**: Should we limit MVP to US1 only, or include US2/US3?
5. **Pricing/Licensing**: Any concerns with Backlog.md's license (likely MIT)?

---

### Document Metadata

**Version**: 1.0 (Draft)
**Last Updated**: 2025-11-23
**Next Review**: After Discovery Sprint (Week 2)
**Approvers**: flowspec Maintainers, Community Feedback
**Status**: Awaiting Validation Experiments

---

**END OF PRD**
