# JP Spec Kit - Claude Code Configuration

## Project Overview

**JP Spec Kit** is a toolkit for Spec-Driven Development (SDD):
- **Specify CLI**: Command-line tool to bootstrap projects (`specify-cli` package)
- **Templates**: SDD templates for multiple AI agents
- **Documentation**: Comprehensive guides in `docs/`

## Essential Commands

```bash
# Development
pytest tests/                    # Run tests
ruff check . --fix               # Lint and auto-fix
ruff format .                    # Format code
uv sync                          # Install dependencies
uv tool install . --force        # Install CLI locally

# Backlog (NEVER edit task files directly!)
backlog task list --plain        # List tasks (AI-friendly output)
backlog task 42 --plain          # View task details
backlog task edit 42 -s "In Progress" -a @myself  # Start work
backlog task edit 42 --check-ac 1  # Mark acceptance criterion done
backlog task edit 42 -s Done     # Complete task
```

## Slash Commands

```bash
/jpspec:assess    # Evaluate SDD workflow suitability
/jpspec:specify   # Create/update feature specs
/jpspec:research  # Research and validation
/jpspec:plan      # Execute planning workflow
/jpspec:implement # Implementation with code review
/jpspec:validate  # QA, security, docs validation
/jpspec:operate   # SRE operations (CI/CD, K8s)
```

## Workflow Configuration

JP Spec Kit uses a configurable workflow system defined in `jpspec_workflow.yml` at the project root.

### Configuration File Location

**Default**: `{project-root}/jpspec_workflow.yml`

The workflow configuration defines:
- **States**: Task progression stages (e.g., Specified, Planned, Validated)
- **Workflows**: `/jpspec` commands with agent assignments
- **Transitions**: Valid state changes between states
- **Agent Loops**: Inner/outer loop classification

### How /jpspec Commands Use Workflow Config

Each `/jpspec` command:
1. Checks current task state from backlog.md
2. Validates state is a valid input for the command (from `jpspec_workflow.yml`)
3. Executes agents assigned to the workflow
4. Transitions task to the command's output state
5. Creates artifacts defined in transitions

Example:
```yaml
workflows:
  implement:
    command: "/jpspec:implement"
    agents:
      - frontend-engineer
      - backend-engineer
    input_states: ["Planned"]
    output_state: "In Implementation"
```

### Validate Workflow Configuration

```bash
specify workflow validate

# Example output:
# ✓ Configuration structure valid (schema v1.1)
# ✓ No cycles detected in state transitions
# ✓ All states reachable from "To Do"
# ✓ Terminal states configured
```

### Quick Reference: Commands and Workflow Phases

| Command | Input State(s) | Output State | Agents |
|---------|---------------|--------------|--------|
| `/jpspec:assess` | To Do | Assessed | workflow-assessor |
| `/jpspec:specify` | Assessed | Specified | product-requirements-manager |
| `/jpspec:research` | Specified | Researched | researcher, business-validator |
| `/jpspec:plan` | Specified, Researched | Planned | software-architect, platform-engineer |
| `/jpspec:implement` | Planned | In Implementation | frontend/backend engineers, reviewers |
| `/jpspec:validate` | In Implementation | Validated | quality-guardian, secure-by-design-engineer |
| `/jpspec:operate` | Validated | Deployed | sre-agent |

### Customizing Your Workflow

You can customize the workflow by editing `jpspec_workflow.yml`:
- Add/remove phases
- Change agent assignments
- Add custom states
- Modify transitions

See [Workflow Customization Guide](docs/guides/workflow-customization.md) for details.

### Workflow Documentation

- [Workflow State Mapping](docs/guides/workflow-state-mapping.md) - State and command mapping
- [Workflow Customization Guide](docs/guides/workflow-customization.md) - How to modify workflows
- [Workflow Architecture](docs/guides/workflow-architecture.md) - Overall design
- [Workflow Troubleshooting](docs/guides/workflow-troubleshooting.md) - Common issues
- [Configuration Examples](docs/examples/workflows/) - Working example configs

## Critical Rules

### No Direct Commits to Main (ABSOLUTE - NO EXCEPTIONS)
**NEVER commit directly to main.** All changes MUST go through a PR:
1. Create branch → 2. Make changes → 3. Create PR → 4. CI passes → 5. Merge → 6. Mark task Done

Not for "urgent" fixes. Not for "small" changes. **NO EXCEPTIONS.**

See `memory/constitution.md` for full details.

### DCO Sign-off (Required)
All commits MUST include sign-off:
```bash
git commit -s -m "feat: description"
```

### Version Management
When modifying `src/specify_cli/__init__.py`:
1. Update version in `pyproject.toml`
2. Add entry to `CHANGELOG.md`
3. Follow semantic versioning

### Backlog.md Task Management
**NEVER edit task files directly** - Use `backlog task edit` CLI commands only.
Direct file editing breaks metadata sync, Git tracking, and relationships.

See: `backlog/CLAUDE.md` for detailed guidance.

### PR-Task Synchronization (Required)
When a PR completes a backlog task, update the task **before or with** PR creation:
```bash
# Mark ACs complete and set status with PR reference
backlog task edit <id> --check-ac 1 --check-ac 2 -s Done \
  --notes $'Completed via PR #<number>\n\nStatus: Pending CI verification'
```

**If PR fails CI**: Revert task to "In Progress" and uncheck incomplete ACs.
The backlog must always reflect reality.

### Git Worktrees for Parallel Work
Worktree name MUST match branch name:
```bash
git worktree add ../feature-auth feature-auth  # Correct
git worktree add ../work1 feature-auth         # Wrong
```

## Project Structure

