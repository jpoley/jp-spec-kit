# PRD: Task Rigor Rules Integration into Flowspec

**Document Version**: 1.1
**Date**: 2025-12-17
**Author**: @pm-planner
**Status**: Draft

---

## CRITICAL: UNIVERSAL ENFORCEMENT

**These rigor rules are MANDATORY for ALL users of Flowspec, not just this project.**

When any developer, team, or organization adopts Flowspec as their development workflow, they are required to follow these rules. This is not optional guidance - it is the foundational law that ensures Flowspec delivers on its promise of quality, traceability, and maintainable software.

**GOD-level enforcement**: The Flowspec workflow will actively block, warn, or require confirmation when rules are violated. Users cannot proceed through workflow phases without satisfying rigor requirements.

---

## 1. Executive Summary

### Problem Statement
Flowspec workflow commands (/flow:assess, /flow:specify, /flow:plan, /flow:implement, /flow:validate, /flow:operate) lack consistent enforcement of critical task hygiene rules. These rules ensure quality, traceability, and maintainability across the development lifecycle, but they are scattered across documentation or missing entirely from individual workflow steps.

**This gap means Flowspec users can bypass essential quality gates, leading to inconsistent outcomes across projects that adopt the Flowspec methodology.**

### Proposed Solution
Integrate the Task Rigor Rules from `build-docs/task-rigor.md` as mandatory, immutable "laws" that are enforced at every phase of the Flowspec workflow. These rules will be embedded into shared include files that all workflow commands consume, ensuring consistent enforcement regardless of which command is executed.

**For all Flowspec users worldwide**: When you use `/flow:*` commands, you agree to follow these rules. The workflow will enforce them.

### Success Metrics (North Star)
- **Primary**: 100% of workflow commands enforce all applicable rigor rules
- **Secondary**: Zero PRs submitted with merge conflicts, failing CI, or missing traceability
- **Tertiary**: All decisions logged in JSONL format with task linkage

### Business Value and Strategic Alignment
- **Quality**: Ensures consistent quality gates across all workflow phases
- **Traceability**: All decisions and artifacts are linked to tasks
- **Maintainability**: Code is always in a working state, even during freeze/push cycles
- **Reduced Friction**: Clear, documented rules reduce ambiguity and rework

---

## 2. User Stories and Use Cases

### Primary User Personas

**Persona 1: Developer (Inner Loop)**
- Executes /flow:implement, /flow:validate
- Needs clear guidance on pre-PR validation, branching, and task updates
- Wants automated enforcement of rules to avoid manual checklist fatigue

**Persona 2: Product Manager (Outer Loop)**
- Executes /flow:assess, /flow:specify
- Needs clear acceptance criteria and traceability requirements
- Wants task dependencies documented before task ordering

**Persona 3: Platform Engineer (DevOps)**
- Executes /flow:plan, /flow:operate
- Needs git worktree conventions, CI validation requirements
- Wants rebase-before-merge enforcement

**Persona 4: AI Agent (Automated Workflow)**
- Executes all workflow commands as subagent
- Needs consistent rule injection at runtime
- Must track current flow status and next steps

### User Journey Map

```
Task Created → Assess → Specify → Plan → Implement → Validate → Operate → Done
     ↓           ↓         ↓        ↓         ↓          ↓         ↓
  Rules:      Plan    Dependencies  Branch   Pre-PR    Rebase    DCO+CI
  Clear AC   Documented  First     Naming   Validation  Check   Sign-off
```

### Detailed User Stories

**US-1: As a developer, I want rigor rules enforced automatically during /flow:implement, so I don't accidentally skip pre-PR validation steps.**

Acceptance Criteria:
- [ ] Pre-PR validation (lint + tests) is mandatory before any PR suggestion
- [ ] Branch naming follows `hostname/task-#/slug-description` pattern
- [ ] Git worktree name matches branch name
- [ ] All decisions are logged to JSONL with task reference

**US-2: As a PM running /flow:specify, I want the command to require clear acceptance criteria before proceeding, so every task is testable.**

Acceptance Criteria:
- [ ] Command validates that acceptance criteria are present and measurable
- [ ] Inter-task dependencies are documented before task ordering
- [ ] Tasks link to relevant beads/agentic task lists

**US-3: As an agent, I want to always know what comes next when a workflow step completes, so I maintain context across handoffs.**

Acceptance Criteria:
- [ ] Each workflow step emits clear "next step" guidance
- [ ] Task memory is updated with key facts specific to the task
- [ ] Workflow state is tracked explicitly in task labels

**US-4: As a developer preparing a PR, I want the validation workflow to prevent submission if CI will fail, so I avoid noisy failed PRs.**

