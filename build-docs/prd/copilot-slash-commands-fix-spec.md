# Product Requirements Document: VS Code Copilot Slash Commands Support

**Feature**: Enable flowspec and speckit slash commands in VS Code Copilot Chat
**Status**: Draft
**Created**: 2025-12-07
**Author**: PM Planner Agent

---

## 1. Executive Summary

### Problem Statement

JP Flowspec provides 23 custom slash commands for Spec-Driven Development workflows via the `.claude/commands/` directory structure. These commands work perfectly in Claude Code CLI but are **completely invisible** in VS Code and VS Code Insiders when using the GitHub Copilot extension.

This creates a significant usability gap: developers working in VS Code cannot access critical workflow commands (`/flow:specify`, `/flow:implement`, `/speckit:plan`, etc.) directly in their IDE, forcing them to context-switch to the CLI or manually copy prompts.

**Root Cause**: VS Code Copilot uses a completely different agent system from Claude Code:

| System | Directory | Frontmatter Format |
|--------|-----------|-------------------|
| Claude Code | `.claude/commands/` | `mode: agent` |
| GitHub Copilot | `.github/agents/` | `mode: <command-name>` |

### Proposed Solution

Create a dual-agent system that supports both Claude Code CLI and VS Code Copilot by:

1. **Mirroring commands** from `.claude/commands/flow/*.md` and `.claude/commands/speckit/*.md` to `.github/agents/flowspec.*.md` and `.github/agents/speckit.*.md`
2. **Transforming frontmatter** from `mode: agent` to `mode: flowspec.<name>` or `mode: speckit.<name>`
3. **Automating synchronization** via a conversion script (manual or pre-commit hook)
4. **Testing in both IDEs** to ensure commands appear and execute correctly

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Command Discoverability | 100% of 23 commands appear in VS Code Copilot Chat picker | Manual verification in VS Code + Insiders |
| Command Execution | 100% of commands execute successfully in Copilot Chat | Smoke test suite (run each command with sample input) |
| Developer Experience | Zero context-switching required between CLI and IDE | User feedback survey |
| Maintenance Burden | Command changes propagate automatically | Sync script run time < 1 second |

### Business Value

- **Velocity**: Developers can invoke SDD workflows directly in their IDE, eliminating context-switching overhead
- **Adoption**: Lowers barrier to entry for JP Flowspec - developers don't need to learn a separate CLI tool
- **Consistency**: Ensures identical workflow experience across Claude Code CLI and VS Code environments
- **Strategic Alignment**: Positions JP Flowspec as IDE-agnostic, supporting both Claude AI and GitHub Copilot ecosystems

---

## 2. User Stories and Use Cases

### Primary User Personas

**Persona 1: Full-Stack Engineer (React + Python)**
- **Name**: Alex Chen
- **Environment**: VS Code with GitHub Copilot
- **Workflow**: Uses `/flow:specify` to create PRDs, `/flow:implement` to generate code
- **Pain Point**: Cannot access flowspec commands in Copilot Chat - must switch to terminal

**Persona 2: Platform Engineer**
- **Name**: Jordan Martinez
- **Environment**: VS Code Insiders (testing pre-release features)
- **Workflow**: Uses `/flow:plan` for architecture design, `/flow:operate` for SRE tasks
- **Pain Point**: Commands work in stable VS Code but break in Insiders due to directory structure assumptions

**Persona 3: Product Manager (Non-Technical)**
- **Name**: Sam Taylor
- **Environment**: VS Code with Copilot (no Python/CLI tools installed)
- **Workflow**: Uses `/speckit:specify` to create feature specifications collaboratively with engineers
- **Pain Point**: Cannot use flowspec commands without installing CLI tools - wants IDE-only experience

### User Journey Maps

#### Journey 1: Feature Specification in VS Code

```
Current State (Broken):
1. Alex opens VS Code Copilot Chat
2. Types "/" to see available commands
3. No flowspec commands appear ❌
4. Alex switches to terminal, runs `specify` CLI
5. Copies output back to VS Code

Desired State (Fixed):
1. Alex opens VS Code Copilot Chat
2. Types "/flow:" and sees autocomplete list ✅
3. Selects /flow:specify, provides feature description
4. Command executes in chat, creates PRD
5. Alex continues working in IDE without context switch
```

#### Journey 2: Cross-IDE Workflow (VS Code + Insiders)

```
Current State:
1. Jordan uses VS Code Insiders for testing
2. Slash commands don't appear (Insiders uses different agent paths)
3. Jordan falls back to VS Code stable
4. Commands still don't work (no .github/agents/ directory)

Desired State:
1. Jordan works in VS Code Insiders
2. All flowspec commands available via Copilot Chat
3. Commands work identically to VS Code stable
4. No environment-specific configuration required
```

### Detailed User Stories

**US-1: Command Discovery in Copilot Chat**
```
As a developer using VS Code with GitHub Copilot,
I want to see all flowspec and speckit slash commands in the Copilot Chat command picker,
So that I can discover and use SDD workflows without leaving my IDE.

Acceptance Criteria:
- When I type "/" in Copilot Chat, I see commands grouped by prefix (flowspec, speckit)
- Each command shows a brief description (from frontmatter)
- Commands are filtered as I type (e.g., "/flow:sp" filters to specify, speckit.specify)
- Commands work identically in VS Code and VS Code Insiders
```

**US-2: Command Execution in VS Code**
```
As a developer,
I want flowspec commands to execute correctly when invoked in Copilot Chat,
So that I can create specs, generate code, and validate work without CLI tools.

Acceptance Criteria:
- /flow:specify creates a PRD in docs/prd/ with proper frontmatter
- /flow:implement generates implementation code with tests
- /speckit:plan creates architecture decision records in docs/adr/
- All commands respect flowspec_workflow.yml state transitions
- Error messages are displayed if workflow state is invalid
```

