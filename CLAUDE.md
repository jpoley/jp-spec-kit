# JP Spec Kit - Claude Code Configuration

This file provides essential context for Claude Code when working on the JP Spec Kit project. It covers development workflows, testing strategies, and integration with the inner/outer loop processes.

## Project Overview

**JP Spec Kit** is a comprehensive toolkit for implementing Spec-Driven Development (SDD). It includes:
- **Specify CLI**: Command-line tool to bootstrap projects (`specify-cli` package)
- **Templates**: Spec-driven development templates for multiple AI agents
- **Scripts**: Automation scripts for setup, testing, and CI/CD
- **Documentation**: Comprehensive guides for inner/outer loop development

## Quick Reference

### Common Commands

```bash
# Development and Testing
python -m pytest tests/              # Run all tests
python -m pytest tests/ -v          # Run tests with verbose output
python -m pytest tests/ -k "test_name"  # Run specific test

# Linting and Formatting
ruff check .                         # Check code quality
ruff check . --fix                   # Auto-fix issues
ruff format .                        # Format code

# Build and Install
uv build                             # Build the package
uv tool install . --force            # Install locally for testing

# Package Management
uv sync                              # Sync dependencies
uv add <package>                     # Add new dependency
uv remove <package>                  # Remove dependency

# Local CI/CD Testing
./scripts/bash/run-local-ci.sh      # Run full CI simulation locally
./scripts/bash/install-act.sh       # Install act (GitHub Actions local runner)
act -l                               # List available workflows
act -j <job-name>                    # Run specific workflow job locally
```

### Slash Commands (jpspec)

When working on this repository, you have access to specialized workflow commands:

```bash
/jpspec:specify      # Create/update feature specs (PM planner agent)
/jpspec:plan         # Execute planning workflow (architect + platform engineer)
/jpspec:research     # Execute research and validation (researcher + business validator)
/jpspec:implement    # Execute implementation (frontend + backend engineers + code review)
/jpspec:validate     # Execute QA and validation (QA + security + docs + release)
/jpspec:operate      # Execute operations (SRE agent for CI/CD + K8s + DevSecOps)
```

### Backlog.md Integration (Task Management)

This project uses **Backlog.md** for enhanced task management:

```bash
# View tasks
backlog board              # Terminal Kanban board
backlog browser            # Web UI
backlog overview           # Project statistics

# Manage tasks via CLI
backlog task create "Title" --labels "US1,backend"
backlog task edit task-12
backlog task view task-12

# Or ask Claude (via MCP):
# "Show me all tasks for User Story 1"
# "Mark task-12 as in progress"
# "Create a task for implementing password reset"
```

**Documentation**:
- Quick Start: `docs/guides/backlog-quickstart.md`
- User Guide: `docs/guides/backlog-user-guide.md`
- Command Reference: `docs/reference/backlog-commands.md`

### Backlog Flush (Archiving Done Tasks)

The backlog flush feature automatically archives completed tasks and generates summary reports.

#### Manual Execution

```bash
# Preview what would be archived (recommended first step)
./scripts/bash/flush-backlog.sh --dry-run

# Archive all Done tasks and generate summary
./scripts/bash/flush-backlog.sh

# Archive without generating summary
./scripts/bash/flush-backlog.sh --no-summary

# Archive and auto-commit changes
./scripts/bash/flush-backlog.sh --auto-commit

# Show help
./scripts/bash/flush-backlog.sh --help
```

#### Automated via GitHub Actions

Include `flush-backlog` (case-insensitive) in your commit message to trigger automatic archival:

```bash
git commit -m "Complete feature implementation flush-backlog"
git push origin main
```

The workflow will:
1. Install backlog.md CLI
2. Run the flush script
3. Generate a timestamped summary
4. Commit and push the changes

#### Flush Summary Format

Summaries are saved to `backlog/archive/flush-YYYY-MM-DD-HHMMSS.md`:

```markdown
# Backlog Flush Summary

**Date**: 2025-11-26 14:30:00 UTC
**Archived Tasks**: 5
**Triggered By**: manual

## Tasks Archived

### task-013 - Technical Feasibility - GitHub API Spike
- **Status**: Done
- **Priority**: High
- **Labels**: research, api
- **Acceptance Criteria**: 3/3 completed

---

## Statistics
- Total archived: 5
- By priority: High (2), Medium (2), Low (1)
- Common labels: api (3), backend (2)
```

#### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - tasks archived |
| 1 | Validation error (backlog CLI not installed, no backlog/ directory) |
| 2 | No Done tasks to archive |
| 3 | Partial failure (some tasks failed to archive) |

#### Troubleshooting

**"backlog: command not found"**
Install backlog.md CLI: `npm install -g backlog.md`

**"No backlog directory found"**
Run from project root containing `backlog/` directory, or initialize with `backlog init`

**"No Done tasks to archive"**
This is normal - means all tasks are still in progress. Exit code 2 is informational, not an error.

**Permission denied**
Make script executable: `chmod +x scripts/bash/flush-backlog.sh`

#### Comparison with `backlog cleanup`

