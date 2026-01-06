# ADR-003: Upgrade-Repo Implementation Approach

## Status

Proposed

## Context

Following [ADR-002: Upgrade-Repo Architecture Redesign](./ADR-002-upgrade-repo-architecture-redesign.md), this ADR defines the specific implementation approach, ordering, and dependencies for fixing the `flowspec upgrade-repo` command.

### Implementation Constraints

1. **P0 Blocker Status**: This is blocking the flowspec release
2. **Backward Compatibility**: Must not break existing projects
3. **Testing Requirements**: Each phase must be testable independently
4. **Size Management**: The `__init__.py` file is already 360KB - refactoring may be needed
5. **Migration Path**: Users may be on v1.0, v1.5, or even unreleased versions

### Work Breakdown

Based on the task-579 epic, there are **18 subtasks** organized into 5 phases:

- **Phase 0 (P0)**: Root cause fixes - 6 tasks
- **Phase 1 (P1)**: Core template fixes - 6 tasks
- **Phase 2 (P2)**: MCP configuration - 3 tasks
- **Phase 4 (P4)**: Documentation - 2 tasks
- **Phase 5 (P5)**: Verification - 1 task

## Decision

**We will implement the upgrade-repo fix in a strict dependency-ordered sequence with validation gates between phases.**

### Implementation Phases

#### Phase 0: Foundation (P0 - Critical Path)

**Goal:** Remove broken/deprecated elements that block everything else.

**Tasks:**

| Task | Description | Blocking | Output Artifact |
|------|-------------|----------|-----------------|
| 579.01 | Remove ALL `/flow:operate` references | 579.05, 579.16 | Clean codebase |
| 579.02 | Remove ALL broken `{{INCLUDE:}}` directives | 579.07 | Clean templates |
| 579.03 | Fix `upgrade-repo` to call `generate_mcp_json()` | None | Updated CLI |
| 579.04 | Fix `upgrade-repo` to sync `.claude/skills/` | None | Updated CLI |
| 579.05 | Fix `upgrade-repo` to update `flowspec_workflow.yml` to v2.0 | 579.01 | Updated CLI |
| 579.06 | Fix `upgrade-repo` to remove deprecated files/directories | None | Updated CLI |

**Critical Path:** 579.01 → 579.05

**Verification Gate:**
```bash
# No /flow:operate references remain
rg -i "flow:operate" . --type md --type py --type yaml | wc -l
# Should return: 0

# No {{INCLUDE:}} directives remain in templates
rg "{{INCLUDE:" templates/ | wc -l
# Should return: 0

# upgrade-repo function contains new logic
rg "generate_mcp_json|sync_skills|upgrade_workflow_config" src/flowspec_cli/__init__.py | wc -l
# Should return: >= 3
```

**Duration Estimate:** 2-3 days

---

#### Phase 1: Agent Template Fixes (P1 - High Priority)

**Goal:** Fix agent naming convention and template structure.

**Tasks:**

| Task | Description | Blocking | Output Artifact |
|------|-------------|----------|-----------------|
| 579.07 | Fix agent filename convention (hyphens → dots) | 579.12 | Updated templates |
| 579.08 | Fix agent names (kebab-case → PascalCase) | 579.12 | Updated frontmatter |
| 579.09 | Add missing `flow.assess.agent.md` template | None | New template |
| 579.10 | Add `.github/agents/` to flowspec repository itself | None | New directory |
| 579.11 | Remove `/spec:*` commands from templates | None | Cleaned templates |
| 579.12 | Update agent handoffs to use new naming convention | 579.07, 579.08 | Updated handoffs |

**Critical Path:** 579.07 → 579.08 → 579.12

**Verification Gate:**
```bash
# All agent templates use dot notation
ls templates/.github/agents/*.agent.md | grep "flow\." | wc -l
# Should return: 6

# All agent names are PascalCase
rg '^name: Flow[A-Z]' templates/.github/agents/*.agent.md | wc -l
# Should return: 6

# Assess agent exists
[ -f templates/.github/agents/flow.assess.agent.md ] && echo "OK"
# Should return: OK

# No /spec:* commands in templates
ls templates/commands/spec/ 2>/dev/null | wc -l
# Should return: 0
```

**Duration Estimate:** 3-4 days

---

#### Phase 2: MCP Configuration (P2 - Medium Priority)

**Goal:** Ensure comprehensive MCP server configuration.

**Tasks:**

