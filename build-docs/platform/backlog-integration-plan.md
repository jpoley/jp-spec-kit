# JP Flowspec - Backlog

**Project:** flowspec
**Last Updated:** 2025-11-24
**Source:** [docs/copilot-next.md](docs/copilot-next.md) - Backlog.md Integration Analysis

---

## Overview

This backlog contains structured tasks for integrating Backlog.md task management into flowspec, organized by implementation phase and priority.

### Priority Legend
- **P0 - Critical**: Must be done first, blocks other work
- **P1 - High**: Important for core functionality
- **P2 - Medium**: Valuable improvement
- **P3 - Low**: Nice-to-have

### Status Legend
- **To Do**: Not started
- **In Progress**: Currently being worked on
- **Review**: Completed, pending verification
- **Done**: Completed and verified

---

## Phase 1: Foundation (P0 - Critical)

**Goal:** Replace TODO/ with backlog/, basic integration
**Estimated Effort:** 2-3 hours

### TASK-001: Install Backlog.md CLI Tool

```yaml
id: task-001
title: Install Backlog.md CLI Tool
status: To Do
priority: P0
phase: 1
labels: [setup, foundation, tooling]
dependencies: []
estimated_effort: 5 minutes
```

**Description:**
Install the backlog.md npm package globally to enable CLI-based task management.

**Acceptance Criteria:**
- [ ] Run `npm install -g backlog.md`
- [ ] Verify installation with `backlog --version` (expect 1.20.1+)
- [ ] Confirm `backlog --help` shows available commands

**Commands:**
```bash
npm install -g backlog.md
backlog --version
backlog --help
```

---

### TASK-002: Initialize Backlog.md in flowspec

```yaml
id: task-002
title: Initialize Backlog.md in flowspec
status: To Do
priority: P0
phase: 1
labels: [setup, foundation, configuration]
dependencies: [task-001]
estimated_effort: 10 minutes
```

**Description:**
Initialize backlog.md in the flowspec project with MCP integration mode for AI agent support.

**Acceptance Criteria:**
- [ ] Run `backlog init flowspec --defaults --integration-mode mcp`
- [ ] Verify `backlog/` directory created with proper structure:
  - `backlog/config.yml`
  - `backlog/tasks/`
  - `backlog/completed/`
  - `backlog/drafts/`
  - `backlog/docs/`
  - `backlog/decisions/`
- [ ] Verify config.yml has MCP integration configured

**Commands:**
```bash
cd /home/jpoley/ps/flowspec
backlog init flowspec --defaults --integration-mode mcp
ls -la backlog/
cat backlog/config.yml
```

---

### TASK-003: Configure Backlog.md Settings

```yaml
id: task-003
title: Configure Backlog.md Settings
status: To Do
priority: P0
phase: 1
labels: [setup, foundation, configuration]
dependencies: [task-002]
estimated_effort: 15 minutes
```

**Description:**
Customize backlog/config.yml with flowspec specific settings, statuses, and labels.

**Acceptance Criteria:**
- [ ] Add custom statuses: `["To Do", "In Progress", "Review", "Blocked", "Done"]`
- [ ] Add flowspec labels: `["foundation", "slash-commands", "agents", "documentation", "ci-cd", "infrastructure"]`
- [ ] Add milestones: `["Phase 1: Foundation", "Phase 2: Slash Commands", "Phase 3: Agents", "Phase 4: Docs", "Phase 5: CI/CD", "Phase 6: Polish"]`
- [ ] Set appropriate defaults for the project

**Implementation:**
Edit `backlog/config.yml`:
```yaml
project_name: "flowspec"
default_status: "To Do"
statuses: ["To Do", "In Progress", "Review", "Blocked", "Done"]
labels: ["foundation", "slash-commands", "agents", "documentation", "ci-cd", "infrastructure", "mcp", "testing"]
milestones: ["Phase 1: Foundation", "Phase 2: Slash Commands", "Phase 3: Agents", "Phase 4: Docs", "Phase 5: CI/CD", "Phase 6: Polish"]
date_format: yyyy-mm-dd
max_column_width: 25
auto_open_browser: true
default_port: 6420
remote_operations: true
auto_commit: false
bypass_git_hooks: false
```

