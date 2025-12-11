# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

### Task Quality (NON-NEGOTIABLE)
Every task created in the backlog MUST have:
- **At least one acceptance criterion** - Tasks without ACs are incomplete and must not be created
- **Clear, testable criteria** - Each AC must be outcome-oriented and objectively verifiable
- **Proper description** - Explains the "why" and context for the task

Tasks without acceptance criteria will be rejected or archived. This ensures all work is:
1. Clearly scoped before implementation begins
2. Verifiable upon completion
3. Aligned with the Definition of Done

### Task Workflow Metadata (AUTOMATIC)

Every task automatically captures execution context metadata. **This is NOT manual input** - it's captured by tooling for reporting and traceability.

#### Automatic Metadata Fields

| Field | Source | Purpose |
|-------|--------|---------|
| `workflow_stage` | Workflow command executed | Which stage in PRD→Runbook progression |
| `host` | `$HOSTNAME` environment | Which machine executed the work |
| `tool` | Agent/tool identifier | Which coding tool (claude-code, cursor, codex) |
| `model` | Model configuration | Which AI model (opus, sonnet, gpt-4) |
| `started_at` | Timestamp | When work began |
| `completed_at` | Timestamp | When stage completed |

#### Workflow Stages

```
PRD → FunctionalSpec → TechnicalSpec → ADR → Implementation → Runbook → Done
```

#### Example Task Metadata (Auto-Captured)

```yaml
# Stored in task implementation notes or separate metadata
metadata:
  workflow_history:
    - stage: PRD
      host: galway
      tool: claude-code
      model: opus
      started: 2025-12-04T10:00:00Z
      completed: 2025-12-04T10:30:00Z
    - stage: FunctionalSpec
      host: galway
      tool: claude-code
      model: opus
      started: 2025-12-04T10:30:00Z
      completed: 2025-12-04T11:00:00Z
    - stage: Implementation
      host: muckross
      tool: cursor
      model: sonnet
      started: 2025-12-04T14:00:00Z
```

#### Querying by Metadata

```bash
# What is galway working on?
backlog task list -l host:galway --plain

# What's in Implementation stage?
backlog task list -l workflow:Implementation --plain

# What did opus produce?
backlog task list -l model:opus --plain
```

#### Why This Matters

- **Traceability**: Know which host/model produced which artifacts
- **Debugging**: "This code has issues - who/what wrote it?"
- **Capacity Planning**: "How much work is galway handling?"
- **Quality Tracking**: "Which model produces best results?"
- **Audit Trail**: Complete history of task progression

#### Next Step Assignment (Optional)

You can assign the **next workflow step** to a specific host/tool/model. This enables:
- Different models for implementation vs review (diversity improves quality)
- Specific hosts for specific workloads (GPU host for ML tasks)
- Tool specialization (cursor for frontend, claude-code for backend)

**Assignment Fields:**

| Field | Purpose | Example |
|-------|---------|---------|
| `next_host` | Which machine should pick this up | `next_host:muckross` |
| `next_tool` | Which tool should execute | `next_tool:cursor` |
| `next_model` | Which model to use | `next_model:sonnet` |
| `next_stage` | Which workflow stage is next | `next_stage:CodeReview` |

**Example: Hand off implementation to review**

```yaml
# After Implementation completes, assign review to different model
metadata:
  current_stage: Implementation
  completed_by:
    host: galway
    tool: claude-code
    model: opus
  next_step:
    stage: CodeReview
    host: muckross        # Different host
    tool: claude-code
    model: sonnet         # Different model for diverse review
    reason: "Use different model for review to catch blind spots"
```

**Example: Assign test review to specialized setup**

```yaml
metadata:
  next_step:
    stage: TestReview
    host: dublin
    tool: cursor
    model: gpt-4
    reason: "GPT-4 has strong test coverage analysis"
```

**Querying Assigned Work:**

```bash
# What's assigned to muckross?
backlog task list -l next_host:muckross --plain

# What needs sonnet review?
backlog task list -l next_model:sonnet --plain

# What's waiting for code review?
backlog task list -l next_stage:CodeReview --plain
```

**Best Practices:**
- Use different models for implementation vs review (reduces blind spots)
- Assign compute-heavy tasks to appropriate hosts
- Document `reason` for non-default assignments
- Clear assignments after task is picked up

### PR-Task Synchronization (NON-NEGOTIABLE)
When creating a PR that completes a backlog task:

1. **Before PR creation**: Mark all completed acceptance criteria
   ```bash
   backlog task edit <id> --check-ac 1 --check-ac 2 ...
   ```

