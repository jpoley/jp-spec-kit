# Flowspec Commands Audit: Task Management Integration Analysis

**Audit Date**: 2025-11-28
**Auditor**: Claude Agent
**Purpose**: Identify backlog.md integration points across all flowspec commands

---

## Executive Summary

This audit examines all 6 flowspec commands to document their current task management approach and identify integration points for backlog.md CLI integration. The analysis reveals:

- **6 primary commands** with distinct workflows
- **15+ sub-agent spawn points** across all commands
- **Multiple lifecycle hooks** for task tracking (pre-execution, during-execution, post-execution)
- **No current backlog.md integration** - all task management is manual/ad-hoc
- **Standardized Task tool invocations** make integration straightforward

---

## Command Overview

| Command | Purpose | Sub-Agents | Current Task Handling |
|---------|---------|------------|----------------------|
| `/flow:specify` | Create/update feature specs | 1 (PM Planner) | Creates task breakdown in PRD (section 6) but no CLI calls |
| `/flow:plan` | Architecture & platform planning | 2 (Architect, Platform Engineer) | Creates architectural principles but no task tracking |
| `/flow:research` | Research & business validation | 2 (Researcher, Business Validator) | Sequential execution, no task tracking |
| `/flow:implement` | Feature implementation | 3-5 (Frontend, Backend, AI/ML Engineers + Code Reviewers) | No task tracking, manual coordination |
| `/flow:validate` | QA, security, docs, release | 4 (Quality Guardian, Security, Tech Writer, Release Manager) | Manual checklist in Release Manager, no CLI integration |
| `/flow:operate` | SRE operations & infrastructure | 1 (SRE Agent) | No task tracking |

**Total sub-agents across all commands**: 15+ (exact count depends on feature requirements in implement phase)

---

## Detailed Command Analysis

### 1. `/flow:specify` - Product Requirements Manager

**File**: `.claude/commands/flow/specify.md`

#### Current Task Handling
- **Section 6 of PRD Template**: "Task Breakdown"
  - Epics and user stories
  - Task dependencies
  - Priority ordering (P0, P1, P2)
  - Estimated complexity (S, M, L, XL)
  - Success criteria for each task
- **No CLI integration**: Tasks are created manually in spec.md or tasks.md, not via backlog.md CLI

#### Sub-Agents
1. **Product Requirements Manager** (general-purpose agent)
   - SVPG principles expert
   - Outcome-driven development
   - DVF+V risk framework

#### Integration Points

**Pre-Execution (Entry Point)**:
```bash
# Before launching PM agent
backlog task list -s "To Do" --plain  # Show available specification tasks
backlog task <id> --plain             # Show details of current spec task
backlog task edit <id> -s "In Progress" -a @pm-planner  # Mark task in progress
```

**During Execution (Within Agent)**:
- PM agent could call backlog CLI to:
  - Create tasks from task breakdown (section 6)
  - Set dependencies between tasks
  - Assign priorities and labels

**Post-Execution (Exit Point)**:
```bash
# After PRD completion
backlog task edit <id> --check-ac 1 --check-ac 2  # Mark PRD ACs complete
backlog task edit <id> --notes "PRD created with X epics, Y user stories, Z tasks"
backlog task edit <id> -s Done
```

**Recommended CLI Calls**:
- [ ] Entry: `backlog task edit <id> -s "In Progress" -a @pm-planner`
- [ ] During: `backlog task create` for each epic/user story in task breakdown
- [ ] During: `backlog task edit <subtask-id> --dep task-<parent>` for dependencies
- [ ] Exit: `backlog task edit <id> --check-ac <indices>` for all ACs
- [ ] Exit: `backlog task edit <id> --notes "<summary>"`
- [ ] Exit: `backlog task edit <id> -s Done`

---

### 2. `/flow:plan` - Architecture & Platform Planning

**File**: `.claude/commands/flow/plan.md`

#### Current Task Handling
- **Parallel execution model**: Two agents work simultaneously
- **Builds constitution**: Architectural and platform principles
- **No task tracking**: Manual coordination between agents