**US-3: Automated Command Synchronization**
```
As a maintainer of JP Flowspec,
I want changes to .claude/commands/ to automatically sync to .github/agents/,
So that I don't need to manually maintain two copies of every command.

Acceptance Criteria:
- Running `scripts/bash/sync-copilot-agents.sh` converts all commands
- Script transforms frontmatter: mode: agent → mode: flowspec.<name>
- Script preserves all prompt content and includes
- Script runs in < 1 second for 23 commands
- Optional: Pre-commit hook calls script automatically
```

**US-4: Cross-IDE Compatibility Testing**
```
As a QA engineer,
I want a test suite that verifies command availability in both VS Code editions,
So that we can catch compatibility regressions before release.

Acceptance Criteria:
- Test script checks command presence in .github/agents/
- Test script validates frontmatter format (mode: <command-name>)
- Test script runs smoke tests (invoke each command with sample input)
- Test results show pass/fail for VS Code + Insiders separately
```

### Edge Cases and Error Scenarios

**Edge Case 1: Command Name Conflicts**
- **Scenario**: VS Code has native slash commands that conflict with flowspec
- **Handling**: Use namespaced format (`flow:specify` not just `specify`)
- **Validation**: Check VS Code Copilot docs for reserved command names

**Edge Case 2: Frontmatter Include Directives**
- **Scenario**: Commands use `{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}`
- **Handling**: Sync script must resolve includes and embed content in .github/agents/ files
- **Validation**: Test that included content appears in Copilot command execution

**Edge Case 3: Insiders Pre-Release Changes**
- **Scenario**: VS Code Insiders changes agent directory structure in new builds
- **Handling**: Monitor VS Code Insiders release notes, update sync script as needed
- **Validation**: Test suite runs against both stable and Insiders weekly

**Error Scenario 1: Missing .github/agents/ Directory**
- **Error Message**: "GitHub Copilot agents directory not found. Run `scripts/bash/sync-copilot-agents.sh` to create."
- **Recovery**: Script automatically creates directory and converts commands

**Error Scenario 2: Invalid Frontmatter Format**
- **Error Message**: "Invalid frontmatter in .github/agents/flowspec.specify.md: mode must be 'flowspec.specify', found 'agent'"
- **Recovery**: Validation script identifies incorrectly formatted files and shows fix command

---

## 3. DVF+V Risk Assessment

### Value Risk (Desirability)

**Question**: Will developers actually use flowspec commands in VS Code Copilot, or do they prefer the CLI?

**Risk Level**: LOW

**Validation Plan**:
- **Concierge Test**: Manually convert 3 commands (specify, implement, plan) for early testing
- **Prototype**: Create .github/agents/ for flowspec.specify only, share with 5 beta users
- **Success Criteria**: 3 out of 5 users prefer VS Code Copilot over CLI for spec creation

**Mitigation**:
- Survey current flowspec users: "Would you use flowspec commands in VS Code Copilot if available?"
- Hypothesis: Developers already using Copilot Chat prefer in-IDE workflows over CLI

### Usability Risk (Experience)

**Question**: Can users figure out how to discover and invoke flowspec commands in Copilot Chat?

**Risk Level**: LOW

**Validation Plan**:
- **Usability Test**: Ask 3 developers to "create a feature spec using flowspec" without instructions
- **Metrics**: Time to discover command, number of failed attempts, need for documentation
- **Success Criteria**: All 3 users find and execute `/flow:specify` in < 2 minutes

**Mitigation**:
- Add README section: "Using flowspec with VS Code Copilot"
- Include screenshot of Copilot Chat command picker showing flowspec commands
- Hypothesis: Command picker autocomplete makes discovery intuitive

### Feasibility Risk (Technical)

**Question**: Can we reliably transform Claude Code command format to GitHub Copilot format?

**Risk Level**: MEDIUM

**Validation Plan**:
- **Spike**: Build prototype sync script for 1 command, test in VS Code
- **Technical Constraints**:
  - Frontmatter format differences (mode: agent vs mode: <command-name>)
  - Include directives (`{{INCLUDE:...}}`) need resolution
  - File naming conventions (flowspec/specify.md vs flowspec.specify.md)
- **Success Criteria**: Sync script converts all 23 commands without manual edits

**Mitigation**:
- **Risk**: Include directives fail in Copilot → Solution: Pre-process includes during sync
- **Risk**: Command naming conflicts → Solution: Use namespaced prefixes (flow:, speckit:)
- **Risk**: VS Code Insiders breaks compatibility → Solution: Monitor release notes, maintain test suite

### Business Viability Risk (Organizational)

**Question**: Does supporting two agent systems increase maintenance burden beyond acceptable limits?

**Risk Level**: LOW

**Validation Plan**:
- **Cost Analysis**: Estimate time to maintain dual systems (1-2 hours/month for sync script updates)
- **Benefit**: Unlocks entire VS Code/Copilot user base (>> Claude Code CLI users)
- **Success Criteria**: Sync automation reduces manual work to < 30 minutes/month

**Mitigation**:
- Automate sync with pre-commit hook (zero manual effort)
- Add CI check: Fail PR if .claude/commands/ and .github/agents/ are out of sync
- Hypothesis: Automation makes dual-system maintenance negligible

---

## 4. Functional Requirements

### FR-1: Directory Structure for GitHub Copilot

**Requirement**: Create `.github/agents/` directory with flat file structure for Copilot commands.