Acceptance Criteria:
- [ ] Rebase from main is enforced (zero merge conflicts)
- [ ] All CI checks simulated locally before PR creation
- [ ] DCO sign-off is verified
- [ ] Copilot comments from previous PRs are addressed

**US-5: As a task owner, I want to freeze work in a safe state, so I can resume without losing context.**

Acceptance Criteria:
- [ ] Task memory is updated with key facts before freeze
- [ ] Code is in a working (if incomplete) state
- [ ] Repo is pushed to remote with facts/decisions documented

### Edge Cases and Error Scenarios

1. **No plan documented**: Block /flow:implement until plan exists
2. **Missing acceptance criteria**: Block /flow:validate until ACs are defined
3. **Merge conflicts detected**: Block PR creation until rebase completed
4. **CI failures predicted**: Block PR, suggest fixes
5. **Decision not logged**: Warn and prompt for JSONL entry
6. **Task freeze without memory update**: Warn that context may be lost

---

## 3. DVF+V Risk Assessment

### Value Risk (Desirability)
- **Risk**: Developers may see rules as bureaucratic overhead
- **Mitigation**: Automate enforcement so rules are invisible when followed; only surface when violated
- **Validation**: Survey developers after 2 weeks of use

### Usability Risk (Experience)
- **Risk**: Too many blocks/warnings could frustrate users
- **Mitigation**: Provide clear, actionable error messages with fix commands
- **Validation**: User testing with verbose vs. minimal messaging

### Feasibility Risk (Technical)
- **Risk**: Modifying all 7+ workflow commands consistently is complex
- **Mitigation**: Use shared include files (`_rigor-rules.md`) consumed by all commands
- **Validation**: Implement for /flow:implement first, then propagate

### Business Viability Risk (Organizational)
- **Risk**: Adoption resistance from teams with existing workflows
- **Mitigation**: Make rules configurable (strict mode vs. warn mode)
- **Validation**: Rollout to one project first, collect feedback

---

## 4. Functional Requirements

### 4.1 Core Features and Capabilities

#### 4.1.1 Shared Rigor Rules Include File

Create `.claude/partials/flow/_rigor-rules.md` containing all mandatory rules organized by phase:

**Setup Phase Rules (Pre-work)**:
- Must have clear, documented plan of action
- Must plan inter-task dependencies first
- Must have clear, testable acceptance criteria
- Must use git worktree with matching branch name
- Branch naming: `hostname/task-#/slug-description`

**Execution Phase Rules (During work)**:
- Log all decisions to JSONL format with task traceability
- Use subagents as much as possible (in parallel)
- Always track current flow status and what's next
- Link backlog tasks to beads for handoffs

**Freeze/Push Rules (Pausing work)**:
- Update task memory with key facts before freeze
- Code must be in working state (incomplete is OK)
- Push to remote with facts documented

**Validation Phase Rules (Pre-merge)**:
- Run /flow:validate on all aspects
- Lint code and perform SAST
- Check coding style and rules
- Verify all CI will pass locally
- Rebase from main (zero merge conflicts)
- Ensure acceptance criteria are met
- Update task status (PR must include task updates)
- Clean up bead statuses

**PR Submission Rules**:
- DCO sign-off required
- CI must pass before submission
- Wait for Copilot review comments
- Fix each comment in new branch (-v2, -v3)
- Close old PR, create new with updated branch
- Repeat until zero Copilot comments

#### 4.1.2 Rule Enforcement Modes

```yaml
rigor_mode: strict  # Options: strict, warn, off
```

- **strict**: Block workflow on rule violations
- **warn**: Show warning but allow continuation
- **off**: Disable checks (not recommended)

#### 4.1.3 Decision Logging

All workflow commands must log decisions to `memory/decisions/{task-id}.jsonl`:

```json
{"timestamp": "2025-12-17T12:00:00Z", "task_id": "task-123", "phase": "implement", "decision": "Use React Query for data fetching", "rationale": "Better caching and error handling", "alternatives_considered": ["SWR", "Custom hooks"]}
```

### 4.2 User Interface Requirements

- Terminal output with clear phase indicators
- Color-coded status: green (pass), yellow (warn), red (block)
- Actionable error messages with specific fix commands
- Progress tracking across workflow phases

### 4.3 API Requirements

No external API changes. Internal changes only.

### 4.4 Integration Requirements

- Integrate with existing `_constitution-check.md` and `_workflow-state.md`
- Extend backlog CLI usage patterns in `_backlog-instructions.md`
- Add new include file referenced by all flow commands

### 4.5 Data Requirements