| Task | Description | Blocking | Output Artifact |
|------|-------------|----------|-----------------|
| 579.13 | Create comprehensive `.mcp.json` template | 579.14 | Template file |
| 579.14 | Update `generate_mcp_json()` for comprehensive config | 579.13 | Updated function |
| 579.15 | Add MCP server health check to init/upgrade | 579.14 | Health check logic |

**Critical Path:** 579.13 → 579.14 → 579.15

**Verification Gate:**
```bash
# Template has all required servers
jq '.mcpServers | keys | length' templates/.mcp.json
# Should return: >= 6 (backlog, github, serena, trivy, semgrep, playwright-test)

# generate_mcp_json includes comprehensive servers
rg "trivy|semgrep|serena" src/flowspec_cli/__init__.py | wc -l
# Should return: >= 3

# Health check function exists
rg "def.*health.*check.*mcp|def.*check.*mcp.*health" src/flowspec_cli/__init__.py | wc -l
# Should return: >= 1
```

**Duration Estimate:** 2-3 days

---

#### Phase 3: Integration & Refactoring (Optional - Technical Debt)

**Goal:** Refactor large `__init__.py` for maintainability (NOT blocking release).

**Tasks:**

| Task | Description | Output Artifact |
|------|-------------|-----------------|
| N/A | Extract migrations to `src/flowspec_cli/migrations/` | New module |
| N/A | Extract validators to `src/flowspec_cli/validators/` | New module |
| N/A | Extract synchronizers to `src/flowspec_cli/synchronizers/` | New module |
| N/A | Extract embedded templates to separate module | New module |

**Note:** This phase is NOT required for the release. It addresses technical debt.

**Duration Estimate:** 3-5 days (if pursued)

---

#### Phase 4: Documentation (P4 - Post-Implementation)

**Goal:** Update documentation to reflect changes.

**Tasks:**

| Task | Description | Blocking | Output Artifact |
|------|-------------|----------|-----------------|
| 579.16 | Update documentation for command namespace changes | None | Updated docs |
| 579.17 | Archive `build-docs/` with `/spec:*` and `/flow:operate` refs | None | Archived docs |

**Verification Gate:**
```bash
# User docs have no /spec:* or /flow:operate references
rg "/spec:|/flow:operate" user-docs/ | wc -l
# Should return: 0

# Build docs are moved to archive
[ -d docs/archive/build-docs ] && echo "OK"
# Should return: OK
```

**Duration Estimate:** 1-2 days

---

#### Phase 5: Verification (P5 - Validation)

**Goal:** End-to-end testing on real target repository.

**Tasks:**

| Task | Description | Output Artifact |
|------|-------------|-----------------|
| 579.18 | Test upgrade-repo fixes on auth.poley.dev | Verified deployment |

**Test Procedure:**

1. **Baseline:** Capture current state of auth.poley.dev
2. **Upgrade:** Run `flowspec upgrade-repo` from updated flowspec
3. **Verify Agents:**
   - VSCode Copilot shows 6 agents: FlowAssess, FlowSpecify, FlowPlan, FlowImplement, FlowValidate, FlowSubmitPR
   - Agent files use dot notation
   - Agent names are PascalCase
4. **Verify MCP:**
   - `.mcp.json` has 6+ servers
   - MCP servers start successfully
5. **Verify Workflow:**
   - `flowspec_workflow.yml` is v2.0
   - No `operate` workflow exists
   - Roles, custom_workflows, agent_loops sections present
6. **Verify Cleanup:**
   - `.specify/` directory removed
   - `_DEPRECATED_*.md` files removed
   - No `{{INCLUDE:}}` directives in `.github/prompts/`
7. **Verify Skills:**
   - `.claude/skills/` has 21 skill files
8. **Regression Testing:**
   - Run `/flow:assess` in VSCode Copilot
   - Run `/flow:specify` in VSCode Copilot
   - Verify agents handoff correctly

**Duration Estimate:** 2-3 days

---

### Dependency Graph

