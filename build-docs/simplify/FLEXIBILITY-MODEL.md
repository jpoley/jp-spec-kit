# Flowspec Flexibility Model

## Core Principle

Flowspec provides **9 core workflows** with **required rigor features**, but allows users to **customize how they work** without breaking the system.

## What Users CAN Customize

### 1. Ad-Hoc Workflows (Create New Standalone Workflows)
Users can create their own ad-hoc workflows like the existing:
- `/flow:submit-n-watch-pr` - PR submission and iteration
- `/flow:timed-task` - Time-boxed autonomous task completion
- `/flow:refactor` - Full refactor loop

**Example:** User creates `/flow:my-security-scan` that runs custom security tools

### 2. Customize Logic Within Existing Steps
Users can modify **how** each core workflow operates:
- **Specify logic**: Change how PRDs are generated, which sections are included
- **Plan logic**: Customize architecture decision process, ADR templates
- **Implement logic**: Modify code generation approach, testing strategy
- **Validate logic**: Add custom quality gates, security scans

**Key:** Users customize the **implementation** but keep the **rigor requirements** (logging, backlog, memory, constitution)

### 3. Agent Customization
Users can:
- **Tweak existing agents**: Modify .claude/agents/*.md to change behavior
- **Add new agents**: Create custom agents for specialized tasks
- **Specify agent participation**: Define which agents participate in each step

**Example workflow configuration:**
```yaml
workflows:
  implement:
    command: "/flow:implement"
    agents:
      - frontend-engineer
      - backend-engineer
      - my-custom-devops-engineer  # User-added agent
    input_states: ["Planned"]
    output_state: "In Implementation"
```

### 4. Prompt Customization
Users can edit:
- `.claude/commands/flow/*/prompt.md` - Workflow prompts
- `.claude/skills/*/prompt.md` - Skill prompts
- Templates in `templates/`

### 5. Constitution Customization
Users can customize:
- `.specify/memory/constitution.md` - Project principles and guidelines
- Custom rigor rules (beyond the required ones)

### 6. Workflow Sequences (Orchestration)
Users can define custom sequences in `flowspec_workflow.yml`:

```yaml
custom_workflows:
  quick_build:
    name: "Quick Build"
    mode: "vibing"  # autonomous
    steps:
      - workflow: specify
      - workflow: implement
      # Skip plan for simple features
    rigor:
      log_decisions: true  # REQUIRED
      log_events: true     # REQUIRED
      backlog_integration: true  # REQUIRED
      memory_tracking: true      # REQUIRED
      follow_constitution: true  # REQUIRED
```

## What Users CANNOT Do (Without Losing Features)

### ❌ Create Replacement Core Workflows
Users should NOT create `/flow:my-specify` that completely replaces `/flow:specify`.

**Why:** They lose:
- Automatic backlog integration
- Decision/event logging
- Memory tracking
- Constitution enforcement

### ❌ Remove Required Features
Users cannot disable:
- **Logging**: .logs/decisions/*.jsonl, .logs/events/*.jsonl, ADRs
- **Backlog integration**: Task state management via MCP
- **Memory system**: Cross-session task state tracking
- **Constitution**: Project principle enforcement

**These are ALWAYS enforced by flowspec core**

## Primary User Patterns (Encouraged)

### Pattern 1: Tweak Agents (Most Common)
```bash
# User edits .claude/agents/backend-engineer.md
# Changes Python testing approach from pytest to unittest
# Flowspec continues to work, just uses modified agent
```

### Pattern 2: Add Ad-Hoc Workflows
```bash
# User creates /flow:my-db-migration
# Runs database migration scripts with safety checks
# Follows rigor rules (logging, backlog, memory, constitution)
```

### Pattern 3: Customize Logic Within Steps
```bash
# User edits .claude/commands/flow/specify/prompt.md
# Adds custom PRD sections for compliance requirements
# Rigor features still enforced
```

### Pattern 4: Custom Sequences
```yaml
# User defines "design-only" workflow
custom_workflows:
  design_only:
    steps:
      - workflow: specify
      - workflow: plan
    # Stops before implementation
```

## CI/CD Validation Strategy

### ✅ What CI/CD DOES Validate
- **Rigor enforcement code**: Logging, backlog, memory, constitution MUST work
- **Security**: No eval(), no curl pipes in flowspec core code
- **Agent sync**: All agents accessible across tools (Claude Code, Copilot, etc.)
- **Schema validation**: flowspec_workflow.yml matches schema

### ❌ What CI/CD DOES NOT Validate
- **User prompt content**: Users can write any prompts they want
- **User agent behavior**: Users define how agents work
- **Custom workflow logic**: Users' ad-hoc workflows are their responsibility
- **Constitution content**: User-defined project principles

**Principle:** "Can't over-scrutinize prompts at CI/CD time in terms of changing"

## Architecture Requirements

### Flowspec Core Must Provide

1. **9 Built-in Workflows**
   - 4 Core: specify, plan, implement, validate
   - 2 Supporting: assess, research
   - 3 Ad-hoc: submit-n-watch-pr, timed-task, refactor

2. **Rigor Enforcement** (mandatory, always on)
   - Decision logging to .logs/decisions/*.jsonl
   - Event logging to .logs/events/*.jsonl
   - ADR generation for architectural decisions
   - Backlog integration via MCP
   - Memory tracking across sessions
   - Constitution enforcement

3. **Extension Points** (user customization)
   - Agent loading from .claude/agents/
   - Prompt loading from .claude/commands/, .claude/skills/
   - Custom workflow loading from flowspec_workflow.yml
   - Ad-hoc workflow registration

4. **Multi-Tool Support**
   - Works across Claude Code, GitHub Copilot, Cursor, Gemini
   - Shared agents, prompts, skills via file system

## Summary

**Flexibility = Customize HOW workflows operate, not REPLACE them**

Users are encouraged to:
- 👍 Create ad-hoc workflows for specialized tasks
- 👍 Tweak agents to fit their coding style
- 👍 Customize logic within existing steps
- 👍 Define custom sequences for their projects

Users should avoid:
- 👎 Replacing core workflows entirely
- 👎 Removing required rigor features

**Result:** Maximum flexibility while maintaining quality guarantees
