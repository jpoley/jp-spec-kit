<div align="center">
    <img src="./images/jp-spec-kit.jpeg"/>
    <h1>JP Spec Kit</h1>
    <h3><em>Spec-Driven Development with AI-Powered Task Management</em></h3>
</div>

<p align="center">
    <strong>Plan features with specialized AI agents. Track progress in backlog.md. Ship with confidence.</strong>
</p>

<p align="center">
    <a href="https://github.com/jpoley/jp-spec-kit/actions/workflows/release.yml"><img src="https://github.com/jpoley/jp-spec-kit/actions/workflows/release.yml/badge.svg" alt="Release"/></a>
    <a href="https://github.com/jpoley/jp-spec-kit/stargazers"><img src="https://img.shields.io/github/stars/jpoley/jp-spec-kit?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/jpoley/jp-spec-kit/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jpoley/jp-spec-kit" alt="License"/></a>
</p>

---

## What is JP Spec Kit?

JP Spec Kit combines **Spec-Driven Development** with **[Backlog.md](https://github.com/MrLesk/Backlog.md)** task management through a suite of AI-powered slash commands. Each command launches specialized agents (PM planners, architects, engineers, SREs) that create and track tasks in your backlog.

**The key insight**: AI agents work from backlog tasks, not loose instructions. Every `/jpspec` command discovers existing tasks, creates new ones with acceptance criteria, and tracks progress through the backlog CLI.

## Quick Start

```bash
# Install the tools
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git
pnpm i -g backlog.md

# Initialize a project
specify init my-project --ai claude
cd my-project
backlog init "$(basename "$PWD")"

# Establish the principles

/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements.  Only Humans merge PRs.

# Assess complexity first (optional but recommended)
/jpspec:assess Build a REST API with authentication

# Create specification with tasks
/jpspec:specify Build a REST API for task management with JWT authentication

# View and work on tasks
backlog board
backlog task list --plain
```

## The /jpspec Workflow

The `/jpspec` commands form a complete development lifecycle, each backed by specialized AI agents:

```
/jpspec:assess   →  Is SDD appropriate? (Full/Light/Skip)
       ↓
/jpspec:specify  →  PRD + backlog tasks (PM Planner agent)
       ↓
/jpspec:research →  Market & technical validation (Researcher + Business Validator)
       ↓
/jpspec:plan     →  Architecture + infrastructure design (Architect + Platform Engineer)
       ↓
/jpspec:implement → Code with review (Frontend/Backend Engineers + Code Reviewers)
       ↓
/jpspec:validate →  QA, security, docs, release (Multiple validation agents)
       ↓
/jpspec:operate  →  CI/CD, K8s, observability (SRE agent)
```

### Command Reference

| Command | Purpose | Subagents | Execution |
|---------|---------|-----------|-----------|
| `/jpspec:assess` | Evaluate feature complexity (8-question scoring) | Interactive | Single |
| `/jpspec:specify` | Create PRD with implementation tasks | Product Requirements Manager | Single |
| `/jpspec:research` | Market research + business validation | Research Analyst → Business Validator | Sequential |
| `/jpspec:plan` | System architecture + platform design | Software Architect + Platform Engineer | Parallel |
| `/jpspec:implement` | Implementation with code review | Frontend/Backend/ML Engineers + Code Reviewers | Multi-phase |
| `/jpspec:validate` | QA, security, docs, release readiness | Quality Guardian + Security Engineer → Tech Writer → Release Manager | Multi-phase |
| `/jpspec:operate` | CI/CD, Kubernetes, observability setup | Site Reliability Engineer | Single |
| `/jpspec:prune-branch` | Clean up merged local branches | — | Utility |

See **[JP Spec Workflow Diagram](docs/diagrams/jpspec-workflow.md)** for the complete visual workflow with all 15 specialized agents.

### Subagent Details

<details>
<summary><strong>/jpspec:specify</strong> — 1 agent</summary>

- **Product Requirements Manager** (SVPG Principles Expert)
  - Creates comprehensive PRD with user stories
  - Applies DVF+V risk framework (Desirability, Usability, Feasibility, Viability)
  - Creates backlog tasks with acceptance criteria
</details>

<details>
<summary><strong>/jpspec:plan</strong> — 2 agents (parallel)</summary>

- **Software Architect** (Hohpe's Principles Expert)
  - System architecture and component design
  - Enterprise Integration Patterns
  - Architecture Decision Records (ADRs)

- **Platform Engineer** (DevSecOps & CI/CD Excellence)
  - DORA metrics optimization
  - CI/CD pipeline architecture
  - Infrastructure and observability design
</details>

<details>
<summary><strong>/jpspec:research</strong> — 2 agents (sequential)</summary>

1. **Senior Research Analyst**
   - Market intelligence (TAM/SAM/SOM)
   - Competitive analysis
   - Technical feasibility assessment

2. **Business Analyst & Strategic Advisor**
   - Financial viability analysis
   - Go/No-Go recommendation
   - Risk assessment with mitigations
</details>

<details>
<summary><strong>/jpspec:implement</strong> — 3-5 agents (multi-phase)</summary>

**Phase 1 — Implementation (parallel):**
- **Frontend Engineer** (React/React Native, TypeScript)
- **Backend Engineer** (Go, TypeScript/Node.js, Python)
- **AI/ML Engineer** (MLOps, model deployment) — conditional

**Phase 2 — Code Review (sequential):**
- **Frontend Code Reviewer** (Principal Engineer)
- **Backend Code Reviewer** (Principal Engineer)
</details>

<details>
<summary><strong>/jpspec:validate</strong> — 4 agents (multi-phase with human gate)</summary>

**Phase 1 — Testing (parallel):**
- **Quality Guardian** (QA, risk analysis, failure modes)
- **Secure-by-Design Engineer** (security assessment, threat modeling)

**Phase 2 — Documentation (sequential):**
- **Technical Writer** (API docs, user guides, release notes)

**Phase 3 — Release (sequential with human approval):**
- **Release Manager** (deployment coordination)
- **Human Approval Gate** — manual checkpoint required
</details>

<details>
<summary><strong>/jpspec:operate</strong> — 1 agent</summary>

- **Site Reliability Engineer** (SRE)
  - CI/CD pipelines (GitHub Actions)
  - Kubernetes deployment manifests
  - Observability stack (metrics, logs, traces)
  - SLI/SLO definitions
  - Runbooks and incident response
</details>

### Backlog Integration

Every `/jpspec` command:
1. **Discovers** existing tasks: `backlog search "<feature>" --plain`
2. **Creates** tasks with acceptance criteria via CLI
3. **Assigns** agent identity (e.g., `@pm-planner`, `@sre-agent`)
4. **Tracks** progress by checking ACs: `backlog task edit <id> --check-ac 1`
5. **Marks** tasks done only when Definition of Done is met

## Complexity Assessment

Not every feature needs full SDD. Use `/jpspec:assess` first:

| Score | Classification | Recommendation |
|-------|----------------|----------------|
| 8-12 | Simple | **Skip SDD** - Just create a task and implement |
| 13-20 | Medium | **Spec-Light** - Use `/jpspec:specify` + `/jpspec:implement` |
| 21-32 | Complex | **Full SDD** - Use all `/jpspec` phases |

## Working with Tasks

```bash
# View kanban board
backlog board

# List tasks (AI-friendly output)
backlog task list --plain
backlog task list -s "To Do" --plain

# Search for tasks
backlog search "authentication" --plain

# View task details
backlog task 42 --plain

# Start work on a task
backlog task edit 42 -s "In Progress" -a @myself

# Check off acceptance criteria as you work
backlog task edit 42 --check-ac 1
backlog task edit 42 --check-ac 2

# Add implementation notes
backlog task edit 42 --notes $'Implemented JWT auth using jose library\n\nChanges:\n- Added auth middleware\n- Created token service'

# Complete task
backlog task edit 42 -s Done
```

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for Python package management
- Node.js 18+ with pnpm
- Git
- A supported AI coding agent

### Install Both Tools

```bash
# Specify CLI (project initialization)
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git

# Backlog.md (task management)
pnpm i -g backlog.md
```

### Upgrade

```bash
uv tool install specify-cli --force --from git+https://github.com/jpoley/jp-spec-kit.git
pnpm update -g backlog.md
```

## Supported AI Agents

| Agent | Support |
|-------|---------|
| [Claude Code](https://www.anthropic.com/claude-code) | Fully supported (primary) |
| [GitHub Copilot](https://code.visualstudio.com/) | Fully supported |
| [Cursor](https://cursor.sh/) | Fully supported |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Fully supported |
| [Codex CLI](https://github.com/openai/codex) | Fully supported |
| [Windsurf](https://windsurf.com/) | Fully supported |

### Multi-Agent Support

Initialize with multiple agents for teams using different tools:

```bash
# Interactive selection
specify init my-project

# Multiple agents via CLI
specify init my-project --ai claude,copilot,cursor-agent
```

## Specify CLI Commands

| Command | Description |
|---------|-------------|
| `specify init <name>` | Initialize new project with SDD templates |
| `specify upgrade` | Upgrade to latest template versions |
| `specify check` | Verify tool installation |
| `specify backlog migrate` | Convert legacy tasks.md to backlog.md format |

## Documentation

### Workflow & Architecture
- **[JP Spec Workflow Diagram](docs/diagrams/jpspec-workflow.md)** - Visual workflow with all 15 subagents
- **[Agent Loop Classification](docs/reference/agent-loop-classification.md)** - Which agents for which phases
- **[Inner Loop Reference](docs/reference/inner-loop.md)** - Development cycle details
- **[Outer Loop Reference](docs/reference/outer-loop.md)** - CI/CD and deployment

### Task Management
- **[Backlog Quick Start](docs/guides/backlog-quickstart.md)** - Get started in 5 minutes
- **[Backlog User Guide](docs/guides/backlog-user-guide.md)** - Complete task management guide
- **[JP Spec + Backlog Integration](docs/guides/jpspec-backlog-workflow.md)** - How /jpspec commands integrate with backlog.md

### Guides
- **[Problem Sizing Assessment](docs/guides/problem-sizing-assessment.md)** - When to use SDD

## Legacy /speckit Commands

The original `/speckit.*` commands from [GitHub's spec-kit](https://github.com/github/spec-kit) are still available but **do not integrate with backlog.md**:

| Command | Status |
|---------|--------|
| `/speckit:specify` | Available (no backlog integration) |
| `/speckit:plan` | Available (no backlog integration) |
| `/speckit:tasks` | Available (generates tasks.md, not backlog) |
| `/speckit:implement` | Available (no backlog integration) |
| `/speckit:clarify` | Available (no backlog integration) |
| `/speckit:constitution` | Available (no backlog integration) |
| `/speckit:checklist` | Available (no backlog integration) |
| `/speckit:analyze` | Available (no backlog integration) |

**Recommendation**: Use `/jpspec` commands for the integrated backlog workflow. Use `/speckit` commands only if you prefer the traditional tasks.md approach.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. All commits require DCO sign-off:

```bash
git commit -s -m "feat: your feature"
```

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">
    <p><em>Built on <a href="https://github.com/github/spec-kit">GitHub's spec-kit</a> | Powered by <a href="https://github.com/MrLesk/Backlog.md">Backlog.md</a></em></p>
</div>
