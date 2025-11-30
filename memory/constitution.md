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