2. **With PR creation**: Update task status and reference the PR
   ```bash
   backlog task edit <id> -s Done --notes $'Completed via PR #<number>\n\nStatus: Pending CI verification'
   ```

3. **PR-Task coupling**: If the PR fails CI or is rejected:
   - Revert task status to "In Progress"
   - Uncheck any ACs that weren't actually completed
   - The backlog must accurately reflect reality

4. **Implementation notes format**:
   ```
   Completed via PR #<number>

   Status: Pending CI verification

   Changes:
   - <summary of changes>
   ```

This ensures:
- Backlog always reflects actual project state
- PRs are traceable to tasks
- Failed PRs don't leave orphaned "Done" tasks

## Committer Skill (Separation of Concerns)

### Purpose

The **Committer** is a specialized skill/agent that handles ALL git operations. This creates a clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      SEPARATION OF CONCERNS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   DOMAIN AGENTS                          COMMITTER SKILL                 │
│   ─────────────                          ──────────────                  │
│                                                                          │
│   ┌─────────────────┐                    ┌─────────────────┐            │
│   │ Frontend Eng    │                    │                 │            │
│   │ Backend Eng     │ ───── Code ─────►  │   Committer     │            │
│   │ Architect       │                    │                 │            │
│   │ PM Planner      │                    │  • Lint         │            │
│   │ QA Engineer     │                    │  • Format       │            │
│   │ SRE Agent       │                    │  • Test         │            │
│   └─────────────────┘                    │  • DCO Sign-off │            │
│                                          │  • Commit       │            │
│   Focus: Domain expertise                │  • PR Creation  │            │
│   NOT: Git mechanics                     │  • CI Validation│            │
│                                          │                 │            │
│                                          └─────────────────┘            │
│                                                                          │
│                                          Focus: Git mechanics           │
│                                          NOT: Domain logic              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why This Matters

Git operations are **noise** for domain agents. When a Backend Engineer needs to:
- Know `ruff` vs `black` formatting rules
- Remember DCO sign-off syntax (`-s` flag)
- Handle pre-commit hook failures
- Resolve merge conflicts
- Ensure CI passes before PR

...they lose focus on their actual job: writing good backend code.

### Committer Responsibilities

| Task | Command | Validation |
|------|---------|------------|
| **Lint** | `ruff check . --fix` | No lint errors |
| **Format** | `ruff format .` | Consistent formatting |
| **Test** | `pytest tests/` | All tests pass |
| **Type Check** | `mypy src/` (if configured) | No type errors |
| **DCO Sign-off** | `git commit -s` | Sign-off present |
| **Commit** | Conventional commits | Message format correct |
| **Branch** | Create/switch branches | Branch naming convention |
| **PR Creation** | `gh pr create` | PR template filled |
| **CI Validation** | Check CI status | All checks green |

### Committer Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        COMMITTER WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Domain Agent completes work                                            │
│         │                                                                │
│         ▼                                                                │
│   ┌──────────────┐                                                      │
│   │ 1. Lint      │  ruff check . --fix                                  │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐                                                      │
│   │ 2. Format    │  ruff format .                                       │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐                                                      │
│   │ 3. Test      │  pytest tests/ -v                                    │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐     ┌─────────────────────────────────────────────┐ │
│   │ 4. Stage     │────►│ git add -A                                   │ │
│   └──────┬───────┘     └─────────────────────────────────────────────┘ │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐     ┌─────────────────────────────────────────────┐ │
│   │ 5. Commit    │────►│ git commit -s -m "type(scope): message"     │ │
│   └──────┬───────┘     └─────────────────────────────────────────────┘ │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐     ┌─────────────────────────────────────────────┐ │
│   │ 6. Push      │────►│ git push -u origin branch-name              │ │
│   └──────┬───────┘     └─────────────────────────────────────────────┘ │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐     ┌─────────────────────────────────────────────┐ │
│   │ 7. PR        │────►│ gh pr create --title "..." --body "..."     │ │
│   └──────┬───────┘     └─────────────────────────────────────────────┘ │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐                                                      │
│   │ 8. CI Check  │  Wait for CI, report status                          │
│   └──────────────┘                                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Integration with /flowspec Commands

Every `/flowspec` command that produces artifacts should invoke the Committer:

