# Flowspec - Claude Code Configuration

## Project Overview

**Flowspec** is a standalone toolkit for Spec-Driven Development (SDD):
- **Flowspec CLI**: Command-line tool to bootstrap projects (`flowspec-cli` package)
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
# Workflow Commands (stateful, sequential stages)
/flow:assess    # Evaluate SDD workflow suitability
/flow:specify   # Create/update feature specs
/flow:research  # Research and validation (optional)
/flow:plan      # Execute planning workflow
/flow:implement # Implementation with code review
/flow:validate  # QA, security, docs validation

# Setup & Configuration Commands
/flow:init      # Initialize constitution (greenfield/brownfield)
/flow:reset     # Re-run workflow configuration prompts
/flow:intake    # Process INITIAL docs to create backlog tasks with context
/flow:generate-prp  # Generate PRP context bundle from task artifacts
/flow:map-codebase  # Generate bounded directory tree listings for codebase areas

# Casual Development
/vibe           # Casual mode - just logs and light docs (see Default Development Mode)
```

## Default Development Mode

**When no explicit `/flow:*` command is specified**, default to **vibe mode** principles:

| Situation | Approach |
|-----------|----------|
| Quick fix, small change | Just code it, log decisions to `.logs/` |
| Exploring an idea | Use `/vibe` - minimal ceremony |
| Prototyping | Use `/vibe` - fast iteration |
| Learning/experimenting | Use `/vibe` - low overhead |
| Feature with clear requirements | Start with `/flow:assess` |
| Complex multi-session work | Use full SDD workflow |

**Vibe mode always requires**:
- Log significant decisions to `.logs/decisions/`
- Log events to `.logs/events/`

**Vibe mode does NOT require**:
- Formal PRD or spec documents
- Backlog task creation
- Workflow state management
- Constitution validation

**When to escalate to full SDD**: If work grows larger than expected, involves multiple people, touches security/compliance, or needs formal requirements.

## INITIAL Document Workflow

**CRITICAL**: Before running `/flow:assess` or `/flow:specify`, ALWAYS look for and read the INITIAL document for the feature.

### What is an INITIAL Document?

INITIAL documents are the **primary source of high-level context** for features. They provide structured, comprehensive context that flows into PRDs, PRPs, and implementation tasks.

### Location and Naming

- **Location**: `docs/features/<feature-slug>-initial.md`
- **Template**: `templates/docs/initial/initial-feature-template.md`
- **Example**: `docs/features/backlog-task-management-initial.md`

### When to Read INITIAL Documents

**ALWAYS** check for an INITIAL document before running:
- `/flow:assess` - Assessment requires understanding the full feature context
- `/flow:specify` - PRD creation builds directly from INITIAL document content

### What INITIAL Documents Contain

Each INITIAL document includes:
1. **FEATURE**: Problem statement, desired outcome, constraints, business impact
2. **EXAMPLES**: Relevant example files, usage patterns, expected behaviors
3. **DOCUMENTATION**: Links to PRDs, ADRs, external specs, related tasks
4. **OTHER CONSIDERATIONS**: Gotchas, failures, dependencies, security, performance

### Workflow Integration

```bash
# 1. Check for INITIAL document
ls docs/features/*-initial.md

# 2. Read the INITIAL document FIRST
# (Use Read tool to load docs/features/<feature-slug>-initial.md)

# 3. THEN run assessment or specification
/flow:assess    # With full context from INITIAL doc
/flow:specify   # Building PRD from INITIAL doc content
```

### Key Principle

The INITIAL document is the **canonical source** for feature context. All downstream artifacts (assessments, PRDs, PRPs, tasks) should reference and build upon the context established in the INITIAL document.

If no INITIAL document exists and the user requests `/flow:assess` or `/flow:specify`, suggest creating one first using `/flow:intake` or by manually copying the template.

## Engineering Subagents

Flowspec includes specialized engineering subagents for implementation tasks. These agents are invoked during `/flow:implement` and provide focused expertise:

### Backend Engineer
**Location**: `.claude/agents/backend-engineer.md`

**Expertise**:
- Python 3.11+ (FastAPI, Flask)
- APIs and REST endpoints
- Database design (SQLAlchemy, PostgreSQL, SQLite)
- Server-side business logic
- pytest and test automation

**Use for**: API development, database work, backend services, data processing

### Frontend Engineer
**Location**: `.claude/agents/frontend-engineer.md`

**Expertise**:
- React 18+ and Next.js 14+
- TypeScript strict mode
- UI components and styling (Tailwind CSS)
- Accessibility (WCAG compliance)
- Vitest, React Testing Library, Playwright

**Use for**: React components, UI/UX, browser interactions, client-side logic

### QA Engineer
**Location**: `.claude/agents/qa-engineer.md`

**Expertise**:
- Test pyramid strategy (unit, integration, E2E)
- pytest, Vitest, Playwright
- Test coverage and quality metrics
- Test automation and CI/CD integration
- Property-based testing (hypothesis)

**Use for**: Test creation, coverage analysis, E2E testing, quality validation

### Security Reviewer
**Location**: `.claude/agents/security-reviewer.md`

**Expertise**:
- OWASP Top 10 compliance
- Vulnerability assessment
- SLSA compliance (Levels 1-4)
- Security scanning (bandit, npm audit, trivy)
- Threat modeling and secure design

**Use for**: Security reviews, vulnerability scanning, compliance checks, threat analysis

**Note**: Security reviewer has **read-only** access to code. It analyzes and reports findings but does not make code changes directly.

### Agent Invocation

Agents are automatically invoked by `/flow:implement` based on task labels:
- Tasks labeled `backend` → backend-engineer
- Tasks labeled `frontend` → frontend-engineer
- All tasks → qa-engineer (for test coverage)
- All tasks → security-reviewer (for security review)

See [Workflow Configuration](#workflow-configuration) for customizing agent assignments.

## Workflow Configuration

Flowspec uses a configurable workflow system defined in `flowspec_workflow.yml` at the project root.

### Configuration File Location

**Default**: `{project-root}/flowspec_workflow.yml`

The workflow configuration defines:
- **States**: Task progression stages (e.g., Specified, Planned, Validated)
- **Workflows**: `/flow:*` commands with agent assignments
- **Transitions**: Valid state changes between states
- **Agent Loops**: Inner/outer loop classification

### How /flow:* Commands Use Workflow Config

Each `/flow:*` command:
1. Checks current task state from backlog.md
2. Validates state is a valid input for the command (from `flowspec_workflow.yml`)
3. Executes agents assigned to the workflow
4. Transitions task to the command's output state
5. Creates artifacts defined in transitions

Example:
```yaml
workflows:
  implement:
    command: "/flow:implement"
    agents:
      - frontend-engineer
      - backend-engineer
    input_states: ["Planned"]
    output_state: "In Implementation"
```

### Validate Workflow Configuration

```bash
# Validate default flowspec_workflow.yml
flowspec workflow validate

# Validate custom workflow file
flowspec workflow validate --file custom_workflow.yml

# Show detailed output with warnings
flowspec workflow validate --verbose

# JSON output for CI/automation
flowspec workflow validate --json

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
| `/flow:assess` | To Do | Assessed | workflow-assessor |
| `/flow:specify` | Assessed | Specified | product-requirements-manager |
| `/flow:research` | Specified | Researched | researcher, business-validator |
| `/flow:plan` | Specified, Researched | Planned | software-architect, platform-engineer |
| `/flow:implement` | Planned | In Implementation | frontend/backend engineers, reviewers |
| `/flow:validate` | In Implementation | Validated | quality-guardian, secure-by-design-engineer |

*Note: `/flow:research` is optional.*

### Customizing Your Workflow

You can customize the workflow by editing `flowspec_workflow.yml`:
- Add/remove phases
- Change agent assignments
- Add custom states
- Modify transitions

See [Workflow Customization Guide](docs/guides/workflow-customization.md) for details.

### /flow:* + Backlog.md Integration

Every `/flow:*` command integrates with backlog.md:

**Design commands create tasks**:
```bash
# /flow:specify creates implementation tasks with ACs
backlog task create "Implement feature X" --ac "AC 1" --ac "AC 2" -l backend
```

**Implementation commands consume tasks**:
```bash
# /flow:implement discovers and works from existing tasks
backlog task edit task-42 -s "In Progress" -a @backend-engineer
backlog task edit task-42 --check-ac 1  # Check ACs progressively
```

**Key rule**: Never run `/flow:implement` without first running `/flow:specify` to create tasks.

See [Flowspec + Backlog.md Integration Guide](docs/guides/flowspec-backlog-workflow.md) for complete details.

### Workflow Documentation

- [Flowspec + Backlog.md Integration](docs/guides/flowspec-backlog-workflow.md) - Complete integration guide
- [Workflow State Mapping](docs/guides/workflow-state-mapping.md) - State and command mapping
- [Workflow Customization Guide](docs/guides/workflow-customization.md) - How to modify workflows
- [Workflow Architecture](docs/guides/workflow-architecture.md) - Overall design
- [Workflow Troubleshooting](docs/guides/workflow-troubleshooting.md) - Common issues
- [Configuration Examples](docs/examples/workflows/) - Working example configs

@import memory/critical-rules.md

@import .claude/partials/flow/_rigor-rules.md

## Project Structure

```
flowspec/
├── src/flowspec_cli/       # CLI source code
├── tests/                  # Test suite (pytest)
├── templates/              # Project templates
│   ├── docs/               # Workflow artifact directories (copied to project docs/)
│   │   ├── assess/         # Assessment reports (/flow:assess)
│   │   ├── prd/            # Product Requirements Documents (/flow:specify)
│   │   ├── research/       # Research reports (/flow:research)
│   │   ├── adr/            # Architecture Decision Records (/flow:plan)
│   │   ├── platform/       # Platform design docs (/flow:plan)
│   │   ├── qa/             # QA reports (/flow:validate)
│   │   └── security/       # Security reports (/flow:validate)
│   ├── skills/             # Skill templates (copied to .claude/skills/)
│   ├── *-template.md       # Artifact templates
│   └── commands/           # Slash command templates (flow/, vibe/)
├── docs/                   # Documentation
│   ├── guides/             # User guides
│   └── reference/          # Reference docs
├── memory/                 # Constitution & specs
├── scripts/bash/           # Automation scripts
├── backlog/                # Task management
├── .claude/commands/       # Slash command implementations (flow/, vibe/)
└── .claude/skills/         # Model-invoked skills
```

### Template Files in memory/

The `memory/constitution.md` file is a **template** for project-specific constitutions. It contains placeholder tokens like `[PROJECT_NAME]`, `[PRINCIPLE_1_NAME]`, etc. that are intentionally left unfilled.

**Purpose**: When users run `flowspec init` in a new project, they can customize this template with their project-specific values.

**Placeholders are intentional** and should NOT be replaced with "Flowspec" values. The flowspec repository itself does not need a filled constitution - it provides the template for other projects.

See `memory/README.md` for details on all modular components in the memory directory.

@import memory/code-standards.md

@import memory/test-quality-standards.md

## Task Management: Two-Tier Approach

Flowspec uses a hierarchical task management system:

| Layer | Tool | Purpose | Audience |
|-------|------|---------|----------|
| **Feature/Task** | Backlog.md | High-level work items, acceptance criteria, status | Humans, planning |
| **Agent Work** | Beads | Detailed implementation steps, dependencies, blockers | Agents, execution |

**Quick Decision**:
- **Simple tasks** (single-session, no dependencies): Track entirely in Backlog.md
- **Complex tasks** (multi-session, agent coordination): Use Backlog.md + Beads

**Workflow Summary**:
1. All work starts in **Backlog.md** (human-visible tasks)
2. Move task to "In Progress" when starting work
3. For complex implementations, create **Beads** issues for detailed agent tracking
4. Beads work rolls up to the parent backlog task on completion
5. Update backlog with notes and check acceptance criteria as work completes

See [Two-Tier Task Management Guide](docs/guides/task-management-tiers.md) for complete details.

## Documentation References

| Topic | Location |
|-------|----------|
| Two-Tier Task Management | `docs/guides/task-management-tiers.md` |
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
| `GITHUB_FLOWSPEC` | GitHub token for API requests |
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
