# ADR: Role Selection During Initialization

**Status**: Proposed
**Date**: 2025-12-09
**Author**: Enterprise Software Architect
**Related Tasks**: task-358
**Dependencies**: [ADR: Role-Based Command Namespaces](./ADR-role-based-command-namespaces.md)

---

## Context and Problem Statement

With the adoption of role-based command namespaces (`/pm`, `/arch`, `/dev`, `/sec`, `/qa`, `/ops`), we need a mechanism for users to:

1. **Declare their primary role** during project initialization
2. **Configure which commands appear prominently** in their IDE (VS Code, Claude Code)
3. **Customize agent auto-loading** for handoffs and suggestions
4. **Switch roles easily** as their responsibilities change

Without role awareness, the system cannot provide:
- Intelligent command suggestions
- Role-appropriate agent handoffs
- Personalized developer experience (DX)
- Reduced cognitive load

### The Penthouse View (Strategic Framing)

**Business Objective**: Maximize developer productivity by reducing time spent searching for the right command

**Organizational Impact**:
- Product Managers spend 80% of their time in `/pm` commands
- Developers spend 90% in `/dev` commands
- Security engineers need focused access to `/sec` workflows

By capturing role information upfront, we can:
- **Reduce onboarding time** from 2 hours to 30 minutes
- **Improve command discoverability** (3-8 suggestions vs 18+)
- **Enable role-based analytics** (which roles use which workflows)

---

## Decision Drivers

1. **User Experience**: Selection must be intuitive and quick (< 30 seconds)
2. **Flexibility**: Users can change their role at any time
3. **Multi-Role Support**: Some users wear multiple hats (Dev + PM)
4. **Persistence**: Choice persists across IDE restarts and git pulls
5. **Team Coordination**: Role config should be project-scoped, not global
6. **Default Behavior**: Must work without role selection (fallback: show all)
7. **No Lock-In**: Role selection is advisory, not restrictive

---

## Considered Options

### Option 1: Global User Config (~/.flowspec/config.yml)
Store role preference in user's home directory.

**Pros**:
- Persists across all projects
- User sets once, applies everywhere
- No git conflicts

**Cons**:
- Not project-specific (user may have different roles per project)
- Doesn't reflect team structure of a project
- Can't share role configuration with team
- Wrong abstraction level (role is project context, not user identity)

**Verdict**: ❌ Rejected - wrong scope

---

### Option 2: Project Config (flowspec_workflow.yml)
Extend existing workflow config with role section.

**Pros**:
- Project-scoped (correct abstraction)
- Git-tracked (team can share configurations)
- Colocated with workflow definitions
- Single source of truth
- Easy to version and review

**Cons**:
- Git conflicts possible (mitigated by JSON merge strategy)
- Each team member might want different role
- File could become large

**Verdict**: ✅ **SELECTED** - Best fit for project-level context

---

### Option 3: Separate Role Config File (.flowspec-role.yml)
Create dedicated file for role configuration.

**Pros**:
- Separation of concerns
- Smaller file, less conflicts
- Can gitignore if desired

**Cons**:
- Extra file to manage
- Splits related configuration
- Users must know about two config files
- Harder to discover

**Verdict**: ❌ Rejected - unnecessary fragmentation

---

### Option 4: IDE-Only Storage (VS Code settings.json)
Store role in IDE settings, not in project.

**Pros**:
- IDE-native
- No git conflicts
- Per-workspace configuration

**Cons**:
- Claude Code CLI users have no access
- Not portable across IDEs
- Platform lock-in
- Breaks principle of tool-agnostic design

**Verdict**: ❌ Rejected - not portable

---

## Decision Outcome

**Chosen Option**: Option 2 - Extend flowspec_workflow.yml

Store role configuration in project's `flowspec_workflow.yml` with user-specific overrides via environment variable.

---

## Role Selection Mechanism

### Interactive Prompt During Init/Reset

When user runs `/flow:init` or `/flow:reset`:

```bash
specify init

# Output:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Flowspec - Project Initialization                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Select your primary role for command suggestions:

  1. 👔 Product Manager (PM)
     • Specification & requirements (/pm:*)
     • Assessment & research
     • Agents: @pm-planner, @researcher

  2. 💻 Developer (Dev)
     • Planning & implementation (/dev:*)
     • Architecture & operations
     • Agents: @software-architect, @frontend-engineer, @backend-engineer

  3. 🔒 Security Engineer (Sec)
     • Security workflows (/sec:*)
     • Vulnerability scanning & triaging
     • Agents: @secure-by-design-engineer

  4. ✅ QA Engineer (QA)
     • Validation & testing (/qa:*)
     • Quality assurance
     • Agents: @quality-guardian, @tech-writer

  5. ⚙️  SRE/DevOps (Ops)
     • Infrastructure & deployment (/ops:*)
     • Monitoring & incident response
     • Agents: @sre-agent

  6. 🌐 All Roles (Show all commands)
     • Full command access
     • All agents available

Enter selection [1-6] (default: 2): _
```

