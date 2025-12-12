# SK-003: Multi-Agent Support Expansion

**Inspired by:** [spec-kitty](https://github.com/Priivacy-ai/spec-kitty) multi-agent support
**Priority:** P3 - Nice to Have
**Complexity:** Low (estimated 3-5 days implementation)
**Dependencies:** None

---

## 1. Problem Statement

Flowspec currently supports 5 AI coding agents:
- Claude Code
- GitHub Copilot
- Cursor
- Gemini CLI
- Windsurf

Spec-kitty supports **11 agents**, including:
- Qwen Code
- opencode
- Kilo Code
- Auggie CLI
- Roo Code
- Codex CLI
- Amazon Q Developer CLI

Teams using these additional agents cannot use flowspec's slash commands without manual setup.

---

## 2. Solution Overview

Extend `specify init` to generate commands for all 11 AI coding agents. Each agent has specific requirements:

| Agent | Directory | File Format | Argument Syntax |
|-------|-----------|-------------|-----------------|
| Claude Code | `.claude/commands/` | Markdown | `$ARGUMENTS` |
| GitHub Copilot | `.github/prompts/` | Markdown | `$ARGUMENTS` |
| Cursor | `.cursor/commands/` | Markdown | `$ARGUMENTS` |
| Gemini CLI | `.gemini/commands/` | TOML | `{{args}}` |
| Windsurf | `.windsurf/commands/` | Markdown | `$ARGUMENTS` |
| **Qwen Code** | `.qwen/commands/` | Markdown | `$ARGUMENTS` |
| **opencode** | `.opencode/commands/` | Markdown | `$ARGUMENTS` |
| **Kilo Code** | `.kilocode/commands/` | Markdown | `$ARGUMENTS` |
| **Auggie CLI** | `.augment/commands/` | Markdown | `$ARGUMENTS` |
| **Roo Code** | `.roo/commands/` | Markdown | `$ARGUMENTS` |
| **Codex CLI** | `.codex/commands/` | Markdown | `$ARGUMENTS` |
| **Amazon Q** | `.amazonq/prompts/` | Markdown | N/A (no args) |

---

## 3. User Stories

### US-1: Initialize with New Agent
**As a** developer using Qwen Code
**I want to** run `specify init --ai qwen`
**So that** I get slash commands compatible with my agent

**Acceptance Criteria:**
- [ ] `--ai qwen` creates `.qwen/commands/` with all flowspec commands
- [ ] Commands use correct argument syntax for agent
- [ ] Agent detection works if Qwen CLI is installed

### US-2: Multiple Agent Initialization
**As a** team using multiple AI tools
**I want to** run `specify init --ai claude,qwen,cursor`
**So that** all team members can use their preferred agent

**Acceptance Criteria:**
- [ ] Comma-separated agent list creates all directories
- [ ] Each agent gets correctly formatted commands
- [ ] No conflicts between agent command directories

### US-3: Agent Auto-Detection
**As a** developer
**I want** flowspec to detect installed agents
**So that** I don't have to specify which I'm using

**Acceptance Criteria:**
- [ ] Check for `qwen` CLI in PATH
- [ ] Check for `opencode` CLI in PATH
- [ ] Check for `kilo` CLI in PATH
- [ ] Prompt to select from detected agents

---

## 4. Technical Design

### 4.1 Agent Configuration

```python
# src/specify_cli/agents/config.py

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class AgentType(Enum):
    CLAUDE = "claude"
    COPILOT = "copilot"
    CURSOR = "cursor"
    GEMINI = "gemini"
    WINDSURF = "windsurf"
    QWEN = "qwen"
    OPENCODE = "opencode"
    KILO = "kilo"
    AUGGIE = "auggie"
    ROO = "roo"
    CODEX = "codex"
    AMAZON_Q = "q"

@dataclass
class AgentConfig:
    """Configuration for an AI coding agent."""
    type: AgentType
    display_name: str
    command_dir: str              # e.g., ".claude/commands"
    file_extension: str           # "md" or "toml"
    argument_syntax: str          # "$ARGUMENTS" or "{{args}}" or None
    cli_command: Optional[str]    # CLI to check in PATH
    supports_args: bool           # Whether agent supports command arguments
    is_ide_based: bool            # IDE plugin vs CLI tool

AGENT_CONFIGS = {
    AgentType.CLAUDE: AgentConfig(
        type=AgentType.CLAUDE,
        display_name="Claude Code",
        command_dir=".claude/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="claude",
        supports_args=True,
        is_ide_based=False,
    ),
    AgentType.COPILOT: AgentConfig(
        type=AgentType.COPILOT,
        display_name="GitHub Copilot",
        command_dir=".github/prompts",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command=None,
        supports_args=True,
        is_ide_based=True,
    ),
    AgentType.CURSOR: AgentConfig(
        type=AgentType.CURSOR,
        display_name="Cursor",
        command_dir=".cursor/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="cursor",
        supports_args=True,
        is_ide_based=True,
    ),
    AgentType.GEMINI: AgentConfig(
        type=AgentType.GEMINI,
        display_name="Gemini CLI",
        command_dir=".gemini/commands",
        file_extension="toml",
        argument_syntax="{{args}}",
        cli_command="gemini",
        supports_args=True,
        is_ide_based=False,
    ),
    AgentType.WINDSURF: AgentConfig(
        type=AgentType.WINDSURF,
        display_name="Windsurf",
        command_dir=".windsurf/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="windsurf",
        supports_args=True,
        is_ide_based=True,
    ),
    # New agents from spec-kitty
    AgentType.QWEN: AgentConfig(
        type=AgentType.QWEN,
        display_name="Qwen Code",
        command_dir=".qwen/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="qwen",
        supports_args=True,
        is_ide_based=False,
    ),
    AgentType.OPENCODE: AgentConfig(
        type=AgentType.OPENCODE,
        display_name="opencode",
        command_dir=".opencode/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="opencode",
        supports_args=True,
        is_ide_based=False,
    ),
    AgentType.KILO: AgentConfig(
        type=AgentType.KILO,
        display_name="Kilo Code",
        command_dir=".kilocode/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="kilo",
        supports_args=True,
        is_ide_based=True,
    ),
    AgentType.AUGGIE: AgentConfig(
        type=AgentType.AUGGIE,
        display_name="Auggie CLI",
        command_dir=".augment/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="auggie",
        supports_args=True,
        is_ide_based=False,
    ),
    AgentType.ROO: AgentConfig(
        type=AgentType.ROO,
        display_name="Roo Code",
        command_dir=".roo/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="roo",
        supports_args=True,
        is_ide_based=True,
    ),
    AgentType.CODEX: AgentConfig(
        type=AgentType.CODEX,
        display_name="Codex CLI",
        command_dir=".codex/commands",
        file_extension="md",
        argument_syntax="$ARGUMENTS",
        cli_command="codex",
        supports_args=True,
        is_ide_based=False,
    ),
    AgentType.AMAZON_Q: AgentConfig(
        type=AgentType.AMAZON_Q,
        display_name="Amazon Q Developer CLI",
        command_dir=".amazonq/prompts",
        file_extension="md",
        argument_syntax=None,  # Does not support custom arguments
        cli_command="q",
        supports_args=False,
        is_ide_based=False,
    ),
}
```

### 4.2 Agent Detection

```python
# src/specify_cli/agents/detection.py

import shutil
from typing import List
from .config import AgentType, AGENT_CONFIGS

def detect_installed_agents() -> List[AgentType]:
    """Detect which AI agents are installed on the system."""
    detected = []

    for agent_type, config in AGENT_CONFIGS.items():
        if config.cli_command is None:
            # IDE-based agents - can't detect, skip
            continue

        if shutil.which(config.cli_command):
            detected.append(agent_type)

    return detected

def prompt_agent_selection(detected: List[AgentType]) -> List[AgentType]:
    """Interactive prompt to select agents."""
    from rich.prompt import Prompt
    from rich.console import Console

    console = Console()

    if not detected:
        console.print("[yellow]No AI agents detected in PATH.[/yellow]")
        console.print("Available agents:")
        for i, (agent_type, config) in enumerate(AGENT_CONFIGS.items(), 1):
            console.print(f"  {i}. {config.display_name} ({agent_type.value})")

        selection = Prompt.ask(
            "Enter agent names (comma-separated)",
            default="claude"
        )
    else:
        console.print("[green]Detected agents:[/green]")
        for agent_type in detected:
            config = AGENT_CONFIGS[agent_type]
            console.print(f"  - {config.display_name}")

        selection = Prompt.ask(
            "Which agents to initialize? (comma-separated, or 'all' for detected)",
            default=",".join(a.value for a in detected)
        )

    if selection.lower() == "all":
        return detected

    selected = []
    for name in selection.split(","):
        name = name.strip().lower()
        try:
            selected.append(AgentType(name))
        except ValueError:
            console.print(f"[yellow]Unknown agent: {name}[/yellow]")

    return selected
```

### 4.3 Command Generation

```python
# src/specify_cli/agents/generator.py

from pathlib import Path
from typing import List
from .config import AgentType, AGENT_CONFIGS

def generate_agent_commands(
    project_dir: Path,
    agents: List[AgentType],
    template_dir: Path,
) -> None:
    """Generate command files for specified agents."""

    for agent_type in agents:
        config = AGENT_CONFIGS[agent_type]
        command_dir = project_dir / config.command_dir
        command_dir.mkdir(parents=True, exist_ok=True)

        # Copy command templates
        for template_file in template_dir.glob("**/*.md"):
            # Get relative path for nested commands (e.g., flow/assess.md)
            rel_path = template_file.relative_to(template_dir)

            # Determine output filename and path
            if config.file_extension == "toml":
                output_file = command_dir / rel_path.with_suffix(".toml")
            else:
                output_file = command_dir / rel_path

            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Read template and transform for agent
            content = template_file.read_text()
            transformed = transform_for_agent(content, config)

            output_file.write_text(transformed)

def transform_for_agent(content: str, config) -> str:
    """Transform command template for specific agent."""

    if config.file_extension == "toml":
        # Convert markdown to TOML format for Gemini
        return convert_md_to_toml(content, config.argument_syntax)

    if config.argument_syntax:
        # Replace argument placeholder if needed
        content = content.replace("$ARGUMENTS", config.argument_syntax)

    if not config.supports_args:
        # Remove argument references for agents that don't support them
        content = remove_argument_references(content)

    return content

def convert_md_to_toml(md_content: str, arg_syntax: str) -> str:
    """Convert markdown command to TOML format for Gemini CLI."""
    import re

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', md_content, re.DOTALL)
    if not frontmatter_match:
        return md_content

    # Parse description from frontmatter
    frontmatter = frontmatter_match.group(1)
    description = ""
    for line in frontmatter.split('\n'):
        if line.startswith('description:'):
            description = line.split(':', 1)[1].strip().strip('"\'')
            break

    body = md_content[frontmatter_match.end():]

    # Build TOML
    toml_content = f'''[command]
description = "{description}"

[command.prompt]
text = """
{body.strip()}
"""
'''

    if arg_syntax:
        toml_content = toml_content.replace("$ARGUMENTS", arg_syntax)

    return toml_content

def remove_argument_references(content: str) -> str:
    """Remove $ARGUMENTS and related text for agents that don't support args."""
    import re
    # Remove lines containing $ARGUMENTS
    content = re.sub(r'^.*\$ARGUMENTS.*$\n?', '', content, flags=re.MULTILINE)
    return content
```

### 4.4 CLI Integration

```python
# Update to specify init command

@app.command()
def init(
    project_name: str = typer.Argument(None),
    ai: str = typer.Option(None, "--ai", help="AI agent(s): claude,cursor,gemini,qwen,opencode,kilo,auggie,roo,codex,windsurf,copilot,q"),
    ignore_agent_tools: bool = typer.Option(False, "--ignore-agent-tools", help="Skip agent CLI detection"),
):
    """Initialize a flowspec project."""

    # Parse agent list
    if ai:
        agent_names = [a.strip().lower() for a in ai.split(",")]
        agents = []
        for name in agent_names:
            try:
                agents.append(AgentType(name))
            except ValueError:
                typer.echo(f"Unknown agent: {name}", err=True)
                raise typer.Exit(1)
    else:
        # Auto-detect or prompt
        if ignore_agent_tools:
            agents = [AgentType.CLAUDE]  # Default
        else:
            detected = detect_installed_agents()
            agents = prompt_agent_selection(detected)

    # Generate commands for each agent
    generate_agent_commands(project_dir, agents, template_dir)

    typer.echo(f"Initialized flowspec with agents: {', '.join(a.value for a in agents)}")
```

---

## 5. Template Structure

Commands are stored in `templates/commands/` with markdown format:

```
templates/commands/
├── flow/
│   ├── assess.md
│   ├── specify.md
│   ├── plan.md
│   ├── implement.md
│   ├── validate.md
│   └── operate.md
├── dev/
│   ├── debug.md
│   ├── refactor.md
│   └── cleanup.md
├── sec/
│   ├── scan.md
│   ├── triage.md
│   └── fix.md
└── ...
```

Each agent gets these templates copied to their specific directory with format transformations applied.

---

## 6. Agent-Specific Notes

### Amazon Q Developer CLI
- Does NOT support custom arguments in slash commands
- Commands must be self-contained prompts
- See: https://github.com/aws/amazon-q-developer-cli/issues/3064

### Codex CLI (OpenAI)
- Requires `CODEX_HOME` environment variable
- Point to project's `.codex/` directory
- Can use direnv for automatic loading

### Gemini CLI
- Uses TOML format instead of Markdown
- Arguments via `{{args}}` syntax
- Different frontmatter structure

---

## 7. Implementation Plan

### Phase 1: Configuration (Day 1-2)
1. Create `src/specify_cli/agents/` module
2. Define `AgentConfig` dataclass
3. Add all 11 agent configurations
4. Unit tests for config parsing

### Phase 2: Detection & Generation (Day 2-3)
1. Implement agent detection
2. Implement command generation
3. Add TOML conversion for Gemini
4. Handle argument syntax variations

### Phase 3: CLI Integration (Day 3-4)
1. Update `specify init` command
2. Add `--ai` flag with all agents
3. Interactive agent selection prompt
4. Integration tests

### Phase 4: Documentation (Day 4-5)
1. Update README with all agents
2. Add agent-specific setup notes
3. Update CLAUDE.md

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Agents supported | 11 (from 5) |
| Command generation time | < 2 seconds |
| No breaking changes to existing agents | 100% |

---

## 9. References

- [spec-kitty agent support](https://github.com/Priivacy-ai/spec-kitty#-supported-ai-agents)
- [Qwen Code](https://github.com/QwenLM/qwen-code)
- [opencode](https://opencode.ai/)
- [Kilo Code](https://github.com/Kilo-Org/kilocode)
- [Auggie CLI](https://docs.augmentcode.com/cli/overview)
- [Roo Code](https://roocode.com/)
- [Codex CLI](https://github.com/openai/codex)
- [Amazon Q Developer CLI](https://aws.amazon.com/developer/learning/q-developer-cli/)
