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

JP Spec Kit transforms how you build software with AI. Instead of giving AI loose instructions, you give it **structured specifications** and **tracked tasks**. Each `/jpspec` command launches specialized AI agents that:

1. **Read** existing specifications and tasks
2. **Create** the right artifacts for each phase
3. **Track** progress in your backlog
4. **Commit** with proper formatting and validation

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

### Quick Decision: Run `/jpspec:assess` first

```bash
/jpspec:assess Build a REST API with user authentication
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
│                         /JPSPEC WORKFLOW STATE MACHINE                          │
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
│   /jpspec:specify  ┌──────────┐            • [feature]-prd.md                   │
│                    │Specified │            • [feature]-functional.md            │
│                    └────┬─────┘                                                 │
│                         │                                                       │
│                         ▼                                                       │
│   /jpspec:research ┌──────────┐            • Research reports          OPTIONAL │
│   (optional)       │Researched│            • Competitive analysis               │
│                    └────┬─────┘                                                 │
│                         │                                                       │
│                         ▼                                                       │
│   /jpspec:plan     ┌──────────┐            • [feature]-technical.md             │
│                    │ Planned  │            • adr-XXX-[topic].md                 │
│                    └────┬─────┘            • Platform design docs               │
│                         │                                                       │
│                         ▼                                                       │
│   /jpspec:implement┌──────────┐            • Source code (src/)                 │
│                    │   In     │            • Unit & integration tests           │
│                    │Progress  │            • API documentation                  │
│                    └────┬─────┘                                                 │
│                         │                                                       │
│                         ▼                                                       │
│   /jpspec:validate ┌──────────┐            • QA reports                         │
│                    │Validated │            • Security scan results              │
│                    └────┬─────┘            • Test coverage reports              │
│                         │                                                       │
│                         ▼                                                       │
│   /jpspec:operate  ┌──────────┐            • [service]-runbook.md               │
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

## Quick Start

### 1. Install the Tools

```bash
# Specify CLI (project initialization)
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git

# Backlog.md (task management)
pnpm i -g backlog.md
```

### 2. Initialize Your Project

```bash
specify init my-project --ai claude
cd my-project
backlog init "$(basename "$PWD")"
```

### 3. Establish Principles (Optional but Recommended)

```bash
/speckit:constitution Create principles focused on code quality, testing, and user experience.
```

### 4. Assess Your Feature

```bash
/jpspec:assess Build a REST API for task management with JWT authentication
```

### 5. Run the Appropriate Workflow

**For Full SDD (complex features):**
```bash
/jpspec:specify Build a REST API for task management with JWT authentication
/jpspec:plan
/jpspec:implement
/jpspec:validate
/jpspec:operate
```

**For Light/Medium (medium features):**
```bash
/jpspec:specify Build a new user settings page
/jpspec:implement
```

**For Simple tasks:**
```bash
# Just create a task and implement
backlog task create "Fix login button alignment" --ac "Button aligns with form fields"
# Then code directly
```

## Command Reference

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                            /JPSPEC COMMAND REFERENCE                            │
├──────────────────┬───────────────┬────────────────┬────────────────────────────┤
│     COMMAND      │  INPUT STATE  │  OUTPUT STATE  │     PRIMARY AGENTS         │
├──────────────────┼───────────────┼────────────────┼────────────────────────────┤
│ /jpspec:assess   │ (any)         │ (no change)    │ Complexity Scorer          │
│ /jpspec:specify  │ To Do         │ Specified      │ PM Planner                 │
│ /jpspec:research │ Specified     │ Researched     │ Researcher, Validator      │
│ /jpspec:plan     │ Specified*    │ Planned        │ Architect, Platform Eng    │
│ /jpspec:implement│ Planned       │ In Progress    │ Frontend/Backend Engineers │
│ /jpspec:validate │ In Progress   │ Validated      │ QA, Security Engineers     │
│ /jpspec:operate  │ Validated     │ Deployed       │ SRE Agent                  │
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

Every `/jpspec:implement` produces **three mandatory deliverables**:

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

| Agent | Support |
|-------|---------|
| [Claude Code](https://www.anthropic.com/claude-code) | Fully supported (primary) |
| [GitHub Copilot](https://code.visualstudio.com/) | Fully supported |
| [Cursor](https://cursor.sh/) | Fully supported |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | Fully supported |
| [Codex CLI](https://github.com/openai/codex) | Fully supported |
| [Windsurf](https://windsurf.com/) | Fully supported |

### Multi-Agent Setup

```bash
# Initialize with multiple agents
specify init my-project --ai claude,copilot,cursor-agent
```

## File Structure

```
project/
├── docs/
│   ├── prd/                    # PRDs from /jpspec:specify
│   ├── specs/                  # Functional & Technical specs
│   ├── adr/                    # Architecture Decision Records
│   ├── platform/               # Platform design docs
│   ├── qa/                     # QA reports from /jpspec:validate
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

### Workflow Details
- **[JP Spec Workflow Diagram](docs/diagrams/jpspec-workflow.md)** - Full visual workflow
- **[JP Spec + Backlog Integration](docs/guides/jpspec-backlog-workflow.md)** - How commands integrate
- **[Agent Loop Classification](docs/reference/agent-loop-classification.md)** - Which agents for which phases

### Reference
- **[Backlog User Guide](docs/guides/backlog-user-guide.md)** - Complete task management
- **[Inner Loop Reference](docs/reference/inner-loop.md)** - Development cycle
- **[Outer Loop Reference](docs/reference/outer-loop.md)** - CI/CD and deployment

## Legacy /speckit Commands

The original `/speckit.*` commands from [GitHub's spec-kit](https://github.com/github/spec-kit) are available but **do not integrate with backlog.md**. Use `/jpspec` commands for the integrated workflow.

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
