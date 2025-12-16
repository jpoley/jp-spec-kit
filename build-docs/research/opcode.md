# Opcode Deep Review: Comparison with Flowspec

> **Repository**: https://github.com/winfunc/opcode
> **Review Date**: 2025-12-12
> **Reviewed By**: Claude (automated analysis)

## Executive Summary

**Opcode** and **Flowspec** are both Claude Code enhancement tools, but they solve fundamentally different problems:

| Aspect | Opcode | Flowspec |
|--------|--------|----------|
| **Core Problem** | Claude Code needs a GUI | Claude Code needs structured workflows |
| **Form Factor** | Desktop app (Tauri) | CLI toolkit + templates |
| **User Type** | Individual developers | Teams following SDLC |
| **Interaction Model** | Visual, point-and-click | Command-driven, workflow-based |
| **Session Model** | Session management & replay | Task/backlog management |

**Blunt Assessment**: These tools don't compete - they're complementary. Opcode wraps Claude Code with a UI. Flowspec orchestrates Claude Code through a development lifecycle. A developer could reasonably use both.

---

## Opcode: What It Is

### Core Architecture

Opcode is a **Tauri 2** desktop application:
- **Backend**: Rust (~3,500 LOC across commands, checkpoint, process management)
- **Frontend**: React 18 + TypeScript + Vite 6
- **UI**: Tailwind CSS v4 + shadcn/ui
- **Database**: SQLite (via rusqlite) for agent/session storage
- **Package Manager**: Bun

The application wraps the Claude Code CLI binary, spawning it as a subprocess and streaming output via Tauri's event system.

### Key Features

#### 1. Project & Session Management
```
~/.claude/projects/  →  Visual browser
├── project-encoded-path/
│   ├── session-uuid.jsonl  →  Session history viewer
│   └── ...
```
- Browse all Claude Code sessions visually
- View first message previews and timestamps
- Resume past sessions with full context

#### 2. CC Agents (Custom Agents)
```json
{
  "agent": {
    "name": "Security Scanner",
    "icon": "shield",
    "model": "opus",
    "system_prompt": "...",
    "default_task": "Review the codebase for security issues."
  }
}
```
- Create agents with custom system prompts
- Store in SQLite, export as `.opcode.json`
- Import from GitHub or local files
- Run agents in background processes
- Track execution history with metrics

#### 3. Usage Analytics Dashboard
```rust
// From src-tauri/src/commands/usage.rs
const OPUS_4_INPUT_PRICE: f64 = 15.0;   // per million tokens
const OPUS_4_OUTPUT_PRICE: f64 = 75.0;
const SONNET_4_INPUT_PRICE: f64 = 3.0;
const SONNET_4_OUTPUT_PRICE: f64 = 15.0;
```
- Real-time cost tracking by model, project, date
- Token breakdown (input, output, cache creation, cache read)
- Export data for accounting

#### 4. Timeline & Checkpoints
```rust
pub struct CheckpointManager {
    project_id: String,
    session_id: String,
    project_path: PathBuf,
    file_tracker: Arc<RwLock<FileTracker>>,
    storage: Arc<CheckpointStorage>,
    timeline: Arc<RwLock<SessionTimeline>>,
    current_messages: Arc<RwLock<Vec<String>>>,
}
```
- Create checkpoints at any point in session
- Visual timeline with branching support
- Restore to any checkpoint (code + session state)
- Fork sessions from checkpoints
- Diff viewer between checkpoints
- Auto-checkpoint strategies (manual, per-prompt, per-tool-use, smart)

#### 5. MCP Server Management
- Central UI for Model Context Protocol servers
- Add servers via UI or import from Claude Desktop
- Connection testing
- Per-project server configuration

#### 6. CLAUDE.md Editor
- Built-in markdown editor with live preview
- Find all CLAUDE.md files in project tree
- Syntax highlighting