### Non-Interactive Mode (CI/Automation)

```bash
# Skip prompt, use default or env var
specify init --role dev

# Or via environment variable
export FLOWSPEC_PRIMARY_ROLE=pm
specify init
```

---

## Storage Format: flowspec_workflow.yml Extension

Add new top-level `role_config` section:

```yaml
# Existing workflow configuration (states, workflows, transitions, etc.)
version: "1.1"
states: [...]
workflows: [...]
transitions: [...]

# === NEW: Role-Based Configuration ===
role_config:
  # User's primary role (set by /speckit:init or /speckit:configure)
  primary_role: "dev"  # Options: pm, arch, dev, sec, qa, ops, all

  # Global preferences
  show_all_commands: false       # Override to always show all namespaces
  deprecated_warnings: true      # Show warnings for deprecated commands
  role_selection_date: "2025-12-09T15:30:00Z"  # When role was last selected

  # Role-specific configurations (user-customizable)
  roles:
    pm:
      display_name: "Product Manager"
      icon: "📋"
      commands: ["assess", "define", "discover"]
      auto_load_agents:
        - "@product-requirements-manager"
        - "@workflow-assessor"
        - "@researcher"
        - "@business-validator"
      default_workflow_entry: "/pm:assess"

    arch:
      display_name: "Architect"
      icon: "🏗️"
      commands: ["design", "decide", "model"]
      auto_load_agents:
        - "@software-architect"
        - "@platform-engineer"
      default_workflow_entry: "/arch:design"

    dev:
      display_name: "Developer"
      icon: "💻"
      commands: ["build", "debug", "refactor"]
      auto_load_agents:
        - "@frontend-engineer"
        - "@backend-engineer"
        - "@ai-ml-engineer"
      default_workflow_entry: "/dev:build"

    sec:
      display_name: "Security Engineer"
      icon: "🔒"
      commands: ["scan", "triage", "fix", "audit"]
      auto_load_agents:
        - "@secure-by-design-engineer"
      default_workflow_entry: "/sec:scan"

    qa:
      display_name: "QA Engineer"
      icon: "✅"
      commands: ["test", "verify", "review"]
      auto_load_agents:
        - "@quality-guardian"
        - "@tech-writer"
        - "@release-manager"
      default_workflow_entry: "/qa:verify"

    ops:
      display_name: "SRE/DevOps"
      icon: "🚀"
      commands: ["deploy", "monitor", "respond", "scale"]
      auto_load_agents:
        - "@sre-agent"
      default_workflow_entry: "/ops:deploy"

    all:
      display_name: "All Roles"
      icon: "🌐"
      commands: []  # All commands
      auto_load_agents: []  # Load all agents
      default_workflow_entry: "/pm:assess"
```

---

## Environment Variable Override

Users can override their role per-session without modifying config:

```bash
# Temporary role switch for this session
export FLOWSPEC_PRIMARY_ROLE=pm
claude code

# Run single command as different role
FLOWSPEC_PRIMARY_ROLE=sec /sec:scan-web
```

**Precedence Order**:
1. `FLOWSPEC_PRIMARY_ROLE` environment variable (highest)
2. `role_config.primary_role` in `flowspec_workflow.yml`
3. Default to `"all"` (show all commands)

---

## VS Code Copilot Integration

### Handoff Priority

When role is selected, Copilot handoffs prioritize role-appropriate agents:

**Example: Developer role selected**

After running `/dev:plan`, handoff buttons appear:
```
✓ Planning Complete → Begin Implementation [/dev:implement]
✓ Need More Research? → Research Feature [/pm:research]
✓ Security Review → Scan for Vulnerabilities [/sec:scan-web]
```

**Ordering**:
1. **Primary**: Next step in workflow for selected role (`/dev:implement`)
2. **Secondary**: Cross-role handoffs (`/pm:research`, `/sec:scan-web`)

### Agent Visibility in Chat

When user types `@` in VS Code Copilot chat, agents are shown in priority order:

**Developer role selected**:
```
Suggested Agents:
  @software-architect ⭐
  @frontend-engineer ⭐
  @backend-engineer ⭐
  @platform-engineer
  @pm-planner
  @quality-guardian
  @secure-by-design-engineer
  (⭐ = auto-loaded based on your role)
```

### Autocomplete Filtering

When user types `/` in Copilot chat, commands are shown in priority order:

**Developer role selected**:
```
Developer Commands (Primary):
  /dev:plan - Execute planning workflow
  /dev:implement - Execute implementation
  /dev:operate - Execute operations workflow
  /dev:init - Initialize project

Related Commands:
  /pm:specify - Create requirements (cross-role)
  /qa:validate - Run validation (cross-role)

Utilities:
  /speckit:constitution - View project constitution
  /speckit:tasks - Manage backlog tasks
```