---

### TASK-004: Add Backlog MCP Server to .mcp.json

```yaml
id: task-004
title: Add Backlog MCP Server to .mcp.json
status: To Do
priority: P0
phase: 1
labels: [setup, foundation, mcp, agents]
dependencies: [task-002]
estimated_effort: 10 minutes
```

**Description:**
Add the backlog.md MCP server configuration to `.mcp.json` to enable AI agents to manage tasks programmatically.

**Acceptance Criteria:**
- [ ] Read current .mcp.json configuration
- [ ] Add backlog server entry
- [ ] Verify MCP server can start: `backlog mcp start`
- [ ] Test that Claude Code recognizes the MCP server

**Implementation:**
Add to `.mcp.json`:
```json
{
  "backlog": {
    "command": "backlog",
    "args": ["mcp", "start"],
    "description": "Task management via Backlog.md"
  }
}
```

---

### TASK-005: Migrate Existing TODO Tasks

```yaml
id: task-005
title: Migrate Existing TODO Tasks to Backlog
status: To Do
priority: P0
phase: 1
labels: [foundation, migration, data]
dependencies: [task-002, task-003]
estimated_effort: 45 minutes
```

**Description:**
Migrate existing tasks from the ad-hoc `TODO/` directory to structured `backlog/tasks/` format.

**Acceptance Criteria:**
- [ ] Audit existing TODO/ files (active and completed)
- [ ] Create migration script or manually migrate:
  - TODO/task-015-summary.md
  - TODO/task-009-suggestions.md
  - TODO/task-012a-summary.md
  - TODO/task-012b-summary.md
  - TODO/task-013-response.md
  - TODO/task-014-summary.md
  - TODO/task-20-suggestions.md
- [ ] Verify migrated tasks have proper YAML frontmatter
- [ ] Verify tasks appear in `backlog task list`
- [ ] Move completed TODO/ tasks to backlog/completed/

**Commands:**
```bash
# For each task to migrate:
backlog task create "Task title from TODO file" \
    --description "Description from TODO file" \
    --priority medium \
    --labels "migrated,foundation"

# Verify migration
backlog task list
backlog board
```

---

### TASK-006: Test Backlog.md CLI Commands

```yaml
id: task-006
title: Test Backlog.md CLI Commands
status: To Do
priority: P0
phase: 1
labels: [foundation, testing, validation]
dependencies: [task-005]
estimated_effort: 20 minutes
```

**Description:**
Verify all key backlog.md CLI commands work correctly in the flowspec project.

**Acceptance Criteria:**
- [ ] `backlog task list` - Lists all tasks
- [ ] `backlog board` - Shows Kanban board in terminal
- [ ] `backlog browser` - Opens web UI (port 6420)
- [ ] `backlog task edit <id> --status "In Progress"` - Updates status
- [ ] `backlog search <keyword>` - Finds tasks
- [ ] `backlog sequence` - Shows dependency chain
- [ ] `backlog overview` - Shows project metrics

**Commands:**
```bash
backlog task list
backlog board
backlog browser
backlog task edit task-1 --status "In Progress"
backlog search "foundation"
backlog sequence
backlog overview
```

---

### TASK-007: Archive Old TODO Directory

```yaml
id: task-007
title: Archive Old TODO Directory
status: To Do
priority: P0
phase: 1
labels: [foundation, cleanup, migration]
dependencies: [task-005, task-006]
estimated_effort: 10 minutes
```

**Description:**
After successful migration and verification, archive the old TODO/ directory.

**Acceptance Criteria:**
- [ ] Verify all active tasks migrated to backlog/tasks/
- [ ] Verify all completed tasks migrated to backlog/completed/
- [ ] Rename TODO/ to TODO.archived/ (preserve history)
- [ ] Add TODO.archived/ to .gitignore (optional)
- [ ] Update any documentation referencing TODO/

**Commands:**
```bash
# After verification
mv TODO TODO.archived
echo "# TODO.archived/" >> .gitignore  # Optional
```

---

## Phase 2: Slash Command Integration (P1 - High)

**Goal:** Integrate backlog.md with /flowspec commands
**Estimated Effort:** 4-6 hours

