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
/jpspec:specify   # Create/update feature specs
/jpspec:plan      # Execute planning workflow
/jpspec:research  # Research and validation
/jpspec:implement # Implementation with code review
/jpspec:validate  # QA, security, docs validation
/jpspec:operate   # SRE operations (CI/CD, K8s)
```

## Critical Rules

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