| Command | Domain Work | Committer Invocation |
|---------|-------------|---------------------|
| `/flow:specify` | Creates PRD, functional spec | Commits docs, creates PR |
| `/flow:plan` | Creates technical spec, ADRs | Commits docs, creates PR |
| `/flow:implement` | Writes code, tests, docs | Lint, format, test, commit, PR |
| `/flow:validate` | Creates QA/security reports | Commits reports, creates PR |
| `/flow:operate` | Creates runbooks, configs | Commits ops docs, creates PR |

### Committer Skill Definition

```yaml
# .claude/skills/committer.md
name: committer
description: |
  Handles all git operations: lint, format, test, commit with DCO,
  create branches and PRs, validate CI. Invoked at end of every
  workflow step that produces artifacts.

triggers:
  - "commit these changes"
  - "create a PR"
  - "prepare for merge"
  - After any /flowspec command completes

responsibilities:
  - Pre-commit validation (lint, format, test)
  - DCO sign-off on all commits
  - Conventional commit message format
  - Branch creation with proper naming
  - PR creation with template
  - CI status monitoring
```

### Benefits

1. **Domain agents stay focused** - No context switching to git mechanics
2. **Consistent quality** - Every commit passes lint, format, tests
3. **Proper compliance** - DCO sign-off never forgotten
4. **Reduced errors** - No accidental commits to main, proper branch naming
5. **Clean history** - Conventional commits, proper PR descriptions

---

## Git Commit Requirements (NON-NEGOTIABLE)

### No Direct Commits to Main (ABSOLUTE)
**NEVER commit directly to the main branch.** All changes MUST go through a PR:

1. **Create a branch** for the task
2. **Make changes** on the branch
3. **Create a PR** referencing the backlog task
4. **PR must pass CI** before merge
5. **Task marked Done** only after PR is merged

**NO EXCEPTIONS.** Not for "urgent" fixes, not for "small" changes, not for any reason.

If a direct commit to main occurs:
1. **Revert immediately**
2. **Create proper branch and PR**
3. **Document the violation**

This rule exists because:
- Direct commits bypass code review
- Direct commits bypass CI validation
- Direct commits break traceability
- "Urgent" is never an excuse to skip process

### DCO Sign-Off Required
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

**Always use `git commit -s` to automatically add the sign-off.**

```
feat(scope): description

Signed-off-by: Your Name <your.email@example.com>
```

Commits without sign-off will block PRs from being merged.

## Parallel Task Execution (NON-NEGOTIABLE)

### Git Worktree Requirements
When executing tasks in parallel, git worktrees MUST be used to isolate work:

1. **Worktree name must match branch name** - The worktree directory name MUST be identical to the branch name
   ```bash
   # Correct: worktree name matches branch name
   git worktree add ../feature-auth feature-auth

   # Wrong: mismatched names
   git worktree add ../work1 feature-auth
   ```

2. **One branch per worktree** - Each parallel task gets its own worktree and branch

3. **Clean isolation** - Worktrees prevent merge conflicts and allow simultaneous work on multiple features

4. **Worktree cleanup** - Remove worktrees when work is complete:
   ```bash
   git worktree remove ../feature-auth
   ```

This ensures:
- Clear mapping between filesystem locations and branches
- No accidental commits to wrong branches
- Easy identification of which worktree corresponds to which task
- Clean parallel development without interference

## Planning Artifacts

The SDD workflow produces structured documents in a specific progression. Each artifact builds on the previous, moving from business intent to implementation.

### Artifact Progression (NON-NEGOTIABLE)

```
PRD → Functional Spec → Technical Spec → ADR → Implementation → Runbook
```

| Stage | Artifact | Question Answered | Location |
|-------|----------|-------------------|----------|
| 1 | **PRD** | What the product must do and why the user cares | `docs/prd/` |
| 2 | **Functional Spec** | What behaviors and capabilities are required | `docs/specs/` |
| 3 | **Technical Spec** | How will we build it (architecture, data, APIs) | `docs/specs/` |
| 4 | **ADR** | Why we chose this technical path | `docs/adr/` |
| 5 | **Implementation** | The code itself | `src/` |
| 6 | **Runbook** | How to operate, monitor, and troubleshoot | `docs/runbooks/` |

**Each stage must be completed before the next begins.** Skipping stages leads to:
- Misaligned implementations (skipping PRD)
- Undefined edge cases (skipping Functional Spec)
- Inconsistent architecture (skipping Technical Spec)
- Undocumented decisions (skipping ADR)
- Unrunnable systems (skipping Runbook)