### TASK-008: Update /flow:specify for Task Creation

```yaml
id: task-008
title: Update /flow:specify for Task Creation
status: To Do
priority: P1
phase: 2
labels: [slash-commands, specify, integration]
dependencies: [task-006]
estimated_effort: 45 minutes
```

**Description:**
Modify the `/flow:specify` slash command to automatically create Backlog.md tasks from the PRD task breakdown.

**Acceptance Criteria:**
- [ ] Read current `.claude/commands/flow/specify.md`
- [ ] Add section for task creation after PRD approval
- [ ] Include task creation commands with:
  - Title from PRD task breakdown
  - Priority based on DVF+V risk assessment
  - Assignee based on specialist type
  - Labels from feature category
  - Description from PRD
- [ ] Test with sample specification

**File:** `.claude/commands/flow/specify.md`

**Implementation Notes:**
Add to end of specify.md:
```markdown
## Task Creation

After PRD approval, create tasks in Backlog.md:

```bash
# For each task in PRD task breakdown:
backlog task create "$TASK_TITLE" \
    --description "$DESCRIPTION" \
    --priority "$PRIORITY_FROM_DVFV" \
    --assignee "$SPECIALIST" \
    --labels "$CATEGORY" \
    --status "To Do"
```
```

---

### TASK-009: Update /flow:plan for Dependency Setting

```yaml
id: task-009
title: Update /flow:plan for Dependency Setting
status: To Do
priority: P1
phase: 2
labels: [slash-commands, plan, integration]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Modify the `/flow:plan` slash command to update task dependencies based on architectural design.

**Acceptance Criteria:**
- [ ] Read current `.claude/commands/flow/plan.md`
- [ ] Add section for updating task dependencies
- [ ] Include dependency commands
- [ ] Include sequence verification
- [ ] Test with sample architecture plan

**File:** `.claude/commands/flow/plan.md`

**Implementation Notes:**
Add to end of plan.md:
```markdown
## Task Dependencies

Update Backlog.md tasks with dependencies:

```bash
# For each dependency relationship identified:
backlog task edit task-X --dependencies task-Y,task-Z

# Verify dependency chain:
backlog sequence
```
```

---

### TASK-010: Update /flow:implement for Progress Tracking

```yaml
id: task-010
title: Update /flow:implement for Progress Tracking
status: To Do
priority: P1
phase: 2
labels: [slash-commands, implement, integration]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Modify the `/flow:implement` slash command to track implementation progress in Backlog.md.

**Acceptance Criteria:**
- [ ] Read current `.claude/commands/flow/implement.md`
- [ ] Add section for progress tracking
- [ ] Include status update commands for:
  - Starting work ("In Progress")
  - Adding progress notes
  - Moving to review
  - Completing task
- [ ] Test with sample implementation

**File:** `.claude/commands/flow/implement.md`

**Implementation Notes:**
Add to implement.md:
```markdown
## Progress Tracking

Update task status as you work:

```bash
# Start work
backlog task edit $TASK_ID --status "In Progress"

# Add progress notes
backlog task edit $TASK_ID --note "Implemented core functionality"

# Move to review
backlog task edit $TASK_ID --status "Review" --note "PR #123 created"

# Mark complete
backlog task edit $TASK_ID --status "Done" --note "Merged to main"
```
```

---

### TASK-011: Update /flow:validate for Completion Tracking

```yaml
id: task-011
title: Update /flow:validate for Completion Tracking
status: To Do
priority: P1
phase: 2
labels: [slash-commands, validate, integration]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Modify the `/flow:validate` slash command to mark tasks complete when validation passes.

**Acceptance Criteria:**
- [ ] Read current `.claude/commands/flow/validate.md`
- [ ] Add section for completion tracking
- [ ] Include task completion commands
- [ ] Include overview command for status
- [ ] Test with sample validation

**File:** `.claude/commands/flow/validate.md`

**Implementation Notes:**
Add to validate.md:
```markdown
## Completion Tracking

After successful validation:

```bash
# Mark tasks complete
backlog task edit $TASK_ID --status "Done" --note "All tests passed"

# View completion status
backlog overview
```
```

---

### TASK-012: Test Full flowspec Workflow Integration

```yaml
id: task-012
title: Test Full flowspec Workflow Integration
status: To Do
priority: P1
phase: 2
labels: [slash-commands, testing, integration]
dependencies: [task-008, task-009, task-010, task-011]
estimated_effort: 60 minutes
```

**Description:**
End-to-end test of the complete flowspec workflow with Backlog.md integration.

**Acceptance Criteria:**
- [ ] Run `/flow:specify` and verify tasks created
- [ ] Run `/flow:plan` and verify dependencies set
- [ ] Run `/flow:implement` and verify progress tracked
- [ ] Run `/flow:validate` and verify completion tracked
- [ ] Verify Kanban board shows correct status at each stage
- [ ] Document any issues found

**Test Scenario:**
```
1. /flow:specify - Create spec for "test feature"
   → Verify: Tasks created in backlog/tasks/

2. /flow:plan - Plan architecture
   → Verify: Task dependencies updated

3. /flow:implement - Implement feature
   → Verify: Status changes: To Do → In Progress → Review

4. /flow:validate - Validate implementation
   → Verify: Status changes: Review → Done

5. backlog board
   → Verify: All tasks show correct status
```

---

## Phase 3: Agent Integration (P1 - High)

**Goal:** Update agent personas with task management guidance
**Estimated Effort:** 2-3 hours

### TASK-013: Update Product Requirements Manager Agent

```yaml
id: task-013
title: Update Product Requirements Manager Agent
status: To Do
priority: P1
phase: 3
labels: [agents, prm, integration]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Add Backlog.md task management guidance to the product-requirements-manager-enhanced.md agent persona.

**Acceptance Criteria:**
- [ ] Read `.agents/product-requirements-manager-enhanced.md`
- [ ] Add "Task Management" section
- [ ] Include task creation process guidance
- [ ] Include MCP integration instructions
- [ ] Document priority mapping from DVF+V

**File:** `.agents/product-requirements-manager-enhanced.md`

---

### TASK-014: Update Software Architect Agent

```yaml
id: task-014
title: Update Software Architect Agent
status: To Do
priority: P1
phase: 3
labels: [agents, architect, integration]
dependencies: [task-006]
estimated_effort: 20 minutes
```

**Description:**
Add Backlog.md task dependency guidance to the software-architect-enhanced.md agent persona.

**Acceptance Criteria:**
- [ ] Read `.agents/software-architect-enhanced.md`
- [ ] Add "Task Dependencies" section
- [ ] Include dependency modeling guidance
- [ ] Include sequence verification

**File:** `.agents/software-architect-enhanced.md`

---

### TASK-015: Update Platform Engineer Agent

```yaml
id: task-015
title: Update Platform Engineer Agent
status: To Do
priority: P1
phase: 3
labels: [agents, platform, integration]
dependencies: [task-006]
estimated_effort: 20 minutes
```

**Description:**
Add Backlog.md infrastructure task guidance to the platform-engineer-enhanced.md agent persona.

**Acceptance Criteria:**
- [ ] Read `.agents/platform-engineer-enhanced.md`
- [ ] Add task management section for infrastructure work
- [ ] Include CI/CD task integration guidance

**File:** `.agents/platform-engineer-enhanced.md`

---

### TASK-016: Update Frontend/Backend Engineer Agents