```
Phase 0 (Foundation)
├─ 579.01 (Remove /flow:operate) ────────┐
│                                         ├─► 579.05 (Update workflow to v2.0)
├─ 579.02 (Remove {{INCLUDE:}}) ─────────┤
├─ 579.03 (Call generate_mcp_json)       │
├─ 579.04 (Sync skills)                  │
├─ 579.06 (Remove deprecated files)      │
└─────────────────────────────────────────┘
                  │
                  ▼
Phase 1 (Agent Templates)
├─ 579.07 (Fix filenames: hyphen→dot) ───┐
│                                         ├─► 579.12 (Update handoffs)
├─ 579.08 (Fix names: kebab→PascalCase) ─┤
├─ 579.09 (Add assess agent)             │
├─ 579.10 (Add .github/agents/)          │
├─ 579.11 (Remove /spec:* commands)      │
└─────────────────────────────────────────┘
                  │
                  ▼
Phase 2 (MCP Configuration)
├─ 579.13 (Create .mcp.json template) ───┐
│                                         ├─► 579.15 (Add health check)
└─ 579.14 (Update generate_mcp_json) ────┘
                  │
                  ▼
Phase 4 (Documentation)
├─ 579.16 (Update documentation)
└─ 579.17 (Archive build-docs)
                  │
                  ▼
Phase 5 (Verification)
└─ 579.18 (E2E test on auth.poley.dev)
```

### Critical Path

**The longest dependency chain (critical path):**

```
579.01 → 579.05 → 579.07 → 579.08 → 579.12 → 579.13 → 579.14 → 579.15 → 579.18
```

**Duration:** ~14-18 days (excluding optional Phase 3 refactoring)

---

## Consequences

### Positive

1. **Predictable Timeline**: Clear dependency ordering enables accurate scheduling
2. **Incremental Progress**: Each phase delivers testable value
3. **Validation Gates**: Catch issues early before proceeding
4. **Parallel Work Possible**: Independent tasks within phases can be parallelized
5. **Clear Blocking Issues**: Dependencies explicitly documented
6. **Risk Mitigation**: Critical path identified for monitoring

### Negative

1. **Sequential Phases**: Cannot start Phase 2 until Phase 1 complete
2. **Long Pole**: Critical path is 9 tasks long
3. **Integration Risk**: Multiple components must work together in Phase 5
4. **Rollback Complexity**: Later phases depend on earlier phases
5. **Testing Burden**: Each phase requires verification gates

### Neutral

1. **Timeline Length**: 14-18 days is reasonable for a P0 release blocker
2. **Task Count**: 18 tasks is manageable for a 3-week sprint
3. **Documentation Lag**: Phase 4 happens after implementation (acceptable)

## Alternatives Considered

### Alternative 1: Big Bang Implementation

**Implement all 18 tasks in parallel, integrate at end.**

- **Pros:**
  - Fastest calendar time (if team is large)
  - No waiting on dependencies
- **Cons:**
  - High integration risk
  - Late discovery of issues
  - Difficult to test incrementally
  - Requires large team
- **Why rejected:** High risk for a P0 blocker. Integration issues discovered late are costly.

### Alternative 2: Minimal Viable Fix

**Implement only the bare minimum to unblock release (e.g., just fix agent naming).**

- **Pros:**
  - Fastest time to release
  - Smallest code change
  - Lowest risk
- **Cons:**
  - Leaves other broken functionality
  - Users still need manual fixes
  - Defers technical debt
  - Incomplete solution
- **Why rejected:** Half-fixes erode user trust. Since we're already fixing upgrade-repo, do it properly.

### Alternative 3: Reverse Order (Documentation First)

**Start with documentation/specs, then implement.**

- **Pros:**
  - Clear requirements before coding
  - Forces design thinking
  - Reduces rework
- **Cons:**
  - Delays code delivery
  - Documentation may not survive contact with implementation
  - Blocks progress on clear tasks
- **Why rejected:** Requirements are already clear from the fix-flowspec-plan. Implementation can proceed immediately.

### Alternative 4: Feature Flags for Incremental Rollout

**Use feature flags to enable new upgrade behavior incrementally.**

- **Pros:**
  - Gradual rollout reduces risk
  - Easy rollback
  - A/B testing possible
- **Cons:**
  - Adds code complexity
  - Two code paths to maintain
  - Overkill for CLI tool
  - Users may not upgrade flags
- **Why rejected:** Feature flags are better for SaaS. CLI tools benefit from clean releases with version numbers.

## Implementation Guidelines

### Task Execution Process

For each task:

1. **Read Requirements**: Review task markdown file in `backlog/tasks/`
2. **Create Branch**: `git checkout -b task-579.XX-description`
3. **Implement**: Write code following acceptance criteria
4. **Self-Test**: Verify acceptance criteria locally
5. **Commit**: Atomic commits with conventional commit messages
6. **Phase Gate**: Run phase verification gate before proceeding