### Workflow State Machine (Complete Reference)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           SDD WORKFLOW STATE MACHINE                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                          │
│  ┌──────────┐      /flow:specify        ┌──────────────┐                              │
│  │  To Do   │ ──────────────────────────► │  Specified   │                              │
│  └──────────┘                              └──────┬───────┘                              │
│       │                                           │                                      │
│       │  Artifacts:                               │  Artifacts:                          │
│       │  (none)                                   │  • [feature]-prd.md                  │
│       │                                           │  • [feature]-functional.md           │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                               ┌───────────────────────┐                         │
│       │      /flow:research         │     Researched        │  (optional)             │
│       │      (optional)               │                       │                         │
│       │                               └───────────┬───────────┘                         │
│       │                                           │                                      │
│       │                                           │  Artifacts:                          │
│       │                                           │  • Research reports                  │
│       │                                           │  • Competitive analysis              │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                                    /flow:plan                                  │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                               ┌───────────────────────┐                         │
│       │                               │       Planned         │                         │
│       │                               └───────────┬───────────┘                         │
│       │                                           │                                      │
│       │                                           │  Artifacts:                          │
│       │                                           │  • [feature]-technical.md            │
│       │                                           │  • adr-XXX-[topic].md                │
│       │                                           │  • Platform design docs              │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                                   /flow:implement                              │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                               ┌───────────────────────┐                         │
│       │                               │   In Implementation   │                         │
│       │                               └───────────┬───────────┘                         │
│       │                                           │                                      │
│       │                                           │  Artifacts:                          │
│       │                                           │  • Source code (src/)                │
│       │                                           │  • Unit tests                        │
│       │                                           │  • Integration tests                 │
│       │                                           │  • API documentation                 │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                                   /flow:validate                               │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                               ┌───────────────────────┐                         │
│       │                               │      Validated        │                         │
│       │                               └───────────┬───────────┘                         │
│       │                                           │                                      │
│       │                                           │  Artifacts:                          │
│       │                                           │  • QA reports                        │
│       │                                           │  • Security scan results             │
│       │                                           │  • Test coverage reports             │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                                    /flow:operate                               │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                               ┌───────────────────────┐                         │
│       │                               │       Deployed        │                         │
│       │                               └───────────┬───────────┘                         │
│       │                                           │                                      │
│       │                                           │  Artifacts:                          │
│       │                                           │  • [service]-runbook.md              │
│       │                                           │  • Deployment configs                │
│       │                                           │  • Monitoring dashboards             │
│       │                                           │                                      │
│       │                                           ▼                                      │
│       │                               ┌───────────────────────┐                         │
│       │                               │        Done           │                         │
│       │                               └───────────────────────┘                         │
│                                                                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Command Reference Table

| Command | Input State(s) | Output State | Artifacts Produced |
|---------|---------------|--------------|-------------------|
| `/flow:specify` | To Do | Specified | `[feature]-prd.md`, `[feature]-functional.md` |
| `/flow:research` | Specified | Researched | Research reports, competitive analysis |
| `/flow:plan` | Specified, Researched | Planned | `[feature]-technical.md`, `adr-XXX-[topic].md`, platform docs |
| `/flow:implement` | Planned | In Implementation | Code, tests, API docs |
| `/flow:validate` | In Implementation | Validated | QA reports, security scans, coverage reports |
| `/flow:operate` | Validated | Deployed | `[service]-runbook.md`, deploy configs, dashboards |

