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
# Validate default jpspec_workflow.yml
specify workflow validate

# Validate custom workflow file
specify workflow validate --file custom_workflow.yml

# Show detailed output with warnings
specify workflow validate --verbose

# JSON output for CI/automation
specify workflow validate --json

# Example output:
# ✓ Schema validation passed
# ✓ Validation passed: workflow configuration is valid

# Exit codes:
# 0 = validation passed
# 1 = validation errors (schema or semantic)
# 2 = file errors (not found, invalid YAML)
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

## MCP Configuration

JP Spec Kit uses Model Context Protocol (MCP) servers for enhanced capabilities.

### MCP Server List

| Server | Description |
|--------|-------------|
| `github` | GitHub API: repos, issues, PRs, code search, workflows |
| `serena` | LSP-grade code understanding & safe semantic edits |
| `playwright-test` | Browser automation for testing and E2E workflows |
| `trivy` | Container/IaC security scans and SBOM generation |
| `semgrep` | SAST code scanning for security vulnerabilities |
| `shadcn-ui` | shadcn/ui component library access and installation |
| `chrome-devtools` | Chrome DevTools Protocol for browser inspection |
| `backlog` | Backlog.md task management with kanban integration |

### Health Check

Test connectivity for all configured MCP servers:

```bash
# Check all servers with default settings
./scripts/bash/check-mcp-servers.sh

# Verbose output with custom timeout
./scripts/bash/check-mcp-servers.sh --verbose --timeout 15

# JSON output for automation
./scripts/bash/check-mcp-servers.sh --json
```

**Example output:**
```
[✓] github - Connected successfully
[✓] serena - Connected successfully
[✗] playwright-test - Failed: binary 'npx' not found
[✓] trivy - Connected successfully
[✓] semgrep - Connected successfully
[✓] shadcn-ui - Connected successfully
[✓] chrome-devtools - Connected successfully
[✓] backlog - Connected successfully

Summary: 7/8 servers healthy
```

### Troubleshooting MCP Issues

If health checks fail:

1. **Binary not found**: Install missing prerequisites
   - `npx` - Install Node.js: `brew install node` (macOS) or via nvm
   - `uvx` - Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - `backlog` - Install backlog CLI: `cargo install backlog-md` or use binary

2. **Startup failed**: Check server dependencies
   - Review .mcp.json configuration for typos
   - Verify environment variables are set if required
   - Check server-specific logs in ~/.mcp/logs/

3. **Timeout**: Increase timeout for slow systems
   - Use `--timeout 20` for systems with limited resources
   - Check system load: `uptime`, `top`

4. **Connection refused**: Verify network and firewall settings
   - Some servers may require internet connectivity
   - Check firewall isn't blocking local connections

### MCP Configuration File