```yaml
id: task-016
title: Update Frontend/Backend Engineer Agents
status: To Do
priority: P1
phase: 3
labels: [agents, engineers, integration]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Add Backlog.md progress tracking guidance to frontend and backend engineer agent personas.

**Acceptance Criteria:**
- [ ] Read frontend-engineer.md and backend-engineer.md
- [ ] Add "Progress Tracking" section to both
- [ ] Include status update workflow
- [ ] Include PR linking guidance

**Files:**
- `.agents/frontend-engineer.md`
- `.agents/backend-engineer.md`

---

### TASK-017: Update Quality Guardian Agent

```yaml
id: task-017
title: Update Quality Guardian Agent
status: To Do
priority: P1
phase: 3
labels: [agents, qa, integration]
dependencies: [task-006]
estimated_effort: 20 minutes
```

**Description:**
Add Backlog.md completion tracking guidance to the quality-guardian.md agent persona.

**Acceptance Criteria:**
- [ ] Read `.agents/quality-guardian.md`
- [ ] Add "Completion Tracking" section
- [ ] Include validation-to-completion workflow
- [ ] Include metrics reporting guidance

**File:** `.agents/quality-guardian.md`

---

### TASK-018: Test Agent MCP Task Management

```yaml
id: task-018
title: Test Agent MCP Task Management
status: To Do
priority: P1
phase: 3
labels: [agents, mcp, testing]
dependencies: [task-004, task-013, task-014, task-015, task-016, task-017]
estimated_effort: 45 minutes
```

**Description:**
Verify that AI agents can create and update tasks via the Backlog.md MCP integration.

**Acceptance Criteria:**
- [ ] Verify MCP server is running and accessible
- [ ] Test task creation via agent
- [ ] Test task status updates via agent
- [ ] Test task search via agent
- [ ] Document any issues or limitations

**Test Scenarios:**
```
1. Agent creates task via MCP
2. Agent reads task list via MCP
3. Agent updates task status via MCP
4. Agent searches tasks via MCP
```

---

## Phase 4: Documentation (P2 - Medium)

**Goal:** Comprehensive documentation for developers and agents
**Estimated Effort:** 3-4 hours

### TASK-019: Create Task Management Reference Guide

```yaml
id: task-019
title: Create Task Management Reference Guide
status: To Do
priority: P2
phase: 4
labels: [documentation, reference, task-management]
dependencies: [task-012]
estimated_effort: 60 minutes
```

**Description:**
Create comprehensive documentation for task management with Backlog.md in `docs/reference/task-management.md`.

**Acceptance Criteria:**
- [ ] Create `docs/reference/task-management.md`
- [ ] Include Quick Start section
- [ ] Include integration with /flowspec commands
- [ ] Include MCP integration for AI agents
- [ ] Include CLI reference
- [ ] Include troubleshooting guide

**File:** `docs/reference/task-management.md`

---

### TASK-020: Update CLAUDE.md with Backlog Commands

```yaml
id: task-020
title: Update CLAUDE.md with Backlog Commands
status: To Do
priority: P2
phase: 4
labels: [documentation, claude-md, quick-reference]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Add Backlog.md commands to CLAUDE.md for quick reference by developers and AI agents.

**Acceptance Criteria:**
- [ ] Read current CLAUDE.md
- [ ] Add "Task Management" section under "Common Commands"
- [ ] Include key backlog CLI commands
- [ ] Include MCP integration note

**File:** `CLAUDE.md`

---

### TASK-021: Update AGENTS.md with Task Section

```yaml
id: task-021
title: Update AGENTS.md with Task Section
status: To Do
priority: P2
phase: 4
labels: [documentation, agents, guidance]
dependencies: [task-018]
estimated_effort: 30 minutes
```

**Description:**
Add task management section to AGENTS.md explaining how agents should interact with Backlog.md.

**Acceptance Criteria:**
- [ ] Read current AGENTS.md
- [ ] Add "Task Management" section
- [ ] Include guidelines for task creation
- [ ] Include MCP vs CLI guidance

**File:** `AGENTS.md`

---

### TASK-022: Update Inner Loop Documentation

```yaml
id: task-022
title: Update Inner Loop Documentation
status: To Do
priority: P2
phase: 4
labels: [documentation, inner-loop, principles]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Add task management section to docs/reference/inner-loop.md explaining how Backlog.md supports inner loop development.

**Acceptance Criteria:**
- [ ] Read `docs/reference/inner-loop.md`
- [ ] Add "Task Management in Inner Loop" section
- [ ] Include draft workflow for exploration
- [ ] Include fast feedback principles

**File:** `docs/reference/inner-loop.md`

---

### TASK-023: Update Outer Loop Documentation

```yaml
id: task-023
title: Update Outer Loop Documentation
status: To Do
priority: P2
phase: 4
labels: [documentation, outer-loop, principles]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Add task management section to docs/reference/outer-loop.md explaining CI/CD task automation.

**Acceptance Criteria:**
- [ ] Read `docs/reference/outer-loop.md`
- [ ] Add "Task Management in Outer Loop" section
- [ ] Include CI/CD integration examples
- [ ] Include automation workflows