| Feature | `flush-backlog.sh` | `backlog cleanup` |
|---------|-------------------|-------------------|
| Archives Done tasks | ✓ | ✓ |
| Generates summary report | ✓ | ✗ |
| GitHub Actions integration | ✓ | ✗ |
| Dry-run mode | ✓ | ✗ |
| Statistics | ✓ | ✗ |

Use `flush-backlog.sh` for CI/CD integration and audit trails. Use `backlog cleanup` for quick local cleanup without reports.

### Headless Mode Usage

Claude Code supports headless mode for non-interactive contexts (CI, pre-commit hooks, automation):

```bash
# Basic headless command
claude -p "Review this code for security issues"

# With specific tools allowed
claude -p "Run tests and report results" --allowedTools Read,Bash

# Stream JSON output for automation
claude -p "Generate SBOM for this project" --output-format stream-json

# Verbose mode for debugging
claude -p "Check code quality" --verbose
```

**Examples for this project:**

```bash
# Automated spec review
claude -p "/jpspec:specify Review and validate spec for feature XYZ"

# Automated code review before commit
claude -p "Review changes in git diff for code quality, security, and best practices"

# CI/CD integration
claude -p "/jpspec:validate Run comprehensive validation checks"
```

## Development Workflow

### Inner Loop (Local Development)

The **inner loop** focuses on fast, local iteration (edit → test → debug → repeat):

**Objectives:**
- Instant feedback (<2s hot reload when applicable)
- Local testing before commit
- Pre-commit validation
- CI simulation locally

**Workflow:**

1. **Setup Development Environment**
   ```bash
   # Clone and setup
   git clone <repo-url>
   cd jp-spec-kit
   uv sync                  # Install dependencies
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/description
   ```

3. **Make Changes and Test Locally**
   ```bash
   # Make your changes

   # Run tests
   pytest tests/

   # Check code quality
   ruff check . --fix
   ruff format .

   # Test CLI locally
   uv tool install . --force
   specify check
   ```

4. **Pre-Commit Validation**
   ```bash
   # Run comprehensive local checks
   ./scripts/bash/run-local-ci.sh    # (Once implemented)

   # Or manually:
   ruff check .
   ruff format .
   pytest tests/
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: description"
   ```

**Key Files for Inner Loop:**
- `pyproject.toml` - Project configuration and dependencies
- `tests/` - Test suite
- `scripts/bash/` - Local development scripts
- `scripts/powershell/` - PowerShell equivalent scripts

### Outer Loop (CI/CD Pipeline)

The **outer loop** handles everything after commit (PR → build → test → package → deploy):

**Objectives:**
- Automated testing on PR
- Build once, promote everywhere
- Security scanning and SBOM generation
- Artifact signing and provenance
- Automated deployment

**GitHub Actions Workflows:**
- `.github/workflows/docs.yml` - Documentation deployment
- `.github/workflows/release.yml` - Release automation
- `.github/workflows/ci.yml` - CI/CD pipeline (to be implemented)
- `.github/workflows/security.yml` - Security scanning (to be implemented)

**Workflow Triggers:**
- Push to `main` branch
- Pull request creation/update
- Manual workflow dispatch
- Release tag creation

## Project Structure

```
jp-spec-kit/
├── .claude/
│   └── commands/jpspec/     # Slash command implementations
├── .github/
│   └── workflows/           # GitHub Actions workflows
├── docs/                    # Documentation
│   ├── reference/
│   │   ├── inner-loop.md   # Inner loop principles
│   │   ├── outer-loop.md   # Outer loop principles
│   │   └── agent-loop-classification.md
│   └── ...
├── memory/                  # Project memory and constitution
│   └── constitution.md
├── scripts/
│   ├── bash/               # Bash scripts for automation
│   └── powershell/         # PowerShell equivalents
├── src/specify_cli/        # CLI source code
├── templates/              # Project templates
│   └── commands/jpspec/    # Command templates
├── tests/                  # Test suite
├── AGENTS.md              # AI agent guidance (this file's purpose)
├── CLAUDE.md              # Claude Code configuration (this file)
├── CONTRIBUTING-AGENTS.md # How to add new agent support to Specify CLI
├── pyproject.toml         # Project configuration
└── README.md              # Project readme
```

## Code Style and Standards

### Python Code Style

- **Formatter**: Ruff (replaces Black)
- **Linter**: Ruff (replaces Flake8, isort, pyupgrade)
- **Type Checking**: Use type hints where appropriate
- **Line Length**: 88 characters (Ruff default)

**Key Conventions:**
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and single-purpose
- Prefer composition over inheritance
- Use pathlib for file operations

### Testing Standards

- **Framework**: pytest
- **Coverage Target**: Aim for >80% coverage on core functionality
- **Test Organization**: Mirror source structure in `tests/`
- **Naming**: `test_<functionality>.py` for test files

**Test Types:**
- Unit tests: Test individual functions/classes
- Integration tests: Test CLI commands end-to-end
- Regression tests: Prevent known issues from recurring

### Commit Message Format

Follow conventional commits with **mandatory DCO sign-off**:

```
<type>(<scope>): <description>

[Optional body explaining the change]

Signed-off-by: Your Name <your.email@example.com>
```

**IMPORTANT: All commits MUST include `Signed-off-by` line (DCO requirement).**

Use `git commit -s` to automatically add the sign-off, or include it manually.

**Types:** feat, fix, docs, style, refactor, test, chore

**Examples:**
```bash
# Automatic sign-off (recommended)
git commit -s -m "feat(cli): add support for new AI agent"

# Manual sign-off
git commit -m "fix(templates): correct template variable substitution

Signed-off-by: Your Name <your.email@example.com>"
```

### Parallel Task Execution with Git Worktrees

When executing tasks in parallel, git worktrees MUST be used to isolate work:

**Worktree name must match branch name** - The worktree directory name MUST be identical to the branch name:

```bash
# Correct: worktree name matches branch name
git worktree add ../feature-auth feature-auth

# Wrong: mismatched names
git worktree add ../work1 feature-auth
```

**Key requirements:**
- One branch per worktree - each parallel task gets its own worktree and branch
- Clean isolation - worktrees prevent merge conflicts and allow simultaneous work
- Remove worktrees when complete: `git worktree remove ../feature-auth`

**Benefits:**
- Clear mapping between filesystem locations and branches
- No accidental commits to wrong branches
- Easy identification of which worktree corresponds to which task

## Testing Instructions

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_cli.py

# Specific test function
pytest tests/test_cli.py::test_init_command

# With coverage
pytest tests/ --cov=src/specify_cli --cov-report=html

# Watch mode (requires pytest-watch)
ptw tests/
```

### Writing Tests

**Test Structure:**
```python
def test_feature_description():
    # Arrange - Setup test data
    input_data = {...}

    # Act - Execute functionality
    result = function_under_test(input_data)

    # Assert - Verify results
    assert result == expected_output
```

**Fixtures:**
Use pytest fixtures for common setup:
```python
@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir
```

## Agent Loop Classification

Per `docs/reference/agent-loop-classification.md`:

### Inner Loop Agents
- product-requirements-manager
- software-architect
- platform-engineer
- researcher, business-validator
- frontend-engineer, backend-engineer, ai-ml-engineer
- frontend-code-reviewer, backend-code-reviewer
- quality-guardian, playwright-* agents
- secure-by-design-engineer
- tech-writer

### Outer Loop Agents
- sre-agent (CI/CD, Kubernetes, DevSecOps, observability)
- release-manager (deployment, promotion workflows)

## Important Notes

### Version Management

When modifying `src/specify_cli/__init__.py`:
- **MUST** update version in `pyproject.toml`
- **MUST** add entry to `CHANGELOG.md`
- Follow semantic versioning (MAJOR.MINOR.PATCH)

### Adding New Agent Support

See `CONTRIBUTING-AGENTS.md` for detailed instructions on:
- Adding agent to `AGENT_CONFIG` in `src/specify_cli/__init__.py`
- Updating CLI help text
- Updating README documentation
- Modifying release package scripts
- Updating agent context scripts

### Pull Request Guidelines

Before creating a PR:
1. Run all tests and ensure they pass
2. Run linting and fix any issues
3. Update documentation if needed
4. Test CLI commands locally
5. Ensure commit messages follow conventions
6. Add entry to CHANGELOG.md if applicable

### CI/CD Requirements

All code must pass:
- Linting (ruff check)
- Formatting (ruff format --check)
- Tests (pytest)
- Type checking (if implemented)
- Security scanning (in CI)

## Testing GitHub Actions Locally with act

### Installing act

**act** is a tool that runs GitHub Actions workflows locally using Docker. This allows you to test workflows before pushing to GitHub.

**Installation:**

```bash
# Using the installation script (recommended)
./scripts/bash/install-act.sh

# Or install manually:
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows (PowerShell)
.\scripts\powershell\install-act.ps1
# Or: choco install act-cli
# Or: scoop install act
```

**Prerequisites:**
- Docker must be installed and running
- act uses Docker containers to simulate GitHub Actions runners

### Using act

```bash
# List available workflows and jobs
act -l

# Run all jobs in a workflow
act

# Run a specific job
act -j <job-name>

# Run with specific event
act push
act pull_request

# Dry run (don't execute, just show what would run)
act -n

# Use specific runner image
act -P ubuntu-latest=catthehacker/ubuntu:act-latest

# Run with secrets
act -s GITHUB_JPSPEC=<token>

# Verbose output
act -v
```

**Testing JP Spec Kit CI:**

```bash
# Test the main CI workflow
act -j lint          # Run linting job
act -j test          # Run test suite
act -j build         # Run package build
act -j security      # Run security scanning
```

**Important Notes:**
- ⚠️ **NOT YET TESTED**: The ci.yml workflow has NOT been tested with act yet
- ⚠️ Some GitHub Actions features may not work in act (attestations, OIDC, etc.)
- ⚠️ Multi-platform jobs (macOS, Windows) cannot run in act (Linux only)
- First run will download Docker images (may take several minutes)
- act runs faster than GitHub Actions for quick iterations

**Resources:**
- act documentation: https://github.com/nektos/act
- Docker installation: https://docs.docker.com/get-docker/

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure dependencies are installed
uv sync
```

