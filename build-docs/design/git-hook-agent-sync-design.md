# Design: Git Hook Integration for Agent Sync

**Task:** task-328
**Author:** @muckross
**Date:** 2025-12-14
**Status:** Design Complete

## Overview

Design a pre-commit hook that automatically syncs `.claude/commands/` changes to `.github/agents/` when command files are staged for commit.

## Problem Statement

When developers modify Claude Code commands in `.claude/commands/**/*.md`, the corresponding VS Code Copilot agents in `.github/agents/` must be updated to stay in sync. Currently, this requires manually running `scripts/bash/sync-copilot-agents.sh`, which is easy to forget.

## Solution: Pre-commit Hook

A git pre-commit hook will automatically detect staged command files and run the sync script, ensuring agents are always synchronized.

### Architecture

```
Developer stages .claude/commands/flow/implement.md
    ↓
git commit
    ↓
pre-commit hook fires
    ↓
Hook detects: .claude/commands/*.md files staged
    ↓
Hook runs: scripts/bash/sync-copilot-agents.sh
    ↓
Hook stages: git add .github/agents/
    ↓
Commit proceeds with both source and generated files
```

## Hook Configuration

### Option 1: Pre-commit Framework (Recommended)

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: sync-copilot-agents
        name: Sync Claude commands to Copilot agents
        entry: scripts/bash/pre-commit-agent-sync.sh
        language: script
        files: ^\.claude/commands/.*\.md$|^templates/commands/.*\.md$
        pass_filenames: false
        stages: [commit]
```

### Option 2: Native Git Hook

For projects not using pre-commit framework, add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Pre-commit hook for agent sync

# Check if any .claude/commands files are staged
if git diff --cached --name-only | grep -qE '^\.claude/commands/.*\.md$|^templates/commands/.*\.md$'; then
    echo "Syncing Claude commands to Copilot agents..."
    scripts/bash/pre-commit-agent-sync.sh
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "Agent sync failed. Commit aborted."
        exit 1
    fi
fi
```

## Hook Script Design

Create `scripts/bash/pre-commit-agent-sync.sh`:

```bash
#!/usr/bin/env bash
# pre-commit-agent-sync.sh - Auto-sync Claude commands to Copilot agents
#
# This script is designed to be called by git pre-commit hooks.
# It detects staged .claude/commands files, runs sync, and auto-stages results.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    NC='\033[0m'
else
    GREEN='' YELLOW='' NC=''
fi

log_info() { echo -e "${GREEN}[agent-sync]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[agent-sync]${NC} $*" >&2; }

# Check if command files are staged
check_staged_commands() {
    git diff --cached --name-only 2>/dev/null | \
        grep -qE '^\.claude/commands/.*\.md$|^templates/commands/.*\.md$'
}

# Main execution
main() {
    # Only run if command files are staged
    if ! check_staged_commands; then
        exit 0  # Nothing to do
    fi

    log_info "Detected staged command files, syncing agents..."

    # Run the sync script
    if ! "$SCRIPT_DIR/sync-copilot-agents.sh" --force; then
        log_warn "Agent sync failed!"
        exit 1
    fi

    # Auto-stage generated agent files
    if [ -d "$PROJECT_ROOT/.github/agents" ]; then
        git add "$PROJECT_ROOT/.github/agents/"
        log_info "Auto-staged .github/agents/ files"
    fi

    # Show what was synced
    local synced_count
    synced_count=$(git diff --cached --name-only -- '.github/agents/' | wc -l)
    if [ "$synced_count" -gt 0 ]; then
        log_info "Synced $synced_count agent files:"
        git diff --cached --name-only -- '.github/agents/' | head -5
        if [ "$synced_count" -gt 5 ]; then
            log_info "  ... and $((synced_count - 5)) more"
        fi
    fi

    log_info "Agent sync complete"
}

main "$@"
```

## File Pattern Detection

The hook triggers only when relevant files are staged:

| Pattern | Description |
|---------|-------------|
| `.claude/commands/**/*.md` | Claude Code command files |
| `templates/commands/**/*.md` | Command templates |

Excluded patterns (not triggering sync):
- `.github/agents/*.md` - Already generated files
- `docs/**/*.md` - Documentation
- `backlog/**/*.md` - Task files

## Auto-staging Behavior

After sync, the hook automatically stages generated files:

```bash
git add .github/agents/
```

This ensures the commit includes both:
1. Source files (user's changes to commands)
2. Generated files (synced agents)

## Bypass Mechanism

The hook respects git's standard bypass:

```bash
# Skip pre-commit hooks for emergency commits
git commit --no-verify -m "emergency fix"
```

This is the standard git mechanism and requires no additional implementation.

## Output Examples

### Normal sync (files detected):
```
[agent-sync] Detected staged command files, syncing agents...
OK: Created: flow-implement.agent.md
OK: Created: flow-validate.agent.md
[agent-sync] Auto-staged .github/agents/ files
[agent-sync] Synced 2 agent files:
  .github/agents/flow-implement.agent.md
  .github/agents/flow-validate.agent.md
[agent-sync] Agent sync complete
```

### No relevant files staged:
```
(no output - hook exits silently)
```

### Sync failure:
```
[agent-sync] Detected staged command files, syncing agents...
ERROR: Failed to resolve includes for flow/implement
[agent-sync] Agent sync failed!
```

## Installation

### For Pre-commit Framework Users

1. Add configuration to `.pre-commit-config.yaml` (shown above)
2. Run: `pre-commit install`

### For Native Git Hook Users

1. Copy hook to `.git/hooks/`:
   ```bash
   cp scripts/bash/pre-commit-agent-sync.sh .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. Or symlink:
   ```bash
   ln -s ../../scripts/bash/pre-commit-agent-sync.sh .git/hooks/pre-commit-agent-sync
   ```

### For flowspec init Users

When running `flowspec init`, the hook configuration should be automatically added to `.pre-commit-config.yaml` if the project uses Claude Code.

## Testing

### Manual Testing

```bash
# Test with staged files
git add .claude/commands/flow/implement.md
./scripts/bash/pre-commit-agent-sync.sh

# Test without staged files
git reset HEAD
./scripts/bash/pre-commit-agent-sync.sh  # Should exit silently
```

### Integration Test

```bash
# Full workflow test
echo "test" >> .claude/commands/flow/implement.md
git add .claude/commands/flow/implement.md
git commit -m "test sync"
# Verify .github/agents/flow-implement.agent.md was updated
git show HEAD --name-only | grep '.github/agents/'
```

## Implementation Tasks

Following this design, the implementation (task-334) should:

1. Create `scripts/bash/pre-commit-agent-sync.sh`
2. Add hook configuration to `.pre-commit-config.yaml`
3. Update installation documentation
4. Add integration test

## Acceptance Criteria Mapping

| AC | Design Element |
|----|----------------|
| #1 Hook triggers only when .claude/commands/**/*.md files are staged | File pattern in pre-commit config |
| #2 Hook runs sync-copilot-agents.sh automatically | Script invocation in hook |
| #3 Hook auto-stages generated .github/agents/ files | `git add` in hook script |
| #4 Hook can be bypassed with git commit --no-verify | Git standard behavior |
| #5 Hook shows clear output indicating files synced | Log messages in script |

## Security Considerations

- Hook only runs on explicit git commit (not background processes)
- Uses existing sync-copilot-agents.sh which has security validation
- No network access required
- No secrets handling

## Dependencies

- `scripts/bash/sync-copilot-agents.sh` must exist and be functional
- Python 3.11+ (for YAML parsing in sync script)
- Git repository initialized