**Details**:
```
.github/
└── agents/
    ├── flowspec.assess.md
    ├── flowspec.specify.md
    ├── flowspec.research.md
    ├── flowspec.plan.md
    ├── flowspec.implement.md
    ├── flowspec.validate.md
    ├── flowspec.operate.md
    ├── flowspec.prune-branch.md
    ├── flowspec.init.md
    ├── flowspec.reset.md
    ├── flowspec.security_fix.md
    ├── flowspec.security_report.md
    ├── flowspec.security_triage.md
    ├── flowspec.security_web.md
    ├── flowspec.security_workflow.md
    ├── speckit.specify.md
    ├── speckit.plan.md
    ├── speckit.tasks.md
    ├── speckit.implement.md
    ├── speckit.constitution.md
    ├── speckit.clarify.md
    ├── speckit.analyze.md
    └── speckit.checklist.md
```

**Acceptance Criteria**:
- Directory `.github/agents/` exists and is tracked in git
- All 23 command files present with correct naming (`<namespace>.<command>.md`)
- Files use UTF-8 encoding with LF line endings (Unix-style)

---

### FR-2: Frontmatter Format Transformation

**Requirement**: Convert Claude Code frontmatter format to GitHub Copilot format.

**Details**:

**Input** (Claude Code format - `.claude/commands/flow/specify.md`):
```yaml
---
description: Create or update feature specifications using PM planner agent
mode: agent
---
```

**Output** (GitHub Copilot format - `.github/agents/flowspec.specify.md`):
```yaml
---
description: Create or update feature specifications using PM planner agent
mode: flowspec.specify
---
```

**Transformation Rules**:
1. `mode: agent` → `mode: <namespace>.<command>` (namespace = flowspec or speckit)
2. `description:` field preserved verbatim
3. `scripts:` field (if present) removed (not supported by Copilot)
4. All other frontmatter fields preserved

**Acceptance Criteria**:
- Sync script correctly transforms mode field for all 23 commands
- Description field matches source file exactly
- Invalid frontmatter triggers validation error with helpful message

---

### FR-3: Include Directive Resolution

**Requirement**: Resolve `{{INCLUDE:...}}` directives by embedding referenced file content.

**Details**:

Many flowspec commands include shared prompt fragments:
```markdown
{{INCLUDE:.claude/partials/flow/_constitution-check.md}}
{{INCLUDE:.claude/partials/flow/_workflow-state.md}}
{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}
```

**Sync script must**:
1. Detect `{{INCLUDE:<path>}}` patterns in command file
2. Read referenced file content (relative to `.claude/commands/flow/`)
3. Replace directive with file content inline
4. Preserve markdown formatting and indentation

**Example**:

**Source** (`.claude/commands/flow/specify.md`):
```markdown
## Execution Instructions

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}

Your task is...
```

**Output** (`.github/agents/flowspec.specify.md`):
```markdown
## Execution Instructions

[Full content of _constitution-check.md embedded here]

Your task is...
```

**Acceptance Criteria**:
- All `{{INCLUDE:...}}` directives resolved in .github/agents/ files
- Nested includes (includes within includes) supported (max depth: 3)
- Missing include files trigger clear error: "Include file not found: <path>"

---

### FR-4: Command Synchronization Script

**Requirement**: Provide automation script to convert `.claude/commands/` to `.github/agents/`.

**Details**:

**Script Location**: `scripts/bash/sync-copilot-agents.sh`

**Script Behavior**:
```bash
#!/usr/bin/env bash
# Converts .claude/commands/flow/*.md and .claude/commands/speckit/*.md
# to .github/agents/<namespace>.<command>.md with Copilot-compatible frontmatter

# Usage:
#   ./scripts/bash/sync-copilot-agents.sh           # Convert all commands
#   ./scripts/bash/sync-copilot-agents.sh --dry-run # Show what would change
#   ./scripts/bash/sync-copilot-agents.sh --validate # Check for sync drift
```

**Processing Steps**:
1. Create `.github/agents/` directory if not exists
2. For each `.claude/commands/flow/*.md` (excluding `_*.md` fragments):
   - Read frontmatter and content
   - Transform frontmatter (mode: agent → mode: flowspec.<name>)
   - Resolve all `{{INCLUDE:...}}` directives
   - Write to `.github/agents/flowspec.<name>.md`
3. Repeat for `.claude/commands/speckit/*.md`
4. Output summary: "Converted 23 commands (15 flowspec, 8 speckit)"

**Flags**:
- `--dry-run`: Show files that would be created/updated without writing
- `--validate`: Check if .github/agents/ is in sync with .claude/commands/
- `--force`: Overwrite existing files without prompting

**Acceptance Criteria**:
- Script runs successfully on macOS and Linux (bash 4+)
- Script completes in < 2 seconds for 23 commands
- `--validate` flag exits with code 1 if directories out of sync (for CI)
- Script is executable: `chmod +x scripts/bash/sync-copilot-agents.sh`

---

### FR-5: Pre-Commit Hook Integration (Optional)

**Requirement**: Automatically sync commands when `.claude/commands/` files are modified.

**Details**:

**Hook Location**: `.git/hooks/pre-commit` (via `.flowspec/hooks/hooks.yaml` or manual install)

**Hook Behavior**:
```yaml
# In .flowspec/hooks/hooks.yaml
hooks:
  pre-commit:
    - name: sync-copilot-agents
      description: Sync .claude/commands/ to .github/agents/
      script: scripts/bash/sync-copilot-agents.sh --validate
      on_failure: warn  # Don't block commit, just warn
```

**User Workflow**:
1. Developer edits `.claude/commands/flow/specify.md`
2. Runs `git add .claude/commands/flow/specify.md`
3. Runs `git commit -m "Update specify command"`
4. Pre-commit hook:
   - Detects change to .claude/commands/
   - Runs sync script
   - Auto-stages .github/agents/flowspec.specify.md
   - Commit proceeds with both files

**Acceptance Criteria**:
- Hook triggers only when .claude/commands/ files are staged
- Hook auto-stages generated .github/agents/ files
- Hook can be bypassed with `git commit --no-verify` if needed
- Hook shows clear output: "Synced flowspec.specify.md to .github/agents/"