**New files**:
- `memory/decisions/*.jsonl` - Decision logs per task
- `.claude/partials/flow/_rigor-rules.md` - Shared rules include

**Modified files**:
- All `/flow:*` command templates
- `memory/critical-rules.md` - Reference new rigor rules

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
- Rule checks must complete in <500ms
- Decision logging must not block workflow

### 5.2 Scalability Requirements
- Rules must work for single-person and large team projects
- Decision logs should support thousands of entries per task

### 5.3 Security Requirements
- No secrets in decision logs
- JSONL files should not contain PII

### 5.4 Accessibility Requirements
- Terminal output must be screen-reader friendly
- No color-only indicators (use symbols + color)

### 5.5 Compliance Requirements
- DCO compliance for all commits
- Audit trail via decision logs

---

## 6. Task Breakdown (Backlog Tasks)

**MANDATORY**: Implementation tasks created via backlog CLI.

**All tasks created successfully. Task IDs listed below for traceability.**

### Phase 1: Foundation (Priority: High)

| Task ID | Title | Priority | Labels |
|---------|-------|----------|--------|
| task-541 | Create _rigor-rules.md shared include file | High | rigor, foundation, implement |
| task-542 | Add JSONL decision logging infrastructure | High | rigor, foundation, implement |

### Phase 2: Command Integration (Priority: High/Medium)

| Task ID | Title | Priority | Labels | Dependencies |
|---------|-------|----------|--------|--------------|
| task-543 | Integrate rigor rules into /flow:implement | High | rigor, implement, command | task-541 |
| task-544 | Integrate rigor rules into /flow:validate | High | rigor, validate, command | task-541 |
| task-545 | Integrate rigor rules into /flow:specify | High | rigor, specify, command | task-541 |
| task-546 | Integrate rigor rules into /flow:assess | Medium | rigor, assess, command | task-541 |
| task-547 | Integrate rigor rules into /flow:plan | Medium | rigor, plan, command | task-541, task-542 |
| task-548 | Integrate rigor rules into /flow:operate | Medium | rigor, operate, command | task-541 |

### Phase 3: Tooling (Priority: Medium)

| Task ID | Title | Priority | Labels | Dependencies |
|---------|-------|----------|--------|--------------|
| task-549 | Add /flow:freeze command for task suspension | Medium | rigor, freeze, command, new-feature | task-541 |
| task-550 | Add workflow status tracking to all commands | Medium | rigor, workflow, tracking | task-541 |

### Phase 4: Documentation (Priority: Low)

| Task ID | Title | Priority | Labels | Dependencies |
|---------|-------|----------|--------|--------------|
| task-551 | Update critical-rules.md with rigor rules reference | Low | rigor, docs | task-541 |
| task-552 | Create rigor rules troubleshooting guide | Low | rigor, docs, guide | task-541, task-551 |

### Implementation Order (Dependency Chain)

```
task-541 (Foundation) ─┬─► task-542 (JSONL) ─► task-547 (plan)
                       │
                       ├─► task-543 (implement)
                       ├─► task-544 (validate)
                       ├─► task-545 (specify)
                       ├─► task-546 (assess)
                       ├─► task-548 (operate)
                       ├─► task-549 (freeze)
                       ├─► task-550 (tracking)
                       └─► task-551 (docs) ─► task-552 (troubleshooting)
```

**Total Tasks**: 12 tasks created
**Estimated Effort**: Foundation (2 tasks) → Commands (6 tasks) → Tooling (2 tasks) → Docs (2 tasks)

---

## 7. Discovery and Validation Plan

### Learning Goals and Hypotheses

**H1**: Developers will adopt rigor rules if enforcement is automated and non-intrusive
- **Experiment**: A/B test with strict vs. warn modes
- **Success Criteria**: 80% compliance in strict mode, <20% override requests

**H2**: Decision logging improves context preservation across handoffs
- **Experiment**: Track context recovery time before/after
- **Success Criteria**: 50% reduction in "what happened here?" questions

**H3**: Pre-PR validation reduces CI failures
- **Experiment**: Measure CI failure rate before/after
- **Success Criteria**: 90% reduction in first-attempt CI failures

### Validation Experiments

1. **Pilot Project**: Enable on one active feature branch for 1 week
2. **User Interviews**: Interview 3 developers after pilot
3. **Metrics Collection**: CI failure rates, override frequency, decision log usage

### Go/No-Go Decision Points

- **Go**: 70%+ compliance, positive developer feedback
- **No-Go**: >50% override requests, significant workflow slowdown

---

## 8. Acceptance Criteria and Testing

### Acceptance Test Scenarios

**AT-1: Pre-PR Validation Enforcement**
- Given a developer has code changes
- When they run /flow:validate
- Then lint and tests must pass before PR suggestion appears