---

## Implementation in Copilot Agents

### Agent Metadata Enhancement

Each `.github/agents/*.agent.md` file includes role metadata:

```yaml
name: "dev-plan"
description: "Execute planning workflow using architect and platform engineer"
target: "flowspec"
tools: [Read, Write, Edit, Bash, Grep, Glob, Skill, mcp__backlog__*]

# === NEW: Role-Based Metadata ===
role: "dev"                        # Primary role this command belongs to
priority_for_roles: ["dev"]        # Roles that see this command first
visible_to_roles: ["dev", "all"]   # Roles that can see this command
auto_load_for_roles: ["dev"]       # Roles that auto-load this agent

handoffs:
  - label: "✓ Planning Complete → Begin Implementation"
    agent: "dev-implement"
    prompt: "Based on the architecture and platform design, implement the feature."
    send: false
    priority_for_roles: ["dev"]  # Handoff appears prominently for devs
```

---

## Role Switching Workflow

### Switching Roles Mid-Project

User can change role at any time:

```bash
# Re-run init to select new role
specify init --reset-role

# Or directly via reset
specify reset --role pm

# Or edit config directly
vim flowspec_workflow.yml
# Change: primary_role: "pm"
```

### Multi-Role Users

Some users wear multiple hats (e.g., Full-Stack Dev + PM):

**Option 1: Switch roles as needed**
```bash
# Morning: PM work
specify reset --role pm
/pm:assess feature-x

# Afternoon: Dev work
specify reset --role dev
/dev:implement feature-x
```

**Option 2: Use "All Roles" mode**
```bash
specify init --role all
# See all commands, no filtering
```

---

## Extensibility for Future Roles

### Adding a New Role

To add a new role (e.g., "Data Engineer"):

1. **Add to role_config in flowspec_workflow.yml**:
```yaml
role_config:
  roles:
    data:
      display_name: "Data Engineer"
      icon: "📊"
      preferred_mode: "full"
      auto_load_agents:
        - "@data-engineer"
      default_workflow_entry: "/data:pipeline"
```

2. **Create commands under new namespace**: `/data:*`

3. **Update init prompt** to include new role option

4. **Regenerate Copilot agents** with role metadata

### Dynamic Role Discovery

System automatically discovers available roles from `role_config.roles`:

```python
def get_available_roles(workflow_config: dict) -> list[str]:
    """Discover all configured roles dynamically."""
    return list(workflow_config.get("role_config", {}).get("roles", {}).keys())
```

---

## Consequences

### Positive

1. **Personalized Experience**: Users see commands relevant to their role
2. **Improved Onboarding**: New users can select role and get started immediately
3. **Flexible**: Easy to switch roles or use "All" mode
4. **Team Coordination**: Project config reflects team structure
5. **Cross-Platform**: Works in Claude Code CLI and VS Code Copilot
6. **Extensible**: Adding new roles requires minimal code changes

### Negative

1. **Configuration Complexity**: One more thing to configure
2. **Git Conflicts**: Multiple users editing flowspec_workflow.yml
3. **Discovery Burden**: Users must understand role concept
4. **Migration**: Existing projects need to run init/reset to set role

### Neutral

1. **Default Fallback**: If no role selected, show all commands (no breaking change)
2. **Environment Override**: Power users can override per session
3. **Role vs User**: Role is project-scoped, not tied to user identity

---

## Migration Path

### For Existing Projects

**Phase 1: Optional Adoption (Month 1-3)**
- Role config is optional
- If `role_config.primary_role` not set, default to `"all"`
- No breaking changes

**Phase 2: Prompted Adoption (Month 4-6)**
- When user runs any `/flowspec` command, check if role is set
- If not set, show one-time prompt:
  ```
  🎯 Quick Setup: Select your role to see relevant commands
  Run: specify init --role <role>
  Skip: specify init --role all
  ```

**Phase 3: Recommended Practice (Month 7+)**
- Documentation emphasizes role selection
- Onboarding guides include role selection step
- Analytics track adoption rate

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Users confused by role concept | Medium | Medium | Clear documentation, interactive prompt with descriptions |
| Git conflicts on flowspec_workflow.yml | High | Low | JSON merge strategy, environment variable override |
| Role selection adds friction | Low | Medium | Make selection < 30 seconds, allow skip |
| Users select wrong role | Medium | Low | Easy to switch, "All Roles" fallback |
| Team members have different roles | High | Low | Each user can override with env var |

---

## Implementation Tasks

### Phase 1: Core Functionality (Week 1) ✅
- [x] Add `role_config` schema to flowspec_workflow.yml
- [x] Implement role selection prompt in init/configure commands
- [x] Store selected role in config
- [x] Add environment variable override (FLOWSPEC_PRIMARY_ROLE)