---

### FR-6: VS Code and VS Code Insiders Compatibility

**Requirement**: Commands must work identically in both VS Code stable and VS Code Insiders.

**Details**:

**Testing Matrix**:

| IDE | Version | GitHub Copilot Extension | Test Result |
|-----|---------|-------------------------|-------------|
| VS Code | 1.85+ | Latest stable | PASS/FAIL |
| VS Code Insiders | Latest | Latest pre-release | PASS/FAIL |

**Compatibility Checks**:
1. Commands appear in Copilot Chat command picker (type "/" to list)
2. Commands execute without errors when invoked
3. Command output matches expected behavior (e.g., /flow:specify creates PRD)
4. Include directives are resolved (no `{{INCLUDE:...}}` in output)
5. Workflow state transitions work (flowspec_workflow.yml integration)

**Acceptance Criteria**:
- All 23 commands pass smoke tests in both VS Code and Insiders
- No IDE-specific configuration required (same .github/agents/ works in both)
- Test results documented in `docs/testing/copilot-compatibility-report.md`

---

### FR-7: Command Documentation and Discovery

**Requirement**: Update documentation to explain dual-agent system and VS Code Copilot usage.

**Details**:

**README.md Updates**:
```markdown
## Using flowspec with VS Code Copilot

JP Flowspec commands are available in **both** Claude Code CLI and VS Code Copilot Chat:

### In Claude Code CLI
```bash
specify --help
# Use /flow:specify, /flow:implement, etc.
```

### In VS Code Copilot Chat
1. Open Copilot Chat panel (Cmd+Shift+I or Ctrl+Shift+I)
2. Type "/" to see available commands
3. Select /flow:specify (or any other command)
4. Provide feature description and press Enter

### Command Availability
- **Claude Code**: Uses `.claude/commands/` directory
- **VS Code Copilot**: Uses `.github/agents/` directory
- Both are kept in sync automatically via `scripts/bash/sync-copilot-agents.sh`

### For Maintainers
If you modify commands in `.claude/commands/`, run the sync script:
```bash
./scripts/bash/sync-copilot-agents.sh
git add .github/agents/
git commit -m "Sync Copilot agents"
```
```

**CLAUDE.md Updates**:
```markdown
## Copilot Agent Synchronization

JP Flowspec maintains two agent systems:
- `.claude/commands/` for Claude Code CLI
- `.github/agents/` for VS Code Copilot

**Sync commands**: `scripts/bash/sync-copilot-agents.sh`

See [VS Code Copilot Guide](docs/guides/vscode-copilot-setup.md) for setup instructions.
```

**Acceptance Criteria**:
- README mentions both Claude Code and VS Code Copilot support
- CLAUDE.md documents sync script usage
- New guide created: `docs/guides/vscode-copilot-setup.md` with screenshots

---

## 5. Non-Functional Requirements

### NFR-1: Cross-Platform Compatibility

**Requirement**: Sync script must work on macOS, Linux, and Windows (WSL).

**Details**:
- Script uses POSIX-compliant bash (no bash 5+ specific features)
- File paths use forward slashes (compatible with WSL)
- Script detects OS and adjusts behavior if needed (e.g., `sed` syntax differences)

**Acceptance Criteria**:
- Script tested on macOS 12+, Ubuntu 20.04+, Windows 11 WSL2
- CI runs sync script on all three platforms (GitHub Actions matrix)

---

### NFR-2: Performance

**Requirement**: Sync script completes in under 2 seconds for all 23 commands.

