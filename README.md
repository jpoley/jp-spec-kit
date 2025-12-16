<div align="center">
    <img src="./images/flowspec.png"/>
    <h1>flowspec</h1>
    <h3><em>Spec-Driven Development with AI-Powered Task Management</em></h3>
</div>

<p align="center">
    <strong>Plan features with specialized AI agents. Track progress in backlog.md. Ship with confidence.</strong>
</p>

<p align="center">
    <a href="https://github.com/jpoley/flowspec/actions/workflows/release.yml"><img src="https://github.com/jpoley/flowspec/actions/workflows/release.yml/badge.svg" alt="Release"/></a>
    <a href="https://hub.docker.com/r/jpoley/flowspec-agents"><img src="https://img.shields.io/docker/pulls/jpoley/flowspec-agents" alt="Docker Pulls"/></a>
    <a href="https://github.com/jpoley/flowspec/stargazers"><img src="https://img.shields.io/github/stars/jpoley/flowspec?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/jpoley/flowspec/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jpoley/flowspec" alt="License"/></a>
    <a href="https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec"><img src="https://api.scorecard.dev/projects/github.com/jpoley/flowspec/badge" alt="OpenSSF Scorecard"/></a>
</p>

---

## What is flowspec?

flowspec transforms how you build software with AI. Instead of giving AI loose instructions, you give it **structured specifications** and **tracked tasks**. Each `/flowspec` command launches specialized AI agents that:

1. **Read** existing specifications and tasks
2. **Create** the right artifacts for each phase
3. **Track** progress in your backlog
4. **Commit** with proper formatting and validation

## Quick Start

### Option A: Devcontainer 

