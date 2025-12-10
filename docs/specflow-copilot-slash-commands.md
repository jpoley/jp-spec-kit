# Issue: `/specflow:` slash commands not appearing in VS Code Copilot Chat

**Repository:** https://github.com/jpoley/jp-spec-kit  
**Labels:** `bug`, `copilot`, `documentation`  
**Priority:** High  
**Created:** 2025-12-07

---

## Problem Summary

Custom slash commands defined in `.claude/commands/` (e.g., `/specflow:specify`, `/specflow:implement`) are **not appearing** in VS Code Copilot Chat. The commands work correctly in Claude Code CLI but are completely invisible in VS Code / VS Code Insiders with GitHub Copilot extension.

---

## Current Setup

Commands are currently located in `.claude/commands/`:

```
.claude/commands/
├── specflow/
├── specflow._backlog-instructions.md
├── specflow._workflow-state.md
├── specflow.assess.md
├── specflow.implement.md
├── specflow.operate.md
├── specflow.plan.md
├── specflow.prune-branch.md
├── specflow.research.md
├── specflow.specify.md
├── specflow.validate.md
├── speckit.analyze.md
├── speckit.checklist.md
├── speckit.clarify.md
├── speckit.constitution.md
├── speckit.implement.md
├── speckit.plan.md
├── speckit.specify.md
├── speckit.tasks.md
└── speckit.taskstoissues.md
```

### Current File Format (Claude Code)

```markdown
---
description: Create or update feature specifications using PM planner agent
mode: agent
---

## User Input
...
```

---

## Root Cause Analysis