**Details**:
- File I/O optimized (read files once, batch writes)
- Include resolution uses caching (don't re-read same fragment multiple times)
- Progress output optional (quiet mode for CI)

**Acceptance Criteria**:
- Benchmark on 2020+ MacBook Pro: < 1 second average (10 runs)
- No performance degradation with 50+ commands (future-proofing)

---

### NFR-3: Maintainability

**Requirement**: Dual-agent system should not significantly increase maintenance burden.

**Details**:
- Sync script is idempotent (safe to run multiple times)
- Validation mode (`--validate`) integrated into CI
- Clear error messages guide users to resolution

**Acceptance Criteria**:
- CI fails PR if .claude/commands/ changed but .github/agents/ not updated
- Sync script has 80%+ code coverage (tested with bats framework)
- Documentation includes troubleshooting section for common issues

---

### NFR-4: IDE Integration Quality

**Requirement**: Commands should feel native to VS Code Copilot experience.

**Details**:
- Commands appear in autocomplete with descriptions
- Command execution shows progress (if Copilot supports)
- Error messages are actionable (not cryptic stack traces)

**Acceptance Criteria**:
- User survey: 80%+ satisfaction with VS Code Copilot integration
- Commands indistinguishable from native Copilot commands (UX parity)

---

## 6. Task Breakdown (Backlog Tasks)

The following backlog tasks have been created for this implementation:

### Created Tasks

**All 8 tasks have been created in backlog.md:**

- **task-316**: Create .github/agents/ directory structure (Priority: High, Labels: implement,infrastructure)
- **task-317**: Convert flowspec commands to Copilot format (Priority: High, Labels: implement,copilot)
- **task-318**: Convert speckit commands to Copilot format (Priority: High, Labels: implement,copilot)
- **task-319**: Build sync-copilot-agents.sh automation script (Priority: High, Labels: implement,tooling)
- **task-320**: Test commands in VS Code and VS Code Insiders (Priority: High, Labels: test,copilot)
- **task-321**: Create pre-commit hook for agent sync (Priority: Medium, Labels: implement,tooling)
- **task-322**: Add CI check for agent sync drift (Priority: Medium, Labels: implement,ci)
- **task-323**: Update documentation for VS Code Copilot support (Priority: Medium, Labels: docs)

### Task Creation Commands (Reference)

```bash
# Task 1: Create .github/agents/ directory structure
backlog task create "Create .github/agents/ directory structure" \
  -d "Set up the GitHub Copilot agents directory with proper structure for VS Code and VS Code Insiders compatibility" \
  --ac "Directory .github/agents/ exists and is tracked in git" \
  --ac "Directory contains README explaining purpose and sync process" \
  --ac "Directory structure validated by test script" \
  -a @pm-planner \
  -l implement,infrastructure \
  --priority high

# Task 2: Convert flowspec commands to Copilot format
backlog task create "Convert flowspec commands to Copilot format" \
  -d "Convert all 15 flowspec.* commands from .claude/commands/flow/ to .github/agents/ with correct mode: frontmatter and resolved includes" \
  --ac "All 15 flowspec.* files exist in .github/agents/ with correct naming" \
  --ac "Each file has mode: flowspec.<name> frontmatter (not mode: agent)" \
  --ac "All {{INCLUDE:...}} directives are resolved and embedded" \
  --ac "Commands appear in VS Code Copilot Chat command picker" \
  --ac "Commands appear in VS Code Insiders Copilot Chat command picker" \
  -a @pm-planner \
  -l implement,copilot \
  --priority high

# Task 3: Convert speckit commands to Copilot format
backlog task create "Convert speckit commands to Copilot format" \
  -d "Convert all 8 speckit.* commands from .claude/commands/speckit/ to .github/agents/ with correct mode: frontmatter and resolved includes" \
  --ac "All 8 speckit.* files exist in .github/agents/ with correct naming" \
  --ac "Each file has mode: speckit.<name> frontmatter (not mode: agent)" \
  --ac "All {{INCLUDE:...}} directives are resolved and embedded" \
  --ac "Commands appear in VS Code Copilot Chat command picker" \
  --ac "Commands appear in VS Code Insiders Copilot Chat command picker" \
  -a @pm-planner \
  -l implement,copilot \
  --priority high

# Task 4: Build automated sync script
backlog task create "Build sync-copilot-agents.sh automation script" \
  -d "Create Bash script to automate conversion of .claude/commands/ to .github/agents/ with frontmatter transformation and include resolution" \
  --ac "Script located at scripts/bash/sync-copilot-agents.sh with execute permissions" \
  --ac "Script converts all 23 commands (flowspec + speckit) without manual edits" \
  --ac "Script supports --dry-run, --validate, and --force flags" \
  --ac "Script resolves {{INCLUDE:...}} directives correctly (max depth 3)" \
  --ac "Script completes in under 2 seconds for 23 commands" \
  --ac "Script runs successfully on macOS, Linux, and Windows WSL2" \
  -a @pm-planner \
  -l implement,tooling \
  --priority high

# Task 5: Test commands in VS Code and VS Code Insiders
backlog task create "Test commands in VS Code and VS Code Insiders" \
  -d "Verify all 23 slash commands work correctly in both VS Code stable and Insiders editions with comprehensive smoke tests" \
  --ac "Test /flow:specify in VS Code - command appears in picker and executes correctly" \
  --ac "Test /flow:specify in VS Code Insiders - command appears and executes correctly" \
  --ac "Smoke test all 23 commands in both IDEs (invoke with sample input)" \
  --ac "Document any behavioral differences between VS Code and Insiders" \
  --ac "Create test report: docs/testing/copilot-compatibility-report.md" \
  -a @pm-planner \
  -l test,copilot \
  --priority high

# Task 6: Create pre-commit hook integration
backlog task create "Create pre-commit hook for agent sync" \
  -d "Add pre-commit hook to automatically sync .claude/commands/ changes to .github/agents/ when commands are modified" \
  --ac "Hook configuration added to .flowspec/hooks/hooks.yaml" \
  --ac "Hook triggers only when .claude/commands/ files are staged" \
  --ac "Hook auto-stages generated .github/agents/ files" \
  --ac "Hook can be bypassed with git commit --no-verify" \
  --ac "Hook shows clear output indicating which files were synced" \
  -a @pm-planner \
  -l implement,tooling \
  --priority medium

# Task 7: Add CI validation for sync drift
backlog task create "Add CI check for agent sync drift" \
  -d "Create GitHub Actions workflow to validate .claude/commands/ and .github/agents/ are in sync on every PR" \
  --ac "CI workflow runs sync-copilot-agents.sh --validate on every PR" \
  --ac "CI fails if .claude/commands/ changed but .github/agents/ not updated" \
  --ac "CI runs on macOS, Linux, and Windows (GitHub Actions matrix)" \
  --ac "CI performance: validation completes in under 30 seconds" \
  -a @pm-planner \
  -l implement,ci \
  --priority medium

# Task 8: Update documentation for dual-agent support
backlog task create "Update documentation for VS Code Copilot support" \
  -d "Document how flowspec supports both Claude Code CLI and VS Code Copilot with setup instructions and screenshots" \
  --ac "README.md mentions both .claude/commands/ and .github/agents/ directories" \
  --ac "CLAUDE.md documents sync script usage and workflow" \
  --ac "New guide created: docs/guides/vscode-copilot-setup.md with setup steps" \
  --ac "Setup guide includes screenshots of Copilot Chat command picker" \
  --ac "Troubleshooting section added for common sync issues" \
  -a @pm-planner \
  -l docs \
  --priority medium
```

### Task Dependency Graph

```
┌─────────────────────────────────┐
│ Task 1: Create directory        │
│ (Infrastructure)                │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│ Task 2: │      │ Task 3: │
│ Convert │      │ Convert │
│ flowspec  │      │ speckit │
└────┬────┘      └────┬────┘
     │                │
     └────────┬───────┘
              │
              ▼
         ┌─────────┐
         │ Task 4: │
         │ Sync    │
         │ Script  │
         └────┬────┘
              │
         ┌────┴────┐
         │         │
         ▼         ▼
    ┌─────────┐ ┌─────────┐
    │ Task 5: │ │ Task 6: │
    │ Testing │ │ Pre-    │
    │         │ │ commit  │
    └─────────┘ └─────────┘
         │
         ▼
    ┌─────────┐
    │ Task 7: │
    │ CI      │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │ Task 8: │
    │ Docs    │
    └─────────┘
```

### Priority and Complexity Estimates

| Task | Priority | Complexity | Estimated Time |
|------|----------|-----------|----------------|
| Task 1: Directory structure | High | Small | 30 min |
| Task 2: Convert flowspec | High | Medium | 2 hours |
| Task 3: Convert speckit | High | Medium | 1 hour |
| Task 4: Sync script | High | Large | 4 hours |
| Task 5: Testing | High | Medium | 3 hours |
| Task 6: Pre-commit hook | Medium | Small | 1 hour |
| Task 7: CI validation | Medium | Medium | 2 hours |
| Task 8: Documentation | Medium | Medium | 2 hours |
| **Total** | | | **15.5 hours** |

---

## 7. Discovery and Validation Plan

### Learning Goals and Hypotheses

**Hypothesis 1: Developers prefer in-IDE workflows over CLI tools**
- **Learning Goal**: Measure adoption rate of VS Code Copilot commands vs CLI usage
- **Validation**: Track command invocation metrics (CLI vs Copilot) for 2 weeks post-launch
- **Success Criteria**: 60%+ of flowspec command invocations come from Copilot Chat

**Hypothesis 2: Include directive resolution is reliable**
- **Learning Goal**: Verify sync script correctly resolves all nested includes without errors
- **Validation**: Unit tests for include resolution (10 test cases with varying nesting depths)
- **Success Criteria**: 100% pass rate on include resolution tests

**Hypothesis 3: VS Code Insiders compatibility is stable**
- **Learning Goal**: Identify if Insiders releases break agent compatibility
- **Validation**: Weekly automated tests against Insiders pre-release builds
- **Success Criteria**: < 1 compatibility break per quarter (acceptable maintenance burden)

### Validation Experiments

**Experiment 1: Concierge Test (Manual Conversion)**
- **Purpose**: Validate frontmatter format before building automation
- **Method**: Manually convert 3 commands (specify, implement, plan) to .github/agents/
- **Duration**: 1 day
- **Success Criteria**: Commands appear in Copilot Chat and execute correctly

**Experiment 2: Prototype Sync Script**
- **Purpose**: Validate technical feasibility of automated conversion
- **Method**: Build minimal viable sync script for flowspec.specify only
- **Duration**: 2 days
- **Success Criteria**: Script converts 1 command correctly in < 5 seconds

**Experiment 3: Usability Testing with Beta Users**
- **Purpose**: Validate discoverability and usability of Copilot commands
- **Method**: Give 5 users access to converted commands, observe first usage
- **Duration**: 1 week
- **Success Criteria**: All 5 users discover and use /flow:specify without documentation

### Go/No-Go Decision Points

**Decision Point 1: After Concierge Test (Day 1)**
- **Go Criteria**: Commands appear in Copilot Chat and execute successfully
- **No-Go Criteria**: Copilot rejects frontmatter format or commands don't appear
- **Mitigation**: If No-Go, investigate VS Code Copilot documentation for correct agent format

**Decision Point 2: After Prototype Sync Script (Day 3)**
- **Go Criteria**: Script converts 1 command correctly and passes validation
- **No-Go Criteria**: Include resolution fails or script errors on edge cases
- **Mitigation**: If No-Go, simplify approach (flatten includes into main command files)

**Decision Point 3: After Beta Testing (Week 2)**
- **Go Criteria**: 80%+ user satisfaction, < 3 critical bugs reported
- **No-Go Criteria**: Users confused by dual-system or encounter frequent errors
- **Mitigation**: If No-Go, improve documentation and error messages before wider rollout

---

## 8. Acceptance Criteria and Testing

### Overall Definition of Done

The feature is considered complete when:

1. All 23 commands (15 flowspec + 8 speckit) exist in `.github/agents/` with correct frontmatter
2. Commands appear in VS Code and VS Code Insiders Copilot Chat command picker
3. Smoke tests pass for all commands in both IDEs (invoke with sample input, verify output)
4. Sync script completes successfully in < 2 seconds
5. CI validation passes (no sync drift detected)
6. Documentation updated (README, CLAUDE.md, new setup guide)
7. Pre-commit hook integrated and tested
8. Compatibility test report published: `docs/testing/copilot-compatibility-report.md`

### Acceptance Test Scenarios

**Scenario 1: Command Discovery**
```gherkin
Given I am using VS Code with GitHub Copilot extension
When I open Copilot Chat and type "/"
Then I see all 23 flowspec and speckit commands in the autocomplete list
And each command shows its description from frontmatter
```

**Scenario 2: Command Execution (flow:specify)**
```gherkin
Given I have a project with flowspec_workflow.yml configured
When I invoke /flow:specify with "Add user authentication feature"
Then the PM Planner agent creates a PRD at docs/prd/user-auth-spec.md
And the PRD includes all 10 required sections
And backlog tasks are created with proper labels and assignments
```

**Scenario 3: Sync Script Dry Run**
```gherkin
Given I have modified .claude/commands/flow/specify.md
When I run ./scripts/bash/sync-copilot-agents.sh --dry-run
Then I see output: "Would update: .github/agents/flowspec.specify.md"
And no files are actually modified
```

**Scenario 4: Include Directive Resolution**
```gherkin
Given .claude/commands/flow/specify.md contains {{INCLUDE:_backlog-instructions.md}}
When I run the sync script
Then .github/agents/flowspec.specify.md contains the full content of _backlog-instructions.md
And no {{INCLUDE:...}} directives remain in the output file
```

**Scenario 5: VS Code Insiders Compatibility**
```gherkin
Given I am using VS Code Insiders (pre-release build)
When I invoke /flow:implement with a task ID
Then the command executes identically to VS Code stable
And no Insiders-specific errors occur
```

### Quality Gates

**Gate 1: Code Review**
- Sync script reviewed by 2+ maintainers
- Bash best practices followed (shellcheck passes)
- Include resolution logic has unit tests

**Gate 2: Testing**
- All smoke tests pass in VS Code + Insiders
- Sync script performance < 2 seconds
- CI validation detects intentional sync drift (negative test)

**Gate 3: Documentation**
- README updated with VS Code Copilot instructions
- Setup guide includes screenshots
- Troubleshooting section covers common issues

**Gate 4: User Acceptance**
- 3+ beta users successfully use Copilot commands
- User feedback survey shows 80%+ satisfaction
- No critical bugs reported in beta period

### Test Coverage Requirements

**Unit Tests** (scripts/bash/sync-copilot-agents.sh):
- Frontmatter transformation (5 test cases)
- Include directive resolution (10 test cases with nesting)
- File naming conversion (3 test cases)
- Edge cases (empty files, missing includes, nested directories)
- Target: 80% code coverage

**Integration Tests** (VS Code Copilot):
- Command discovery (all 23 commands appear)
- Command execution (smoke test with sample input)
- Include resolution (verify embedded content)
- Cross-IDE compatibility (VS Code vs Insiders)
- Target: 100% command coverage

**Performance Tests**:
- Sync script baseline: < 1 second for 23 commands
- Sync script scalability: < 5 seconds for 100 commands
- CI validation: < 30 seconds total runtime

---

## 9. Dependencies and Constraints

### Technical Dependencies

**External Dependencies**:
- VS Code 1.85+ with GitHub Copilot extension (latest stable)
- VS Code Insiders with GitHub Copilot pre-release extension
- Bash 4+ (for sync script - macOS, Linux, WSL2)
- Git 2.30+ (for pre-commit hooks)

**Internal Dependencies**:
- Existing `.claude/commands/` command structure
- `flowspec_workflow.yml` for state transitions
- Backlog.md CLI for task management integration

**Breaking Changes**:
- None - this is purely additive (adds .github/agents/, doesn't modify .claude/commands/)

### External Dependencies

**GitHub Copilot API**:
- Agent system is undocumented/beta - may change in future releases
- Risk: Microsoft changes .github/agents/ format or directory structure
- Mitigation: Monitor VS Code release notes, maintain test suite to catch breaking changes

**VS Code Insiders Releases**:
- Pre-release builds may introduce incompatibilities
- Risk: Commands work in stable but break in Insiders
- Mitigation: Weekly automated tests against Insiders, allow 1 week SLA for fixes

### Timeline Constraints

**Ideal Delivery**: 2 weeks (10 working days)
- Week 1: Tasks 1-4 (directory setup, conversion, sync script)
- Week 2: Tasks 5-8 (testing, CI, hooks, documentation)

**Minimum Viable Product (MVP)**: 1 week
- Convert only flowspec.* commands (skip speckit for MVP)
- Manual sync (skip pre-commit hook and CI)
- Test in VS Code stable only (defer Insiders testing)

### Resource Constraints

**Engineering Time**:
- Estimated: 15.5 hours total (see Task Breakdown section)
- Available: 1 full-time engineer for 2 weeks (80 hours) - sufficient capacity

**Testing Environment**:
- Requires access to VS Code stable and Insiders
- Requires GitHub Copilot license (beta access if needed)
- Requires macOS, Linux, and Windows WSL2 VMs for CI testing

### Risk Factors

**Risk 1: Undocumented Copilot Agent Format**
- **Likelihood**: Medium
- **Impact**: High (feature fails completely if format is wrong)
- **Mitigation**: Validate with concierge test before building automation

**Risk 2: Include Directive Complexity**
- **Likelihood**: Medium
- **Impact**: Medium (sync script may fail on edge cases)
- **Mitigation**: Unit test all include resolution patterns, handle errors gracefully

**Risk 3: VS Code Insiders Instability**
- **Likelihood**: Low
- **Impact**: Low (only affects pre-release users)
- **Mitigation**: Weekly tests, 1-week SLA for compatibility fixes

**Risk 4: Increased Maintenance Burden**
- **Likelihood**: Low
- **Impact**: Medium (dual-system maintenance overhead)
- **Mitigation**: Automate sync with pre-commit hook, add CI validation

---

## 10. Success Metrics (Outcome-Focused)

### North Star Metric

**Command Invocation Rate in VS Code Copilot**
- **Definition**: Percentage of flowspec command invocations that occur via VS Code Copilot (vs CLI)
- **Target**: 60% of command invocations from Copilot within 4 weeks post-launch
- **Measurement**: Telemetry (optional - privacy-respecting analytics) or user survey

### Leading Indicators (Early Signals)

**Metric 1: Command Discovery Rate**
- **Definition**: Percentage of VS Code users who discover flowspec commands via Copilot Chat picker
- **Target**: 90%+ discovery rate within 1 week of feature announcement
- **Measurement**: User survey: "How did you first discover flowspec commands?" (options: Copilot picker, docs, word-of-mouth)

**Metric 2: First-Time Execution Success Rate**
- **Definition**: Percentage of users who successfully execute a flowspec command on first attempt
- **Target**: 80%+ success rate
- **Measurement**: Error logs (track failed command invocations), user survey

**Metric 3: Sync Script Adoption**
- **Definition**: Number of PRs that include both .claude/commands/ and .github/agents/ changes
- **Target**: 100% of command-modifying PRs include both directories
- **Measurement**: CI validation pass rate (should be 100% after pre-commit hook integration)

### Lagging Indicators (Final Outcomes)

**Metric 1: Developer Productivity Gain**
- **Definition**: Time saved by using in-IDE commands vs context-switching to CLI
- **Target**: 5-10 minutes saved per command invocation (average)
- **Measurement**: User survey: "How much time does in-IDE flowspec save you per day?"

**Metric 2: flowspec Adoption Rate**
- **Definition**: Percentage of VS Code users who use flowspec commands at least weekly
- **Target**: 50%+ weekly active users (up from 30% CLI-only baseline)
- **Measurement**: Telemetry or user survey

**Metric 3: Support Burden Reduction**
- **Definition**: Number of support requests related to "flowspec commands don't work in VS Code"
- **Target**: Zero support requests after documentation update
- **Measurement**: GitHub Issues, Slack support channel

### Measurement Approach

**Data Collection Methods**:
1. **Optional Telemetry** (privacy-respecting, opt-in):
   - Track command invocation source (CLI vs Copilot)
   - Track command execution success/failure
   - No PII collected (anonymous usage statistics only)

2. **User Surveys**:
   - Post-launch survey (1 week): Discovery, first use experience
   - Follow-up survey (4 weeks): Productivity impact, satisfaction
   - Target: 20+ responses for statistical significance

3. **CI Metrics**:
   - Sync validation pass rate (should be 100% with pre-commit hook)
   - CI runtime performance (should be < 30 seconds)

4. **GitHub Analytics**:
   - PR review time for command changes (should decrease with automation)
   - Number of manual sync errors (should be zero with hooks)

### Target Values and Thresholds

| Metric | Baseline | Target | Stretch Goal |
|--------|----------|--------|--------------|
| Copilot command invocation rate | 0% (not supported) | 60% | 80% |
| Discovery rate | N/A | 90% | 95% |
| First-time success rate | N/A | 80% | 90% |
| Weekly active users | 30% (CLI) | 50% | 70% |
| Support requests | 5/month | 0/month | 0/month |
| CI sync validation pass rate | N/A | 100% | 100% |

---

## Appendices

### Appendix A: Command Inventory

**flowspec Commands** (15 total):
1. flowspec.assess
2. flowspec.specify
3. flowspec.research
4. flowspec.plan
5. flowspec.implement
6. flowspec.validate
7. flowspec.operate
8. flowspec.prune-branch
9. flowspec.init
10. flowspec.reset
11. flowspec.security_fix
12. flowspec.security_report
13. flowspec.security_triage
14. flowspec.security_web
15. flowspec.security_workflow

**speckit Commands** (8 total):
1. speckit.specify
2. speckit.plan
3. speckit.tasks
4. speckit.implement
5. speckit.constitution
6. speckit.clarify
7. speckit.analyze
8. speckit.checklist

**Total**: 23 commands requiring conversion

### Appendix B: Frontmatter Format Reference

**Claude Code Format** (`.claude/commands/flow/specify.md`):
```yaml
---
description: Create or update feature specifications using PM planner agent
mode: agent
---
```

**GitHub Copilot Format** (`.github/agents/flowspec.specify.md`):
```yaml
---
description: Create or update feature specifications using PM planner agent
mode: flowspec.specify
---
```

**Key Difference**: `mode` field value changes from `agent` to `<namespace>.<command>`.

### Appendix C: Include Directive Examples

**Simple Include**:
```markdown
{{INCLUDE:.claude/partials/flow/_constitution-check.md}}
```

**Nested Include** (_constitution-check.md contains another include):
```markdown
{{INCLUDE:.claude/partials/flow/_workflow-base.md}}
```

**Relative Path Resolution**:
- Include paths are relative to `.claude/commands/flow/`
- Sync script must resolve paths correctly from root directory

### Appendix D: Testing Checklist

**Manual Testing Checklist** (before release):
- [ ] Test command discovery in VS Code stable (type "/" in Copilot Chat)
- [ ] Test command discovery in VS Code Insiders
- [ ] Execute /flow:specify in VS Code - verify PRD creation
- [ ] Execute /flow:implement in VS Code - verify code generation
- [ ] Execute /speckit:plan in VS Code - verify ADR creation
- [ ] Run sync script on macOS - verify output
- [ ] Run sync script on Linux - verify output
- [ ] Run sync script on Windows WSL2 - verify output
- [ ] Test pre-commit hook - modify .claude/commands/, verify auto-sync
- [ ] Test CI validation - intentionally create sync drift, verify failure

**Automated Testing Checklist** (CI):
- [ ] Sync script unit tests (80%+ coverage)
- [ ] Include resolution tests (10 test cases)
- [ ] Frontmatter transformation tests (5 test cases)
- [ ] Command discovery smoke tests (23 commands)
- [ ] Cross-platform compatibility tests (macOS, Linux, Windows)

### Appendix E: Rollback Plan

If VS Code Copilot integration fails or introduces critical bugs:

**Rollback Steps**:
1. Remove `.github/agents/` directory: `git rm -rf .github/agents/`
2. Revert README/CLAUDE.md documentation changes
3. Remove pre-commit hook from `.flowspec/hooks/hooks.yaml`
4. Announce rollback to users: "VS Code Copilot support temporarily disabled - use Claude Code CLI"

**Rollback Criteria**:
- Critical bug affecting > 50% of users
- VS Code Copilot format change breaks all commands
- Sync script causes data loss or corruption

**Recovery Time Objective (RTO)**: < 1 hour (simple git revert + docs update)

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-07 | PM Planner Agent | Initial PRD creation |

---

**Next Steps**:
1. Review PRD with engineering team (estimate: 1 hour)
2. Prioritize backlog tasks (see section 6 for task IDs)
3. Run `/flow:plan` to create architecture design
4. Execute `/flow:implement` to begin development