**File:** `docs/reference/outer-loop.md`

---

### TASK-024: Add Examples to README.md

```yaml
id: task-024
title: Add Examples to README.md
status: To Do
priority: P2
phase: 4
labels: [documentation, readme, examples]
dependencies: [task-019]
estimated_effort: 20 minutes
```

**Description:**
Add Backlog.md integration examples to the main README.md.

**Acceptance Criteria:**
- [ ] Read current README.md
- [ ] Add brief task management section
- [ ] Include link to full documentation
- [ ] Include quick example commands

**File:** `README.md`

---

## Phase 5: CI/CD Integration (P2 - Medium)

**Goal:** Automate task updates from CI/CD pipeline
**Estimated Effort:** 3-4 hours

### TASK-025: Add Task Status Update to CI Workflow

```yaml
id: task-025
title: Add Task Status Update to CI Workflow
status: To Do
priority: P2
phase: 5
labels: [ci-cd, automation, github-actions]
dependencies: [task-012]
estimated_effort: 45 minutes
```

**Description:**
Add task status update step to `.github/workflows/ci.yml` to automatically update tasks on PR events.

**Acceptance Criteria:**
- [ ] Read current `.github/workflows/ci.yml`
- [ ] Add job for task status updates on PR merge
- [ ] Extract task ID from PR title/branch
- [ ] Update task to "Done" status
- [ ] Test with sample PR

**File:** `.github/workflows/ci.yml`

**Implementation Notes:**
```yaml
- name: Update Task Status
  if: github.event_name == 'pull_request' && github.event.action == 'closed'
  run: |
    TASK_ID=$(echo "${{ github.event.pull_request.title }}" | grep -oP 'task-\d+')
    if [ -n "$TASK_ID" ]; then
      backlog task edit $TASK_ID --status "Done" \
          --note "Merged PR #${{ github.event.pull_request.number }}"
    fi
```

---

### TASK-026: Implement Task ID Parsing from PR

```yaml
id: task-026
title: Implement Task ID Parsing from PR
status: To Do
priority: P2
phase: 5
labels: [ci-cd, automation, parsing]
dependencies: [task-025]
estimated_effort: 30 minutes
```

**Description:**
Create robust task ID extraction from PR titles and branch names.

**Acceptance Criteria:**
- [ ] Parse task IDs from PR title (e.g., "[task-5] Feature name")
- [ ] Parse task IDs from branch name (e.g., "feature/task-5-description")
- [ ] Handle multiple task IDs
- [ ] Handle missing task IDs gracefully
- [ ] Add script to scripts/bash/

**File:** `scripts/bash/extract-task-id.sh`

---

### TASK-027: Link Tasks to Releases

```yaml
id: task-027
title: Link Tasks to Releases
status: To Do
priority: P2
phase: 5
labels: [ci-cd, releases, automation]
dependencies: [task-025]
estimated_effort: 45 minutes
```

**Description:**
Automatically link completed tasks to releases in the CI/CD pipeline.

**Acceptance Criteria:**
- [ ] On release tag, identify tasks completed since last release
- [ ] Add release note to completed tasks
- [ ] Generate release notes from task titles
- [ ] Test with sample release

---

### TASK-028: Generate Task Completion Metrics

```yaml
id: task-028
title: Generate Task Completion Metrics
status: To Do
priority: P2
phase: 5
labels: [ci-cd, metrics, dora]
dependencies: [task-025]
estimated_effort: 30 minutes
```

**Description:**
Generate task completion metrics for tracking development velocity.

**Acceptance Criteria:**
- [ ] Count tasks completed per period
- [ ] Track average task duration
- [ ] Track task throughput
- [ ] Output metrics in CI logs or artifact

---

## Phase 6: Polish & Optimization (P3 - Low)

**Goal:** Additional improvements and refinements
**Estimated Effort:** 2-3 hours

### TASK-029: Add Pre-commit Hook for Task Validation

```yaml
id: task-029
title: Add Pre-commit Hook for Task Validation
status: To Do
priority: P3
phase: 6
labels: [infrastructure, validation, hooks]
dependencies: [task-006]
estimated_effort: 20 minutes
```