#### 7. Web Server Mode
```
┌─────────────────┐    WebSocket     ┌─────────────────┐
│   Browser UI    │ ←──────────────→ │  Rust Backend   │
│                 │    REST API      │   (Axum Server) │
└─────────────────┘                  └─────────────────┘
```
- Access Claude Code from mobile/browser
- WebSocket streaming for real-time output
- **Status**: Functional but incomplete (session isolation issues)

---

## Flowspec: What It Is

### Core Architecture

Flowspec is a **CLI toolkit** for Spec-Driven Development:
- **CLI**: Python (`flowspec-cli` package via uv)
- **Templates**: Markdown templates for artifacts
- **Configuration**: YAML-based workflow definitions
- **Integration**: backlog.md MCP server for task management
- **Skills**: 17 Claude skills (5 core workflow + 12 security)

### Key Features

#### 1. Structured Workflow Commands
```bash
/flow:assess    # Evaluate SDD workflow suitability
/flow:specify   # Create/update feature specs
/flow:research  # Research and validation
/flow:plan      # Architecture planning
/flow:implement # Implementation with code review
/flow:validate  # QA, security, docs validation
/flow:operate   # SRE operations
```

#### 2. Workflow State Machine
```yaml
# flowspec_workflow.yml
workflows:
  implement:
    command: "/flow:implement"
    agents:
      - frontend-engineer
      - backend-engineer
    input_states: ["Planned"]
    output_state: "In Implementation"
```
- Tasks progress through defined states
- Commands validate state prerequisites
- Transitions create documented artifacts

#### 3. Engineering Subagents
```
.claude/agents/
├── backend-engineer.md    # Python, APIs, databases
├── frontend-engineer.md   # React, TypeScript, accessibility
├── qa-engineer.md         # Test pyramid, coverage
└── security-reviewer.md   # OWASP, SLSA, threat modeling
```
- Specialized agent definitions in markdown
- Auto-invoked based on task labels
- Read-only security reviewer

#### 4. Skills System
```
.claude/skills/
├── architect/           # ADRs, system design
├── pm-planner/          # Task decomposition
├── qa-validator/        # Test planning
├── security-reviewer/   # Vulnerability assessment
├── security-fixer/      # Patch generation
├── security-reporter/   # Audit reports
└── ... (17 total)
```
- Model-invoked skills for specific tasks
- Security-focused skills (triage, CodeQL, DAST, custom rules)

#### 5. Backlog Integration
```bash
backlog task list --plain        # AI-friendly output
backlog task edit 42 -s "In Progress"
backlog task edit 42 --check-ac 1  # Mark acceptance criterion
```
- MCP server for task management
- Tasks have acceptance criteria
- State transitions tracked

#### 6. Documentation Artifact Generation
```
docs/
├── assess/     # Assessment reports
├── prd/        # Product Requirements Documents
├── research/   # Research reports
├── adr/        # Architecture Decision Records
├── platform/   # Platform design docs
├── qa/         # QA reports
└── security/   # Security reports
```

---

## Head-to-Head Comparison

### What Opcode Does That Flowspec Doesn't

| Feature | Opcode | Flowspec Gap |
|---------|--------|--------------|
| **GUI Interface** | Full desktop app | Terminal-only |
| **Session Browser** | Visual project/session navigation | No session management UI |
| **Cost Tracking** | Real-time usage dashboard | No cost tracking |
| **Checkpoint/Timeline** | Full versioning system | No checkpoint system |
| **MCP Management UI** | Visual server management | Manual JSON editing |
| **CLAUDE.md Editor** | Built-in with preview | External editor required |
| **Agent Execution Metrics** | Duration, tokens, cost per run | No execution metrics |
| **Mobile Access** | Web server mode | Terminal only |
| **Process Registry** | Track/kill running processes | No process management |

### What Opcode Does Better

#### 1. User Experience
Opcode provides immediate visual feedback. You see:
- All your projects at a glance
- Session history with previews
- Real-time streaming output
- Cost accumulation as you work

Flowspec requires terminal fluency and command memorization.

#### 2. Session Management
```rust
// Opcode's session resumption
pub async fn resume_claude_code(
    session_id: String,
    prompt: String,
    model: String,
) -> Result<(), String>
```
Opcode makes session resumption trivial - click a session, you're back in context. Flowspec has no session concept.