**AT-2: Branch Naming Convention**
- Given a developer starts /flow:implement
- When they create a git worktree
- Then branch name must match `hostname/task-#/slug-description`

**AT-3: Decision Logging**
- Given a developer makes an architecture decision
- When /flow:plan completes
- Then a JSONL entry exists in `memory/decisions/`

**AT-4: Merge Conflict Prevention**
- Given a PR is being created
- When merge conflicts exist with main
- Then PR creation is blocked with rebase instructions

**AT-5: Task Memory Update on Freeze**
- Given a developer runs /flow:freeze
- When freeze completes
- Then task memory contains updated key facts

### Definition of Done

1. All rigor rules documented in `_rigor-rules.md`
2. All /flow:* commands include rigor rules
3. Decision logging infrastructure operational
4. Pre-PR validation enforced in /flow:implement and /flow:validate
5. /flow:freeze command implemented
6. Workflow status tracking in all commands
7. Documentation updated
8. Unit tests for rule validation logic
9. Integration tests for command flows

### Quality Gates

- 100% rule coverage across workflow commands
- 80%+ test coverage for new code
- Zero critical lint violations
- All existing tests continue to pass

### Test Coverage Requirements

- Unit tests for each rigor rule check
- Integration tests for command sequences
- E2E test for full workflow with rules enabled

---

## 9. Dependencies and Constraints

### Technical Dependencies

- Backlog.md CLI (existing)
- Git CLI (existing)
- JSONL logging capability (new)
- Template include system (existing)

### External Dependencies

- None (all internal to Flowspec)

### Timeline Constraints

- Foundation tasks should complete first (enable other work)
- Command integration can proceed in parallel after foundation

### Resource Constraints

- Single PM for task creation and tracking
- Developer resources for implementation

### Risk Factors

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Developer resistance to rules | High | Medium | Warn mode option, clear messaging |
| Performance overhead | Medium | Low | Async logging, caching |
| Breaking existing workflows | High | Low | Gradual rollout, feature flags |

---

## 10. Success Metrics (Outcome-Focused)

### North Star Metric

**100% Rigor Rule Compliance Rate**: Percentage of workflow runs that pass all applicable rigor rules without overrides.

### Leading Indicators (Early Signals)

- Number of rule violations detected (should decrease over time)
- Override frequency (should be <10%)
- Decision log entries per task (should be >0)

### Lagging Indicators (Final Outcomes)

- CI first-attempt pass rate (target: 95%)
- Context recovery time for paused tasks (target: <5 minutes)
- Merge conflict occurrences (target: zero)

### Measurement Approach

- Log all rule checks with pass/fail status
- Track overrides with reason codes
- Weekly metrics review during rollout

### Target Values

| Metric | Baseline | Target | Timeframe |
|--------|----------|--------|-----------|
| CI first-pass rate | 70% | 95% | 4 weeks |
| Rule compliance | 0% | 100% | 2 weeks |
| Override rate | N/A | <10% | 4 weeks |
| Merge conflicts/week | 3+ | 0 | 4 weeks |

---

## Appendix A: Rules Reference

### From task-rigor.md

**Task Setup Hygiene**:
1. Must have a clear and documented plan of action (ask if missing)
2. Must plan inter-task dependencies first (for task order chain)
3. Must have clear and testable acceptance criteria
4. Must use subagents as much as possible (in parallel)
5. Must use git worktree with matching branch name
6. Branch naming: `hostname/task-#/slug-description`
7. All decisions must be logged in JSONL format (with task traceability)
8. Use backlog for human tasks, link to beads for agentic handoffs
9. Agent MUST track current flow status and what's next

**Task Freeze/Push**:
1. Must continuously update task memory with key facts
2. Keep repo (remote) up to date with code + facts
3. Code must be in working state (incomplete OK)

**Task Validation**:
1. Always run /flow:validate on all aspects
2. Must have traceability of decisions (JSONL), documentation, passing tests
3. Always lint code and perform SAST
4. Always check coding style + rules
5. Always verify all CI will pass
6. Always rebase from main (zero merge conflicts)
7. Ensure acceptance criteria are met
8. Must update task status as we go (PR must include task updates)
9. Must clean up bead statuses

**Task Push**:
1. Push a PR
2. Ensure DCO + all CI passes (fix if not, same PR)
3. Wait for Copilot comments
4. Review and fix each comment in new branch (-v2, -v3)
5. Close old PR, push new one with updated branch
6. Repeat until zero Copilot comments (then ready for human review)

---

*PRD generated by @pm-planner agent for Flowspec Spec-Driven Development*