**Description:**
Create pre-commit hook to validate Backlog.md task files before commit.

**Acceptance Criteria:**
- [ ] Create `.git/hooks/pre-commit` script
- [ ] Validate task file formats
- [ ] Check for broken dependencies
- [ ] Allow bypass with `--no-verify`

**File:** `.git/hooks/pre-commit`

---

### TASK-030: Create Task Templates

```yaml
id: task-030
title: Create Task Templates
status: To Do
priority: P3
phase: 6
labels: [infrastructure, templates, productivity]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Create task templates for common task types in flowspec.

**Acceptance Criteria:**
- [ ] Feature task template
- [ ] Bug fix task template
- [ ] Documentation task template
- [ ] Infrastructure task template
- [ ] Add templates to backlog/docs/ or similar

---

### TASK-031: Add Shell Completion Scripts

```yaml
id: task-031
title: Add Shell Completion Scripts
status: To Do
priority: P3
phase: 6
labels: [infrastructure, productivity, shell]
dependencies: [task-001]
estimated_effort: 15 minutes
```

**Description:**
Configure shell completion for the backlog CLI for improved productivity.

**Acceptance Criteria:**
- [ ] Run `backlog completion` for zsh
- [ ] Add to ~/.zshrc or project script
- [ ] Verify tab completion works

**Commands:**
```bash
backlog completion zsh >> ~/.zshrc
source ~/.zshrc
```

---

### TASK-032: Customize Labels and Milestones

```yaml
id: task-032
title: Customize Labels and Milestones
status: To Do
priority: P3
phase: 6
labels: [infrastructure, configuration]
dependencies: [task-003]
estimated_effort: 20 minutes
```

**Description:**
Fine-tune labels and milestones based on flowspec workflow needs.

**Acceptance Criteria:**
- [ ] Review label usage after initial implementation
- [ ] Add/remove labels as needed
- [ ] Update milestone definitions
- [ ] Document label conventions

---

### TASK-033: Team Collaboration Features

```yaml
id: task-033
title: Team Collaboration Features
status: To Do
priority: P3
phase: 6
labels: [infrastructure, collaboration]
dependencies: [task-006]
estimated_effort: 30 minutes
```

**Description:**
Configure team collaboration features for multi-developer workflows.

**Acceptance Criteria:**
- [ ] Define assignee conventions
- [ ] Configure notification preferences (if available)
- [ ] Document collaboration workflow
- [ ] Test multi-assignee scenarios

---

## Summary

### Task Count by Phase

| Phase | Priority | Tasks | Status |
|-------|----------|-------|--------|
| Phase 1: Foundation | P0 | 7 | To Do |
| Phase 2: Slash Commands | P1 | 5 | To Do |
| Phase 3: Agent Integration | P1 | 6 | To Do |
| Phase 4: Documentation | P2 | 6 | To Do |
| Phase 5: CI/CD | P2 | 4 | To Do |
| Phase 6: Polish | P3 | 5 | To Do |
| **Total** | | **33** | |

### Estimated Total Effort

| Phase | Effort |
|-------|--------|
| Phase 1 | 2-3 hours |
| Phase 2 | 4-6 hours |
| Phase 3 | 2-3 hours |
| Phase 4 | 3-4 hours |
| Phase 5 | 3-4 hours |
| Phase 6 | 2-3 hours |
| **Total** | **16-23 hours** |

### Dependency Graph (Critical Path)

```
TASK-001 (Install)
    └── TASK-002 (Initialize)
            ├── TASK-003 (Configure)
            │       └── TASK-005 (Migrate)
            │               └── TASK-006 (Test CLI)
            │                       └── TASK-007 (Archive TODO)
            │                       └── TASK-008...011 (Slash Commands)
            │                               └── TASK-012 (Test Workflow)
            │                                       └── TASK-019...024 (Documentation)
            │                                       └── TASK-025...028 (CI/CD)
            │                       └── TASK-013...017 (Agents)
            │                               └── TASK-018 (Test MCP)
            └── TASK-004 (MCP Config)
                    └── TASK-018 (Test MCP)
```

---

**Document Status:** Ready for Implementation
**Created:** 2025-11-24
**Source:** [docs/copilot-next.md](docs/copilot-next.md)