#### 3. Checkpoint System
```rust
pub struct FileSnapshot {
    checkpoint_id: String,
    file_path: PathBuf,
    content: String,
    hash: String,
    is_deleted: bool,
    permissions: Option<u32>,
    size: u64,
}
```
Opcode's checkpoint system captures:
- Full file state (content, hash, permissions)
- Session messages at checkpoint time
- Ability to restore and fork

Flowspec has no equivalent - you'd use git manually.

#### 4. Cost Visibility
```rust
// Real-time cost calculation
fn calculate_cost(model: &str, usage: &UsageData) -> f64 {
    // Accurate per-model pricing
    let (input_price, output_price, cache_write_price, cache_read_price) =
        if model.contains("opus-4") { ... }
}
```
Developers often don't realize how much they're spending. Opcode surfaces this immediately.

#### 5. CC Agents (Quick Custom Agents)
```json
{
  "system_prompt": "You are a security scanner...",
  "default_task": "Review the codebase for security issues.",
  "model": "opus"
}
```
Creating a custom agent in Opcode takes 30 seconds. In Flowspec, you'd:
1. Create a skill file
2. Register it in CLAUDE.md
3. Create a slash command to invoke it
4. Possibly update workflow configuration

### What Flowspec Does That Opcode Doesn't

| Feature | Flowspec | Opcode Gap |
|---------|----------|------------|
| **Structured Workflow** | /flow:assess → /flow:operate | No workflow orchestration |
| **State Machine** | Task states with transitions | No task state management |
| **Backlog Integration** | Full MCP server for tasks | No task management |
| **Document Generation** | PRD, ADR, QA reports | No artifact generation |
| **Team Workflow** | Multi-agent orchestration | Single-agent focus |
| **Quality Gates** | Validation phase required | No quality enforcement |
| **Specialized Agents** | Backend/frontend/QA/security | Generic agents only |
| **Security Workflow** | Scan → triage → fix → report | Security scanner only |
| **Template System** | Copy templates to project | No project scaffolding |

### What Flowspec Does Better

#### 1. Development Lifecycle
```
assess → specify → research → plan → implement → validate → operate
```
Flowspec enforces a lifecycle. You can't jump to implementation without planning. Opcode lets you do anything anytime.

#### 2. Task Decomposition
```bash
# Flowspec's /flow:specify creates structured tasks
backlog task create "Implement feature X" \
  --ac "AC 1: User can..." \
  --ac "AC 2: System validates..." \
  -l backend
```
Tasks have acceptance criteria that get checked off progressively. Opcode agents just run commands.

#### 3. Multi-Agent Orchestration
```yaml
workflows:
  implement:
    agents:
      - frontend-engineer  # Runs first
      - backend-engineer   # Runs second
      - qa-engineer        # Reviews both
      - security-reviewer  # Final audit
```
Flowspec can chain agents in defined sequences. Opcode runs one agent at a time.

#### 4. Security Workflow
```bash
/sec:scan     # Find vulnerabilities
/sec:triage   # Prioritize findings
/sec:fix      # Generate patches
/sec:report   # Create audit report
```
Flowspec has a 12-skill security suite. Opcode has one security scanner agent.

#### 5. Documentation as First-Class
```
docs/
├── adr/
│   └── 001-technology-choice.md
├── prd/
│   └── feature-x-requirements.md
└── security/
    └── audit-report.md
```
Flowspec generates documentation artifacts automatically. Opcode doesn't generate docs.

#### 6. Team Standardization
```yaml
# flowspec_workflow.yml - Shared across team
states:
  - To Do
  - Assessed
  - Specified
  - Planned
  - In Implementation
  - Validated
  - Deployed
```
Teams can share workflow configurations. Opcode is inherently single-user.

---

## Architecture Comparison

