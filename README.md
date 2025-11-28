<div align="center">
    <img src="./images/jp-spec-kit.jpeg"/>
    <h1>JP Spec Kit</h1>
    <h3><em>Spec-Driven Development meets AI-Powered Task Management</em></h3>
</div>

<p align="center">
    <strong>Unify your planning and execution workflow. Define specs, generate tasks, track progress - all in one seamless system.</strong>
</p>

<p align="center">
    <a href="https://github.com/jpoley/jp-spec-kit/actions/workflows/release.yml"><img src="https://github.com/jpoley/jp-spec-kit/actions/workflows/release.yml/badge.svg" alt="Release"/></a>
    <a href="https://github.com/jpoley/jp-spec-kit/stargazers"><img src="https://img.shields.io/github/stars/jpoley/jp-spec-kit?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/jpoley/jp-spec-kit/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jpoley/jp-spec-kit" alt="License"/></a>
</p>

---

## What is JP Spec Kit?

JP Spec Kit brings together two powerful ideas:

1. **Spec-Driven Development** (from [GitHub's spec-kit](https://github.com/github/spec-kit)) - Transform requirements into executable specifications, plans, and tasks
2. **Backlog.md** - AI-powered task management with visual Kanban boards, MCP integration, and git-native tracking

The result: a unified workflow where **specs generate tasks that flow directly into a managed backlog**, trackable via CLI, web UI, or AI assistants.

```
Requirements → Spec → Plan → Tasks → Backlog.md
     ↓          ↓      ↓       ↓         ↓
   /specify  /plan  /tasks  generate  → board, browser, AI
```

## Quick Start
(assuuming you have uv and pnpm installed)

### 1. Install

```bash
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git && pnpm i -g backlog.md
```

### 2. Initialize a Project

```bash
specify init my-project --ai claude
cd my-project
backlog init `basename "$PWD"`
```

### 3. Define What You Want to Build

```bash
/speckit.specify Build a REST API for task management with user authentication
```

### 4. Create a Technical Plan

```bash
/speckit.plan Use FastAPI with PostgreSQL, JWT auth, and Docker deployment
```

### 5. Generate Tasks

```bash
/speckit.tasks
```

Tasks are automatically created in Backlog.md format, ready for tracking.

### 6. Track Progress

```bash
# Terminal Kanban board
backlog board

# Web UI
backlog browser

# Or ask your AI assistant
"Show me all tasks labeled backend"
```

## The Workflow

### From Spec to Done

| Phase | Command | Output |
|-------|---------|--------|
| **Define** | `/speckit.specify` | `spec.md` - User stories and requirements |
| **Plan** | `/speckit.plan` | `plan.md` - Technical architecture |
| **Break Down** | `/speckit.tasks` | `backlog/tasks/` - Individual task files |
| **Execute** | `/speckit.implement` | Working code |
| **Track** | `backlog board` | Visual progress |

### Task Management with Backlog.md

Once tasks are generated, you have multiple ways to manage them:

**CLI**
```bash
backlog task list --plain           # List all tasks
backlog task edit 1 -s "In Progress" # Update status
backlog overview                     # Project stats
```

**AI Assistant (via MCP)**
```
"Create a task for implementing user registration"
"Mark task-5 as done"
"What tasks are blocking the auth feature?"
```

**Web UI**
```bash
backlog browser   # Opens Kanban board in browser
```

## Installation Options

### Persistent Install (Recommended)

```bash
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git
```

### One-time Run

```bash
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init my-project
```

### Upgrade

```bash
uv tool install specify-cli --force --from git+https://github.com/jpoley/jp-spec-kit.git
```

## Architecture

JP Spec Kit is a **layered extension** of GitHub's spec-kit:

```
┌─────────────────────────────────────────┐
│  Your Project                           │
│  ┌───────────────────────────────────┐  │
│  │ JP Spec Kit (Layer 2)            │  │
│  │ • Backlog.md integration          │  │
│  │ • Multi-language expertise        │  │
│  │ • Advanced agent workflows        │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ Base Spec Kit (Layer 1)          │  │
│  │ • /speckit.* commands             │  │
│  │ • Core templates                  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Extension overrides base** where conflicts exist. Upgrade both with `specify upgrade`.

## Supported AI Agents

| Agent | Support |
|-------|---------|
| [Claude Code](https://www.anthropic.com/claude-code) | Fully supported |
| [GitHub Copilot](https://code.visualstudio.com/) | Fully supported |
| [Cursor](https://cursor.sh/) | Fully supported |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Fully supported |
| [Codex CLI](https://github.com/openai/codex) | Fully supported |
| [Windsurf](https://windsurf.com/) | Fully supported |

[See all supported agents →](docs/installation.md)

## Commands Reference

### Specify CLI

| Command | Description |
|---------|-------------|
| `specify init <name>` | Initialize new project |
| `specify upgrade` | Upgrade to latest versions |
| `specify check` | Verify tool installation |
| `specify backlog migrate` | Convert tasks.md to Backlog.md format |

### Slash Commands

| Command | Description |
|---------|-------------|
| `/speckit.specify` | Define requirements and user stories |
| `/speckit.plan` | Create technical implementation plan |
| `/speckit.tasks` | Generate actionable task breakdown |
| `/speckit.implement` | Execute implementation |
| `/speckit.clarify` | Clarify underspecified areas |
| `/jpspec:assess` | Evaluate feature complexity and recommend workflow (Full SDD / Spec-light / Skip SDD) |

## Documentation

- **[Spec-Driven Development Guide](spec-driven.md)** - Complete methodology
- **[Problem Sizing Assessment Guide](docs/guides/problem-sizing-assessment.md)** - When to use SDD vs traditional development
- **[Backlog.md Quick Start](docs/guides/backlog-quickstart.md)** - Get started in 5 minutes
- **[Backlog.md User Guide](docs/guides/backlog-user-guide.md)** - Full task management docs
- **[Migration Guide](docs/guides/backlog-migration.md)** - Convert from tasks.md
- **[Architecture Details](docs/architecture/LAYERED-EXTENSION-ARCHITECTURE.md)** - How layering works

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** for package management
- **Git**
- A [supported AI coding agent](#supported-ai-agents)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">
    <p><em>Built on <a href="https://github.com/github/spec-kit">GitHub's spec-kit</a> • Powered by <a href="https://github.com/MrLesk/Backlog.md">Backlog.md</a></em></p>
</div>