Research into [github/spec-kit](https://github.com/jpoley/jp-spec-kit) reveals that **VS Code Copilot uses a completely different directory structure and file format** than Claude Code:

### Agent Directory Comparison

| Agent | Directory | Format | CLI Tool |
|-------|-----------|--------|----------|
| Claude Code | `.claude/commands/` | Markdown | `claude` |
| **GitHub Copilot** | **`.github/agents/`** | Markdown | N/A (IDE-based) |
| Cursor | `.cursor/commands/` | Markdown | `cursor-agent` |
| Gemini | `.gemini/commands/` | TOML | `gemini` |

### File Format Difference

**Claude Code format:**
```markdown
---
description: "Command description"
mode: agent
---
```

**GitHub Copilot format (REQUIRED):**
```markdown
---
description: "Command description"
mode: specflow.specify
---
```

Key difference: Copilot requires `mode: <command-name>` where the mode value becomes the slash command name (e.g., `mode: specflow.specify` → `/specflow.specify`).

---

## Evidence from spec-kit

### From AGENTS.md

> **GitHub Copilot** | `.github/agents/` | Markdown | N/A (IDE-based) | GitHub Copilot in VS Code

### From CHANGELOG.md (v0.0.22)

> - Support for VS Code/Copilot agents, and moving away from prompts to proper agents with hand-offs.
> - Move to use `AGENTS.md` for Copilot workloads, since it's already supported out-of-the-box.

### From Command File Formats section

**GitHub Copilot Chat Mode format:**

```markdown
---
description: "Command description"
mode: speckit.command-name
---

Command content with {SCRIPT} and $ARGUMENTS placeholders.
```

---

## Solution Required

### 1. Create `.github/agents/` Directory

```bash
mkdir -p .github/agents
```

### 2. Convert Commands to Copilot Format

For each command in `.claude/commands/specflow.*.md`, create a corresponding file in `.github/agents/` with:

**Example: `.github/agents/specflow.specify.md`**
```markdown
---
description: Create or update feature specifications using PM planner agent (manages /speckit.tasks).
mode: specflow.specify
---

## User Input

$ARGUMENTS

## Execution Instructions
...
```

### 3. Commands to Convert

| Source File | Target File | Mode Value |
|-------------|-------------|------------|
| `.claude/commands/specflow.specify.md` | `.github/agents/specflow.specify.md` | `specflow.specify` |
| `.claude/commands/specflow.implement.md` | `.github/agents/specflow.implement.md` | `specflow.implement` |
| `.claude/commands/specflow.assess.md` | `.github/agents/specflow.assess.md` | `specflow.assess` |
| `.claude/commands/specflow.plan.md` | `.github/agents/specflow.plan.md` | `specflow.plan` |
| `.claude/commands/specflow.research.md` | `.github/agents/specflow.research.md` | `specflow.research` |
| `.claude/commands/specflow.validate.md` | `.github/agents/specflow.validate.md` | `specflow.validate` |
| `.claude/commands/specflow.operate.md` | `.github/agents/specflow.operate.md` | `specflow.operate` |
| `.claude/commands/specflow.prune-branch.md` | `.github/agents/specflow.prune-branch.md` | `specflow.prune-branch` |
| `.claude/commands/speckit.specify.md` | `.github/agents/speckit.specify.md` | `speckit.specify` |
| `.claude/commands/speckit.plan.md` | `.github/agents/speckit.plan.md` | `speckit.plan` |
| `.claude/commands/speckit.tasks.md` | `.github/agents/speckit.tasks.md` | `speckit.tasks` |
| `.claude/commands/speckit.implement.md` | `.github/agents/speckit.implement.md` | `speckit.implement` |
| `.claude/commands/speckit.constitution.md` | `.github/agents/speckit.constitution.md` | `speckit.constitution` |
| `.claude/commands/speckit.clarify.md` | `.github/agents/speckit.clarify.md` | `speckit.clarify` |
| `.claude/commands/speckit.analyze.md` | `.github/agents/speckit.analyze.md` | `speckit.analyze` |
| `.claude/commands/speckit.checklist.md` | `.github/agents/speckit.checklist.md` | `speckit.checklist` |
| `.claude/commands/speckit.taskstoissues.md` | `.github/agents/speckit.taskstoissues.md` | `speckit.taskstoissues` |

### 4. Update Documentation

- Add note to README about dual-agent support (Claude Code + VS Code Copilot)
- Document that both `.claude/commands/` and `.github/agents/` must be kept in sync
- Consider creating a sync script to generate Copilot agents from Claude commands

---

## Acceptance Criteria

- [ ] `.github/agents/` directory exists with all specflow commands
- [ ] All commands have correct `mode:` frontmatter
- [ ] `/specflow:specify` appears in VS Code Copilot Chat
- [ ] `/specflow:implement` appears in VS Code Copilot Chat
- [ ] All other `/specflow:*` commands appear
- [ ] All `/speckit.*` commands appear
- [ ] Commands execute correctly when invoked
- [ ] Documentation updated

---

## Environment

- **IDE:** VS Code Insiders (also affects regular VS Code)
- **Extension:** GitHub Copilot Chat
- **OS:** macOS
- **Working:** Claude Code CLI (`claude` command)
- **Not Working:** VS Code Copilot Chat

---

## References

- [github/spec-kit repository](https://github.com/jpoley/jp-spec-kit)
- [AGENTS.md - Agent configuration](https://github.com/jpoley/jp-spec-kit/blob/main/AGENTS.md)
- [Command File Formats](https://github.com/jpoley/jp-spec-kit/blob/main/AGENTS.md#command-file-formats)
- [Copilot directory convention](https://github.com/jpoley/jp-spec-kit/blob/main/AGENTS.md#directory-conventions)

---

## Quick Fix (Manual)

If you need this working immediately, run:

```bash
# From jp-spec-kit repo root
mkdir -p .github/agents

# For each command, copy and modify the frontmatter
# Example for specflow.specify:
cp .claude/commands/specflow.specify.md .github/agents/specflow.specify.md

# Then edit .github/agents/specflow.specify.md and change:
# mode: agent
# to:
# mode: specflow.specify
```

Or use spec-kit's CLI to regenerate:

```bash
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init --here --force --ai copilot
```

**Warning:** The spec-kit command will overwrite files. Back up customizations first.