**CLI Not Found:**
```bash
# Reinstall the tool
uv tool install . --force
```

**Tests Failing:**
```bash
# Check Python version (requires 3.11+)
python --version

# Reinstall dependencies
uv sync --force
```

**Permission Errors:**
```bash
# Make scripts executable
chmod +x scripts/bash/*.sh
```

**act Issues:**
```bash
# Ensure Docker is running
docker ps

# Pull latest runner images
docker pull catthehacker/ubuntu:act-latest

# Clear act cache
rm -rf ~/.actrc

# Check act version
act --version
```

## Resources

- [Inner Loop Principles](docs/reference/inner-loop.md)
- [Outer Loop Principles](docs/reference/outer-loop.md)
- [Agent Loop Classification](docs/reference/agent-loop-classification.md)
- [Backlog.md Quick Start](docs/guides/backlog-quickstart.md)
- [Backlog.md User Guide](docs/guides/backlog-user-guide.md)
- [Backlog.md Migration Guide](docs/guides/backlog-migration.md)
- [Backlog.md Commands](docs/reference/backlog-commands.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Spec-Driven Development Guide](spec-driven.md)
- [Claude Code Documentation](https://docs.claude.com/claude-code)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_JPSPEC` | GitHub token for API requests |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repos |

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review closed issues for solutions

---

*This file is automatically loaded by Claude Code for context. Keep it concise and up-to-date.*

<!-- BACKLOG.MD GUIDELINES START -->
# Instructions for the usage of Backlog.md CLI Tool

## Backlog.md: Comprehensive Project Management Tool via CLI

### Assistant Objective

Efficiently manage all project tasks, status, and documentation using the Backlog.md CLI, ensuring all project metadata
remains fully synchronized and up-to-date.

### Core Capabilities

- ✅ **Task Management**: Create, edit, assign, prioritize, and track tasks with full metadata
- ✅ **Search**: Fuzzy search across tasks, documents, and decisions with `backlog search`
- ✅ **Acceptance Criteria**: Granular control with add/remove/check/uncheck by index
- ✅ **Board Visualization**: Terminal-based Kanban board (`backlog board`) and web UI (`backlog browser`)
- ✅ **Git Integration**: Automatic tracking of task states across branches
- ✅ **Dependencies**: Task relationships and subtask hierarchies
- ✅ **Documentation & Decisions**: Structured docs and architectural decision records
- ✅ **Export & Reporting**: Generate markdown reports and board snapshots
- ✅ **AI-Optimized**: `--plain` flag provides clean text output for AI processing

### Why This Matters to You (AI Agent)

1. **Comprehensive system** - Full project management capabilities through CLI
2. **The CLI is the interface** - All operations go through `backlog` commands
3. **Unified interaction model** - You can use CLI for both reading (`backlog task 1 --plain`) and writing (
   `backlog task edit 1`)
4. **Metadata stays synchronized** - The CLI handles all the complex relationships

### Key Understanding

- **Tasks** live in `backlog/tasks/` as `task-<id> - <title>.md` files
- **You interact via CLI only**: `backlog task create`, `backlog task edit`, etc.
- **Use `--plain` flag** for AI-friendly output when viewing/listing
- **Never bypass the CLI** - It handles Git, metadata, file naming, and relationships

---

# ⚠️ CRITICAL: NEVER EDIT TASK FILES DIRECTLY. Edit Only via CLI

**ALL task operations MUST use the Backlog.md CLI commands**

- ✅ **DO**: Use `backlog task edit` and other CLI commands
- ✅ **DO**: Use `backlog task create` to create new tasks
- ✅ **DO**: Use `backlog task edit <id> --check-ac <index>` to mark acceptance criteria
- ❌ **DON'T**: Edit markdown files directly
- ❌ **DON'T**: Manually change checkboxes in files
- ❌ **DON'T**: Add or modify text in task files without using CLI

**Why?** Direct file editing breaks metadata synchronization, Git tracking, and task relationships.

---

## 1. Source of Truth & File Structure

### 📖 **UNDERSTANDING** (What you'll see when reading)

- Markdown task files live under **`backlog/tasks/`** (drafts under **`backlog/drafts/`**)
- Files are named: `task-<id> - <title>.md` (e.g., `task-42 - Add GraphQL resolver.md`)
- Project documentation is in **`backlog/docs/`**
- Project decisions are in **`backlog/decisions/`**

### 🔧 **ACTING** (How to change things)

- **All task operations MUST use the Backlog.md CLI tool**
- This ensures metadata is correctly updated and the project stays in sync
- **Always use `--plain` flag** when listing or viewing tasks for AI-friendly text output

---

## 2. Common Mistakes to Avoid

### ❌ **WRONG: Direct File Editing**

```markdown
# DON'T DO THIS:

1. Open backlog/tasks/task-7 - Feature.md in editor
2. Change "- [ ]" to "- [x]" manually
3. Add notes directly to the file
4. Save the file
```

### ✅ **CORRECT: Using CLI Commands**

```bash
# DO THIS INSTEAD:
backlog task edit 7 --check-ac 1  # Mark AC #1 as complete
backlog task edit 7 --notes "Implementation complete"  # Add notes
backlog task edit 7 -s "In Progress" -a @agent-k  # Multiple commands: change status and assign the task when you start working on the task
```

---

## 3. Understanding Task Format (Read-Only Reference)

⚠️ **FORMAT REFERENCE ONLY** - The following sections show what you'll SEE in task files.
**Never edit these directly! Use CLI commands to make changes.**

### Task Structure You'll See

```markdown
---
id: task-42
title: Add GraphQL resolver
status: To Do
assignee: [@sara]
labels: [backend, api]
---

## Description

Brief explanation of the task purpose.

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 First criterion
- [x] #2 Second criterion (completed)
- [ ] #3 Third criterion

<!-- AC:END -->

## Implementation Plan

1. Research approach
2. Implement solution

## Implementation Notes

Summary of what was done.
```

### How to Modify Each Section

| What You Want to Change | CLI Command to Use                                       |
|-------------------------|----------------------------------------------------------|
| Title                   | `backlog task edit 42 -t "New Title"`                    |
| Status                  | `backlog task edit 42 -s "In Progress"`                  |
| Assignee                | `backlog task edit 42 -a @sara`                          |
| Labels                  | `backlog task edit 42 -l backend,api`                    |
| Description             | `backlog task edit 42 -d "New description"`              |
| Add AC                  | `backlog task edit 42 --ac "New criterion"`              |
| Check AC #1             | `backlog task edit 42 --check-ac 1`                      |
| Uncheck AC #2           | `backlog task edit 42 --uncheck-ac 2`                    |
| Remove AC #3            | `backlog task edit 42 --remove-ac 3`                     |
| Add Plan                | `backlog task edit 42 --plan "1. Step one\n2. Step two"` |
| Add Notes (replace)     | `backlog task edit 42 --notes "What I did"`              |
| Append Notes            | `backlog task edit 42 --append-notes "Another note"` |

---

## 4. Defining Tasks

### Creating New Tasks

**Always use CLI to create tasks:**

```bash
# Example - ALWAYS include at least one --ac flag
backlog task create "Task title" -d "Description" --ac "First criterion" --ac "Second criterion"
```

**⚠️ MANDATORY: Never create a task without acceptance criteria.** Tasks without ACs are considered incomplete and will be rejected or archived.

### Title (one liner)

Use a clear brief title that summarizes the task.

### Description (The "why")

Provide a concise summary of the task purpose and its goal. Explains the context without implementation details.

### Acceptance Criteria (The "what")

**Understanding the Format:**

- Acceptance criteria appear as numbered checkboxes in the markdown files
- Format: `- [ ] #1 Criterion text` (unchecked) or `- [x] #1 Criterion text` (checked)

**Managing Acceptance Criteria via CLI:**

⚠️ **IMPORTANT: How AC Commands Work**

- **Adding criteria (`--ac`)** accepts multiple flags: `--ac "First" --ac "Second"` ✅
- **Checking/unchecking/removing** accept multiple flags too: `--check-ac 1 --check-ac 2` ✅
- **Mixed operations** work in a single command: `--check-ac 1 --uncheck-ac 2 --remove-ac 3` ✅

```bash
# Examples

# Add new criteria (MULTIPLE values allowed)
backlog task edit 42 --ac "User can login" --ac "Session persists"

# Check specific criteria by index (MULTIPLE values supported)
backlog task edit 42 --check-ac 1 --check-ac 2 --check-ac 3  # Check multiple ACs
# Or check them individually if you prefer:
backlog task edit 42 --check-ac 1    # Mark #1 as complete
backlog task edit 42 --check-ac 2    # Mark #2 as complete

# Mixed operations in single command
backlog task edit 42 --check-ac 1 --uncheck-ac 2 --remove-ac 3

# ❌ STILL WRONG - These formats don't work:
# backlog task edit 42 --check-ac 1,2,3  # No comma-separated values
# backlog task edit 42 --check-ac 1-3    # No ranges
# backlog task edit 42 --check 1         # Wrong flag name

# Multiple operations of same type
backlog task edit 42 --uncheck-ac 1 --uncheck-ac 2  # Uncheck multiple ACs
backlog task edit 42 --remove-ac 2 --remove-ac 4    # Remove multiple ACs (processed high-to-low)
```

**Key Principles for Good ACs:**

- **Outcome-Oriented:** Focus on the result, not the method.
- **Testable/Verifiable:** Each criterion should be objectively testable
- **Clear and Concise:** Unambiguous language
- **Complete:** Collectively cover the task scope
- **User-Focused:** Frame from end-user or system behavior perspective

Good Examples:

- "User can successfully log in with valid credentials"
- "System processes 1000 requests per second without errors"
- "CLI preserves literal newlines in description/plan/notes; `\\n` sequences are not auto‑converted"

Bad Example (Implementation Step):

- "Add a new function handleLogin() in auth.ts"
- "Define expected behavior and document supported input patterns"

### Task Breakdown Strategy

1. Identify foundational components first
2. Create tasks in dependency order (foundations before features)
3. Ensure each task delivers value independently
4. Avoid creating tasks that block each other

### Task Requirements

- **⚠️ MANDATORY: Every task MUST have at least one acceptance criterion** - Tasks without ACs are incomplete and should not be created
- Tasks must be **atomic** and **testable** or **verifiable**
- Each task should represent a single unit of work for one PR
- **Never** reference future tasks (only tasks with id < current task id)
- Ensure tasks are **independent** and don't depend on future work

---

## 4.5. Design Tasks vs Implementation Tasks (Design→Implement Workflow)

### What is a Design Task?

A **design task** produces artifacts (documents, diagrams, architecture decisions, research findings) that require follow-up implementation. Design tasks are identified by:

**Labels** (any of these indicate a design task):
- `design` - Architecture, system design, UI/UX design
- `audit` - Analysis that produces recommendations
- `architecture` - System architecture decisions
- `research` - Research that produces actionable findings
- `spike` - Technical exploration/proof of concept
- `planning` - Planning that produces actionable plans

**Title patterns** (any of these indicate a design task):
- "Design ..." - e.g., "Design authentication flow"
- "... Architecture" - e.g., "Plugin Architecture"
- "Audit ..." - e.g., "Audit API endpoints"
- "Research ..." - e.g., "Research caching strategies"
- "Spike: ..." - e.g., "Spike: GraphQL performance"

### ⚠️ CRITICAL: Design Tasks MUST Create Implementation Tasks

**Design tasks CANNOT be marked Done without corresponding implementation task(s).**

When completing a design task:

1. **Before marking Done**, create implementation tasks that:
   - Reference the design task as a dependency
   - Have specific, actionable acceptance criteria
   - Cover all actionable items from the design deliverables

2. **Implementation Notes MUST include**:
   - "Follow-up Implementation Tasks:" section listing created task IDs
   - Summary of key design decisions
   - Files/artifacts created

### Design Task Completion Workflow

```bash
# 1. Complete design work (produce artifacts, documents, etc.)

# 2. Create implementation tasks BEFORE marking design task Done
backlog task create "Implement [specific feature from design]" \
  -d "Implementation based on task-106 design" \
  --ac "Implement X per ADR-001" \
  --ac "Add tests for X" \
  --dep task-106 \
  -l implement,backend

# 3. Add implementation notes with follow-up task references
backlog task edit 106 --notes $'Designed comprehensive architecture.\n\nDeliverables:\n- ADR-001: Architecture decision record\n- templates/auth-flow.md: Flow diagram\n\nFollow-up Implementation Tasks:\n- task-107: Implement auth service\n- task-108: Implement auth middleware\n- task-109: Add auth tests'

# 4. Only NOW mark design task as Done
backlog task edit 106 -s Done
```

### Design Task Definition of Done

A design task is **Done** only when **ALL** of the following are complete:

1. ✅ All acceptance criteria checked
2. ✅ Design artifacts created (ADRs, diagrams, specs)
3. ✅ **Implementation tasks created** (MANDATORY for design tasks)
4. ✅ Implementation notes include "Follow-up Implementation Tasks:" section
5. ✅ Status set to Done

### Naming Convention for Follow-up Tasks

Implementation tasks should clearly reference their design origin:

| Design Task | Implementation Task(s) |
|------------|------------------------|
| Design authentication flow | Implement auth service, Implement auth middleware |
| Audit API endpoints | Update deprecated endpoints, Add missing validation |
| Research caching strategy | Implement Redis caching layer, Add cache invalidation |
| Spike: GraphQL performance | Implement DataLoader pattern, Add query complexity limits |

### Why This Matters

- **Traceability**: Every design decision has corresponding implementation
- **No orphaned designs**: Prevents valuable design work from being forgotten
- **Clear dependencies**: Implementation tasks can reference design artifacts
- **Audit trail**: Easy to trace from requirement → design → implementation

---

## 5. Implementing Tasks

### 5.1. First step when implementing a task

The very first things you must do when you take over a task are:

* set the task in progress
* assign it to yourself

```bash
# Example
backlog task edit 42 -s "In Progress" -a @{myself}
```

### 5.2. Create an Implementation Plan (The "how")

Previously created tasks contain the why and the what. Once you are familiar with that part you should think about a
plan on **HOW** to tackle the task and all its acceptance criteria. This is your **Implementation Plan**.
First do a quick check to see if all the tools that you are planning to use are available in the environment you are
working in.   
When you are ready, write it down in the task so that you can refer to it later.

```bash
# Example
backlog task edit 42 --plan "1. Research codebase for references\n2Research on internet for similar cases\n3. Implement\n4. Test"
```

## 5.3. Implementation

Once you have a plan, you can start implementing the task. This is where you write code, run tests, and make sure
everything works as expected. Follow the acceptance criteria one by one and MARK THEM AS COMPLETE as soon as you
finish them.

### 5.4 Implementation Notes (PR description)

When you are done implementing a tasks you need to prepare a PR description for it.
Because you cannot create PRs directly, write the PR as a clean description in the task notes.
Append notes progressively during implementation using `--append-notes`:

```
backlog task edit 42 --append-notes "Implemented X" --append-notes "Added tests"
```

```bash
# Example
backlog task edit 42 --notes "Implemented using pattern X because Reason Y, modified files Z and W"
```

**IMPORTANT**: Do NOT include an Implementation Plan when creating a task. The plan is added only after you start the
implementation.

- Creation phase: provide Title, Description, Acceptance Criteria, and optionally labels/priority/assignee.
- When you begin work, switch to edit, set the task in progress and assign to yourself
  `backlog task edit <id> -s "In Progress" -a "..."`.
- Think about how you would solve the task and add the plan: `backlog task edit <id> --plan "..."`.
- After updating the plan, share it with the user and ask for confirmation. Do not begin coding until the user approves the plan or explicitly tells you to skip the review.
- Add Implementation Notes only after completing the work: `backlog task edit <id> --notes "..."` (replace) or append progressively using `--append-notes`.

## Phase discipline: What goes where

- Creation: Title, Description, Acceptance Criteria, labels/priority/assignee.
- Implementation: Implementation Plan (after moving to In Progress and assigning to yourself).
- Wrap-up: Implementation Notes (Like a PR description), AC and Definition of Done checks.

**IMPORTANT**: Only implement what's in the Acceptance Criteria. If you need to do more, either:

1. Update the AC first: `backlog task edit 42 --ac "New requirement"`
2. Or create a new follow up task: `backlog task create "Additional feature"`

---

## 6. Typical Workflow

```bash
# 1. Identify work
backlog task list -s "To Do" --plain

# 2. Read task details
backlog task 42 --plain

# 3. Start work: assign yourself & change status
backlog task edit 42 -s "In Progress" -a @myself

# 4. Add implementation plan
backlog task edit 42 --plan "1. Analyze\n2. Refactor\n3. Test"

# 5. Share the plan with the user and wait for approval (do not write code yet)

# 6. Work on the task (write code, test, etc.)

# 7. Mark acceptance criteria as complete (supports multiple in one command)
backlog task edit 42 --check-ac 1 --check-ac 2 --check-ac 3  # Check all at once
# Or check them individually if preferred:
# backlog task edit 42 --check-ac 1
# backlog task edit 42 --check-ac 2
# backlog task edit 42 --check-ac 3

# 8. Add implementation notes (PR Description)
backlog task edit 42 --notes "Refactored using strategy pattern, updated tests"

# 9. Mark task as done
backlog task edit 42 -s Done
```

---

## 7. Definition of Done (DoD)

A task is **Done** only when **ALL** of the following are complete:

### ✅ Via CLI Commands:

1. **All acceptance criteria checked**: Use `backlog task edit <id> --check-ac <index>` for each
2. **Implementation notes added**: Use `backlog task edit <id> --notes "..."`
3. **Status set to Done**: Use `backlog task edit <id> -s Done`

### ✅ Via Code/Testing:

4. **Tests pass**: Run test suite and linting
5. **Documentation updated**: Update relevant docs if needed
6. **Code reviewed**: Self-review your changes
7. **No regressions**: Performance, security checks pass

⚠️ **NEVER mark a task as Done without completing ALL items above**

---

## 8. Finding Tasks and Content with Search

When users ask you to find tasks related to a topic, use the `backlog search` command with `--plain` flag:

```bash
# Search for tasks about authentication
backlog search "auth" --plain

# Search only in tasks (not docs/decisions)
backlog search "login" --type task --plain

# Search with filters
backlog search "api" --status "In Progress" --plain
backlog search "bug" --priority high --plain
```

**Key points:**
- Uses fuzzy matching - finds "authentication" when searching "auth"
- Searches task titles, descriptions, and content
- Also searches documents and decisions unless filtered with `--type task`
- Always use `--plain` flag for AI-readable output

---

## 9. Quick Reference: DO vs DON'T

### Viewing and Finding Tasks

| Task         | ✅ DO                        | ❌ DON'T                         |
|--------------|-----------------------------|---------------------------------|
| View task    | `backlog task 42 --plain`   | Open and read .md file directly |
| List tasks   | `backlog task list --plain` | Browse backlog/tasks folder     |
| Check status | `backlog task 42 --plain`   | Look at file content            |
| Find by topic| `backlog search "auth" --plain` | Manually grep through files |

### Modifying Tasks

| Task          | ✅ DO                                 | ❌ DON'T                           |
|---------------|--------------------------------------|-----------------------------------|
| Check AC      | `backlog task edit 42 --check-ac 1`  | Change `- [ ]` to `- [x]` in file |
| Add notes     | `backlog task edit 42 --notes "..."` | Type notes into .md file          |
| Change status | `backlog task edit 42 -s Done`       | Edit status in frontmatter        |
| Add AC        | `backlog task edit 42 --ac "New"`    | Add `- [ ] New` to file           |

---

## 10. Complete CLI Command Reference

### Task Creation

| Action           | Command                                                                             |
|------------------|-------------------------------------------------------------------------------------|
| Create task      | `backlog task create "Title"`                                                       |
| With description | `backlog task create "Title" -d "Description"`                                      |
| With AC          | `backlog task create "Title" --ac "Criterion 1" --ac "Criterion 2"`                 |
| With all options | `backlog task create "Title" -d "Desc" -a @sara -s "To Do" -l auth --priority high` |
| Create draft     | `backlog task create "Title" --draft`                                               |
| Create subtask   | `backlog task create "Title" -p 42`                                                 |

### Task Modification

| Action           | Command                                     |
|------------------|---------------------------------------------|
| Edit title       | `backlog task edit 42 -t "New Title"`       |
| Edit description | `backlog task edit 42 -d "New description"` |
| Change status    | `backlog task edit 42 -s "In Progress"`     |
| Assign           | `backlog task edit 42 -a @sara`             |
| Add labels       | `backlog task edit 42 -l backend,api`       |
| Set priority     | `backlog task edit 42 --priority high`      |

### Acceptance Criteria Management

| Action              | Command                                                                     |
|---------------------|-----------------------------------------------------------------------------|
| Add AC              | `backlog task edit 42 --ac "New criterion" --ac "Another"`                  |
| Remove AC #2        | `backlog task edit 42 --remove-ac 2`                                        |
| Remove multiple ACs | `backlog task edit 42 --remove-ac 2 --remove-ac 4`                          |
| Check AC #1         | `backlog task edit 42 --check-ac 1`                                         |
| Check multiple ACs  | `backlog task edit 42 --check-ac 1 --check-ac 3`                            |
| Uncheck AC #3       | `backlog task edit 42 --uncheck-ac 3`                                       |
| Mixed operations    | `backlog task edit 42 --check-ac 1 --uncheck-ac 2 --remove-ac 3 --ac "New"` |

### Task Content

| Action           | Command                                                  |
|------------------|----------------------------------------------------------|
| Add plan         | `backlog task edit 42 --plan "1. Step one\n2. Step two"` |
| Add notes        | `backlog task edit 42 --notes "Implementation details"`  |
| Add dependencies | `backlog task edit 42 --dep task-1 --dep task-2`         |

### Multi‑line Input (Description/Plan/Notes)

The CLI preserves input literally. Shells do not convert `\n` inside normal quotes. Use one of the following to insert real newlines:

- Bash/Zsh (ANSI‑C quoting):
  - Description: `backlog task edit 42 --desc $'Line1\nLine2\n\nFinal'`
  - Plan: `backlog task edit 42 --plan $'1. A\n2. B'`
  - Notes: `backlog task edit 42 --notes $'Done A\nDoing B'`
  - Append notes: `backlog task edit 42 --append-notes $'Progress update line 1\nLine 2'`
- POSIX portable (printf):
  - `backlog task edit 42 --notes "$(printf 'Line1\nLine2')"`
- PowerShell (backtick n):
  - `backlog task edit 42 --notes "Line1`nLine2"`

Do not expect `"...\n..."` to become a newline. That passes the literal backslash + n to the CLI by design.

Descriptions support literal newlines; shell examples may show escaped `\\n`, but enter a single `\n` to create a newline.

### Implementation Notes Formatting

- Keep implementation notes human-friendly and PR-ready: use short paragraphs or
  bullet lists instead of a single long line.
- Lead with the outcome, then add supporting details (e.g., testing, follow-up
  actions) on separate lines or bullets.
- Prefer Markdown bullets (`-` for unordered, `1.` for ordered) so Maintainers
  can paste notes straight into GitHub without additional formatting.
- When using CLI flags like `--append-notes`, remember to include explicit
  newlines. Example:

  ```bash
  backlog task edit 42 --append-notes $'- Added new API endpoint\n- Updated tests\n- TODO: monitor staging deploy'
  ```

### Task Operations

| Action             | Command                                      |
|--------------------|----------------------------------------------|
| View task          | `backlog task 42 --plain`                    |
| List tasks         | `backlog task list --plain`                  |
| Search tasks       | `backlog search "topic" --plain`              |
| Search with filter | `backlog search "api" --status "To Do" --plain` |
| Filter by status   | `backlog task list -s "In Progress" --plain` |
| Filter by assignee | `backlog task list -a @sara --plain`         |
| Archive task       | `backlog task archive 42`                    |
| Demote to draft    | `backlog task demote 42`                     |

---

## Common Issues

| Problem              | Solution                                                           |
|----------------------|--------------------------------------------------------------------|
| Task not found       | Check task ID with `backlog task list --plain`                     |
| AC won't check       | Use correct index: `backlog task 42 --plain` to see AC numbers     |
| Changes not saving   | Ensure you're using CLI, not editing files                         |
| Metadata out of sync | Re-edit via CLI to fix: `backlog task edit 42 -s <current-status>` |

---

## Remember: The Golden Rule

**🎯 If you want to change ANYTHING in a task, use the `backlog task edit` command.**
**📖 Use CLI to read tasks, exceptionally READ task files directly, never WRITE to them.**

Full help available: `backlog --help`

<!-- BACKLOG.MD GUIDELINES END -->