### Artifact Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ARTIFACT FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   SPECIFY                 PLAN                    IMPLEMENT                      │
│   ───────                 ────                    ─────────                      │
│                                                                                  │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│   │    PRD      │         │  Technical  │         │    Code     │               │
│   │             │ ──────► │    Spec     │ ──────► │             │               │
│   │  "What &    │         │             │         │   src/*.py  │               │
│   │   Why"      │         │  "How to    │         │   src/*.ts  │               │
│   │             │         │   build"    │         │   src/*.go  │               │
│   └─────────────┘         └─────────────┘         └─────────────┘               │
│         │                       │                       │                        │
│         ▼                       ▼                       ▼                        │
│   ┌─────────────┐         ┌─────────────┐         ┌─────────────┐               │
│   │ Functional  │         │    ADRs     │         │    Tests    │               │
│   │    Spec     │         │             │         │             │               │
│   │             │         │  "Why this  │         │  tests/*.py │               │
│   │  "What      │         │   path"     │         │  *.test.ts  │               │
│   │   behaviors"│         │             │         │  *_test.go  │               │
│   └─────────────┘         └─────────────┘         └─────────────┘               │
│                                 │                       │                        │
│                                 ▼                       ▼                        │
│                           ┌─────────────┐         ┌─────────────┐               │
│                           │  Platform   │         │  API Docs   │               │
│                           │   Design    │         │             │               │
│                           │             │         │ OpenAPI/    │               │
│                           │ CI/CD, Infra│         │ Swagger     │               │
│                           └─────────────┘         └─────────────┘               │
│                                                                                  │
│   VALIDATE                OPERATE                                                │
│   ────────                ───────                                                │
│                                                                                  │
│   ┌─────────────┐         ┌─────────────┐                                       │
│   │ QA Reports  │         │   Runbook   │                                       │
│   │             │ ──────► │             │                                       │
│   │ Test plans, │         │ Deploy,     │                                       │
│   │ coverage    │         │ monitor,    │                                       │
│   │             │         │ troubleshoot│                                       │
│   └─────────────┘         └─────────────┘                                       │
│         │                       │                                                │
│         ▼                       ▼                                                │
│   ┌─────────────┐         ┌─────────────┐                                       │
│   │  Security   │         │  Deploy     │                                       │
│   │   Scans     │         │  Configs    │                                       │
│   │             │         │             │                                       │
│   │ SAST, DAST, │         │ K8s, Docker │                                       │
│   │ SCA results │         │ Terraform   │                                       │
│   └─────────────┘         └─────────────┘                                       │
│                                 │                                                │
│                                 ▼                                                │
│                           ┌─────────────┐                                       │
│                           │ Dashboards  │                                       │
│                           │             │                                       │
│                           │ Grafana,    │                                       │
│                           │ alerts      │                                       │
│                           └─────────────┘                                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### File Location Summary

```
project/
├── docs/
│   ├── prd/
│   │   └── [feature]-prd.md              # /flow:specify
│   ├── specs/
│   │   ├── [feature]-functional.md       # /flow:specify
│   │   └── [feature]-technical.md        # /flow:plan
│   ├── adr/
│   │   └── adr-XXX-[topic].md            # /flow:plan
│   ├── platform/
│   │   └── [feature]-platform.md         # /flow:plan
│   ├── qa/
│   │   └── [feature]-qa-report.md        # /flow:validate
│   ├── security/
│   │   └── [feature]-security-scan.md    # /flow:validate
│   └── runbooks/
│       └── [service]-runbook.md          # /flow:operate
├── src/
│   └── [feature]/                        # /flow:implement
│       ├── *.py / *.ts / *.go
│       └── ...
└── tests/
    └── [feature]/                        # /flow:implement
        └── test_*.py / *.test.ts / *_test.go
```

### Document Naming Conventions (NON-NEGOTIABLE)

**Always use explicit suffixes** to distinguish document types:

| Document Type | Naming Pattern | Example |
|---------------|----------------|---------|
| PRD | `[feature]-prd.md` | `user-auth-prd.md` |
| Functional Spec | `[feature]-functional.md` | `user-auth-functional.md` |
| Technical Spec | `[feature]-technical.md` | `user-auth-technical.md` |
| ADR | `adr-[number]-[topic].md` | `adr-015-auth-provider.md` |
| Runbook | `[service]-runbook.md` | `auth-service-runbook.md` |

**Why explicit naming matters:**
- `spec.md` alone is ambiguous - is it functional or technical?
- Clear suffixes prevent confusion during reviews
- Enables automated tooling to identify document types
- Makes grep/search results unambiguous

**Never use:**
- `spec.md` (ambiguous)
- `design.md` (ambiguous)
- `notes.md` (not a formal artifact)

---

### 1. PRD - Product Requirements Document

**Definition**: "What the product must do and why the user cares."

PRDs capture the business and user perspective. They answer:
- Who is the user and what problem do they have?
- What does success look like from the user's perspective?
- What are the acceptance criteria for the feature?
- How does this fit into the broader product vision?

**Location**: `docs/prd/`
**Command**: `/flow:specify`

**Format**:
```markdown
# PRD: [Feature Name]

## Problem Statement
[User pain point - why this matters]

## User Stories
[As a X, I want Y, so that Z]

## Requirements
[Functional and non-functional requirements]

## Success Metrics
[How we measure if this solved the problem]

## Out of Scope
[What this feature explicitly does NOT do]
```

---

### 2. Functional Spec

**Definition**: "What behaviors and capabilities are required."

Functional specs translate PRD requirements into system behaviors. They answer:
- What inputs does the system accept?
- What outputs does it produce?
- What are all the edge cases and error conditions?
- What are the business rules and validation logic?

**Location**: `docs/specs/[feature]-functional.md`
**Command**: `/flow:specify` (detailed mode)

**Format**:
```markdown
# Functional Spec: [Feature Name]

## Overview
[Brief description of the feature]

## Functional Requirements
### FR-1: [Requirement Name]
- **Input**: [What the system receives]
- **Output**: [What the system produces]
- **Rules**: [Business logic and validation]
- **Errors**: [Error conditions and messages]

## Use Cases
### UC-1: [Use Case Name]
- **Actor**: [Who performs the action]
- **Preconditions**: [Required state before]
- **Flow**: [Step-by-step sequence]
- **Postconditions**: [State after success]
- **Exceptions**: [Alternative flows]

## Data Requirements
[Data entities, relationships, constraints]
```

---

### 3. Technical Spec

**Definition**: "How will we build it."

Technical specs define the architecture and implementation approach. They answer:
- What components and services are needed?
- How do they interact (APIs, events, data flow)?
- What data models and schemas are required?
- What are the performance and scalability requirements?

**Location**: `docs/specs/[feature]-technical.md`
**Command**: `/flow:plan`

**Format**:
```markdown
# Technical Spec: [Feature Name]

## Architecture Overview
[High-level system design]

## Components
### [Component Name]
- **Responsibility**: [What it does]
- **Interface**: [API/contract]
- **Dependencies**: [What it needs]

## Data Model
[Schemas, entities, relationships]

## API Contracts
[Endpoints, request/response formats]

## Integration Points
[How this connects to existing systems]

## Non-Functional Requirements
[Performance, scalability, security]
```

---

### 4. ADR - Architecture Decision Record

**Definition**: "Why we chose this technical path."

ADRs document significant technical decisions made during planning. They answer:
- What problem are we solving?
- What options did we consider?
- Why did we choose this approach over others?
- What are the trade-offs and risks?

**Location**: `docs/adr/`
**Command**: `/flow:plan`

**Format**:
```markdown
# ADR-XXX: [Decision Title]

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
[Problem statement and background]

## Decision
[What we decided and why]

## Consequences
[Positive and negative implications]

## Alternatives Considered
[Other options and why they were rejected]

## Related Tasks
[Backlog task references]
```

---

### 5. Runbook

**Definition**: "How to operate, monitor, and troubleshoot."

Runbooks provide SRE/Ops teams with operational documentation. They answer:
- How do I deploy and configure this system?
- What should I monitor and alert on?
- How do I troubleshoot common issues?
- What are the recovery procedures?

**Location**: `docs/runbooks/`
**Command**: `/flow:operate`

**Format**:
```markdown
# Runbook: [Service/Feature Name]

## Overview
[Brief description of the service and its purpose]

## Deployment
### Prerequisites
[What must be in place before deployment]

### Deployment Steps
[Step-by-step deployment procedure]

### Configuration
[Environment variables, config files, secrets]

## Monitoring
### Key Metrics
[What metrics to watch and their thresholds]

### Alerts
[Alert conditions and severity levels]

### Dashboards
[Links to relevant dashboards]

## Troubleshooting
### Common Issues
#### [Issue 1: Description]
- **Symptoms**: [What you'll see]
- **Cause**: [Why it happens]
- **Resolution**: [How to fix it]

### Logs
[Where to find logs and what to look for]

## Recovery Procedures
### [Scenario 1: Description]
[Step-by-step recovery procedure]

## Contacts
[Escalation path and on-call information]
```

---

### Supporting Documents

In addition to the core progression, these documents support the workflow:

| Document | Purpose | Location |
|----------|---------|----------|
| **Platform Design** | How infrastructure supports the solution | `docs/platform/` |
| **Risk Assessment** | What could go wrong and how to mitigate | `docs/architecture/` |
| **Architecture Overview** | System boundaries and integration patterns | `docs/architecture/` |

---

### Workflow Command Mapping

| Command | Artifacts Produced |
|---------|-------------------|
| `/flow:specify` | PRD, Functional Spec |
| `/flow:plan` | Technical Spec, ADRs, Platform Design |
| `/flow:implement` | Code, Key Documents, Complete Tests |
| `/flow:operate` | Runbooks, Deployment Docs, Monitoring Config |

### Implementation Deliverables (NON-NEGOTIABLE)

`/flow:implement` produces **three mandatory deliverables**:

| Deliverable | Description | Verification |
|-------------|-------------|--------------|
| **Code** | Production-ready, reviewed source | PR passes CI, review approved |
| **Documents** | API docs, code comments, configs | Docs updated, comments added |
| **Tests** | Unit, integration, edge cases | Test suite passes, coverage met |

**Implementation is NOT complete until all three are delivered.**

Before implementing, `/flow:implement` MUST discover and read:
- All related PRDs in `docs/prd/`
- All related specs in `docs/specs/`
- All related ADRs in `docs/adr/`

---

### Light/Medium Mode (Streamlined Workflow)

In light or medium mode, **artifacts are still produced** - only the review depth changes:

| Mode | Artifacts | Review Depth |
|------|-----------|--------------|
| **Full** | All artifacts | Deep review at each stage, explicit approval gates |
| **Medium** | All artifacts | Quick review, proceed unless issues found |
| **Light** | All artifacts | Minimal review, trust the process |

**What stays the same in all modes:**
- PRD → Functional Spec → Technical Spec → ADR → Implementation → Runbook progression
- All artifacts created (just less formal review)
- Code + Documents + Tests deliverables required
- Runbooks for operational readiness
- Pre-PR validation (lint, format, tests)

**What changes in light/medium:**
- Fewer explicit approval checkpoints
- Combined document creation (PRD+Spec in one pass)
- Faster iteration cycles
- Less formal ADR structure (decision notes vs full ADRs)

**Light mode is NOT an excuse to skip artifacts.** It's permission to move faster through them.

### Principle 13: Task Memory - Persistent Context Management

**Statement**: Every task in "In Progress" state SHALL maintain a persistent, human-readable memory that travels with the task across sessions, machines, and tools.

**Rationale**: Context loss is one of the most expensive inefficiencies in software development. When developers switch machines, resume work after interruptions, or hand off tasks, they spend 15-30 minutes rebuilding mental context. Task Memory eliminates this overhead by creating a persistent, task-scoped knowledge store that captures decisions, approaches tried, open questions, and relevant resources.

**Requirements**:

#### 1. Automatic Lifecycle Management

Task memory MUST be created, maintained, and cleaned up automatically without manual intervention:

- **Creation**: When task transitions from "To Do" to "In Progress", create `backlog/memory/task-{id}.md`
- **Archival**: When task moves to "Done", move memory to `backlog/memory/archive/task-{id}.md`
- **Deletion**: When task is archived permanently, delete memory file
- **Restoration**: When task reopens (Done → In Progress), restore from archive if exists
- **Persistence**: Memory survives across sessions, machines, git sync

**Violation Example**:
```bash
# ❌ WRONG: Manual memory creation required
echo "Notes..." > backlog/memory/task-42.md

# ✅ CORRECT: Automatic on state transition
backlog task edit task-42 -s "In Progress"  # Creates memory automatically
```

#### 2. Human Readability and Editability

Memory files MUST be human-readable markdown, directly editable, and searchable:

- **Format**: Markdown with structured sections (Context, Decisions, Approaches, Questions, Resources)
- **Editability**: Any text editor can open and modify
- **Searchability**: Standard Unix tools (`grep`, `rg`, `fzf`) work
- **Version Control**: Git tracks all changes with full diff/merge support
- **Size Limit**: Files archived when exceeding 1MB to maintain performance

**Compliance Example**:
```markdown
# Task Memory: task-368

**Created**: 2025-12-09T10:30:00Z
**Last Updated**: 2025-12-09T14:22:00Z

## Context
Task Memory - Persistent Context Management System

## Key Decisions
- 2025-12-09 10:35 - Chose file-based storage over database
- 2025-12-09 11:20 - Use CLAUDE.md @import for context injection

## Approaches Tried
### Approach: Embedded storage in task files
**Result**: ❌ Rejected
**Reason**: Complex parsing, format rigidity

## Open Questions
- How to handle memory >1MB? (Add compression/truncation?)

## Resources
- ADR-001: Storage Mechanism Decision
- docs/architecture/task-memory-system.md
```

#### 3. Git-Native Synchronization

Memory MUST sync across machines using standard git operations:

- **No External Services**: No databases, APIs, or cloud sync required
- **Standard Git Sync**: `git push`/`git pull` synchronizes memory
- **Conflict Resolution**: Standard git merge with manual resolution
- **Offline Support**: Works completely offline, syncs when online
- **Transparency**: All sync operations visible in git history

**Conflict Resolution Strategy**:
```bash
# Git merge creates conflict markers
<<<<<<< HEAD (Machine A)
- Tried approach X, failed because of Z
=======
- Decided to use library Y after research
>>>>>>> branch (Machine B)

# Human resolution: Keep both (append-only nature reduces conflicts)
- Tried approach X, failed because of Z
- Decided to use library Y after research
```

#### 4. Agent-Agnostic Context Injection

Memory MUST be accessible to any AI agent without agent-specific configuration:

**Primary: CLAUDE.md @import (Claude Code)**:
```markdown
# backlog/CLAUDE.md

## Active Task Context

@import ../memory/task-368.md
```

**Secondary: MCP Resource (Copilot, others)**:
```python
@server.resource("backlog://memory/{task_id}")
def get_task_memory(task_id: str) -> str:
    return memory_store.read(task_id)
```

**Fallback: Direct File Access (Generic agents)**:
```bash
# Agent instruction: "Read task memory from backlog/memory/task-368.md"
cat backlog/memory/task-368.md
```

#### 5. Memory Content Guidelines

Task memory SHALL record context that accelerates work resumption and prevents repeated mistakes:

**MUST Include**:
- **Key Decisions**: What was decided and why (rationale, trade-offs)
- **Approaches Tried**: What was attempted and the outcome (success/failure reasons)
- **Open Questions**: Blockers, unknowns, areas needing research
- **External Resources**: Links to docs, ADRs, specs, research papers
- **Implementation Notes**: Non-obvious choices, gotchas, warnings

**MUST NOT Include**:
- **Secrets**: Passwords, API keys, tokens, credentials
- **Personally Identifiable Information (PII)**: Email addresses, phone numbers, personal data
- **Large Artifacts**: Full code dumps, logs, data exports (link to external files instead)
- **Redundant Information**: Content already in task description or linked specs

**Violation Example**:
```markdown
# ❌ WRONG: Secrets in memory
## Resources
- Database: postgresql://admin:SuperSecret123@db.example.com:5432
- API Key: sk_live_51AbCdEfGh...

# ✅ CORRECT: Reference without secrets
## Resources
- Database: See AWS Secrets Manager: `prod/taskflow/db-credentials`
- API Key: Stored in 1Password vault "Engineering Team" as "TaskFlow Production API"
```

#### 6. Performance Constraints

Memory operations MUST complete quickly to avoid interrupting workflows:

- **Read/Write Operations**: Complete in <50ms (p95)
- **File Size Limit**: Archive when exceeding 1MB
- **Cleanup**: Runs asynchronously, does not block task transitions
- **Search Performance**: Search across 10,000 memories in <1s

**Performance Monitoring**:
```bash
backlog memory stats

# Output:
# Task Memory Analytics
# Active memories: 23
# Archived memories: 156
# Average memory size: 187 KB
# Largest memory: 943 KB (task-245)
# Search queries (30d): 234
# Average read time: 12ms
```

#### 7. Privacy and Security

Memory files MUST be protected with repository-level access controls:

- **No Secrets**: Automated linting prevents accidental credential commits
- **Repository Permissions**: Memory readable only by repository collaborators
- **Audit Trail**: Git history provides complete audit log of changes
- **Retention**: Archived memories retained indefinitely (manual deletion only)

**Security Checks**:
```bash
# Pre-commit hook checks for secrets
rg -i "password|secret|api_key|token" backlog/memory/*.md

# Result: Exit 1 if secrets found, blocks commit
```

#### 8. Violations and Compliance

**Common Violations**:

| Violation | Detection | Remediation |
|-----------|-----------|-------------|
| Secrets in memory | Pre-commit hook, automated scanning | Remove secrets, reference secret manager |
| Manual memory creation | Workflow review | Delete manual file, use lifecycle hooks |
| Memory >1MB not archived | Automated monitoring | Archive large memories, link to external docs |
| Conflicted memory not resolved | Git status check | Manually resolve conflicts, prefer append-only |
| Memory not synced | Git status on machine switch | Commit and push before switching machines |

**Compliance Verification**:
```bash
# Check for manual memories (should be empty)
ls backlog/memory/*.md | grep -v "task-[0-9]*.md"

# Check for oversized memories
find backlog/memory -name "*.md" -size +1M

# Check for secrets
rg -i "password|secret|api_key|token" backlog/memory/

# Check for unsynced changes
git status backlog/memory/
```

**Benefits**:
- **Reduce context rebuild time**: From 15-30 minutes to <2 minutes
- **Enable seamless handoffs**: Team members can pick up mid-task with full context
- **Prevent repeated mistakes**: Document what didn't work and why
- **Build institutional knowledge**: Archived memories become searchable knowledge base
- **Foundation for intelligence**: Structured data enables future ML-driven insights

---

## [SECTION_2_NAME]
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