### Conventional Commit Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]

Task: task-579.XX
```

**Types:**
- `fix`: Bug fix (Phase 0 tasks)
- `feat`: New feature (Phase 1-2 tasks)
- `docs`: Documentation (Phase 4 tasks)
- `test`: Testing (Phase 5 tasks)
- `refactor`: Code refactoring (Phase 3 tasks)

**Examples:**
```
fix(upgrade-repo): remove /flow:operate references from templates

Task: task-579.01
```

```
feat(agents): rename agent files from hyphen to dot notation

- flow-specify.agent.md → flow.specify.agent.md
- flow-plan.agent.md → flow.plan.agent.md
- flow-implement.agent.md → flow.implement.agent.md

Task: task-579.07
```

### Testing Strategy

**Unit Tests** (per task):
- Test individual functions/classes
- Mock external dependencies
- Fast execution (<1s)

**Integration Tests** (per phase):
- Test component interactions
- Use test fixtures
- Moderate execution (<10s)

**E2E Tests** (Phase 5):
- Test complete upgrade flow
- Use real project (test fixture or auth.poley.dev clone)
- Slow execution (~1min)

**Test Organization:**
```
tests/
├── unit/
│   ├── test_migrations.py        # Phase 0
│   ├── test_agent_templates.py   # Phase 1
│   ├── test_mcp_config.py        # Phase 2
│   └── test_validators.py        # All phases
├── integration/
│   ├── test_upgrade_flow.py      # Phase 0-2 integration
│   └── test_mcp_generation.py    # Phase 2
└── e2e/
    └── test_upgrade_repo_e2e.py  # Phase 5
```

### Parallel Work Opportunities

**Within Phase 0:**
- 579.03, 579.04, 579.06 can be done in parallel (independent)
- 579.01 → 579.05 must be sequential
- 579.02 can be done in parallel with 579.03/579.04/579.06

**Within Phase 1:**
- 579.09, 579.10, 579.11 can be done in parallel
- 579.07 → 579.08 → 579.12 must be sequential

**Within Phase 2:**
- 579.13 → 579.14 → 579.15 must be sequential (each builds on previous)

**Within Phase 4:**
- 579.16 and 579.17 can be done in parallel

**Optimal Parallelization:**
If a 2-person team:
- Person A: 579.01 → 579.05 → 579.07 → 579.08 → 579.12 → 579.13 → 579.14 → 579.15 (critical path)
- Person B: 579.02, 579.03, 579.04, 579.06, 579.09, 579.10, 579.11, 579.16, 579.17 (parallel tasks)

**Timeline with 2 people:** ~8-10 days (vs 14-18 days solo)

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Critical path delays** | Daily standup to identify blockers early |
| **Integration failures in Phase 5** | Run integration tests after each phase |
| **Regression in existing functionality** | Comprehensive test suite + manual smoke tests |
| **Scope creep** | Strict adherence to acceptance criteria |
| **Merge conflicts** | Small, atomic commits; rebase frequently |
| **Incomplete validation** | Verification gates mandatory before phase completion |

### Success Criteria

**Release is ready when:**

1. ✅ All Phase 0-2 tasks complete and validated
2. ✅ Phase 5 E2E test passes on auth.poley.dev
3. ✅ `flowspec upgrade-repo` on test project produces:
   - 6 agents with dot notation
   - `.mcp.json` with 6+ servers
   - `flowspec_workflow.yml` v2.0
   - `.claude/skills/` with 21 skills
   - No deprecated files
   - No `/flow:operate` or `{{INCLUDE:}}` references
4. ✅ VSCode Copilot shows all 6 agents correctly
5. ✅ MCP servers start without errors
6. ✅ All tests pass (unit, integration, E2E)

**Phase 4 (documentation) can be completed post-release if needed to unblock.**

## References

- [ADR-001: VSCode Copilot Agent Naming Convention](./ADR-001-vscode-copilot-agent-naming-convention.md)
- [ADR-002: Upgrade-Repo Architecture Redesign](./ADR-002-upgrade-repo-architecture-redesign.md)
- [Task 579 Epic](../../../backlog/tasks/task-579%20-%20EPIC-Flowspec-Release-Alignment-Fix-upgrade-repo-and-Agent-Integration.md)
- [Fix Flowspec Plan](../../building/fix-flowspec-plan.md)

---

*This ADR follows the [Michael Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).*
