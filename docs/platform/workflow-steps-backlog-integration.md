# Platform Integration: Workflow Steps in Backlog.md TUI

**Document Type**: Platform Engineering Design
**Author**: Principal Platform Engineer Agent
**Date**: 2025-11-30
**Status**: Design Proposal
**Related Tasks**: task-095, task-096

---

## Executive Summary

This document provides a comprehensive platform engineering design for integrating JPSpec workflow steps into the backlog.md task management system, transforming it from a simple Kanban board into a workflow-aware development platform.

### Key Objectives

1. **Enhanced Visibility**: Surface workflow progress directly in task management UI
2. **State Synchronization**: Keep backlog status and workflow state aligned
3. **Developer Experience**: Minimize cognitive load when tracking feature progress
4. **DORA Metrics**: Enable measurement of deployment frequency and lead time
5. **Backward Compatibility**: Support projects without workflow configuration

### Decision Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Display Model** | Workflow metadata on task cards | Preserves existing Kanban layout, adds contextual information |
| **Configuration** | Automatic sync from `jpspec_workflow.yml` | Single source of truth, zero manual configuration |
| **CLI Integration** | Read-only workflow display | Workflow transitions via `/jpspec:*` commands only |
| **State Mapping** | Direct mapping: status = workflow state | Simplifies mental model, enforces workflow constraints |
| **Board Columns** | Dynamically generated from workflow states | Flexible, project-specific, scales beyond "To Do / In Progress / Done" |

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [DORA Impact Analysis](#dora-impact-analysis)
3. [CLI/TUI Design](#clitui-design)
4. [Integration Architecture](#integration-architecture)
5. [Developer Experience](#developer-experience)
6. [Configuration Management](#configuration-management)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Platform Principles for Constitution](#platform-principles-for-constitution)
9. [Migration and Compatibility](#migration-and-compatibility)
10. [Metrics and Observability](#metrics-and-observability)

---

## Architecture Overview

### Current State Analysis

**Backlog.md Current Capabilities:**
- Kanban board TUI: `backlog board` (ASCII columns)
- Web UI: `backlog browser` (drag-and-drop)
- Task metadata: status, labels, priority, acceptance criteria, notes
- Custom statuses via `backlog/config.yml`
- Filtering by status, label, assignee
- MCP integration for AI-powered task management

**JPSpec Workflow System:**
- 9 states: To Do → Assessed → Specified → Researched → Planned → In Implementation → Validated → Deployed → Done
- 7 workflow commands: `/jpspec:assess`, `/jpspec:specify`, `/jpspec:research`, `/jpspec:plan`, `/jpspec:implement`, `/jpspec:validate`, `/jpspec:operate`
- Configuration in `jpspec_workflow.yml` (or future location TBD)
- Artifact-driven transitions with validation modes

**Integration Gap:**
- No visual representation of workflow progress in backlog UI
- Status field doesn't reflect workflow states
- No enforcement of workflow constraints in task management
- Manual synchronization required between workflow and task status

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Workflow-Aware Backlog System                    │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│ jpspec_workflow.yml  │ ← Single source of truth
│                      │
│ states:              │
│   - Assessed         │
│   - Specified        │
│   - Planned          │
│   - ...              │
└──────────┬───────────┘
           │
           │ (read at runtime)
           ▼
┌──────────────────────────────────────────────────────────────┐
│              Backlog Configuration Sync                       │
│  • Reads workflow states from jpspec_workflow.yml            │
│  • Updates backlog/config.yml with workflow states           │
│  • Validates state transitions                               │
│  • Enforces workflow constraints                             │
└──────────┬───────────────────────────────────────────────────┘
           │
           │ (generates)
           ▼
┌──────────────────────────────────────────────────────────────┐
│              backlog/config.yml                               │
│                                                               │
│  statuses: ["To Do", "Assessed", "Specified", "Researched",  │
│             "Planned", "In Implementation", "Validated",      │
│             "Deployed", "Done"]                               │
│  workflow_enabled: true                                       │
│  workflow_source: "memory/jpspec_workflow.yml"               │
└──────────┬───────────────────────────────────────────────────┘
           │
           │ (consumed by)
           ▼
┌──────────────────────────────────────────────────────────────┐
│                    Backlog Board TUI                          │
│                                                               │
│  To Do  │ Assessed │ Specified │ Planned │ In Implementation │
│ ─────── │ ──────── │ ───────── │ ─────── │ ───────────────── │
│  #076   │   #182   │   #183    │  #184   │      #185         │
│  RAG    │  Assess  │  Specify  │  Plan   │   Implement       │
│         │  Feature │  Feature  │ Feature │   Feature X       │
│  [H]    │   [H]    │    [H]    │   [H]   │     [H]           │
│         │          │           │         │                   │
│ ──Next: │ ──Next:  │  ──Next:  │ ──Next: │   ──Next:         │
│ /assess │ /specify │ /research │ /impl   │   /validate       │
│         │          │    or     │         │                   │
│         │          │   /plan   │         │                   │
└──────────────────────────────────────────────────────────────┘

Legend: [H] = High priority
        ──Next: = Suggested next workflow command
```

### Key Architectural Decisions

#### 1. Status = Workflow State (Direct Mapping)

**Decision**: The task's `status` field IS the workflow state. No separate field.

**Rationale**:
- Simpler mental model: one state, not two
- No synchronization complexity
- Prevents divergence between status and workflow state
- Backward compatible: projects without workflow use traditional statuses

**Implementation**:
```yaml
# backlog/config.yml (workflow-enabled project)
statuses: ["To Do", "Assessed", "Specified", "Planned", "In Implementation", "Validated", "Deployed", "Done"]
workflow_enabled: true
```

**Trade-offs**:
- ✅ Simplicity: One state to rule them all
- ✅ Consistency: No sync bugs
- ❌ Flexibility: Can't have custom status labels different from workflow states
- ❌ Migration: Existing tasks need status remapping

#### 2. Workflow Transition Enforcement

**Decision**: Task status can ONLY be changed via `/jpspec:*` commands or manual override.

**Rationale**:
- Enforces workflow integrity
- Ensures artifacts are created before state transitions
- Prevents "shortcut" transitions that skip validation
- Maintains audit trail

**Implementation**:
```bash
# Valid: Workflow command transitions state automatically
/jpspec:specify user-auth
# → Task status: "To Do" → "Specified"

# Valid: Manual override for exceptional cases
backlog task edit 42 -s "Specified" --override-workflow

# Invalid: Direct status change blocked
backlog task edit 42 -s "Specified"
# → Error: Workflow enforcement enabled. Use /jpspec:specify or --override-workflow
```

**Override Logging**:
```
2025-11-30 14:32:10 [WARN] Workflow override: task-42 status changed To Do → Specified
  User: jpoley
  Reason: --override-workflow flag
  Previous state: To Do
  New state: Specified
  Audit: Manual override bypasses /jpspec:specify workflow
```

#### 3. Board Column Generation

**Decision**: Dynamically generate Kanban columns from `jpspec_workflow.yml` states.

**Rationale**:
- Project-specific workflows (not all features need Research)
- Scales to custom workflows (team-specific processes)
- Eliminates manual configuration
- Single source of truth

**Implementation**:
```javascript
// backlog board rendering (pseudocode)
const workflowConfig = loadWorkflowConfig(); // jpspec_workflow.yml
const states = workflowConfig ? workflowConfig.states : ["To Do", "In Progress", "Done"];
const columns = states.map(state => ({
  title: state,
  tasks: filterTasksByStatus(state)
}));
renderKanban(columns);
```

**Fallback Behavior**:
```javascript
// No workflow config found → traditional Kanban
if (!workflowConfig) {
  const columns = ["To Do", "In Progress", "Done"];
  // Standard backlog.md behavior
}
```

#### 4. Next Action Hints

**Decision**: Display suggested next `/jpspec:*` command on task cards.

**Rationale**:
- Reduces cognitive load: "What do I do next?"
- Promotes workflow adoption
- Educates developers on workflow progression
- Optional visual aid (can be toggled off)

**Display Format**:
```
┌─────────────────────────────────┐
│ #182 - Assess Feature Complexity│
│ [HIGH] @jpoley                  │
│                                 │
│ Status: To Do                   │
│ → Next: /jpspec:assess          │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ #183 - Specify User Auth        │
│ [HIGH] @jpoley                  │
│                                 │
│ Status: Assessed                │
│ → Next: /jpspec:specify         │
└─────────────────────────────────┘
```

---

## DORA Impact Analysis

### Overview

Integrating workflow steps into backlog.md enables automated measurement of [DORA (DevOps Research and Assessment)](https://www.devops-research.com/research.html) metrics, providing empirical evidence of platform effectiveness.

### Metric 1: Deployment Frequency

**Definition**: How often code is successfully released to production.

**Workflow Visibility Impact**: ⭐⭐⭐⭐⭐ (High)

**Measurement Strategy**:
```sql
-- Count transitions to "Deployed" state per time period
SELECT
  DATE_TRUNC('week', updated_at) AS week,
  COUNT(*) AS deployments
FROM task_state_changes
WHERE new_state = 'Deployed'
GROUP BY week
ORDER BY week DESC;
```

**Improvements Enabled**:
- **Visibility**: Track which features are deployed vs. stuck in validation
- **Bottleneck Detection**: Identify states with longest dwell time
- **Trend Analysis**: Monitor deployment frequency over time
- **Team Comparison**: Compare deployment rates across teams/projects

**Example Dashboard**:
```
Deployment Frequency (Last 30 Days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Week 1: ████████ (8 deployments)
Week 2: ██████ (6 deployments)
Week 3: ██████████ (10 deployments)
Week 4: ████████ (8 deployments)

Average: 8 deployments/week
Trend: +15% vs. previous month
```

### Metric 2: Lead Time for Changes

**Definition**: Time from code commit to code successfully running in production.

**Workflow Visibility Impact**: ⭐⭐⭐⭐⭐ (High)

**Measurement Strategy**:
```sql
-- Calculate time from "In Implementation" → "Deployed"
SELECT
  task_id,
  EXTRACT(EPOCH FROM (deployed_at - implementation_started_at)) / 86400.0 AS lead_time_days
FROM (
  SELECT
    task_id,
    MIN(CASE WHEN new_state = 'In Implementation' THEN updated_at END) AS implementation_started_at,
    MIN(CASE WHEN new_state = 'Deployed' THEN updated_at END) AS deployed_at
  FROM task_state_changes
  GROUP BY task_id
) AS state_times
WHERE deployed_at IS NOT NULL;
```

**Improvements Enabled**:
- **State-Level Breakdown**: Time in each workflow state (Planned, Implementation, Validated)
- **Bottleneck Identification**: Which state takes longest? (e.g., "Validation" taking 40% of total time)
- **Predictive Analytics**: Estimate deployment date based on current state and historical averages
- **Process Improvement**: Focus on reducing time in slowest states

**Example Analysis**:
```
Lead Time Breakdown (Average)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Planned → Implementation:    2.3 days (18%)
In Implementation:           5.8 days (45%)
Implementation → Validated:  3.1 days (24%)
Validated → Deployed:        1.7 days (13%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Lead Time:             12.9 days

🚨 Bottleneck: Implementation phase (45% of total time)
💡 Recommendation: Investigate code review velocity, test coverage
```

### Metric 3: Change Failure Rate

**Definition**: Percentage of deployments causing failure in production.

**Workflow Visibility Impact**: ⭐⭐⭐⭐ (Medium-High)

**Measurement Strategy**:
```sql
-- Track rollbacks: Deployed → Validated transitions
SELECT
  (COUNT(CASE WHEN transition = 'Deployed → Validated' THEN 1 END)::FLOAT /
   COUNT(CASE WHEN new_state = 'Deployed' THEN 1 END)) * 100 AS failure_rate_pct
FROM task_state_changes
WHERE updated_at > NOW() - INTERVAL '30 days';
```

**Improvements Enabled**:
- **Rollback Tracking**: Automatic detection of `Deployed → Validated` transitions
- **Failure Correlation**: Link failures to specific workflow phases (e.g., features that skipped "Research" fail more often)
- **Quality Gates**: Enforce validation phase completion before deployment
- **Incident Response**: Trigger alerts when failure rate exceeds threshold

**Example Alert**:
```
🚨 DORA Alert: Change Failure Rate Exceeded Threshold
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Current Failure Rate: 18.5% (threshold: 15%)
Period: Last 30 days
Failures: 5 rollbacks out of 27 deployments

Recent Failures:
- task-245: API breaking change (Deployed → Validated)
- task-267: Database migration failure (Deployed → Validated)
- task-289: Performance regression (Deployed → Validated)

Action Items:
1. Review validation phase completion for recent features
2. Strengthen integration testing in /jpspec:validate
3. Consider mandatory load testing for API changes
```

### Metric 4: Mean Time to Recovery (MTTR)

**Definition**: Time to restore service after production incident.

**Workflow Visibility Impact**: ⭐⭐⭐ (Medium)

**Measurement Strategy**:
```sql
-- Time from rollback (Deployed → Validated) to re-deployment
SELECT
  AVG(recovery_time_hours) AS mean_recovery_hours
FROM (
  SELECT
    task_id,
    EXTRACT(EPOCH FROM (redeployed_at - rollback_at)) / 3600.0 AS recovery_time_hours
  FROM (
    SELECT
      task_id,
      MIN(CASE WHEN new_state = 'Validated' AND old_state = 'Deployed' THEN updated_at END) AS rollback_at,
      MIN(CASE WHEN new_state = 'Deployed' AND updated_at > rollback_at THEN updated_at END) AS redeployed_at
    FROM task_state_changes
    GROUP BY task_id
  ) AS recovery_times
  WHERE rollback_at IS NOT NULL AND redeployed_at IS NOT NULL
) AS mttr_calc;
```

**Improvements Enabled**:
- **Recovery Tracking**: Measure time from incident (rollback) to fix deployment
- **Workflow Acceleration**: Identify fast paths for critical fixes (optional "hotfix" workflow)
- **Incident Analysis**: Correlate recovery time with fix complexity
- **SLA Monitoring**: Alert if MTTR exceeds SLA threshold

### DORA Maturity Progression

**Current State (No Workflow Visibility)**:
- Manual tracking in spreadsheets
- Deployment frequency: Unknown or estimated
- Lead time: Rough estimates from PR timestamps
- Change failure rate: Anecdotal ("we had a few rollbacks this month")
- MTTR: Incident reports only

**Future State (Workflow-Aware Backlog)**:
- Automated DORA metrics collection
- Real-time dashboards
- Predictive analytics ("this feature will likely deploy in 3 days based on current state")
- Continuous improvement feedback loop

**Maturity Levels**:

| Level | Deployment Frequency | Lead Time | Change Failure Rate | MTTR | Enabled By |
|-------|---------------------|-----------|---------------------|------|------------|
| **Elite** | Multiple per day | < 1 day | < 5% | < 1 hour | Workflow automation, validation gates |
| **High** | Weekly to monthly | 1-7 days | 5-15% | < 1 day | Workflow visibility, bottleneck detection |
| **Medium** | Monthly to bimonthly | 1-4 weeks | 15-30% | 1 day - 1 week | Basic workflow tracking |
| **Low** | Less than monthly | > 4 weeks | > 30% | > 1 week | Manual processes |

**Workflow Integration Impact**: Moves teams from **Low/Medium → High** maturity by providing:
1. Automated state tracking
2. Bottleneck identification
3. Quality gate enforcement
4. Data-driven process improvement

---

## CLI/TUI Design

### New Commands and Flags

#### 1. Enhanced Board Command

```bash
# Standard board view (unchanged for backward compatibility)
backlog board

# Workflow-enhanced view (default if jpspec_workflow.yml exists)
backlog board --workflow

# Compact view (hide workflow hints)
backlog board --compact

# Filter by workflow state
backlog board --state "In Implementation"

# Show transition history
backlog board --show-transitions
```

**Output Example** (`backlog board --workflow`):

```
JPSpec Workflow Board: jp-spec-kit
═══════════════════════════════════════════════════════════════════════════════

To Do          │ Assessed       │ Specified      │ Planned        │ In Implementation
───────────────│────────────────│────────────────│────────────────│──────────────────
#076           │ #182           │ #183           │ #184           │ #185
Local RAG      │ Assess Feature │ Specify Auth   │ Plan Platform  │ Implement API
[HIGH] @unass  │ [HIGH] @jpoley │ [HIGH] @jpoley │ [MED] @jpoley  │ [HIGH] @alice
               │                │                │                │
→ /assess      │ → /specify     │ → /research    │ → /implement   │ → /validate
               │                │    or /plan    │                │
───────────────│────────────────│────────────────│────────────────│──────────────────
#077           │                │                │                │
Doc2Vec        │                │                │                │
[HIGH] @unass  │                │                │                │
               │                │                │                │
→ /assess      │                │                │                │

═══════════════════════════════════════════════════════════════════════════════
Summary: 5 tasks across 5 states
Next Action: Run /jpspec:assess on #076 or #077

Legend: [Priority] @Assignee → Suggested next command
```

#### 2. Workflow Status Command

```bash
# Show workflow status for a specific task
backlog task 182 --workflow

# Output:
Task #182: Assess Feature Complexity
Status: Assessed
Workflow: jpspec-sdd-v1

Workflow Progress:
  ✓ To Do → Assessed (2025-11-28, via /jpspec:assess)
  → Next: /jpspec:specify

State History:
  2025-11-28 10:15 - Created (To Do)
  2025-11-28 14:32 - /jpspec:assess → Assessed

Available Transitions:
  ✓ /jpspec:specify → Specified

Artifacts:
  ✓ ./docs/assess/feature-complexity-assessment.md
```

#### 3. Workflow Validation Command

```bash
# Validate workflow configuration
backlog workflow validate

# Output:
Validating workflow configuration...
✓ jpspec_workflow.yml found at memory/jpspec_workflow.yml
✓ Schema validation passed
✓ 9 states defined
✓ 9 transitions defined
✓ No cycles detected in state graph
✓ All workflow commands mapped

Configuration Summary:
  Version: 1.0
  States: To Do, Assessed, Specified, Researched, Planned, In Implementation, Validated, Deployed, Done
  Commands: 7 (/jpspec:assess, /jpspec:specify, /jpspec:research, /jpspec:plan, /jpspec:implement, /jpspec:validate, /jpspec:operate)

Backlog Integration:
  ✓ Statuses synced to backlog/config.yml
  ✓ Workflow enforcement: enabled
  ✓ 23 tasks using workflow states
```

#### 4. Workflow Sync Command

```bash
# Manually sync workflow states to backlog config
backlog workflow sync

# Output:
Syncing workflow states from memory/jpspec_workflow.yml...
✓ Read 9 states from workflow config
✓ Updated backlog/config.yml statuses
✓ Migrated 5 tasks with old statuses:
  - task-042: "In Progress" → "In Implementation"
  - task-067: "In Progress" → "Validated"
  - task-089: "Done" → "Deployed"
  - task-102: "To Do" → "Assessed"
  - task-134: "To Do" → "Specified"

Sync complete. Run 'backlog board' to see updated states.
```

### Board Display Modifications

#### Horizontal Layout (Default)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Workflow-Aware Kanban Board                        │
├──────────────────────────────────────────────────────────────────────────┤
│  To Do     │ Assessed  │ Specified │ Planned   │ In Implementation       │
│  (2)       │ (1)       │ (1)       │ (1)       │ (1)                     │
│ ──────────────────────────────────────────────────────────────────────── │
│  #076      │ #182      │ #183      │ #184      │ #185                    │
│  RAG Sys   │ Assess X  │ Specify Y │ Plan Z    │ Implement API           │
│  [H] @una  │ [H] @jp   │ [H] @jp   │ [M] @jp   │ [H] @alice              │
│  →/assess  │ →/specify │ →/research│ →/impl    │ →/validate              │
│            │           │   or      │           │                         │
│  #077      │           │   /plan   │           │ AC: 2/5 ✓               │
│  Doc2Vec   │           │           │           │ Days: 3                 │
│  [H] @una  │           │           │           │                         │
│  →/assess  │           │           │           │                         │
└──────────────────────────────────────────────────────────────────────────┘

Legend:
  [H] = High priority, [M] = Medium, [L] = Low
  @una = Unassigned, @jp = jpoley
  → = Suggested next workflow command
  AC: X/Y ✓ = Acceptance Criteria progress
  Days: N = Days in current state
```

#### Vertical Layout (`--layout vertical`)

```
To Do (2 tasks)
════════════════════════════════════════════════════════════
  #076 - Local RAG system for Claude Code subagents
  Priority: HIGH | Assignee: Unassigned
  → Next: /jpspec:assess

  #077 - Doc2Vec implementation with DuckDB
  Priority: HIGH | Assignee: Unassigned
  → Next: /jpspec:assess

Assessed (1 task)
════════════════════════════════════════════════════════════
  #182 - Assess Feature Complexity
  Priority: HIGH | Assignee: @jpoley
  → Next: /jpspec:specify

  Artifacts:
    ✓ docs/assess/feature-complexity-assessment.md

Specified (1 task)
════════════════════════════════════════════════════════════
  #183 - Specify User Authentication
  Priority: HIGH | Assignee: @jpoley
  → Next: /jpspec:research or /jpspec:plan

  Artifacts:
    ✓ docs/prd/user-authentication.md

...
```

#### Compact View (`--compact`)

```
To Do (2)      │ Assessed (1)  │ Specified (1) │ Planned (1)   │ In Implementation (1)
#076, #077     │ #182          │ #183          │ #184          │ #185
```

---

## Integration Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         System Architecture                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐
│ jpspec_workflow.yml     │  ← Configuration Source
│                         │
│ version: "1.0"          │
│ states: [...]           │
│ workflows: {...}        │
│ transitions: [...]      │
└────────────┬────────────┘
             │
             │ (read by)
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              WorkflowConfigLoader (Python)                       │
│  • Parses jpspec_workflow.yml                                   │
│  • Validates schema                                              │
│  • Builds state transition graph                                │
│  • Provides API for state queries                               │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ (used by)
             ▼
┌─────────────────────────────────────────────────────────────────┐
│              BacklogWorkflowSync (Python)                        │
│  • Syncs states to backlog/config.yml                           │
│  • Validates task state transitions                             │
│  • Provides workflow metadata for TUI                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ (invoked by)
             │
      ┌──────┴─────────┬───────────────┬────────────────┐
      │                │               │                │
      ▼                ▼               ▼                ▼
┌──────────┐   ┌──────────────┐  ┌──────────┐  ┌─────────────┐
│ /jpspec  │   │ backlog CLI  │  │ Backlog  │  │ MCP Server  │
│ commands │   │              │  │ Web UI   │  │             │
│          │   │ - board      │  │          │  │ - task_edit │
│ - assess │   │ - workflow   │  │ Drag &   │  │ - task_list │
│ - specify│   │ - task       │  │ Drop     │  │             │
└──────────┘   └──────────────┘  └──────────┘  └─────────────┘
      │                │               │                │
      │                │               │                │
      └────────────────┴───────────────┴────────────────┘
                       │
                       ▼
          ┌──────────────────────────┐
          │   backlog/tasks/*.md     │  ← Task Storage
          │                          │
          │   Frontmatter:           │
          │     status: "Specified"  │
          │     workflow_state: ...  │
          │     priority: high       │
          │     labels: [...]        │
          └──────────────────────────┘
```

### Data Flow: Workflow Transition

```
User runs: /jpspec:specify user-auth

1. JPSpec Command Execution
   ┌─────────────────────────────────────┐
   │ /jpspec:specify                     │
   │ • Validates current state: "Assessed"│
   │ • Generates PRD artifact            │
   │ • Transitions state → "Specified"   │
   └─────────────────┬───────────────────┘
                     │
                     ▼
2. Backlog Task Update
   ┌─────────────────────────────────────┐
   │ backlog task edit <id>              │
   │   -s "Specified"                    │
   │   --workflow-transition             │
   └─────────────────┬───────────────────┘
                     │
                     ▼
3. Workflow Validation
   ┌─────────────────────────────────────┐
   │ BacklogWorkflowSync.validate()      │
   │ • Check: "Assessed" → "Specified" OK│
   │ • Check: Artifacts present          │
   │ • Log: State transition event       │
   └─────────────────┬───────────────────┘
                     │
                     ▼
4. Task File Update
   ┌─────────────────────────────────────┐
   │ backlog/tasks/task-183.md           │
   │ ---                                 │
   │ status: "Specified"                 │
   │ updated_at: 2025-11-30T14:32:00Z    │
   │ workflow_history:                   │
   │   - state: "Assessed"               │
   │     timestamp: 2025-11-28T10:15:00Z │
   │     via: "/jpspec:assess"           │
   │   - state: "Specified"              │
   │     timestamp: 2025-11-30T14:32:00Z │
   │     via: "/jpspec:specify"          │
   │ ---                                 │
   └─────────────────┬───────────────────┘
                     │
                     ▼
5. UI Refresh
   ┌─────────────────────────────────────┐
   │ backlog board                       │
   │ • Reads updated task status         │
   │ • Displays in "Specified" column    │
   │ • Shows next action: →/jpspec:plan  │
   └─────────────────────────────────────┘
```

### State Synchronization Strategy

#### Option 1: Lazy Sync (Recommended)

**Trigger**: On-demand when backlog CLI is invoked

**Pros**:
- No background processes
- Simple implementation
- Works with existing backlog.md CLI

**Cons**:
- Slight delay on first command
- Requires explicit sync call

**Implementation**:
```python
# backlog CLI entrypoint
def main():
    # Check if workflow config exists
    workflow_config_path = find_workflow_config()

    if workflow_config_path and needs_sync():
        sync_workflow_states(workflow_config_path)

    # Continue with normal CLI execution
    run_command(args)
```

#### Option 2: Eager Sync (Future Enhancement)

**Trigger**: File watcher on `jpspec_workflow.yml` changes

**Pros**:
- Always up-to-date
- No delay on CLI commands

**Cons**:
- Requires background daemon or file watcher
- More complex setup
- May conflict with Git operations

**Implementation** (future):
```python
# File watcher daemon
from watchdog.observers import Observer

def on_workflow_config_change(event):
    if event.src_path.endswith('jpspec_workflow.yml'):
        sync_workflow_states(event.src_path)

observer = Observer()
observer.schedule(WorkflowConfigHandler(), path='memory/', recursive=False)
observer.start()
```

**Decision**: Start with **Option 1 (Lazy Sync)**, migrate to Option 2 if performance becomes an issue.

### Validation and Constraint Enforcement

#### Transition Validation

```python
class WorkflowTransitionValidator:
    def __init__(self, workflow_config):
        self.config = workflow_config
        self.transition_graph = self._build_graph()

    def validate_transition(self, from_state: str, to_state: str) -> ValidationResult:
        """Validate if state transition is allowed by workflow."""

        # Check if transition exists in workflow
        if not self._is_valid_transition(from_state, to_state):
            return ValidationResult(
                valid=False,
                message=f"Invalid transition: {from_state} → {to_state}",
                allowed_transitions=self._get_allowed_transitions(from_state)
            )

        # Check if required artifacts exist
        required_artifacts = self._get_required_artifacts(from_state, to_state)
        missing_artifacts = self._check_artifacts(required_artifacts)

        if missing_artifacts:
            return ValidationResult(
                valid=False,
                message=f"Missing required artifacts: {', '.join(missing_artifacts)}",
                missing_artifacts=missing_artifacts
            )

        return ValidationResult(valid=True)

    def _is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if transition exists in workflow configuration."""
        return to_state in self.transition_graph.get(from_state, [])

    def _get_allowed_transitions(self, from_state: str) -> list[str]:
        """Get list of allowed next states."""
        return self.transition_graph.get(from_state, [])
```

**Usage**:
```python
# In backlog task edit command
validator = WorkflowTransitionValidator(workflow_config)
result = validator.validate_transition(current_status, new_status)

if not result.valid:
    if args.override_workflow:
        log_workflow_override(task_id, current_status, new_status, result.message)
        # Allow transition but log warning
    else:
        raise WorkflowViolationError(
            f"{result.message}\n"
            f"Allowed transitions: {', '.join(result.allowed_transitions)}\n"
            f"Use --override-workflow to bypass this check."
        )
```

---

## Developer Experience

### Typical Workflow for Using Workflow Steps

#### Scenario: Implementing a new feature "User Authentication"

**Step 1: Create Feature Task**

```bash
# Create task for the feature
backlog task create "User Authentication" \
  -d "Implement JWT-based authentication for API" \
  --ac "Users can log in with email/password" \
  --ac "JWT tokens are issued on successful login" \
  --ac "Protected routes require valid JWT" \
  --priority high

# Output:
✓ Created task-200 - User Authentication
  Status: To Do
  → Next: /jpspec:assess
```

**Step 2: Assess Feature Complexity**

```bash
# Run assessment workflow
/jpspec:assess user-authentication

# Output:
Assessment Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature: User Authentication
Recommendation: Full SDD
Confidence: High
Report: ./docs/assess/user-authentication-assessment.md

Scoring Summary:
- Complexity: 6.7/10
- Risk: 8.3/10 (Security implications)
- Architecture Impact: 5.0/10
- Total: 20.0/30

Next Command: /jpspec:specify user-authentication

✓ Updated task-200 status: To Do → Assessed
```

**Step 3: Check Backlog**

```bash
backlog board

# Output shows task-200 in "Assessed" column:
To Do          │ Assessed       │ Specified      │ ...
───────────────│────────────────│────────────────│
               │ #200           │                │
               │ User Auth      │                │
               │ [HIGH] @jpoley │                │
               │ → /specify     │                │
```

**Step 4: Specify Requirements**

```bash
/jpspec:specify user-authentication

# Output:
Specification Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature: User Authentication
PRD: ./docs/prd/user-authentication.md
Tasks Generated: 12 tasks

Workflow Progression:
  ✓ Assessed → Specified

Next Command: /jpspec:research user-authentication
  (or skip to: /jpspec:plan user-authentication)

✓ Updated task-200 status: Assessed → Specified
```

**Step 5: Monitor Progress**

```bash
# View detailed workflow status
backlog task 200 --workflow

# Output:
Task #200: User Authentication
Status: Specified
Priority: HIGH
Assignee: @jpoley

Workflow Progress:
  ✓ To Do → Assessed (2025-11-30 10:15, via /jpspec:assess)
  ✓ Assessed → Specified (2025-11-30 14:32, via /jpspec:specify)
  → Next: /jpspec:research or /jpspec:plan

State History:
  2025-11-30 09:45 - Created (To Do)
  2025-11-30 10:15 - /jpspec:assess → Assessed
  2025-11-30 14:32 - /jpspec:specify → Specified

Generated Subtasks:
  - task-201: Setup authentication infrastructure
  - task-202: Implement JWT token generation
  - task-203: Create login endpoint
  ... (9 more tasks)

Artifacts:
  ✓ ./docs/assess/user-authentication-assessment.md
  ✓ ./docs/prd/user-authentication.md

Available Transitions:
  /jpspec:research → Researched
  /jpspec:plan → Planned (skip research)
```

**Step 6: Continue Through Workflow**

```bash
# Skip research, go straight to planning
/jpspec:plan user-authentication

# Implement the feature
/jpspec:implement user-authentication

# Validate (QA + Security)
/jpspec:validate user-authentication

# Deploy to production
/jpspec:operate user-authentication

# Final status
backlog task 200

# Output:
Task #200: User Authentication
Status: Deployed ✓
Priority: HIGH
Completed: 2025-12-05

Workflow completed in 5 days:
  - Assessed: 2025-11-30
  - Specified: 2025-11-30
  - Planned: 2025-12-01
  - In Implementation: 2025-12-02 - 2025-12-04
  - Validated: 2025-12-04
  - Deployed: 2025-12-05
```

### Migration Path for Existing Projects

#### For Projects Without Workflow Configuration

**Behavior**: Backlog.md works exactly as before, no changes.

```yaml
# backlog/config.yml (no workflow)
statuses: ["To Do", "In Progress", "Done"]
workflow_enabled: false  # or omitted
```

```bash
# Board display (unchanged)
To Do          │ In Progress    │ Done
───────────────│────────────────│────────
#076           │ #182           │ #200
RAG System     │ Assess Feature │ User Auth
[H] @una       │ [H] @jpoley    │ [H] @jpoley
```

#### For Projects Adopting Workflow

**Step 1: Initialize Workflow Configuration**

```bash
# Option A: Use jpspec default workflow
specify workflow init --template jpspec-sdd

# Option B: Create custom workflow
specify workflow init --custom

# Option C: Copy from memory/ (already exists)
# No action needed - auto-detected
```

**Step 2: Sync Existing Tasks**

```bash
# Sync workflow states to backlog
backlog workflow sync

# Output:
Syncing workflow states from memory/jpspec_workflow.yml...
✓ Read 9 states from workflow config
✓ Updated backlog/config.yml statuses

Migrating existing tasks...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 23 tasks with legacy statuses:

Mapping:
  "To Do" → "To Do" (no change)
  "In Progress" → needs manual classification

Manual Review Required (12 tasks):
  #042 - Platform integration (In Progress)
    Suggested: "In Implementation" or "Validated"
    Choose: [I]mplementation / [V]alidated / [S]kip

  #067 - Security audit (In Progress)
    Suggested: "Validated"
    Choose: [V]alidated / [S]kip

... (10 more)

Automatic Migrations (11 tasks):
  ✓ #200 - User Auth: "Done" → "Deployed"
  ✓ #134 - Diagrams: "To Do" → "To Do"
  ... (9 more)

Would you like to proceed with automatic migrations? [Y/n]: y

✓ Migrated 11 tasks automatically
⚠ 12 tasks require manual review
```

**Step 3: Manual Task Review**

```bash
# Review and update task states individually
backlog task edit 42 -s "In Implementation"
backlog task edit 67 -s "Validated"
# ... etc.
```

**Step 4: Verify Board**

```bash
backlog board

# Output: Now shows workflow states
To Do  │ Assessed │ Specified │ Planned │ In Implementation │ Validated │ Deployed │ Done
───────│──────────│───────────│─────────│───────────────────│───────────│──────────│─────
#076   │          │           │         │ #042              │ #067      │ #200     │
...
```

### Documentation Requirements

#### 1. User Guide: Workflow Integration

**Location**: `docs/guides/workflow-backlog-integration.md`

**Contents**:
- What are workflow steps?
- How workflow states map to backlog statuses
- How to enable workflow mode
- How to migrate existing projects
- Troubleshooting common issues

#### 2. Reference: Workflow Commands

**Location**: `docs/reference/workflow-commands.md`

**Contents**:
- `backlog board --workflow`
- `backlog workflow validate`
- `backlog workflow sync`
- `backlog task <id> --workflow`

#### 3. Tutorial: First Feature with Workflow

**Location**: `docs/tutorials/workflow-first-feature.md`

**Contents**:
- Step-by-step walkthrough
- Expected outputs at each stage
- Common mistakes and fixes

---

## Configuration Management

### Configuration Schema

#### backlog/config.yml (Enhanced)

```yaml
# Project Configuration
project_name: "jp-spec-kit"
default_status: "To Do"

# Workflow Integration
workflow_enabled: true
workflow_source: "memory/jpspec_workflow.yml"  # Path to workflow config
workflow_sync_mode: "lazy"  # lazy | eager

# Statuses (auto-generated from workflow if enabled)
statuses:
  - "To Do"
  - "Assessed"
  - "Specified"
  - "Researched"
  - "Planned"
  - "In Implementation"
  - "Validated"
  - "Deployed"
  - "Done"

# Display Options
max_column_width: 20
show_workflow_hints: true  # Show "→ /jpspec:*" suggestions
show_state_history: false  # Show history in task cards
compact_mode: false

# Enforcement
enforce_workflow_transitions: true  # Block invalid transitions
require_override_reason: true  # Require reason for --override-workflow

# Legacy (backward compatibility)
labels: []
milestones: []
date_format: yyyy-mm-dd
auto_open_browser: true
default_port: 6420
remote_operations: true
auto_commit: false
bypass_git_hooks: false
check_active_branches: true
active_branch_days: 30
```

### Configuration Precedence

**Priority Order** (highest to lowest):

1. **CLI Flags**: `--workflow`, `--compact`, `--state`
2. **Environment Variables**: `BACKLOG_WORKFLOW_ENABLED=true`
3. **backlog/config.yml**: Project-specific settings
4. **Workflow Auto-Detection**: Inferred from `jpspec_workflow.yml` existence
5. **Defaults**: Standard backlog.md behavior

**Example**:
```bash
# Project has workflow_enabled: false in config.yml
# But user explicitly requests workflow view
backlog board --workflow

# Result: Workflow mode is enabled for this invocation only
```

### Auto-Configuration on `specify init`

When initializing a new jp-spec-kit project:

```bash
specify init my-project --agent claude

# Auto-generates backlog/config.yml with workflow enabled:
cat backlog/config.yml

# Output:
project_name: "my-project"
default_status: "To Do"
workflow_enabled: true
workflow_source: "memory/jpspec_workflow.yml"
statuses: ["To Do", "Assessed", "Specified", "Researched", "Planned", "In Implementation", "Validated", "Deployed", "Done"]
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Read workflow config and sync to backlog.

**Tasks**:
- [ ] Implement `WorkflowConfigLoader` class
  - Load `jpspec_workflow.yml`
  - Validate schema
  - Build state transition graph
- [ ] Implement `BacklogWorkflowSync` class
  - Read workflow states
  - Update `backlog/config.yml`
  - Migrate existing task statuses
- [ ] Add `workflow_enabled` flag to backlog config
- [ ] Write unit tests for config loading and sync

**Deliverables**:
- `src/specify_cli/workflow/config_loader.py`
- `src/specify_cli/backlog/workflow_sync.py`
- Updated `backlog/config.yml` schema

**Acceptance Criteria**:
- [ ] `backlog workflow sync` successfully updates config
- [ ] Workflow states appear in `backlog/config.yml`
- [ ] Existing tasks migrate correctly
- [ ] 90%+ test coverage on new code

---

### Phase 2: CLI Integration (Weeks 3-4)

**Goal**: Display workflow states in board and task views.

**Tasks**:
- [ ] Enhance `backlog board` command
  - Dynamically generate columns from workflow states
  - Display "→ Next:" workflow hints
  - Add `--workflow` flag
- [ ] Enhance `backlog task <id>` command
  - Add `--workflow` flag
  - Display state history
  - Show available transitions
- [ ] Implement `backlog workflow validate` command
- [ ] Add workflow metadata to task card rendering

**Deliverables**:
- Updated board rendering logic
- New `--workflow` flags
- Workflow validation CLI

**Acceptance Criteria**:
- [ ] Board displays workflow columns correctly
- [ ] Task view shows workflow history
- [ ] Validate command checks config validity
- [ ] Visual regression tests pass

---

### Phase 3: Transition Enforcement (Weeks 5-6)

**Goal**: Enforce workflow constraints on task state changes.

**Tasks**:
- [ ] Implement `WorkflowTransitionValidator` class
  - Validate state transitions
  - Check required artifacts
  - Provide error messages
- [ ] Integrate validator into `backlog task edit`
  - Block invalid transitions
  - Allow `--override-workflow` flag
  - Log override events
- [ ] Update `/jpspec:*` commands
  - Auto-update task status after workflow execution
  - Record workflow history in task metadata
- [ ] Add workflow history tracking

**Deliverables**:
- `src/specify_cli/workflow/validator.py`
- Updated `backlog task edit` logic
- Workflow history in task frontmatter

**Acceptance Criteria**:
- [ ] Invalid transitions are blocked
- [ ] Override flag works with logging
- [ ] JPSpec commands update task status
- [ ] History is persisted correctly

---

### Phase 4: DORA Metrics (Weeks 7-8)

**Goal**: Enable DORA metrics collection and reporting.

**Tasks**:
- [ ] Add state transition event logging
  - Timestamp each transition
  - Record via command or manual
  - Store in task history
- [ ] Implement DORA metrics calculator
  - Deployment frequency
  - Lead time for changes
  - Change failure rate
  - MTTR
- [ ] Create `backlog metrics` command
  - Display DORA metrics
  - Support filtering by time period
  - Export to JSON/CSV
- [ ] Add metrics dashboard (optional)

**Deliverables**:
- Event logging system
- `src/specify_cli/backlog/metrics.py`
- `backlog metrics` CLI command

**Acceptance Criteria**:
- [ ] All state transitions are logged
- [ ] Metrics calculations are accurate
- [ ] CLI displays metrics correctly
- [ ] Export formats work

---

### Phase 5: Documentation & Polish (Weeks 9-10)

**Goal**: Finalize documentation and user experience.

**Tasks**:
- [ ] Write user guide: workflow integration
- [ ] Write reference docs: workflow commands
- [ ] Write tutorial: first feature with workflow
- [ ] Create video walkthrough
- [ ] Update CLAUDE.md with workflow instructions
- [ ] Polish UX: colors, formatting, error messages
- [ ] Beta testing with 5 pilot users

**Deliverables**:
- Complete documentation suite
- Video tutorial
- Polished CLI experience
- Beta feedback report

**Acceptance Criteria**:
- [ ] All documentation complete
- [ ] Video published
- [ ] 5 beta users successfully use workflow
- [ ] NPS > 8 from beta users

---

## Platform Principles for Constitution

### Principle: Workflow Tracking Standards

**Title**: VIII. Workflow-Driven Task Management

**Description**:
All features MUST follow the JPSpec workflow pipeline, with state tracked and enforced through the backlog system.

**Requirements**:
- **State Visibility**: Every task's workflow state is visible in the backlog
- **Transition Enforcement**: State changes occur only through valid workflow commands
- **Artifact Coupling**: Workflow transitions require artifact completion
- **History Preservation**: All state transitions are logged with timestamps and triggers

**Implementation**:
```bash
# ✓ Valid: Workflow command triggers state change
/jpspec:specify user-auth  # Updates task status automatically

# ✓ Valid: Emergency override with reason
backlog task edit 42 -s "Planned" --override-workflow

# ✗ Invalid: Direct status change without workflow
backlog task edit 42 -s "Planned"  # Blocked by enforcement
```

**Rationale**:
- **Quality**: Ensures artifacts are created before progression
- **Traceability**: Complete audit trail of feature evolution
- **Metrics**: Enables DORA metrics for continuous improvement
- **Collaboration**: Team has shared understanding of feature status

---

### Principle: Configuration Conventions

**Title**: IX. Workflow Configuration Management

**Description**:
Workflow configuration follows single-source-of-truth principles with automatic synchronization.

**Requirements**:
- **Single Source**: `jpspec_workflow.yml` is the authoritative workflow definition
- **Auto-Sync**: Backlog config syncs from workflow config automatically
- **No Manual Editing**: Never manually edit `statuses` in `backlog/config.yml`
- **Validation**: Always validate workflow config before using

**Implementation**:
```bash
# ✓ Valid: Edit workflow source
vim memory/jpspec_workflow.yml
backlog workflow sync  # Propagates changes

# ✓ Valid: Validate before using
backlog workflow validate

# ✗ Invalid: Edit backlog config directly
vim backlog/config.yml  # Changes will be overwritten
```

**Rationale**:
- **Consistency**: Prevents divergence between workflow and backlog
- **Maintainability**: One place to update workflow definition
- **Reliability**: Validation catches errors before they affect tasks

---

### Principle: CLI Design Patterns

**Title**: X. Workflow CLI Usability

**Description**:
CLI commands related to workflow follow consistent patterns for discoverability and ease of use.

**Requirements**:
- **Namespacing**: Workflow commands use `backlog workflow <subcommand>` namespace
- **Help Text**: All commands include workflow-specific help text
- **Hints**: Display suggested next actions (e.g., "→ /jpspec:specify")
- **Graceful Degradation**: Commands work with or without workflow config

**Implementation**:
```bash
# Workflow namespace
backlog workflow sync      # Sync states
backlog workflow validate  # Validate config
backlog workflow status    # Show workflow status

# Flags for workflow views
backlog board --workflow   # Workflow-enhanced board
backlog task 42 --workflow # Workflow task details

# Hints in output
→ Next: /jpspec:specify  # Suggested action
```

**Rationale**:
- **Discoverability**: Easy to find workflow-related commands
- **Consistency**: Predictable CLI patterns across all commands
- **Onboarding**: Hints guide new users through workflow
- **Compatibility**: Doesn't break existing non-workflow usage

---

## Migration and Compatibility

### Backward Compatibility Strategy

**Goal**: Existing projects continue working without workflow, new projects get workflow by default.

**Approach**:
1. **Feature Flag**: `workflow_enabled` in `backlog/config.yml`
2. **Auto-Detection**: Presence of `jpspec_workflow.yml` enables workflow
3. **Opt-In**: Users can disable with `workflow_enabled: false`
4. **Graceful Degradation**: All commands work without workflow config

**Compatibility Matrix**:

| Project Type | Config | Behavior |
|--------------|--------|----------|
| **Legacy (no workflow)** | `workflow_enabled: false` or omitted | Standard backlog.md (To Do / In Progress / Done) |
| **New (with workflow)** | `workflow_enabled: true` + `jpspec_workflow.yml` exists | Workflow-enhanced mode |
| **Migrating** | `workflow_enabled: true` but no `jpspec_workflow.yml` | Error: "Workflow config not found. Run `specify workflow init`" |

**Example: Legacy Project**

```yaml
# backlog/config.yml (no workflow)
project_name: "legacy-app"
statuses: ["To Do", "In Progress", "Done"]
# workflow_enabled: false  # Optional, defaults to false
```

```bash
backlog board
# Output: Standard 3-column board (unchanged)
```

**Example: Workflow-Enabled Project**

```yaml
# backlog/config.yml (with workflow)
project_name: "new-feature"
workflow_enabled: true
workflow_source: "memory/jpspec_workflow.yml"
statuses: ["To Do", "Assessed", "Specified", "Planned", "In Implementation", "Validated", "Deployed", "Done"]
```

```bash
backlog board
# Output: 9-column workflow board with hints
```

### Migration Guide

**For Project Maintainers**: See `docs/guides/workflow-migration.md`

**For Individual Features**: Migrate one feature at a time

```bash
# Step 1: Enable workflow for the project
backlog workflow sync

# Step 2: Update specific task to workflow state
backlog task edit 42 -s "In Implementation" --migrate-from "In Progress"

# Step 3: Verify
backlog task 42 --workflow
# Shows: Migrated from "In Progress" to "In Implementation" on 2025-11-30
```

---

## Metrics and Observability

### Key Metrics to Track

#### 1. Workflow Adoption Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Workflow Enablement Rate** | % of projects with `workflow_enabled: true` | 60% by Q2 2026 |
| **Workflow Command Usage** | # of `/jpspec:*` commands run per week | 50/week |
| **Task Workflow Coverage** | % of tasks using workflow states | 80% |

#### 2. Developer Experience Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **Time to First Workflow Use** | Days from project init to first `/jpspec:*` command | < 1 day |
| **Workflow Errors** | # of blocked transitions per week | < 5/week |
| **Override Rate** | % of transitions using `--override-workflow` | < 10% |

#### 3. DORA Metrics (Enabled by Workflow)

See [DORA Impact Analysis](#dora-impact-analysis) section above.

### Instrumentation Points

```python
# Log workflow events for analytics
def log_workflow_event(event_type: str, **metadata):
    """Log workflow event for metrics collection."""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "project": get_project_name(),
        **metadata
    }

    # Write to analytics log
    with open(".backlog/workflow_events.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")

# Event types:
# - workflow_sync: Workflow config synced
# - state_transition: Task state changed
# - workflow_command: /jpspec:* command executed
# - override_used: --override-workflow flag used
# - validation_error: Invalid transition attempted
```

**Example Events**:

```jsonl
{"timestamp": "2025-11-30T14:32:10Z", "event_type": "workflow_command", "command": "/jpspec:specify", "task_id": "task-183", "duration_ms": 4500}
{"timestamp": "2025-11-30T14:32:15Z", "event_type": "state_transition", "task_id": "task-183", "from_state": "Assessed", "to_state": "Specified", "via": "/jpspec:specify"}
{"timestamp": "2025-11-30T15:10:22Z", "event_type": "override_used", "task_id": "task-042", "from_state": "In Progress", "to_state": "Validated", "reason": "Emergency hotfix"}
```

---

## Appendix A: Example Workflow Configurations

### Minimal Workflow (Simple Projects)

```yaml
version: "1.0"
description: "Lightweight workflow for small features"

states:
  - name: "Planned"
  - name: "In Progress"

workflows:
  plan:
    command: "/jpspec:plan"
    agents: ["developer"]
    input_states: ["To Do"]
    output_state: "Planned"

  implement:
    command: "/jpspec:implement"
    agents: ["developer"]
    input_states: ["Planned"]
    output_state: "In Progress"

transitions:
  - from: "To Do"
    to: "Planned"
    via: "plan"
  - from: "Planned"
    to: "In Progress"
    via: "implement"
  - from: "In Progress"
    to: "Done"
    via: "completion"
```

**Board Output**:
```
To Do  │ Planned  │ In Progress  │ Done
───────│──────────│──────────────│──────
#076   │   #182   │     #183     │ #200
```

### Full SDD Workflow (Complex Projects)

See `docs/reference/workflow-artifact-flow.md` for the complete 9-state workflow used in jp-spec-kit.

---

## Appendix B: API Reference

### Python API

```python
from specify_cli.workflow import WorkflowConfig, WorkflowTransitionValidator
from specify_cli.backlog import BacklogWorkflowSync

# Load workflow configuration
config = WorkflowConfig.load("memory/jpspec_workflow.yml")

# Get workflow states
states = config.get_states()  # ["To Do", "Assessed", ...]

# Get transitions
transitions = config.get_transitions()

# Validate transition
validator = WorkflowTransitionValidator(config)
result = validator.validate_transition("Assessed", "Specified")

if result.valid:
    print("✓ Transition allowed")
else:
    print(f"✗ {result.message}")
    print(f"Allowed: {result.allowed_transitions}")

# Sync workflow to backlog
sync = BacklogWorkflowSync(config)
sync.sync_states()  # Updates backlog/config.yml
```

---

## Appendix C: Troubleshooting

### Common Issues

#### Issue: "Workflow config not found"

**Error**:
```
Error: workflow_enabled is true but no workflow config found
Expected location: memory/jpspec_workflow.yml
```

**Solution**:
```bash
# Initialize workflow config
specify workflow init --template jpspec-sdd

# Or disable workflow
vim backlog/config.yml
# Set: workflow_enabled: false
```

#### Issue: "Invalid state transition"

**Error**:
```
Error: Invalid transition: To Do → In Implementation
Allowed transitions from "To Do": ["Assessed"]
```

**Solution**:
```bash
# Follow the workflow path
/jpspec:assess feature-name  # To Do → Assessed
/jpspec:specify feature-name # Assessed → Specified
/jpspec:plan feature-name    # Specified → Planned
/jpspec:implement feature-name # Planned → In Implementation

# Or override (emergency only)
backlog task edit 42 -s "In Implementation" --override-workflow
```

#### Issue: Board shows wrong columns

**Error**: Board displays "To Do / In Progress / Done" instead of workflow states

**Solution**:
```bash
# Re-sync workflow states
backlog workflow sync

# Verify workflow is enabled
cat backlog/config.yml | grep workflow_enabled
# Should be: workflow_enabled: true

# Check for errors
backlog workflow validate
```

---

## Conclusion

This platform integration design transforms backlog.md from a simple Kanban board into a workflow-aware development platform that:

1. **Enhances Visibility**: Developers see exactly where features are in the workflow
2. **Enforces Quality**: Workflow constraints ensure artifacts are created before progression
3. **Enables Metrics**: DORA metrics provide data-driven insights for continuous improvement
4. **Simplifies Onboarding**: Workflow hints guide developers through the process
5. **Maintains Compatibility**: Existing projects continue working without changes

**Next Steps**:
1. Review and approve this design document
2. Create implementation tasks in backlog (task-095, task-096)
3. Begin Phase 1 development (WorkflowConfigLoader)
4. Beta test with 5 pilot users
5. Iterate based on feedback

**Success Criteria**:
- 60% of new projects adopt workflow mode within 6 months
- DORA metrics enable 20% improvement in lead time
- Developer NPS increases by +15 points
- Zero regressions for non-workflow projects

---

**Document Status**: ✅ Design Complete | 🚧 Awaiting Review | ⏳ Implementation Not Started

**Last Updated**: 2025-11-30
