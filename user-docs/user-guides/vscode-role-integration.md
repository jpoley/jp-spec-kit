# VS Code Role Integration Guide

## Overview

Flowspec integrates with VS Code Copilot to provide role-based agent suggestions and command visibility. By configuring your primary role, VS Code will prioritize agents and commands relevant to your work.

## Quick Start

1. **Ensure your role is configured** in `flowspec_workflow.yml`:
   ```bash
   # View current role
   grep "primary:" flowspec_workflow.yml
   ```

2. **Generate VS Code settings**:
   ```bash
   specify vscode generate
   ```

3. **Reload VS Code** to apply the new settings.

## Features

### Agent Pinning

Agents for your selected role appear first in VS Code Copilot suggestions:

- **Developer role**: `@frontend-engineer`, `@backend-engineer`, `@ai-ml-engineer` appear first
- **QA role**: `@quality-guardian`, `@release-manager` appear first
- **Security role**: `@secure-by-design-engineer` appears first

### Prompt Files

The generated settings enable VS Code Copilot prompt files, allowing agents to access project-specific context from `.claude/` directory.

### Extension Recommendations

The settings automatically recommend:
- `github.copilot` - GitHub Copilot extension
- `github.copilot-chat` - GitHub Copilot Chat extension

## Commands

### `specify vscode generate`

Generate `.vscode/settings.json` with role-appropriate configuration.

**Options**:
- `--role <role>` - Override primary role from config (dev, qa, sec, pm, arch, ops)
- `--output <path>` - Custom output path (default: `.vscode/settings.json`)
- `--force` - Overwrite existing settings without merging
- `--no-merge` - Don't merge with existing settings

**Examples**:

```bash
# Generate for primary role (from flowspec_workflow.yml)
specify vscode generate

# Generate for specific role
specify vscode generate --role qa

# Force overwrite without merging
specify vscode generate --force

# Custom output path
specify vscode generate -o custom-settings.json
```

## Configuration Schema

### `.vscode/settings.json`

The generated settings file contains:

```json
{
  "github.copilot.chat.agents": {
    "enabled": true,
    "pinnedAgents": [
      "@frontend-engineer",
      "@backend-engineer",
      "@ai-ml-engineer",
      "@business-validator",
      "@platform-engineer",
      "@product-requirements-manager"
    ]
  },
  "github.copilot.chat.promptFiles": {
    "enabled": true
  },
  "flowspec": {
    "primaryRole": "dev",
    "displayName": "Developer",
    "icon": "💻",
    "commands": ["build", "debug", "refactor"],
    "agentOrder": [
      "@frontend-engineer",
      "@backend-engineer",
      "@ai-ml-engineer",
      // ... all agents in priority order
    ],
    "version": "2.0"
  },
  "extensions": {
    "recommendations": [
      "github.copilot",
      "github.copilot-chat"
    ]
  }
}
```

### Agent Pinning Behavior

- **Limit**: Top 6 agents are pinned for your role
- **Order**: Role-specific agents appear first, then cross-role agents
- **Visibility**: All agents remain accessible; pinning only affects suggestion order

## Role-Specific Configurations

### Developer (dev)

**Pinned agents**:
1. `@frontend-engineer` - React/Next.js development
2. `@backend-engineer` - API/database development
3. `@ai-ml-engineer` - ML/AI features
4. Cross-role agents (platform, QA, security)

**Commands**: `build`, `debug`, `refactor`

### QA Engineer (qa)

**Pinned agents**:
1. `@quality-guardian` - Test creation and execution
2. `@release-manager` - Release validation
3. Cross-role agents (dev, security)

**Commands**: `test`, `verify`, `review`

### Security Engineer (sec)

**Pinned agents**:
1. `@secure-by-design-engineer` - Security analysis and fixes
2. Cross-role agents (dev, QA)

**Commands**: `scan`, `triage`, `fix`, `audit`

### Product Manager (pm)

**Pinned agents**:
1. `@product-requirements-manager` - PRD creation
2. `@workflow-assessor` - Workflow assessment
3. `@researcher` - Market research
4. Cross-role agents (dev, QA)