MCP servers are configured in `.mcp.json` at the project root. See [MCP documentation](https://modelcontextprotocol.io/docs) for details.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_JPSPEC` | GitHub token for API requests |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repos |

## Claude Code Hooks

JP Spec Kit uses Claude Code hooks to provide automated safety checks and code quality enforcement.

### Implemented Hooks

#### 1. SessionStart Hook (SessionStart)

**Hook**: `.claude/hooks/session-start.sh`

Runs when starting or resuming a Claude Code session to verify environment and display context:
- Checks for `uv` (Python package manager)
- Checks for `backlog` CLI (task management)
- Displays versions of installed tools
- Shows active "In Progress" backlog tasks
- Provides warnings for missing dependencies

**Output Example**:
```json
{
  "decision": "allow",
  "reason": "Session started - environment verified",
  "additionalContext": "Session Context:\n  ✓ uv: uv 0.9.11\n  ✓ backlog: 1.22.0\n  ✓ Active tasks: 2 in progress"
}
```

**Behavior**: Always returns `"decision": "allow"` with contextual information. Never blocks session startup (fail-open principle).

**Performance**: Completes in <5 seconds typical, <60 seconds maximum (timeout configured).

#### 2. Sensitive File Protection (PreToolUse)

**Hook**: `.claude/hooks/pre-tool-use-sensitive-files.py`

Asks for confirmation before modifying sensitive files:
- `.env` files (including `.env.*`)
- `.secrets` files
- `package-lock.json`
- `uv.lock`
- `.git/` directory
- `CLAUDE.md` files

**Behavior**: Returns `"decision": "ask"` for sensitive files, prompting Claude to get user confirmation.

#### 3. Git Command Safety Validator (PreToolUse)

**Hook**: `.claude/hooks/pre-tool-use-git-safety.py`

Warns on dangerous Git commands:
- `git push --force` / `-f` (asks for confirmation)
- `git push origin +branch` (force push syntax, asks for confirmation)
- `git reset --hard` (asks for confirmation)
- `git rebase -i` (DENIES - interactive commands not supported)
- `git clean -fd` (asks for confirmation)

**Special handling**: Force pushes to `main`/`master` branches receive extra warnings.

**Behavior**: Returns `"decision": "ask"` for dangerous commands, or `"decision": "deny"` for unsupported interactive commands.

#### 4. Auto-format Python Files (PostToolUse)

**Hook**: `.claude/hooks/post-tool-use-format-python.sh`

Automatically runs `ruff format` on Python files after Edit/Write operations.

**Behavior**: Silently formats Python files and reports if formatting was applied.

#### 5. Auto-lint Python Files (PostToolUse)

**Hook**: `.claude/hooks/post-tool-use-lint-python.sh`

Automatically runs `ruff check --fix` on Python files after Edit/Write operations.

**Behavior**: Attempts to auto-fix linting issues and reports results. Manual fixes may be needed for complex issues.

#### 5. Pre-Implementation Quality Gates

**Hook**: `.claude/hooks/pre-implement.sh`

Runs automated quality gates before `/jpspec:implement` can proceed. Ensures specifications are complete and high-quality before implementation begins.

**Gates Enforced**:
1. **Required Files**: Validates `spec.md`, `plan.md`, and `tasks.md` exist
2. **Spec Completeness**: Detects unresolved markers (`NEEDS CLARIFICATION`, `[TBD]`, `[TODO]`, `???`, `PLACEHOLDER`, `<insert>`)
3. **Constitutional Compliance**: Verifies DCO sign-off, testing requirements, and acceptance criteria are mentioned
4. **Quality Threshold**: Requires spec quality score >= 70/100 using `specify quality` scorer

**Override**: Use `--skip-quality-gates` flag to bypass (NOT RECOMMENDED).

**Testing**: Run `.claude/hooks/test-pre-implement.sh` (14 comprehensive tests).

**Documentation**: See `docs/adr/adr-pre-implementation-quality-gates.md` for full ADR.

**Example Output**:
```bash
# Pass state
✅ All quality gates passed. Proceeding with implementation.

# Fail state with remediation
❌ Quality gates failed:

✗ Unresolved markers found in spec.md:
  - Line 45: NEEDS CLARIFICATION: authentication method
  → Resolve all markers before implementation

✗ Quality score: 58/100 (threshold: 70)
  Recommendations:
  - Add missing section: ## User Story
  - Reduce vague terms (currently: 12 instances)
  → Improve spec quality using /speckit:clarify

Run with --skip-quality-gates to bypass (NOT RECOMMENDED).
```

### Testing Hooks

Run the test suite to verify all hooks are working correctly:

```bash
# Run all hook tests
.claude/hooks/test-hooks.sh

# Test SessionStart hook
.claude/hooks/test-session-start.sh

# Test a specific hook manually
echo '{"tool_name": "Write", "tool_input": {"file_path": ".env"}}' | \
  python .claude/hooks/pre-tool-use-sensitive-files.py

# Test SessionStart hook manually
.claude/hooks/session-start.sh | python3 -m json.tool
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