### Opcode Architecture
```
┌──────────────────────────────────────────────────────────┐
│                    Tauri Application                     │
├──────────────────────────────────────────────────────────┤
│  React Frontend          │  Rust Backend                 │
│  - Tab management        │  - Claude process spawning    │
│  - Session UI            │  - SQLite storage             │
│  - Usage dashboard       │  - Checkpoint management      │
│  - Agent builder         │  - MCP server integration     │
│  - MCP manager           │  - Usage analytics            │
│                          │  - Web server (Axum)          │
├──────────────────────────────────────────────────────────┤
│                   Claude Code CLI                        │
│           (spawned as subprocess, streamed)              │
└──────────────────────────────────────────────────────────┘
```

### Flowspec Architecture
```
┌──────────────────────────────────────────────────────────┐
│                    Claude Code CLI                       │
├──────────────────────────────────────────────────────────┤
│  .claude/commands/       │  .claude/skills/              │
│  - /flow:* commands      │  - architect                  │
│  - /dev:* commands       │  - pm-planner                 │
│  - /sec:* commands       │  - qa-validator               │
│  - /arch:* commands      │  - security-* (12 skills)     │
│  - /qa:* commands        │                               │
│  - /ops:* commands       │                               │
├──────────────────────────────────────────────────────────┤
│  flowspec_workflow.yml   │  backlog.md MCP Server        │
│  - State definitions     │  - Task CRUD                  │
│  - Transitions           │  - Acceptance criteria        │
│  - Agent assignments     │  - Status tracking            │
├──────────────────────────────────────────────────────────┤
│  flowspec-cli (Python)    │  templates/                   │
│  - Project init          │  - Artifact templates         │
│  - Workflow validation   │  - Command templates          │
│  - Feature detection     │  - Skill templates            │
└──────────────────────────────────────────────────────────┘
```

---

## Use Case Analysis

### When to Use Opcode

1. **Individual developer wanting GUI experience**
   - You prefer clicking over typing commands
   - You want to see all projects/sessions visually

2. **Cost-conscious development**
   - You need to track API spend in real-time
   - You want usage analytics by project/model/date

3. **Experimentation and iteration**
   - You want to checkpoint and rollback freely
   - You fork sessions to try different approaches

4. **Quick custom agents**
   - You need a security scanner for this project
   - You want a git commit bot
   - You don't need workflow integration

5. **Session management**
   - You work on many projects simultaneously
   - You need to resume sessions from weeks ago
   - You want to see what you did last time

### When to Use Flowspec

1. **Team development with process**
   - Multiple developers need consistent workflow
   - You want enforceable quality gates
   - Documentation is a deliverable

2. **Complex feature development**
   - Features need specification before coding
   - Architecture decisions need documentation
   - Implementation needs QA and security review

3. **Security-focused development**
   - You need comprehensive security scanning
   - You want triage → fix → report workflow
   - Compliance documentation required

4. **Spec-driven development**
   - Product requirements → Technical spec → Implementation
   - Tasks have acceptance criteria
   - Work is tracked in backlog

5. **CI/CD integration**
   - Workflow validation in pipelines
   - Artifact generation for releases
   - Quality gate enforcement

---

## Integration Possibilities

### Using Both Together

