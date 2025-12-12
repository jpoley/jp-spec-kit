# SK-004: Mission System (Domain Adapters)

**Inspired by:** [spec-kitty](https://github.com/Priivacy-ai/spec-kitty) mission system
**Priority:** P2 - Medium Impact
**Complexity:** Medium (estimated 1-2 weeks implementation)
**Dependencies:** flowspec_workflow.yml schema

---

## 1. Problem Statement

Flowspec's workflow is fixed for software development. While comprehensive for building applications, it doesn't adapt well to other domains:

- **Research projects** need different phases (question → gather → analyze → synthesize)
- **Documentation projects** need review/publish workflows
- **Data analysis** needs exploration/modeling phases
- **Security audits** need assessment/remediation workflows

Spec-kitty solves this with a **mission system** - domain adapters that customize:
- Workflow phases
- Expected artifacts
- Validation rules
- Agent context/personality
- MCP tool recommendations

---

## 2. Solution Overview

Extend flowspec to support **mission profiles** that customize the workflow for different domains. The current workflow becomes the `software-dev` mission (default), with additional missions available.

### Design Approach: Profile-Based Extension

Rather than replacing `flowspec_workflow.yml`, missions extend it with:
1. **State overrides** - Different states for the domain
2. **Artifact templates** - Domain-specific templates
3. **Validation rules** - Custom quality gates
4. **Agent context** - Domain-specific guidance

```yaml
# missions/research/mission.yml
name: "Research Mission"
extends: "base"  # Inherit common structure

states:
  - "Question Defined"
  - "Methodology Designed"
  - "Data Gathered"
  - "Analysis Complete"
  - "Synthesis Ready"
  - "Published"

artifacts:
  required:
    - research-question.md
    - methodology.md
    - findings.md
  optional:
    - literature-review.md
    - data/

agent_context: |
  You are a research agent conducting systematic investigation.
  Document ALL sources with citations and access dates.
  Distinguish raw evidence from interpretation.
```

### Backward Compatibility

- Default mission is `software-dev` (current behavior)
- Existing `flowspec_workflow.yml` continues to work
- Mission selection at project init or via config
- No changes required for existing projects

---

## 3. User Stories

### US-1: Initialize with Mission
**As a** researcher starting a new project
**I want to** initialize with a research mission
**So that** my workflow matches research methodology

**Acceptance Criteria:**
- [ ] `specify init --mission research` creates research-focused workflow
- [ ] States reflect research phases, not software dev phases
- [ ] Templates are research-specific (research-question.md, findings.md)
- [ ] Agent context guides research practices

### US-2: List Available Missions
**As a** developer
**I want to** see available missions
**So that** I can choose the right one for my project

**Acceptance Criteria:**
- [ ] `specify mission list` shows all available missions
- [ ] Each mission shows name, description, domain
- [ ] Built-in missions: software-dev, research
- [ ] User can add custom missions

### US-3: Switch Mission (New Features Only)
**As a** developer in a multi-domain project
**I want to** use different missions for different features
**So that** research spikes use research workflow, features use dev workflow

**Acceptance Criteria:**
- [ ] `/flow:specify --mission research` uses research workflow for that feature
- [ ] Other features continue using project default
- [ ] Feature tracks which mission was used
- [ ] Dashboard shows mission per feature

### US-4: Create Custom Mission
**As a** team with custom workflows
**I want to** define a custom mission
**So that** our specific process is enforced

**Acceptance Criteria:**
- [ ] User can create `.specify/missions/custom-mission/` directory
- [ ] Mission YAML defines states, artifacts, validation
- [ ] Custom mission appears in `specify mission list`
- [ ] Templates from custom mission used during specify

---

## 4. Technical Design

### 4.1 Mission Directory Structure

```
.specify/
├── config.yml              # Project config including default mission
└── missions/               # Custom missions (optional)
    └── security-audit/
        ├── mission.yml     # Mission configuration
        ├── templates/      # Custom templates
        └── validation/     # Custom validators

# Built-in missions (in package)
specify_cli/missions/
├── software-dev/
│   ├── mission.yml
│   ├── templates/
│   │   ├── prd-template.md
│   │   ├── plan-template.md
│   │   └── ...
│   └── validation/
├── research/
│   ├── mission.yml
│   ├── templates/
│   │   ├── research-question.md
│   │   ├── methodology.md
│   │   └── findings.md
│   └── validation/
└── base/
    └── mission.yml         # Shared base configuration
```

### 4.2 Mission Configuration Schema

```yaml
# missions/research/mission.yml

# Mission metadata
name: "Deep Research"
description: "Systematic research with structured methodology and evidence synthesis"
version: "1.0.0"
domain: "research"
extends: "base"  # Optional base mission to inherit from

# Workflow customization
workflow:
  phases:
    - name: "question"
      description: "Define research question and scope"
      command: "/flow:specify"
    - name: "methodology"
      description: "Design research methodology"
      command: "/flow:plan"
    - name: "gather"
      description: "Collect data and sources"
      command: "/flow:implement"
    - name: "analyze"
      description: "Analyze findings"
      command: "/flow:implement"
    - name: "synthesize"
      description: "Synthesize results and draw conclusions"
      command: "/flow:validate"
    - name: "publish"
      description: "Prepare findings for publication"
      command: "/flow:operate"

# State mapping (maps mission phases to flowspec states)
states:
  "Question Defined": "Specified"
  "Methodology Designed": "Planned"
  "Data Gathered": "In Implementation"
  "Analysis Complete": "In Implementation"
  "Synthesis Ready": "Validated"
  "Published": "Deployed"

# Expected artifacts
artifacts:
  required:
    - name: "research-question.md"
      template: "templates/research-question.md"
      phase: "question"
    - name: "methodology.md"
      template: "templates/methodology.md"
      phase: "methodology"
    - name: "findings.md"
      template: "templates/findings.md"
      phase: "synthesize"
  optional:
    - name: "literature-review.md"
      template: "templates/literature-review.md"
    - name: "sources/"
      description: "Source documents directory"
    - name: "data/"
      description: "Raw data directory"

# Path conventions
paths:
  workspace: "research/"
  data: "data/"
  deliverables: "findings/"
  documentation: "reports/"

# Validation rules
validation:
  checks:
    - all_sources_documented
    - methodology_clear
    - findings_synthesized
    - no_unresolved_questions
  custom_validators:
    - name: "citation_check"
      script: "validation/check_citations.py"

# MCP tools recommended for this mission
mcp_tools:
  required:
    - filesystem
    - git
  recommended:
    - web-search
    - pdf-reader
    - citation-manager
  optional:
    - arxiv-search
    - pubmed-search

# Agent personality/instructions
agent_context: |
  You are a research agent conducting systematic literature reviews and empirical research.
  Your mission is to maintain research integrity and methodological rigor.

  Key Practices:
  - Document ALL sources with proper citations, URLs, and access dates
  - Extract findings with confidence levels (high/medium/low)
  - Clearly articulate methodology decisions for reproducibility
  - Distinguish raw evidence from interpretation
  - Identify limitations and alternative explanations
  - Synthesize findings with traceable evidence

  Citation Standards:
  - Use BibTeX or APA format (include DOI or URL when available)
  - Track access dates for all online sources
  - Assign confidence levels commensurate with source quality

# Task metadata fields
task_metadata:
  required:
    - task_id
    - phase
    - status
  optional:
    - assignee
    - evidence_count
    - confidence_level

# Command customization (prompts for this mission)
commands:
  specify:
    prompt: "Define research question, scope, and expected outcomes"
    template: "templates/research-question.md"
  plan:
    prompt: "Design research methodology and data collection strategy"
    template: "templates/methodology.md"
  implement:
    prompt: "Execute research plan and collect findings"
    phases: ["gather", "analyze"]
  validate:
    prompt: "Review findings for validity, completeness, and proper documentation"
    template: "templates/findings.md"
  operate:
    prompt: "Prepare research for publication or presentation"
```

### 4.3 Mission Manager Implementation

```python
# src/specify_cli/mission/manager.py

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml

@dataclass
class Mission:
    """Loaded mission configuration."""
    name: str
    description: str
    version: str
    domain: str
    path: Path
    config: Dict

    @property
    def states(self) -> List[str]:
        return list(self.config.get("states", {}).keys())

    @property
    def artifacts(self) -> Dict:
        return self.config.get("artifacts", {})

    @property
    def agent_context(self) -> str:
        return self.config.get("agent_context", "")

    def get_template_path(self, template_name: str) -> Optional[Path]:
        """Get path to template file."""
        template_path = self.path / "templates" / template_name
        if template_path.exists():
            return template_path
        return None

class MissionManager:
    """Manage mission loading and selection."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self._missions: Dict[str, Mission] = {}
        self._load_builtin_missions()
        self._load_custom_missions()

    def _load_builtin_missions(self):
        """Load built-in missions from package."""
        import importlib.resources as pkg_resources

        # Load from package data
        missions_dir = Path(pkg_resources.files("specify_cli")) / "missions"
        self._load_missions_from_dir(missions_dir, builtin=True)

    def _load_custom_missions(self):
        """Load custom missions from project."""
        custom_dir = self.project_dir / ".specify" / "missions"
        if custom_dir.exists():
            self._load_missions_from_dir(custom_dir, builtin=False)

    def _load_missions_from_dir(self, missions_dir: Path, builtin: bool):
        """Load all missions from a directory."""
        if not missions_dir.exists():
            return

        for mission_path in missions_dir.iterdir():
            if not mission_path.is_dir():
                continue

            config_file = mission_path / "mission.yml"
            if not config_file.exists():
                config_file = mission_path / "mission.yaml"
            if not config_file.exists():
                continue

            config = yaml.safe_load(config_file.read_text())
            mission = Mission(
                name=config.get("name", mission_path.name),
                description=config.get("description", ""),
                version=config.get("version", "1.0.0"),
                domain=config.get("domain", "general"),
                path=mission_path,
                config=config,
            )
            self._missions[mission_path.name] = mission

    def list_missions(self) -> List[Mission]:
        """List all available missions."""
        return list(self._missions.values())

    def get_mission(self, name: str) -> Optional[Mission]:
        """Get a specific mission by name."""
        return self._missions.get(name)

    def get_active_mission(self) -> Mission:
        """Get the active mission for the project."""
        config_file = self.project_dir / ".specify" / "config.yml"
        if config_file.exists():
            config = yaml.safe_load(config_file.read_text())
            mission_name = config.get("mission", "software-dev")
        else:
            mission_name = "software-dev"

        mission = self.get_mission(mission_name)
        if not mission:
            raise ValueError(f"Mission not found: {mission_name}")
        return mission

    def set_active_mission(self, name: str):
        """Set the active mission for the project."""
        if name not in self._missions:
            raise ValueError(f"Unknown mission: {name}")

        config_file = self.project_dir / ".specify" / "config.yml"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        if config_file.exists():
            config = yaml.safe_load(config_file.read_text())
        else:
            config = {}

        config["mission"] = name
        config_file.write_text(yaml.dump(config))
```

### 4.4 CLI Commands

```python
# src/specify_cli/cli/commands/mission.py

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from ..mission.manager import MissionManager

app = typer.Typer(help="Manage flowspec missions")
console = Console()

@app.command("list")
def list_missions():
    """List available missions."""
    manager = MissionManager(Path.cwd())
    missions = manager.list_missions()

    table = Table(title="Available Missions")
    table.add_column("Name", style="cyan")
    table.add_column("Domain", style="green")
    table.add_column("Description")
    table.add_column("Version")

    for mission in missions:
        table.add_row(
            mission.name,
            mission.domain,
            mission.description[:50] + "..." if len(mission.description) > 50 else mission.description,
            mission.version
        )

    console.print(table)

@app.command("current")
def current_mission():
    """Show the active mission."""
    manager = MissionManager(Path.cwd())
    mission = manager.get_active_mission()

    console.print(f"[bold]Active Mission:[/bold] {mission.name}")
    console.print(f"[dim]Domain:[/dim] {mission.domain}")
    console.print(f"[dim]Description:[/dim] {mission.description}")
    console.print(f"[dim]Path:[/dim] {mission.path}")

@app.command("switch")
def switch_mission(name: str):
    """Switch to a different mission."""
    manager = MissionManager(Path.cwd())

    try:
        manager.set_active_mission(name)
        console.print(f"[green]Switched to mission: {name}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command("info")
def mission_info(name: str = typer.Argument(None)):
    """Show detailed information about a mission."""
    manager = MissionManager(Path.cwd())

    if name is None:
        mission = manager.get_active_mission()
    else:
        mission = manager.get_mission(name)
        if not mission:
            console.print(f"[red]Mission not found: {name}[/red]")
            raise typer.Exit(1)

    console.print(f"[bold]{mission.name}[/bold]")
    console.print(f"Version: {mission.version}")
    console.print(f"Domain: {mission.domain}")
    console.print(f"Description: {mission.description}")
    console.print()
    console.print("[bold]States:[/bold]")
    for state in mission.states:
        console.print(f"  - {state}")
    console.print()
    console.print("[bold]Required Artifacts:[/bold]")
    for artifact in mission.artifacts.get("required", []):
        if isinstance(artifact, dict):
            console.print(f"  - {artifact.get('name')}")
        else:
            console.print(f"  - {artifact}")
```

### 4.5 Integration with /flow Commands

Commands use active mission for templates and context:

```python
# In /flow:specify implementation

from ..mission.manager import MissionManager

def specify_command(feature_description: str, mission: str = None):
    manager = MissionManager(Path.cwd())

    # Use specified mission or project default
    if mission:
        active_mission = manager.get_mission(mission)
    else:
        active_mission = manager.get_active_mission()

    # Get template for this mission
    template_path = active_mission.get_template_path("prd-template.md")
    if not template_path:
        template_path = get_default_template("prd-template.md")

    # Include agent context in prompt
    agent_context = active_mission.agent_context

    # ... rest of specify logic using mission-specific templates/context
```

---

## 5. Built-in Missions

### 5.1 Software Development (Default)

```yaml
name: "Software Development"
domain: "software"
description: "Build high-quality software with structured workflows and TDD"

workflow:
  phases:
    - name: "assess"
      command: "/flow:assess"
    - name: "specify"
      command: "/flow:specify"
    - name: "research"
      command: "/flow:research"
      optional: true
    - name: "plan"
      command: "/flow:plan"
    - name: "implement"
      command: "/flow:implement"
    - name: "validate"
      command: "/flow:validate"
    - name: "operate"
      command: "/flow:operate"

artifacts:
  required:
    - prd.md
    - plan.md
    - tests/
  optional:
    - adr/
    - research.md
```

### 5.2 Research Mission

```yaml
name: "Deep Research"
domain: "research"
description: "Systematic research with structured methodology"

workflow:
  phases:
    - name: "question"
      description: "Define research question"
      command: "/flow:specify"
    - name: "methodology"
      description: "Design approach"
      command: "/flow:plan"
    - name: "gather"
      description: "Collect evidence"
      command: "/flow:implement"
    - name: "synthesize"
      description: "Synthesize findings"
      command: "/flow:validate"

artifacts:
  required:
    - research-question.md
    - methodology.md
    - findings.md
```

---

## 6. Implementation Plan

### Phase 1: Core Mission System (Week 1)
1. Create `src/specify_cli/mission/` module
2. Implement `MissionManager` class
3. Create built-in software-dev and research missions
4. Add mission YAML schema

### Phase 2: CLI Integration (Week 1-2)
1. Add `specify mission` command group
2. Integrate mission selection into `specify init`
3. Pass mission context to /flow commands
4. Add `--mission` flag to `/flow:specify`

### Phase 3: Templates & Validation (Week 2)
1. Create research mission templates
2. Add custom validation support
3. Agent context injection
4. Documentation

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Built-in missions | 2 (software-dev, research) |
| Mission switch time | < 1 second |
| No regressions for default workflow | 100% |
| Custom mission support | Working |

---

## 8. Future Missions (Post-MVP)

- **Security Audit** - Vulnerability assessment workflow
- **Documentation** - Technical writing workflow
- **Data Analysis** - Exploratory data analysis workflow
- **API Design** - API-first development workflow

---

## 9. References

- [spec-kitty mission system](https://github.com/Priivacy-ai/spec-kitty/tree/main/.kittify/missions)
- [spec-kitty software-dev mission](https://github.com/Priivacy-ai/spec-kitty/blob/main/.kittify/missions/software-dev/mission.yaml)
- [spec-kitty research mission](https://github.com/Priivacy-ai/spec-kitty/blob/main/.kittify/missions/research/mission.yaml)