**Commands**: `assess`, `define`, `discover`

### Architect (arch)

**Pinned agents**:
1. `@software-architect` - Architecture design
2. `@platform-engineer` - Infrastructure design
3. Cross-role agents (dev, ops)

**Commands**: `design`, `decide`, `model`

### SRE/DevOps (ops)

**Pinned agents**:
1. `@sre-agent` - Infrastructure and operations
2. Cross-role agents (dev, security)

**Commands**: `deploy`, `monitor`, `respond`, `scale`

## Merging with Existing Settings

By default, `specify vscode generate` **merges** with existing `.vscode/settings.json`:

- Existing settings are preserved
- Flowspec settings are added/updated
- Extension recommendations are merged (not replaced)

### Force Overwrite

To replace settings entirely without merging:

```bash
specify vscode generate --force --no-merge
```

### Selective Merge

To preserve existing settings but regenerate Flowspec config:

```bash
specify vscode generate  # Default behavior
```

## Cross-Role Handoffs

While agents are prioritized for your role, you can still access agents from other roles:

**Example**: Developer needs security review
```
Type @secure-by-design-engineer in Copilot Chat
```

**Example**: QA needs architecture clarification
```
Type @software-architect in Copilot Chat
```

Agent pinning is **advisory**, not restrictive. All agents remain accessible.

## VS Code Insiders Support

The generated settings work in both:
- **VS Code** (stable)
- **VS Code Insiders** (preview)

Settings location: `.vscode/settings.json` (same for both versions)

## Troubleshooting

### Settings Not Applied

**Solution**: Reload VS Code after generating settings:
```
Cmd/Ctrl + Shift + P → "Developer: Reload Window"
```

### Agent Not Appearing

**Verify agent exists in workflow config**:
```bash
grep -A5 "agents:" flowspec_workflow.yml
```

**Regenerate settings**:
```bash
specify vscode generate --force
```

### Wrong Role Applied

**Check primary role in workflow config**:
```bash
grep "primary:" flowspec_workflow.yml
```

**Override with specific role**:
```bash
specify vscode generate --role <correct-role>
```

### Settings Overwritten

**Use merge mode (default)**:
```bash
specify vscode generate  # Merges with existing
```

**Avoid `--no-merge` unless you want to replace all settings**.

## Best Practices

1. **Generate after role changes**: Re-run `specify vscode generate` when changing roles in `flowspec_workflow.yml`

2. **Commit to git**: Add `.vscode/settings.json` to version control for team consistency

3. **Per-workspace override**: Users can override role per-session:
   ```bash
   FLOWSPEC_PRIMARY_ROLE=qa code .
   ```

4. **Review pinned agents**: Run `specify vscode generate` to see which agents will be pinned

5. **Update regularly**: Regenerate settings when agents are added/removed from workflow config

## Integration with flowspec_workflow.yml

Settings generation reads from `flowspec_workflow.yml`:

```yaml
roles:
  primary: "dev"  # Used by default

  definitions:
    dev:
      display_name: "Developer"
      icon: "💻"
      commands: ["build", "debug", "refactor"]
      agents:
        - "@frontend-engineer"
        - "@backend-engineer"
        - "@ai-ml-engineer"
```

Changing `roles.primary` in workflow config changes the default role for `specify vscode generate`.

## Future Enhancements

Planned features:
- [ ] Auto-regenerate on `flowspec init`
- [ ] VS Code extension for one-click role switching
- [ ] Command palette integration for role selection
- [ ] Agent handoff customization per role
- [ ] Cross-role approval gates (e.g., security approval before deploy)

## Related Documentation

- [ADR: Role Selection During Initialization](../adr/ADR-role-selection-during-initialization.md)
- [ADR: Role-Based Command Namespaces](../adr/ADR-role-based-command-namespaces.md)
- [Workflow Configuration Guide](../reference/workflow-configuration.md)
- [VS Code Copilot Agents Plan](../platform/vscode-copilot-agents-plan.md)

## References

- [VS Code Settings Reference](https://code.visualstudio.com/docs/getstarted/settings)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Flowspec Workflow Schema](../../schemas/flowspec_workflow.schema.json)