### Phase 2: IDE Integration (Week 2) ✅
- [x] Update VS Code agent metadata with role fields
- [x] Implement handoff priority based on role
- [x] Implement agent pinning based on role
- [x] Test in VS Code and VS Code Insiders
- [x] Create `specify vscode generate` command
- [x] Generate .vscode/settings.json with role config

### Phase 3: CLI Integration (Week 3)
- [ ] Filter command suggestions by role in Claude Code
- [ ] Show role-appropriate agent suggestions
- [ ] Add role indicator to CLI prompt

### Phase 4: Documentation (Week 4)
- [ ] Migration guide for existing projects
- [ ] Role selection quickstart
- [ ] FAQ for multi-role users
- [ ] Video walkthrough

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to select role | < 30 seconds | User testing |
| Role adoption rate | > 75% by Month 6 | Telemetry |
| Command discovery time | < 15 seconds | User testing |
| User satisfaction with role feature | > 4.0/5.0 | Survey |
| Multi-role user adoption of env var | > 50% | Telemetry |

---

## Related Documents

- [ADR: Role-Based Command Namespaces](./ADR-role-based-command-namespaces.md)
- [Design: Command Migration Path](./design-command-migration-path.md)
- [Workflow Configuration Schema](../../flowspec_workflow.yml)
- [VS Code Copilot Agents Plan](../platform/vscode-copilot-agents-plan.md)

---

## Implementation Details (Phase 2)

### VS Code Settings Generation

**Module**: `src/specify_cli/vscode/settings_generator.py`

The `VSCodeSettingsGenerator` class provides:
- Role-based agent ordering (primary role agents first)
- Automatic merging with existing settings
- GitHub Copilot agent pinning configuration
- Prompt file enablement
- Extension recommendations

**Key Features**:
1. **Agent Prioritization**: Top 6 agents pinned for role
2. **Settings Merge**: Preserves existing VS Code settings
3. **Idempotent**: Safe to run multiple times
4. **Role Override**: Can generate for any role, not just primary

### CLI Command

**Command**: `specify vscode generate`

**Options**:
- `--role <role>`: Override primary role from config
- `--output <path>`: Custom output path (default: `.vscode/settings.json`)
- `--force`: Overwrite without merging
- `--no-merge`: Don't merge with existing settings

**Example Usage**:
```bash
# Generate for primary role
specify vscode generate

# Generate for specific role
specify vscode generate --role qa

# Force overwrite
specify vscode generate --force
```

### Generated Settings Structure

```json
{
  "github.copilot.chat.agents": {
    "enabled": true,
    "pinnedAgents": ["@agent1", "@agent2", ...]
  },
  "github.copilot.chat.promptFiles": {
    "enabled": true
  },
  "flowspec": {
    "primaryRole": "dev",
    "displayName": "Developer",
    "icon": "💻",
    "commands": ["build", "debug", "refactor"],
    "agentOrder": ["@agent1", "@agent2", ...],
    "version": "2.0"
  },
  "extensions": {
    "recommendations": ["github.copilot", "github.copilot-chat"]
  }
}
```

### Agent Filtering Strategy

**Design Decision**: **De-prioritize, not hide**

We chose to re-order agents rather than hide them:
- All agents remain accessible in VS Code Copilot
- Role-appropriate agents appear first (top 6 pinned)
- Cross-role agents remain discoverable
- No gatekeeping or artificial restrictions

**Rationale**:
- Developers often wear multiple hats
- Security reviews needed by all roles
- Encourages collaboration across teams
- Reduces friction in workflow

### Cross-Role Handoff Support

While agents are prioritized by role, users can:
1. Type `@<any-agent>` to invoke any agent
2. See all agents in autocomplete (just re-ordered)
3. Switch roles easily via `--role` flag

Example cross-role handoff:
- Developer types `@secure-by-design-engineer` for security review
- PM types `@software-architect` for architecture questions
- QA types `@backend-engineer` to understand implementation

### Testing

**Test Coverage**: 16 tests in `tests/test_vscode_settings_generator.py`

Key test scenarios:
- Role-based agent ordering
- Settings merging with existing files
- Agent pinning limits (6 agents max)
- Different roles generate different settings
- File creation and overwriting
- JSON validity
- Extension recommendations merging

### Documentation

- **User Guide**: `docs/guides/vscode-role-integration.md`
- **Template**: `templates/vscode/settings.json.template`
- **API Docs**: Docstrings in `VSCodeSettingsGenerator` class

---

**Reviewers**: @product-requirements-manager, @software-architect
**Status**: Phase 2 Complete (VS Code integration implemented)
**Last Updated**: 2025-12-09
**Next Review Date**: 2025-12-16
