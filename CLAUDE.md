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

### /jpspec + Backlog.md Integration

Every `/jpspec` command integrates with backlog.md:

**Design commands create tasks**:
```bash
# /jpspec:specify creates implementation tasks with ACs
backlog task create "Implement feature X" --ac "AC 1" --ac "AC 2" -l backend
```

**Implementation commands consume tasks**:
```bash
# /jpspec:implement discovers and works from existing tasks
backlog task edit task-42 -s "In Progress" -a @backend-engineer
backlog task edit task-42 --check-ac 1  # Check ACs progressively
```

**Key rule**: Never run `/jpspec:implement` without first running `/jpspec:specify` to create tasks.

See [JP Spec + Backlog.md Integration Guide](docs/guides/jpspec-backlog-workflow.md) for complete details.

### Workflow Documentation

- [JP Spec + Backlog.md Integration](docs/guides/jpspec-backlog-workflow.md) - Complete integration guide
- [Workflow State Mapping](docs/guides/workflow-state-mapping.md) - State and command mapping
- [Workflow Customization Guide](docs/guides/workflow-customization.md) - How to modify workflows
- [Workflow Architecture](docs/guides/workflow-architecture.md) - Overall design
- [Workflow Troubleshooting](docs/guides/workflow-troubleshooting.md) - Common issues
- [Configuration Examples](docs/examples/workflows/) - Working example configs

@import memory/critical-rules.md

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
│   ├── skills/             # Skill templates (copied to .claude/skills/)
│   ├── *-template.md       # Artifact templates
│   └── commands/           # Slash command templates
├── docs/                   # Documentation
│   ├── guides/             # User guides
│   └── reference/          # Reference docs
├── memory/                 # Constitution & specs
├── scripts/bash/           # Automation scripts
├── backlog/                # Task management
├── .claude/commands/       # Slash command implementations
└── .claude/skills/         # Model-invoked skills (5 core SDD skills)
```

@import memory/code-standards.md

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

@import memory/mcp-configuration.md

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_JPSPEC` | GitHub token for API requests |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repos |

@import memory/claude-hooks.md

@import memory/claude-checkpoints.md

@import memory/claude-skills.md

@import memory/claude-thinking.md

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