```
┌─────────────────────────────────────────────────────────┐
│                    Developer Workflow                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Open Opcode → Browse projects → Select one          │
│                                                         │
│  2. In Opcode session → Run /flow:specify               │
│     (Flowspec creates tasks in backlog.md)              │
│                                                         │
│  3. Use Opcode's cost tracking while implementing       │
│                                                         │
│  4. Create checkpoint before major changes              │
│                                                         │
│  5. Run /flow:validate (Flowspec's QA/security)         │
│                                                         │
│  6. Use Opcode's usage dashboard for billing report     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Missing Integration Points

1. **Opcode could show Flowspec task state**
   - Display current workflow phase
   - Show acceptance criteria progress

2. **Flowspec could use Opcode's checkpoints**
   - Auto-checkpoint on workflow transitions
   - Rollback to phase boundaries

3. **Shared agent definitions**
   - Opcode's CC Agents → Flowspec skills
   - Convert between formats

---

## Critical Assessment

### Opcode Strengths
- **Immediate value**: Install, run, see all your sessions
- **Low friction**: No configuration, just works
- **Visual feedback**: See what's happening, what it costs
- **Recovery options**: Checkpoints and session history
- **Mobile access**: Web server mode (WIP)

### Opcode Weaknesses
- **No workflow**: Just wraps CLI, no orchestration
- **Single-agent**: Can't chain agents automatically
- **No documentation**: Doesn't generate artifacts
- **No team features**: Single-user only
- **Incomplete web mode**: Session isolation issues, no cancellation

### Flowspec Strengths
- **Process enforcement**: Can't skip steps
- **Multi-agent orchestration**: Chain agents in workflows
- **Documentation generation**: PRD, ADR, security reports
- **Security depth**: 12 specialized security skills
- **Team standardization**: Shared workflow configs
- **Backlog integration**: Tasks with acceptance criteria

### Flowspec Weaknesses
- **Learning curve**: Many commands to learn
- **No GUI**: Terminal-only
- **No session management**: Can't browse/resume sessions
- **No cost tracking**: Don't know what you're spending
- **No checkpoints**: Manual git commits only
- **Setup required**: Configure workflow.yml, install MCP server

---

## Recommendations

### For Flowspec

1. **Consider adding cost tracking**
   - Parse JSONL files for usage data
   - Display cost per workflow phase
   - Budget warnings

2. **Consider session management**
   - Allow resuming from specific tasks
   - Show session history per task

3. **Consider checkpoint integration**
   - Auto-checkpoint on phase transitions
   - Rollback to phase boundaries

4. **Consider a minimal TUI**
   - Task list view
   - Workflow state visualization
   - Not a full GUI, just task-focused

### For Opcode Adoption

1. **Evaluate CC Agent for complex workflows**
   - Security scanner agent is good
   - But can't chain: scan → triage → fix

2. **Use checkpoints strategically**
   - Before destructive operations
   - At logical boundaries

3. **Track costs proactively**
   - Set mental budgets per session
   - Review usage dashboard weekly

---

## Conclusion

**Opcode** is a well-built GUI wrapper for Claude Code that solves real usability problems: session management, cost tracking, checkpoints, and visual feedback. It's excellent for individual developers who want a friendlier interface.

**Flowspec** is a workflow orchestration system that enforces development process: specification before implementation, quality gates, security review, and documentation generation. It's excellent for teams that need consistent, documented development cycles.

**The honest answer**: If you're a solo developer who wants a nice GUI for Claude Code, use Opcode. If you're building software with a process (especially with security requirements), use Flowspec. If you want both usability and process, consider using them together.

---

## Appendix: Feature Matrix

| Feature | Opcode | Flowspec |
|---------|:------:|:--------:|
| GUI interface | Yes | No |
| CLI interface | No | Yes |
| Session browser | Yes | No |
| Session resume | Yes | Via backlog tasks |
| Cost tracking | Yes | No |
| Checkpoint system | Yes | No |
| Timeline visualization | Yes | No |
| Rollback/restore | Yes | Manual git |
| Fork sessions | Yes | No |
| Custom agents | Yes (CC Agents) | Yes (Skills) |
| Agent import/export | Yes (.opcode.json) | Yes (markdown) |
| Multi-agent orchestration | No | Yes |
| Workflow state machine | No | Yes |
| Task management | No | Yes (backlog.md) |
| Acceptance criteria | No | Yes |
| Document generation | No | Yes |
| MCP management | Yes (UI) | Yes (JSON) |
| CLAUDE.md editor | Yes | No |
| Security scanning | Yes (single agent) | Yes (12 skills) |
| Security workflow | No | Yes (scan/triage/fix/report) |
| Usage analytics | Yes | No |
| Mobile access | Yes (WIP) | No |
| Team workflows | No | Yes |
| Process enforcement | No | Yes |
| Template system | No | Yes |
| CI/CD integration | No | Yes |

---

*This review is based on analysis of the opcode repository at commit history available on 2025-12-12 and comparison with the flowspec repository.*