#### Sub-Agents
1. **Software Architect** (general-purpose agent)
   - Gregor Hohpe's principles
   - Enterprise Integration Patterns
   - Platform Quality Framework (7 C's)
   - Outputs: ADRs, architecture blueprints, architectural principles for constitution

2. **Platform Engineer** (general-purpose agent)
   - DevSecOps and CI/CD excellence
   - DORA metrics mandate
   - SLSA compliance
   - Outputs: CI/CD pipeline design, infrastructure architecture, platform principles for constitution

#### Integration Points

**Pre-Execution (Entry Point)**:
```bash
# Before launching planning agents
backlog task edit <id> -s "In Progress" -a @architect,@platform-engineer
backlog task edit <id> --plan "1. Parallel architecture & platform planning\n2. Consolidate findings\n3. Build constitution"
```

> **Note on `--plan` flag**: This is an existing backlog.md CLI feature for adding implementation plans to tasks. For multi-line plans, use shell-appropriate quoting:
> - **Bash/Zsh**: `--plan $'Step 1\nStep 2\nStep 3'` (ANSI-C quoting)
> - **POSIX**: `--plan "$(printf 'Step 1\nStep 2')"` (printf subshell)
> - **PowerShell**: `--plan "Step 1\`nStep 2"` (backtick-n)

**During Execution (Within Agents)**:
- Each agent could track subtasks:
  - Architect: ADR creation, architecture blueprint, integration patterns
  - Platform Engineer: CI/CD design, infrastructure planning, DevSecOps setup

**Post-Execution (Exit Point)**:
```bash
# After both agents complete
backlog task edit <id> --check-ac 1  # Architecture design complete
backlog task edit <id> --check-ac 2  # Platform design complete
backlog task edit <id> --check-ac 3  # Constitution updated
backlog task edit <id> --notes "Architecture and platform planning complete. ADRs: X, Constitution sections: Y"
backlog task edit <id> -s Done
```

**Recommended CLI Calls**:
- [ ] Entry: `backlog task edit <id> -s "In Progress" -a @architect,@platform-engineer`
- [ ] Entry: `backlog task edit <id> --plan "<multi-step plan>"`
- [ ] During: `backlog task create` for architecture subtasks
- [ ] During: `backlog task create` for platform subtasks
- [ ] Exit: `backlog task edit <id> --check-ac <indices>`
- [ ] Exit: `backlog task edit <id> --notes "<consolidated summary>"`
- [ ] Exit: `backlog task edit <id> -s Done`

---

### 3. `/flow:research` - Research & Business Validation

**File**: `.claude/commands/flow/research.md`

#### Current Task Handling
- **Sequential execution**: Researcher → Business Validator
- **Context passing**: Research findings passed to business validator
- **No task tracking**: Manual coordination, no CLI integration

#### Sub-Agents
1. **Researcher** (general-purpose agent)
   - Market intelligence
   - Technical assessment
   - Competitive analysis
   - Trend forecasting
   - Outputs: Research report with market analysis, competitive landscape, technical feasibility

2. **Business Validator** (general-purpose agent)
   - Financial viability assessment
   - Market validation
   - Operational feasibility
   - Strategic alignment
   - Outputs: Business validation report with Go/No-Go recommendation

#### Integration Points

**Pre-Execution (Entry Point)**:
```bash
# Before launching researcher
backlog task edit <id> -s "In Progress" -a @researcher
backlog task edit <id> --plan "1. Market & technical research\n2. Business validation\n3. Consolidate reports"
```

**During Execution (Phase Transitions)**:
```bash
# After research phase, before validation phase
backlog task edit <id> --check-ac 1  # Research complete
backlog task edit <id> -a @business-validator  # Change assignee
```

**Post-Execution (Exit Point)**:
```bash
# After both phases complete
backlog task edit <id> --check-ac 2  # Business validation complete
backlog task edit <id> --notes "Research: TAM $X, SAM $Y. Validation: Go/No-Go with confidence Z%"
backlog task edit <id> -s Done
```

**Recommended CLI Calls**:
- [ ] Entry: `backlog task edit <id> -s "In Progress" -a @researcher`
- [ ] Entry: `backlog task edit <id> --plan "<phase plan>"`
- [ ] Phase transition: `backlog task edit <id> --check-ac 1` (research done)
- [ ] Phase transition: `backlog task edit <id> -a @business-validator`
- [ ] Exit: `backlog task edit <id> --check-ac 2` (validation done)
- [ ] Exit: `backlog task edit <id> --notes "<findings summary>"`
- [ ] Exit: `backlog task edit <id> -s Done`

---

### 4. `/flow:implement` - Feature Implementation

**File**: `.claude/commands/flow/implement.md`

#### Current Task Handling
- **Conditional parallel execution**: Launch applicable engineers (frontend/backend/AI-ML)
- **Sequential code review**: After implementation, review agents run
- **No task tracking**: Manual coordination across multiple agents

#### Sub-Agents (Variable based on requirements)

**Phase 1 - Implementation (Parallel)**:
1. **Frontend Engineer** (general-purpose agent, conditional)
   - React/React Native expertise
   - Performance, accessibility, TypeScript
   - Outputs: Component code, tests, styling

2. **Backend Engineer** (general-purpose agent, conditional)
   - Go/TypeScript/Python expertise
   - API development, CLI tools, database design
   - Outputs: API code, business logic, tests

3. **AI/ML Engineer** (ai-ml-engineer agent, conditional)
   - Model development, MLOps
   - Outputs: Training pipeline, inference service, monitoring

**Phase 2 - Code Review (Sequential)**:
4. **Frontend Code Reviewer** (general-purpose agent, if frontend implemented)
   - Code quality, performance, accessibility review
   - Outputs: Categorized feedback (Critical/High/Medium/Low)

5. **Backend Code Reviewer** (general-purpose agent, if backend implemented)
   - Security, performance, API design review
   - Outputs: Categorized feedback with remediation steps

#### Integration Points

**Pre-Execution (Entry Point)**:
```bash
# Before launching implementation
backlog task edit <id> -s "In Progress" -a @frontend,@backend
backlog task edit <id> --plan "1. Parallel implementation (FE/BE)\n2. Code review\n3. Address feedback\n4. Integration testing"
```

**During Execution (Phase Transitions)**:
```bash
# After implementation phase
backlog task edit <id> --check-ac 1  # Frontend implementation complete
backlog task edit <id> --check-ac 2  # Backend implementation complete

# After code review phase
backlog task edit <id> --check-ac 3  # Code reviews complete
backlog task edit <id> --append-notes "Review feedback: X critical, Y high priority items"
```

> **⚠️ BLOCKED**: Automatic code review phase tracking requires backlog.md CLI integration to be implemented first. See task-107 (Entry/Exit Hooks) and task-108 (Progress Tracking) as prerequisites.

**Post-Execution (Exit Point)**:
```bash
# After all phases complete
backlog task edit <id> --check-ac 4  # All feedback addressed
backlog task edit <id> --check-ac 5  # Integration tests passing
backlog task edit <id> --notes "Implementation complete. Frontend: X components, Backend: Y endpoints. All reviews addressed."
backlog task edit <id> -s Done
```

**Recommended CLI Calls**:
- [ ] Entry: `backlog task edit <id> -s "In Progress" -a @frontend,@backend`
- [ ] Entry: `backlog task edit <id> --plan "<implementation plan>"`
- [ ] Phase 1 done: `backlog task edit <id> --check-ac 1 --check-ac 2` (implementation complete)
- [ ] Phase 2 done: `backlog task edit <id> --check-ac 3` (reviews complete)
- [ ] Iteration: `backlog task edit <id> --append-notes "<feedback summary>"`
- [ ] Final: `backlog task edit <id> --check-ac 4 --check-ac 5`
- [ ] Exit: `backlog task edit <id> --notes "<final summary>"`
- [ ] Exit: `backlog task edit <id> -s Done`

> **📋 AC Prerequisite**: Acceptance criteria must be defined in the task **before** using `--check-ac`. The indices (1-5 in this example) correspond to the order ACs were added via `backlog task edit <id> --ac "criterion"`. Tasks should be created with complete ACs upfront, or ACs added during entry phase before checking begins.

---

### 5. `/flow:validate` - QA & Validation

**File**: `.claude/commands/flow/validate.md`

#### Current Task Handling
- **Phase 1 (Parallel)**: QA testing + Security validation
- **Phase 2 (Sequential)**: Documentation after validation results available
- **Phase 3 (Final Gate)**: Release management with human approval
- **Manual checklist**: Release Manager has checklist but no CLI integration

#### Sub-Agents

**Phase 1 - Testing & Security (Parallel)**:
1. **Quality Guardian** (general-purpose agent)
   - Functional, API, integration, performance testing
   - Risk analysis and failure mode identification
   - Outputs: Comprehensive test report with quality metrics

2. **Secure-by-Design Engineer** (general-purpose agent)
   - Code security review, dependency scanning
   - Infrastructure security, compliance validation
   - Threat modeling, penetration testing
   - Outputs: Security report with severity-categorized findings

**Phase 2 - Documentation (Sequential)**:
3. **Technical Writer** (general-purpose agent)
   - API, user, technical, release documentation
   - Outputs: Complete documentation package

**Phase 3 - Release Management (Final Gate)**:
4. **Release Manager** (general-purpose agent)
   - Pre-release validation checklist
   - Risk assessment
   - **Human approval checkpoint** (critical)
   - Outputs: Release readiness report with go/no-go recommendation

#### Integration Points

**Pre-Execution (Entry Point)**:
```bash
# Before launching validation
backlog task edit <id> -s "In Progress" -a @qa,@security
backlog task edit <id> --plan "1. Parallel QA + Security validation\n2. Documentation\n3. Release readiness\n4. Human approval"
```

**During Execution (Phase Transitions)**:
```bash
# After Phase 1 (QA + Security)
backlog task edit <id> --check-ac 1  # QA tests complete
backlog task edit <id> --check-ac 2  # Security assessment complete
backlog task edit <id> --append-notes "QA: X tests passed, Y failed. Security: Z findings (A critical, B high)"
backlog task edit <id> -a @tech-writer

# After Phase 2 (Documentation)
backlog task edit <id> --check-ac 3  # Documentation complete
backlog task edit <id> -a @release-manager

# Phase 3 (Release Management)
backlog task edit <id> --check-ac 4  # Pre-release validation complete
# Human approval checkpoint - DO NOT proceed without explicit approval
```

**Post-Execution (After Human Approval)**:
```bash
# After human approval granted
backlog task edit <id> --append-notes "Human approval: APPROVED by <name> on <date>"
backlog task edit <id> -s Done
```

**Recommended CLI Calls**:
- [ ] Entry: `backlog task edit <id> -s "In Progress" -a @qa,@security`
- [ ] Entry: `backlog task edit <id> --plan "<validation plan>"`
- [ ] Phase 1 done: `backlog task edit <id> --check-ac 1 --check-ac 2`
- [ ] Phase 1 done: `backlog task edit <id> --append-notes "<test/security results>"`
- [ ] Phase 2 assignee: `backlog task edit <id> -a @tech-writer`
- [ ] Phase 2 done: `backlog task edit <id> --check-ac 3`
- [ ] Phase 3 assignee: `backlog task edit <id> -a @release-manager`
- [ ] Phase 3 done: `backlog task edit <id> --check-ac 4`
- [ ] **Human approval gate**: Wait for explicit approval, do NOT mark Done
- [ ] Post-approval: `backlog task edit <id> --append-notes "Approval: <details>"`
- [ ] Exit: `backlog task edit <id> -s Done`

> **🔒 CRITICAL: Human Approval Gate**
>
> This command has a **mandatory human approval checkpoint** before release. The Release Manager agent:
> 1. Generates a release readiness report with go/no-go recommendation
> 2. **MUST** pause execution and notify the human operator
> 3. Human reviews: security findings, test results, documentation completeness
> 4. Human explicitly approves (via comment, CLI, or designated channel)
> 5. Only after documented approval can the task be marked Done
>
> **Never** mark a validate task as Done without explicit human sign-off. This ensures production deployments are human-verified.

---

### 6. `/flow:operate` - SRE Operations

**File**: `.claude/commands/flow/operate.md`

#### Current Task Handling
- **Single-agent execution**: SRE agent handles all operational aspects
- **Complex deliverables**: CI/CD, Kubernetes, observability, incident management
- **Template references**: Command references GitHub Actions templates in `templates/github-actions/`
- **No task tracking**: Manual coordination across deliverables

#### Sub-Agents
1. **SRE Agent** (general-purpose agent)
   - CI/CD excellence (using stack-specific templates)
   - Kubernetes operations
   - DevSecOps integration
   - Observability (metrics, logs, traces)
   - Incident management
   - Infrastructure as Code
   - Outputs: Complete operational package (pipelines, manifests, runbooks, IaC)

#### Key Operational Areas
1. Service Level Objectives (SLOs)
2. CI/CD Pipeline Architecture (GitHub Actions with outer-loop templates)
3. Kubernetes Architecture and Configuration
4. DevSecOps Integration
5. Observability Stack
6. Incident Management
7. Infrastructure as Code (IaC)
8. Performance and Scalability
9. Disaster Recovery and Business Continuity

#### Integration Points

**Pre-Execution (Entry Point)**:
```bash
# Before launching SRE agent
backlog task edit <id> -s "In Progress" -a @sre-agent
backlog task edit <id> --plan "1. SLO definition\n2. CI/CD pipeline setup\n3. K8s config\n4. DevSecOps\n5. Observability\n6. Incident mgmt\n7. IaC\n8. Perf & scale\n9. DR planning"
```

**During Execution (Granular Tracking)**:
```bash
# As SRE agent completes each operational area
backlog task edit <id> --check-ac 1  # SLOs defined
backlog task edit <id> --check-ac 2  # CI/CD pipelines implemented
backlog task edit <id> --check-ac 3  # K8s manifests created
backlog task edit <id> --check-ac 4  # DevSecOps integrated
backlog task edit <id> --check-ac 5  # Observability stack deployed
backlog task edit <id> --check-ac 6  # Incident procedures documented
backlog task edit <id> --check-ac 7  # IaC implemented
backlog task edit <id> --check-ac 8  # Perf/scale validated
backlog task edit <id> --check-ac 9  # DR procedures tested
```

**Post-Execution (Exit Point)**:
```bash
# After all operational deliverables complete
backlog task edit <id> --notes "Operations complete. Pipelines: X, K8s manifests: Y, SLOs: Z, Runbooks: W"
backlog task edit <id> -s Done
```

**Recommended CLI Calls**:
- [ ] Entry: `backlog task edit <id> -s "In Progress" -a @sre-agent`
- [ ] Entry: `backlog task edit <id> --plan "<9-phase operational plan>"`
- [ ] During: `backlog task edit <id> --check-ac <index>` for each completed area (1-9)
- [ ] During: `backlog task edit <id> --append-notes "<progress update>"`
- [ ] Exit: `backlog task edit <id> --notes "<comprehensive summary>"`
- [ ] Exit: `backlog task edit <id> -s Done`

**Special Note**: This command has the most granular deliverables (9 areas), making AC tracking especially valuable.

---

## Cross-Command Patterns

### Common Lifecycle Hooks

All commands follow similar patterns that can be standardized:

1. **Entry Hook (Pre-Execution)**
   - Mark task as "In Progress"
   - Assign to agent(s)
   - Add implementation plan

2. **Progress Tracking (During Execution)**
   - Check acceptance criteria as completed
   - Append notes for progress updates
   - Change assignees for sequential phases

3. **Exit Hook (Post-Execution)**
   - Check all remaining ACs
   - Add final implementation notes (PR description)
   - Mark task as Done

### Agent Assignment Patterns

| Command | Entry Assignee(s) | Phase Transitions |
|---------|------------------|-------------------|
| specify | `@pm-planner` | None (single-agent) |
| plan | `@architect,@platform-engineer` | None (parallel agents) |
| research | `@researcher` → `@business-validator` | Sequential transition |
| implement | `@frontend-eng,@backend-eng` → `@frontend-reviewer,@backend-reviewer` | Implementation (parallel) → Code Review (sequential) |
| validate | `@qa-guardian,@security-eng` → `@tech-writer` → `@release-mgr` | 3-phase sequential |
| operate | `@sre-agent` | None (single-agent, multi-phase deliverables) |

### Standard Agent Naming Convention

All agent assignees use a consistent naming pattern: `@<role>[-<specialty>]`

| Agent | Standard Name | Description |
|-------|--------------|-------------|
| Product Requirements Manager | `@pm-planner` | PRD creation, SVPG methodology |
| Software Architect | `@architect` | Architecture design, ADRs |
| Platform Engineer | `@platform-engineer` | CI/CD, infrastructure |
| Researcher | `@researcher` | Market/technical research |
| Business Validator | `@business-validator` | Financial/strategic validation |
| Frontend Engineer | `@frontend-eng` | React/React Native implementation |
| Backend Engineer | `@backend-eng` | Go/TypeScript/Python APIs |
| AI/ML Engineer | `@aiml-eng` | Model development, MLOps |
| Frontend Code Reviewer | `@frontend-reviewer` | Frontend quality review |
| Backend Code Reviewer | `@backend-reviewer` | Backend security/performance review |
| Quality Guardian | `@qa-guardian` | Comprehensive testing |
| Secure-by-Design Engineer | `@security-eng` | Security assessment |
| Technical Writer | `@tech-writer` | Documentation creation |
| Release Manager | `@release-mgr` | Release coordination |
| SRE Agent | `@sre-agent` | Operations, observability |

---

## Integration Point Checklist

### Per-Command Integration Requirements

#### `/flow:specify`
- [ ] Entry: Set task in progress, assign PM planner
- [ ] During: Create tasks from task breakdown (section 6 of PRD)
- [ ] During: Set task dependencies and priorities
- [ ] Exit: Check ACs, add notes, mark done

#### `/flow:plan`
- [ ] Entry: Set in progress, assign both architects
- [ ] Entry: Add implementation plan
- [ ] During: Create architecture subtasks
- [ ] During: Create platform subtasks
- [ ] Exit: Check ACs, add consolidated notes, mark done

#### `/flow:research`
- [ ] Entry: Set in progress, assign researcher
- [ ] Entry: Add phase plan
- [ ] Phase 1→2: Check research AC, change assignee to validator
- [ ] Exit: Check validation AC, add findings summary, mark done

#### `/flow:implement`
- [ ] Entry: Set in progress, assign applicable engineers
- [ ] Entry: Add implementation plan
- [ ] Phase 1 done: Check implementation ACs (FE/BE/ML)
- [ ] Phase 2 done: Check review AC, append feedback notes
- [ ] Iteration: Append feedback resolution notes
- [ ] Exit: Check all ACs, add final summary, mark done

#### `/flow:validate`
- [ ] Entry: Set in progress, assign QA + security
- [ ] Entry: Add 4-phase plan
- [ ] Phase 1 done: Check QA + security ACs, append results
- [ ] Phase 2 assignee: Change to tech writer
- [ ] Phase 2 done: Check documentation AC
- [ ] Phase 3 assignee: Change to release manager
- [ ] Phase 3 done: Check release readiness AC
- [ ] **CRITICAL**: Wait for human approval before marking done
- [ ] Post-approval: Append approval details, mark done

#### `/flow:operate`
- [ ] Entry: Set in progress, assign SRE agent
- [ ] Entry: Add 9-phase operational plan
- [ ] During: Check ACs for each completed operational area (1-9)
- [ ] During: Append progress notes per area
- [ ] Exit: Add comprehensive summary, mark done

---

## Recommendations

### High-Priority Integration Points

1. **Entry Hooks (All Commands)**
   - Standardize task activation: `backlog task edit <id> -s "In Progress" -a <agent>`
   - Always add implementation plan before agent execution

2. **Progress Tracking (Multi-Phase Commands)**
   - Use AC checking for phase completion tracking
   - Use `--append-notes` for incremental progress updates
   - Change assignees to reflect current phase owner

3. **Exit Hooks (All Commands)**
   - Standardize task completion: Check all ACs, add notes, mark done
   - Implementation notes should serve as PR description template

4. **Human Approval Gates (validate command)**
   - Never bypass the human approval checkpoint
   - Clearly document approval decision in task notes

### Implementation Strategy

**Phase 1: Entry/Exit Hooks (Foundation)**
- Add entry hook to all 6 commands (assign + in-progress)
- Add exit hook to all 6 commands (check ACs + notes + done)

**Phase 2: Progress Tracking (Enhancement)**
- Add phase transition tracking for multi-phase commands
- Implement AC checking during execution
- Add progress notes for long-running agents

**Phase 3: Task Creation (Advanced)**
- Enable PM planner to create subtasks from task breakdown
- Enable agents to create follow-up tasks
- Implement dependency tracking

### Code Changes Required

All integration points require modifications to:
- `.claude/commands/flow/*.md` - Add CLI invocations around Task tool calls
- Documentation updates - Document new task tracking behavior

No changes required to:
- Agent context (remains unchanged)
- Task tool invocations (already standardized)
- Underlying agent capabilities

---

## Appendix: Sub-Agent Summary

### Complete Agent Roster (15+ agents)

| # | Agent | Type | Command | Role |
|---|-------|------|---------|------|
| 1 | Product Requirements Manager | General-purpose | specify | PRD creation with DVF+V framework |
| 2 | Software Architect | General-purpose | plan | Architecture design, ADRs, integration patterns |
| 3 | Platform Engineer | General-purpose | plan | CI/CD, infrastructure, DevSecOps |
| 4 | Researcher | General-purpose | research | Market intelligence, technical assessment |
| 5 | Business Validator | General-purpose | research | Financial viability, strategic fit |
| 6 | Frontend Engineer | General-purpose | implement | React/React Native implementation |
| 7 | Backend Engineer | General-purpose | implement | Go/TypeScript/Python API/CLI development |
| 8 | AI/ML Engineer | ai-ml-engineer | implement | Model development, MLOps |
| 9 | Frontend Code Reviewer | General-purpose | implement | Frontend quality, performance, accessibility |
| 10 | Backend Code Reviewer | General-purpose | implement | Backend security, performance, API design |
| 11 | Quality Guardian | General-purpose | validate | Comprehensive testing, risk analysis |
| 12 | Secure-by-Design Engineer | General-purpose | validate | Security assessment, compliance |
| 13 | Technical Writer | General-purpose | validate | Documentation creation |
| 14 | Release Manager | General-purpose | validate | Release coordination, human approval |
| 15 | SRE Agent | General-purpose | operate | Operations, CI/CD, observability, incident mgmt |

---

## Conclusion

This audit identifies comprehensive integration opportunities across all 6 flowspec commands. The standardized Task tool invocation pattern makes integration straightforward - all commands follow similar lifecycle patterns (entry → progress → exit) that map cleanly to backlog.md CLI operations.

Key findings:
- ✅ Clear integration points at command boundaries
- ✅ Standardized agent spawn patterns
- ✅ Well-defined lifecycle hooks
- ✅ Existing task awareness in PRD task breakdown and constitution outputs
- ❌ Zero current CLI integration (manual task management)
- ❌ No automated task creation from agent outputs

**Next Steps**: Implement Phase 1 (entry/exit hooks) across all 6 commands to establish foundation for task tracking integration.
