# agents.md Integration for Claude Code

This document explains how jp-spec-kit integrates the [agents.md specification](https://agents.md/) with Claude Code's slash commands.

## Overview

jp-spec-kit uses **15 specialized AI agents** defined in `.agents/` directory following the agents.md standard. These agents are dynamically loaded into Claude Code slash commands via a Python integration layer.

## Architecture

```
.agents/                          # Agent definitions (agents.md spec)
├── sre-agent.md
├── software-architect-enhanced.md
├── platform-engineer-enhanced.md
├── product-requirements-manager-enhanced.md
├── researcher.md
├── business-validator.md
├── frontend-engineer.md
├── backend-engineer.md
├── ai-ml-engineer.md
├── frontend-code-reviewer.md
├── backend-code-reviewer.md
├── quality-guardian.md
├── secure-by-design-engineer.md
├── tech-writer.md
└── release-manager.md

.claude/                          # Claude Code integration layer
├── load-agent.py                # Agent context loader script
├── agents-config.json           # Agent-to-workflow mapping
└── commands/flowspec/             # Slash commands that use agents
    ├── specify.md
    ├── plan.md
    ├── research.md
    ├── implement.md
    ├── validate.md
    └── operate.md
```

## How It Works

### 1. Agent Definition (agents.md Standard)

Each agent file in `.agents/` follows this format:

```markdown
---
name: sre-agent
description: Expert Site Reliability Engineer...
tools: Glob, Grep, Read, Write, Edit, mcp__github__*
model: sonnet
color: blue
loop: outer
---

You are a Principal Site Reliability Engineer...
[Full agent instructions]
```

### 2. Agent Loading

The `.claude/load-agent.py` script loads agent contexts:

```bash
# Load single agent
python .claude/load-agent.py sre-agent

# Load multiple agents
python .claude/load-agent.py software-architect-enhanced platform-engineer-enhanced
```

The script:
- Strips YAML frontmatter
- Returns clean agent instructions
- Can combine multiple agent contexts

### 3. Agent Configuration

`.claude/agents-config.json` maps agents to workflows:

```json
{
  "workflows": {
    "operate": {
      "agents": ["sre-agent"],
      "phase": "operations"
    },
    "plan": {
      "agents": ["software-architect-enhanced", "platform-engineer-enhanced"],
      "parallel": true
    }
  }
}
```

### 4. Slash Command Integration

Claude Code slash commands reference agents using the `Task` tool. Example from `/flow:operate`:

```markdown
Use the Task tool to launch a **general-purpose** agent with the following prompt:

\`\`\`
# Agent Context (loaded from .agents/sre-agent.md)
$(python .claude/load-agent.py sre-agent)

# TASK: Design and implement operational infrastructure for: [USER INPUT]
...
\`\`\`
```

## Workflow-to-Agent Mapping

| Workflow       | Agents                                                                                                        | Phase        |
|----------------|---------------------------------------------------------------------------------------------------------------|--------------|
| `/flow:specify`  | `product-requirements-manager-enhanced`                                                                      | Requirements |
| `/flow:plan`     | `software-architect-enhanced`, `platform-engineer-enhanced`                                                  | Architecture |
| `/flow:research` | `researcher`, `business-validator`                                                                          | Research     |
| `/flow:implement` | `frontend-engineer`, `backend-engineer`, `ai-ml-engineer`, `frontend-code-reviewer`, `backend-code-reviewer` | Development  |
| `/flow:validate` | `quality-guardian`, `secure-by-design-engineer`, `tech-writer`, `release-manager`                           | Validation   |
| `/flow:operate`  | `sre-agent`                                                                                                  | Operations   |

## Agent Loop Classification

Agents are classified by development loop:

### Inner Loop (Local Development)
- product-requirements-manager-enhanced
- software-architect-enhanced
- platform-engineer-enhanced
- researcher, business-validator
- frontend-engineer, backend-engineer, ai-ml-engineer
- frontend-code-reviewer, backend-code-reviewer
- quality-guardian
- secure-by-design-engineer
- tech-writer

### Outer Loop (CI/CD, Production)
- sre-agent
- release-manager

## Adding a New Agent

1. **Create agent file** in `.agents/`:
   ```bash
   touch .agents/my-new-agent.md
   ```

2. **Write agent definition** following agents.md spec:
   ```markdown
   ---
   name: my-new-agent
   description: Expert in...
   tools: Glob, Grep, Read, Write, Edit
   model: sonnet
   color: green
   loop: inner
   ---

   You are a...
   ```

3. **Update** `.claude/agents-config.json`:
   ```json
   {
     "agents": {
       "my-new-agent": {
         "file": "my-new-agent.md",
         "role": "New Agent Role",
         "workflows": ["my-workflow"],
         "loop": "inner"
       }
     }
   }
   ```

4. **Reference in slash command**:
   ```markdown
   $(python .claude/load-agent.py my-new-agent)
   ```

5. **Test**:
   ```bash
   python .claude/load-agent.py my-new-agent
   ```

## Benefits of This Approach

### 1. Standards Compliance
- ✅ Follows agents.md specification
- ✅ Portable across AI coding assistants (Claude, Cursor, Windsurf, etc.)
- ✅ Single source of truth for agent definitions

### 2. Maintainability
- ✅ Agents defined once, used in multiple workflows
- ✅ Easy to update agent behavior
- ✅ Clear separation of concerns

### 3. Scalability
- ✅ Add new agents without modifying slash commands
- ✅ Compose agents dynamically
- ✅ Parallel agent execution support

### 4. Discoverability
- ✅ Agent catalog in `.claude/agents-config.json`
- ✅ Self-documenting with YAML frontmatter
- ✅ Clear agent-to-workflow mapping

## Testing Agents

### Test Agent Loading
```bash
# List available agents
python .claude/load-agent.py

# Load single agent
python .claude/load-agent.py sre-agent | head -20

# Load multiple agents
python .claude/load-agent.py researcher business-validator | grep "##"
```

### Test Slash Commands
```bash
# In Claude Code
/flow:operate Build a production-ready deployment pipeline
/flow:plan Design architecture for e-commerce platform
/flow:research Analyze market for AI coding assistants
```

## Troubleshooting

### Agent file not found
```bash
Error: Agent file not found: .agents/my-agent.md
Available agents: sre-agent, frontend-engineer, ...
```
**Solution**: Check agent name spelling, ensure `.agents/my-agent.md` exists

### YAML frontmatter in output
**Problem**: Agent context includes `---` markers
**Solution**: Verify `.claude/load-agent.py` regex correctly strips frontmatter

### Agent not loaded in slash command
**Problem**: Slash command doesn't reference agent
**Solution**: Update slash command to include:
```markdown
$(python .claude/load-agent.py agent-name)
```

## Migration from Inline Agents

If you previously had inline agent contexts in slash commands:

1. **Extract agent content** to `.agents/agent-name.md`
2. **Add YAML frontmatter** following agents.md spec
3. **Replace inline content** with:
   ```markdown
   $(python .claude/load-agent.py agent-name)
   ```
4. **Test** the slash command
5. **Remove** old inline content

## Future Enhancements

Potential improvements to the integration layer:

1. **Agent validation script**: Validate agents.md YAML frontmatter
2. **Agent catalog generator**: Auto-generate agent documentation
3. **Dependency resolution**: Handle agent dependencies
4. **Template variables**: Support agent parameter injection
5. **Performance caching**: Cache loaded agents in memory

## Resources

- **agents.md Spec**: https://agents.md/
- **Claude Code Docs**: https://docs.claude.com/claude-code
- **JP Spec Kit**: https://github.com/yourrepo/jp-spec-kit
- **Spec-Driven Development**: See `spec-driven.md`

## Support

For issues or questions:
- Check `.claude/agents-config.json` for agent-workflow mappings
- Test agent loading with `.claude/load-agent.py`
- Review slash command definitions in `.claude/commands/flowspec/`
- Open GitHub issue for bugs or enhancement requests

---

*This integration layer ensures jp-spec-kit remains compatible with the agents.md standard while providing seamless integration with Claude Code's slash command system.*