Use the pre-built [`jpoley/flowspec-agents`](https://hub.docker.com/r/jpoley/flowspec-agents) Docker image with all AI coding assistants pre-installed:

```bash
# Copy devcontainer template to your project
mkdir -p .devcontainer
curl -o .devcontainer/devcontainer.json \
  https://raw.githubusercontent.com/jpoley/flowspec/main/templates/devcontainer/devcontainer.json
```

Open in VS Code → "Reopen in Container". The image includes:
- **Claude Code**, **Codex**, **Gemini CLI**, **GitHub Copilot CLI**
- Python 3.11, Node.js 20, pnpm, uv, backlog.md

### Option B: Local Installation

```bash
# Specify CLI (project initialization)
uv tool install flowspec-cli --from git+https://github.com/jpoley/flowspec.git

# Backlog.md (task management)
pnpm i -g backlog.md
```

### Initialize Your Project

```bash
flowspec init my-project --ai claude
cd my-project
backlog init "$(basename "$PWD")"
```

### Establish Principles (Optional but Recommended)

```bash
/flow:init   # Creates constitution with project principles
```

### Assess Your Feature

```bash
/flow:assess Build a REST API for task management with JWT authentication
```

### Run the Appropriate Workflow

**For Full SDD (complex features):**
```bash
/flow:specify Build a REST API for task management with JWT authentication
/flow:plan
/flow:implement
/flow:validate
/flow:operate
```

**For Light/Medium (medium features):**
```bash
/flow:specify Build a new user settings page
/flow:implement
```

**For Simple tasks:**
```bash
# Just create a task and implement
backlog task create "Fix login button alignment" --ac "Button aligns with form fields"
# Then code directly
```


## Choose Your Workflow Mode

```
┌────────────────────────────────────────────────────────────────────────┐
│                        WORKFLOW MODE SELECTION                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐              │
│  │   SIMPLE    │     │   MEDIUM    │     │   COMPLEX   │              │
│  │  (Score 8-12)│     │ (Score 13-20)│    │ (Score 21+) │              │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘              │
│         │                   │                   │                      │
│         ▼                   ▼                   ▼                      │
│    Skip SDD           Light/Medium            Full SDD                 │
│    Just code          Quick specs             All phases               │
│                                                                         │
│  Examples:            Examples:               Examples:                 │
│  • Bug fix            • New endpoint          • New auth system         │
│  • Config change      • UI component          • Payment integration     │
│  • Doc update         • Small feature         • Major refactor          │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Quick Decision: Run `/flow:assess` first

```bash
/flow:assess Build a REST API with user authentication
```

This scores your feature across 8 dimensions and recommends: **Skip SDD**, **Light/Medium**, or **Full SDD**.

## Workflow Modes Explained

All modes produce the same artifacts - only the **review depth** changes:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           WORKFLOW MODES                                 │
├───────────┬─────────────────────────┬───────────────────────────────────┤
│   MODE    │    ARTIFACTS PRODUCED   │         REVIEW APPROACH           │
├───────────┼─────────────────────────┼───────────────────────────────────┤
│   FULL    │ PRD                     │ Deep review at each stage         │
│           │ Functional Spec         │ Explicit approval gates           │
│           │ Technical Spec          │ Formal ADRs                       │
│           │ ADRs                    │ Multi-reviewer sign-off           │
│           │ Code + Tests            │                                   │
│           │ Runbook                 │                                   │
├───────────┼─────────────────────────┼───────────────────────────────────┤
│  MEDIUM   │ PRD                     │ Quick review                      │
│           │ Functional Spec         │ Proceed unless issues found       │
│           │ Technical Spec          │ Combined passes allowed           │
│           │ ADRs                    │ Single reviewer OK                │
│           │ Code + Tests            │                                   │
│           │ Runbook                 │                                   │
├───────────┼─────────────────────────┼───────────────────────────────────┤
│   LIGHT   │ PRD                     │ Minimal review                    │
│           │ Functional Spec         │ Trust the process                 │
│           │ Technical Spec          │ Decision notes (not full ADRs)    │
│           │ ADRs                    │ Fast iteration                    │
│           │ Code + Tests            │                                   │
│           │ Runbook                 │                                   │
└───────────┴─────────────────────────┴───────────────────────────────────┘

Light mode is NOT an excuse to skip artifacts. It's permission to move faster.
```

## The Workflow: Commands → Artifacts → States

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        FLOWSPEC WORKFLOW STATE MACHINE                          │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   COMMAND              STATE                ARTIFACTS PRODUCED                  │
│   ───────              ─────                ─────────────────                   │
│                                                                                 │
│   (start)          ┌──────────┐                                                │
│                    │  To Do   │            (none)                               │
│                    └────┬─────┘                                                 │
│                         │                                                       │
│                         ▼                                                       │
│   /flow:specify  ┌──────────┐            • [feature]-prd.md                   │
│                    │Specified │            • [feature]-functional.md            │
│                    └────┬─────┘                                                 │
│                         │                                                       │
│                         ▼                                                       │
│   /flow:research ┌──────────┐            • Research reports          OPTIONAL │
│   (optional)       │Researched│            • Competitive analysis               │
│                    └────┬─────┘                                                 │
│                         │                                                       │
│                         ▼                                                       │
│   /flow:plan     ┌──────────┐            • [feature]-technical.md             │
│                    │ Planned  │            • adr-XXX-[topic].md                 │
│                    └────┬─────┘            • Platform design docs               │
│                         │                                                       │
│                         ▼                                                       │
│   /flow:implement┌──────────┐            • Source code (src/)                 │
│                    │   In     │            • Unit & integration tests           │
│                    │Progress  │            • API documentation                  │
│                    └────┬─────┘                                                 │
│                         │                                                       │
│                         ▼                                                       │
│   /flow:validate ┌──────────┐            • QA reports                         │
│                    │Validated │            • Security scan results              │
│                    └────┬─────┘            • Test coverage reports              │
│                         │                                                       │
│                         ▼                                                       │
│   /flow:operate  ┌──────────┐            • [service]-runbook.md               │
│                    │Deployed  │            • Deployment configs                 │
│                    └────┬─────┘            • Monitoring dashboards              │
│                         │                                                       │
│                         ▼                                                       │
│                    ┌──────────┐                                                │
│                    │   Done   │                                                 │
│                    └──────────┘                                                 │
│                                                                                 │
└────────────────────────────────────────────────────────────────────────────────┘
```


## Command Reference

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           FLOWSPEC COMMAND REFERENCE                            │
├──────────────────┬───────────────┬────────────────┬────────────────────────────┤
│     COMMAND      │  INPUT STATE  │  OUTPUT STATE  │     PRIMARY AGENTS         │
├──────────────────┼───────────────┼────────────────┼────────────────────────────┤
│ /flow:assess   │ (any)         │ (no change)    │ Complexity Scorer          │
│ /flow:specify  │ To Do         │ Specified      │ PM Planner                 │
│ /flow:research │ Specified     │ Researched     │ Researcher, Validator      │
│ /flow:plan     │ Specified*    │ Planned        │ Architect, Platform Eng    │
│ /flow:implement│ Planned       │ In Progress    │ Frontend/Backend Engineers │
│ /flow:validate │ In Progress   │ Validated      │ QA, Security Engineers     │
│ /flow:operate  │ Validated     │ Deployed       │ SRE Agent                  │
└──────────────────┴───────────────┴────────────────┴────────────────────────────┘
* Also accepts "Researched" state
```

## Artifact Progression

Every feature follows this document progression:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          ARTIFACT PROGRESSION                                 │
│                                                                               │
│   PRD ──► Functional ──► Technical ──► ADR ──► Code ──► Runbook             │
│           Spec           Spec                                                 │
│                                                                               │
│   "What &    "What        "How to      "Why this   Actual    "How to         │
│    Why"      behaviors"    build"       path"      code      operate"        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Stage | Artifact | Question Answered | Location |
|-------|----------|-------------------|----------|
| 1 | **PRD** | What must it do and why the user cares | `docs/prd/` |
| 2 | **Functional Spec** | What behaviors are required | `docs/specs/` |
| 3 | **Technical Spec** | How will we build it | `docs/specs/` |
| 4 | **ADR** | Why we chose this technical path | `docs/adr/` |
| 5 | **Implementation** | The code itself | `src/` |
| 6 | **Runbook** | How to operate and troubleshoot | `docs/runbooks/` |

### Document Naming

| Document | Pattern | Example |
|----------|---------|---------|
| PRD | `[feature]-prd.md` | `user-auth-prd.md` |
| Functional Spec | `[feature]-functional.md` | `user-auth-functional.md` |
| Technical Spec | `[feature]-technical.md` | `user-auth-technical.md` |
| ADR | `adr-[number]-[topic].md` | `adr-015-auth-provider.md` |
| Runbook | `[service]-runbook.md` | `auth-service-runbook.md` |

## Working with Tasks

```bash
# View kanban board
backlog board

# List tasks (AI-friendly)
backlog task list --plain

# Start work on a task
backlog task edit 42 -s "In Progress" -a @myself

# Check off acceptance criteria as you work
backlog task edit 42 --check-ac 1
backlog task edit 42 --check-ac 2

# Complete task
backlog task edit 42 -s Done
```

## Implementation = Code + Docs + Tests

Every `/flow:implement` produces **three mandatory deliverables**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION DELIVERABLES                           │
├─────────────────┬─────────────────────┬─────────────────────────────────┤
│   DELIVERABLE   │    DESCRIPTION      │        VERIFICATION             │
├─────────────────┼─────────────────────┼─────────────────────────────────┤
│   Code          │ Production-ready    │ PR passes CI, review approved   │
│                 │ reviewed source     │                                 │
├─────────────────┼─────────────────────┼─────────────────────────────────┤
│   Documents     │ API docs, comments  │ Docs updated, comments added    │
│                 │ config examples     │                                 │
├─────────────────┼─────────────────────┼─────────────────────────────────┤
│   Tests         │ Unit, integration   │ Test suite passes               │
│                 │ edge cases          │ Coverage threshold met          │
└─────────────────┴─────────────────────┴─────────────────────────────────┘

Implementation is NOT complete until all three are delivered.
```

## Supported AI Agents

| Agent | Support | Included in Devcontainer |
|-------|---------|--------------------------|
| [Claude Code](https://www.anthropic.com/claude-code) | Fully supported (primary) | ✅ |
| [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli/) | Fully supported | ✅ |
| [Codex CLI](https://github.com/openai/codex) | Fully supported | ✅ |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Fully supported | ✅ |
| [Cursor](https://cursor.sh/) | Fully supported | - |
| [Windsurf](https://windsurf.com/) | Fully supported | - |

### Devcontainer: All AI Agents Pre-Installed

The [`jpoley/flowspec-agents`](https://hub.docker.com/r/jpoley/flowspec-agents) Docker image provides a ready-to-use development environment with Claude Code, Codex, Gemini CLI, and GitHub Copilot CLI pre-installed. See [Quick Start](#quick-start) for setup instructions.

### Multi-Agent Setup

```bash
# Initialize with multiple agents
flowspec init my-project --ai claude,copilot,cursor-agent
```

## File Structure

```
project/
├── .devcontainer/              # Devcontainer configuration
│   └── devcontainer.json       # Uses jpoley/flowspec-agents image
├── docs/
│   ├── prd/                    # PRDs from /flow:specify
│   ├── specs/                  # Functional & Technical specs
│   ├── adr/                    # Architecture Decision Records
│   ├── platform/               # Platform design docs
│   ├── qa/                     # QA reports from /flow:validate
│   ├── security/               # Security scans
│   └── runbooks/               # Operational runbooks
├── src/                        # Implementation code
├── tests/                      # Test suites
├── backlog/                    # Task management
└── memory/                     # Constitution and specs
    └── constitution.md         # Project principles
```

## Documentation

### Getting Started
- **[Backlog Quick Start](docs/guides/backlog-quickstart.md)** - 5-minute intro
- **[Problem Sizing Assessment](docs/guides/problem-sizing-assessment.md)** - When to use SDD
- **[Devcontainer Template](templates/devcontainer/README.md)** - Devcontainer setup guide

### Workflow Details
- **[Flowspec Workflow Diagram](docs/diagrams/flowspec-workflow.md)** - Full visual workflow
- **[Flowspec + Backlog Integration](docs/guides/flowspec-backlog-workflow.md)** - How commands integrate
- **[Agent Loop Classification](docs/reference/agent-loop-classification.md)** - Which agents for which phases

### Reference
- **[Backlog User Guide](docs/guides/backlog-user-guide.md)** - Complete task management
- **[Inner Loop Reference](docs/reference/inner-loop.md)** - Development cycle
- **[Outer Loop Reference](docs/reference/outer-loop.md)** - CI/CD and deployment
- **[Docker Hub Architecture](docs/platform/dockerhub-devcontainer-architecture.md)** - flowspec-agents image details

## Legacy /speckit Commands

The original `/speckit.*` commands are available for standalone specification work but **do not integrate with backlog.md**. Use `/flow:*` commands for the fully integrated workflow with task tracking.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. All commits require DCO sign-off:

```bash
git commit -s -m "feat: your feature"
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">
    <p><em>Built on <a href="https://github.com/github/spec-kit">GitHub's spec-kit</a> | Powered by <a href="https://github.com/MrLesk/Backlog.md">Backlog.md</a> | Docker: <a href="https://hub.docker.com/r/jpoley/flowspec-agents">jpoley/flowspec-agents</a></em></p>
</div>