```
jp-spec-kit/
├── src/specify_cli/        # CLI source code
├── tests/                  # Test suite (pytest)
├── templates/              # Project templates
│   ├── docs/               # Workflow artifact directories (copied to project docs/)
│   │   ├── assess/         # Assessment reports (/jpspec:assess)
│   │   ├── prd/            # Product Requirements Documents (/jpspec:specify)
│   │   ├── research/       # Research reports (/jpspec:research)
│   │   ├── adr/            # Architecture Decision Records (/jpspec:plan)
│   │   ├── platform/       # Platform design docs (/jpspec:plan)
│   │   ├── qa/             # QA reports (/jpspec:validate)
│   │   └── security/       # Security reports (/jpspec:validate)
│   ├── *-template.md       # Artifact templates
│   └── commands/           # Slash command templates
├── docs/                   # Documentation
│   ├── guides/             # User guides
│   └── reference/          # Reference docs
├── memory/                 # Constitution & specs
├── scripts/bash/           # Automation scripts
├── backlog/                # Task management
└── .claude/commands/       # Slash command implementations
```

## Code Standards

### Python
- **Linter/Formatter**: Ruff (replaces Black, Flake8, isort)
- **Line length**: 88 characters
- **Type hints**: Required for public APIs
- **File paths**: Use `pathlib`

### Testing
- **Framework**: pytest
- **Coverage**: >80% on core functionality
- **Pattern**: Arrange-Act-Assert (AAA)

### Commits
Follow conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Documentation References

| Topic | Location |
|-------|----------|
| Backlog Quick Start | `docs/guides/backlog-quickstart.md` |
| Backlog User Guide | `docs/guides/backlog-user-guide.md` |
| Backlog Commands | `docs/reference/backlog-commands.md` |
| Inner Loop | `docs/reference/inner-loop.md` |
| Outer Loop | `docs/reference/outer-loop.md` |
| Agent Classification | `docs/reference/agent-loop-classification.md` |
| Flush Backlog | `docs/guides/backlog-flush.md` |

## Subfolder Context

Additional context loaded when working in specific directories:
- `backlog/CLAUDE.md` - Task management workflow
- `scripts/CLAUDE.md` - Script execution guidance
- `src/CLAUDE.md` - Python code standards

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_JPSPEC` | GitHub token for API requests |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repos |

## Claude Code Hooks

JP Spec Kit uses Claude Code hooks to provide automated safety checks and code quality enforcement.

### Implemented Hooks

#### 1. Sensitive File Protection (PreToolUse)

**Hook**: `.claude/hooks/pre-tool-use-sensitive-files.py`

Asks for confirmation before modifying sensitive files:
- `.env` files (including `.env.*`)
- `.secrets` files
- `package-lock.json`
- `uv.lock`
- `.git/` directory
- `CLAUDE.md` files

**Behavior**: Returns `"decision": "ask"` for sensitive files, prompting Claude to get user confirmation.

#### 2. Git Command Safety Validator (PreToolUse)

**Hook**: `.claude/hooks/pre-tool-use-git-safety.py`

Warns on dangerous Git commands:
- `git push --force` / `-f` (asks for confirmation)
- `git push origin +branch` (force push syntax, asks for confirmation)
- `git reset --hard` (asks for confirmation)
- `git rebase -i` (DENIES - interactive commands not supported)
- `git clean -fd` (asks for confirmation)

**Special handling**: Force pushes to `main`/`master` branches receive extra warnings.

**Behavior**: Returns `"decision": "ask"` for dangerous commands, or `"decision": "deny"` for unsupported interactive commands.

#### 3. Auto-format Python Files (PostToolUse)

**Hook**: `.claude/hooks/post-tool-use-format-python.sh`

Automatically runs `ruff format` on Python files after Edit/Write operations.

**Behavior**: Silently formats Python files and reports if formatting was applied.

#### 4. Auto-lint Python Files (PostToolUse)

**Hook**: `.claude/hooks/post-tool-use-lint-python.sh`

Automatically runs `ruff check --fix` on Python files after Edit/Write operations.

**Behavior**: Attempts to auto-fix linting issues and reports results. Manual fixes may be needed for complex issues.

### Testing Hooks

Run the test suite to verify all hooks are working correctly:

```bash
# Run all hook tests
.claude/hooks/test-hooks.sh

# Test a specific hook manually
echo '{"tool_name": "Write", "tool_input": {"file_path": ".env"}}' | \
  python .claude/hooks/pre-tool-use-sensitive-files.py
```

### Customizing Hook Behavior

Hooks are configured in `.claude/settings.json`. To customize:

1. **Modify sensitive file patterns**: Edit `SENSITIVE_PATTERNS` in `pre-tool-use-sensitive-files.py`
2. **Add/remove dangerous git patterns**: Edit `DANGEROUS_GIT_PATTERNS` in `pre-tool-use-git-safety.py`
3. **Adjust timeouts**: Modify timeout values in `.claude/settings.json`
4. **Disable specific hooks**: Remove or comment out hooks in `.claude/settings.json`

### Hook Design Principles

- **Fail open**: Hooks default to "allow" on errors to avoid breaking Claude's workflow
- **Fast execution**: All hooks complete in <5 seconds (10s for PostToolUse)
- **Clear communication**: Hooks provide detailed reasons and context for decisions
- **Non-blocking**: Only interactive commands (like `git rebase -i`) are denied; everything else asks for confirmation

## Quick Troubleshooting

```bash
# Dependencies issues
uv sync --force

# CLI not found
uv tool install . --force

# Make scripts executable
chmod +x scripts/bash/*.sh

# Check Python version (requires 3.11+)
python --version

# Test hooks
.claude/hooks/test-hooks.sh
```

---

*Subfolder CLAUDE.md files provide additional context when working in those directories.*
