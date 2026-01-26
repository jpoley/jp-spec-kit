# Flowspec - Claude Code Configuration

Standalone toolkit for Spec-Driven Development (SDD): CLI tool (`flowspec-cli`), templates for AI agents, and comprehensive documentation.

## Essential Commands

```bash
pytest tests/                    # Run tests
ruff check . --fix && ruff format .  # Lint and format
uv sync                          # Install dependencies
uv tool install . --force        # Install CLI locally
```

## Backlog Commands

```bash
backlog task list --plain        # List tasks (AI-friendly)
backlog task 42 --plain          # View task details
backlog task edit 42 -s "In Progress" -a @myself  # Start work
backlog task edit 42 --check-ac 1  # Mark AC done
backlog task edit 42 -s Done     # Complete task
```

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/flow:assess` | Evaluate SDD workflow suitability |
| `/flow:specify` | Create/update feature specs |
| `/flow:research` | Research and validation (optional) |
| `/flow:plan` | Execute planning workflow |
| `/flow:implement` | Implementation with code review |
| `/flow:validate` | QA, security, docs validation |
| `/flow:init` | Initialize constitution |
| `/flow:intake` | Process INITIAL docs to create tasks |
| `/flow:reset` | Reset or restart current flow state |
| `/flow:generate-prp` | Generate PRP context bundle |
| `/flow:map-codebase` | Map codebase for context |
| `/vibe` | Casual mode - just logs and light docs |

_Full command list: `.claude/commands/flow/`_

## Default Mode

When no `/flow:*` command is specified, default to **vibe mode**:
- Quick fixes, prototypes, exploration: just code it
- Log decisions to `.flowspec/logs/decisions/`
- Escalate to full SDD if work grows complex

## INITIAL Documents

**ALWAYS** check for `docs/features/<feature-slug>-initial.md` before `/flow:assess` or `/flow:specify`. Contains feature context, examples, constraints.

## Engineering Subagents

| Agent | Location | Use For |
|-------|----------|---------|
| Backend | `.claude/agents/backend-engineer.md` | APIs, databases, Python |
| Frontend | `.claude/agents/frontend-engineer.md` | React, TypeScript, UI |
| QA | `.claude/agents/qa-engineer.md` | Tests, coverage |
| Security | `.claude/agents/security-reviewer.md` | Security review (read-only) |

## Workflow Configuration

Defined in `flowspec_workflow.yml`. Validate with:

```bash
flowspec workflow validate
```

| Command | Input State | Output State |
|---------|-------------|--------------|
| `/flow:assess` | To Do | Assessed |
| `/flow:specify` | Assessed | Specified |
| `/flow:research` | Specified | Researched |
| `/flow:plan` | Specified/Researched | Planned |
| `/flow:implement` | Planned | In Implementation |
| `/flow:validate` | In Implementation | Validated |

## Project Structure

```
flowspec/
├── src/flowspec_cli/       # CLI source code
├── tests/                  # Test suite (pytest)
├── templates/              # Project templates
│   ├── docs/               # Workflow artifact directories
│   └── commands/           # Slash command templates
├── docs/                   # Documentation
│   ├── guides/             # User guides
│   └── reference/          # Reference docs
├── memory/                 # Constitution & specs
├── backlog/                # Task management
├── .claude/commands/       # Slash command implementations
├── .claude/skills/         # Model-invoked skills
└── .claude/rules/          # Automatic rules
```

## Task Management

| Layer | Tool | Purpose |
|-------|------|---------|
| Feature/Task | Backlog.md | High-level work items, ACs |
| Agent Work | Beads | Detailed implementation steps |

Simple tasks: Backlog.md only. Complex tasks: Backlog.md + Beads.

## Documentation

| Topic | Location |
|-------|----------|
| Backlog Quick Start | `user-docs/guides/backlog-quickstart.md` |
| Workflow Integration | `user-docs/guides/flowspec-backlog-workflow.md` |
| Task Tiers | `docs/guides/task-management-tiers.md` |
| Inner/Outer Loop | `user-docs/reference/inner-loop.md`, `user-docs/reference/outer-loop.md` |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_FLOWSPEC` | GitHub token for API requests |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repos |

## MCP Servers

| Server | Description |
|--------|-------------|
| `github` | GitHub API: repos, issues, PRs |
| `backlog` | Backlog.md task management |
| `serena` | LSP-grade code understanding |
| `playwright-test` | Browser automation |
| `trivy` | Container/IaC security scans |
| `semgrep` | SAST code scanning |

Health check: `./scripts/check-mcp-servers.sh`

## Claude Code Hooks

| Hook | Type | Purpose |
|------|------|---------|
| `session-start.sh` | SessionStart | Environment verification |
| `pre-tool-use-sensitive-files.py` | PreToolUse | Protect .env, secrets |
| `pre-tool-use-git-safety.py` | PreToolUse | Warn on dangerous git |
| `post-tool-use-format-python.sh` | PostToolUse | Auto-format Python |
| `post-tool-use-lint-python.sh` | PostToolUse | Auto-lint Python |
| `stop-quality-gate.py` | Stop | Backlog task quality gate |

Test hooks: `.claude/hooks/test-hooks.sh`

## Claude Code Skills

Specialized skills auto-invoked by context. Key skills:
- `pm-planner`: Task creation and breakdown
- `architect`: Architecture decisions and ADRs
- `qa-validator`: Test plans and quality gates
- `security-reviewer`: Vulnerability assessment

Full list: `memory/claude-skills.md` or `.claude/skills/`

## Checkpoints

Press `Esc Esc` to undo last change. Use `/rewind` for interactive restore.

## Extended Thinking

| Trigger | Budget | Use Case |
|---------|--------|----------|
| `think` | 4K tokens | Quick decisions |
| `think hard` | 10K tokens | Architecture, security |
| `megathink` | 10K tokens | Complex research |
| `ultrathink` | 32K tokens | Critical decisions |

## Quick Troubleshooting

```bash
uv sync --force              # Dependencies issues
uv tool install . --force    # CLI not found
chmod +x scripts/bash/*.sh   # Make scripts executable
python --version             # Check Python 3.11+
.claude/hooks/test-hooks.sh  # Test hooks
```

---

*Rules in `.claude/rules/` are automatically loaded by Claude Code. See that directory for critical rules, coding standards, security, testing, and rigor enforcement.*
