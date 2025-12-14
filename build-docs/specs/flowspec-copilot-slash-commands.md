# Issue: `/flow:` slash commands not appearing in VS Code Copilot Chat

**Repository:** https://github.com/jpoley/flowspec  
**Labels:** `bug`, `copilot`, `documentation`  
**Priority:** High  
**Created:** 2025-12-07

---

## Problem Summary

Custom slash commands defined in `.claude/commands/` (e.g., `/flow:specify`, `/flow:implement`) are **not appearing** in VS Code Copilot Chat. The commands work correctly in Claude Code CLI but are completely invisible in VS Code / VS Code Insiders with GitHub Copilot extension.

---

## Current Setup

Commands are currently located in `.claude/commands/`:

```
.claude/commands/
├── flowspec/
├── flowspec._backlog-instructions.md
├── flowspec._workflow-state.md
├── flowspec.assess.md
├── flowspec.implement.md
├── flowspec.operate.md
├── flowspec.plan.md
├── flowspec.prune-branch.md
├── flowspec.research.md
├── flowspec.specify.md
├── flowspec.validate.md
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

Research into [github/spec-kit](https://github.com/jpoley/flowspec) reveals that **VS Code Copilot uses a completely different directory structure and file format** than Claude Code:

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
mode: flowspec.specify
---
```

Key difference: Copilot requires `mode: <command-name>` where the mode value becomes the slash command name (e.g., `mode: flowspec.specify` → `/flowspec.specify`).

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

For each command in `.claude/commands/flow.*.md`, create a corresponding file in `.github/agents/` with:

**Example: `.github/agents/flowspec.specify.md`**
```markdown
---
description: Create or update feature specifications using PM planner agent (manages /speckit.tasks).
mode: flowspec.specify
---

## User Input

$ARGUMENTS

## Execution Instructions
...
```

### 3. Commands to Convert

| Source File | Target File | Mode Value |
|-------------|-------------|------------|
| `.claude/commands/flow.specify.md` | `.github/agents/flowspec.specify.md` | `flowspec.specify` |
| `.claude/commands/flow.implement.md` | `.github/agents/flowspec.implement.md` | `flowspec.implement` |
| `.claude/commands/flow.assess.md` | `.github/agents/flowspec.assess.md` | `flowspec.assess` |
| `.claude/commands/flow.plan.md` | `.github/agents/flowspec.plan.md` | `flowspec.plan` |
| `.claude/commands/flow.research.md` | `.github/agents/flowspec.research.md` | `flowspec.research` |
| `.claude/commands/flow.validate.md` | `.github/agents/flowspec.validate.md` | `flowspec.validate` |
| `.claude/commands/flow.operate.md` | `.github/agents/flowspec.operate.md` | `flowspec.operate` |
| `.claude/commands/flow.prune-branch.md` | `.github/agents/flowspec.prune-branch.md` | `flowspec.prune-branch` |
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

- [ ] `.github/agents/` directory exists with all flowspec commands
- [ ] All commands have correct `mode:` frontmatter
- [ ] `/flow:specify` appears in VS Code Copilot Chat
- [ ] `/flow:implement` appears in VS Code Copilot Chat
- [ ] All other `/flow:*` commands appear
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

- [github/spec-kit repository](https://github.com/jpoley/flowspec)
- [AGENTS.md - Agent configuration](https://github.com/jpoley/flowspec/blob/main/AGENTS.md)
- [Command File Formats](https://github.com/jpoley/flowspec/blob/main/AGENTS.md#command-file-formats)
- [Copilot directory convention](https://github.com/jpoley/flowspec/blob/main/AGENTS.md#directory-conventions)

---

## Quick Fix (Manual)

If you need this working immediately, run:

```bash
# From flowspec repo root
mkdir -p .github/agents

# For each command, copy and modify the frontmatter
# Example for flowspec.specify:
cp .claude/commands/flow.specify.md .github/agents/flowspec.specify.md

# Then edit .github/agents/flowspec.specify.md and change:
# mode: agent
# to:
# mode: flowspec.specify
```

Or use spec-kit's CLI to regenerate:

```bash
uvx --from git+https://github.com/jpoley/flowspec.git specify init --here --force --ai copilot
```

**Warning:** The spec-kit command will overwrite files. Back up customizations first.
